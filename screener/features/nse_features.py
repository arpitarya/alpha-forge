"""Phase 2.4 — NSE-Specific Features.

Computes features from delivery %, bulk/block deals data fetched in Phase 1.
- Delivery percentage (institutional conviction signal)
- Bulk/block deal presence flags
- FII/DII net activity (when available)

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import NSE_SUPP_DIR

logger = logging.getLogger(__name__)

# Cache loaded NSE supplementary data
_delivery_cache: pd.DataFrame | None = None
_bulk_deals_cache: pd.DataFrame | None = None
_block_deals_cache: pd.DataFrame | None = None


def _load_delivery_data() -> pd.DataFrame | None:
    """Load and cache delivery percentage data."""
    global _delivery_cache
    if _delivery_cache is not None:
        return _delivery_cache

    filepath = NSE_SUPP_DIR / "delivery_data.csv"
    if not filepath.exists():
        logger.warning("Delivery data not found: %s", filepath)
        return None

    df = pd.read_csv(filepath)

    # Normalize column names
    df.columns = [c.strip().upper() for c in df.columns]

    # Parse date — nselib format is dd-Mon-yyyy or dd-mm-yyyy
    date_col = None
    for col in df.columns:
        if "DATE" in col:
            date_col = col
            break

    if date_col:
        df["DATE"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
    else:
        logger.warning("No date column found in delivery data. Columns: %s", list(df.columns))
        return None

    # Filter to EQ series only
    if "SERIES" in df.columns:
        df = df[df["SERIES"].str.strip() == "EQ"]

    _delivery_cache = df
    logger.info("Loaded delivery data: %d rows", len(df))
    return df


def _load_bulk_deals() -> pd.DataFrame | None:
    """Load and cache bulk deals data."""
    global _bulk_deals_cache
    if _bulk_deals_cache is not None:
        return _bulk_deals_cache

    filepath = NSE_SUPP_DIR / "bulk_deals.csv"
    if not filepath.exists():
        logger.warning("Bulk deals not found: %s", filepath)
        return None

    df = pd.read_csv(filepath)
    df.columns = [c.strip().upper() for c in df.columns]

    # Parse date
    date_col = None
    for col in df.columns:
        if "DATE" in col:
            date_col = col
            break

    if date_col:
        df["DATE"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    _bulk_deals_cache = df
    logger.info("Loaded bulk deals: %d rows", len(df))
    return df


def _load_block_deals() -> pd.DataFrame | None:
    """Load and cache block deals data."""
    global _block_deals_cache
    if _block_deals_cache is not None:
        return _block_deals_cache

    filepath = NSE_SUPP_DIR / "block_deals.csv"
    if not filepath.exists():
        logger.warning("Block deals not found: %s", filepath)
        return None

    df = pd.read_csv(filepath)
    df.columns = [c.strip().upper() for c in df.columns]

    date_col = None
    for col in df.columns:
        if "DATE" in col:
            date_col = col
            break

    if date_col:
        df["DATE"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    _block_deals_cache = df
    logger.info("Loaded block deals: %d rows", len(df))
    return df


def compute_delivery_features(
    stock_dates: pd.DatetimeIndex,
    symbol: str,
) -> pd.DataFrame:
    """Compute delivery percentage features for a stock.

    Args:
        stock_dates: DatetimeIndex of the stock's OHLCV data.
        symbol: NSE symbol (e.g., "RELIANCE").

    Returns:
        DataFrame with delivery features aligned to stock_dates.
    """
    features = pd.DataFrame(index=stock_dates)
    delivery_data = _load_delivery_data()

    if delivery_data is None:
        features["DELIVERY_PCT"] = np.nan
        features["DELIVERY_PCT_5D_AVG"] = np.nan
        return features

    # Filter for this symbol
    sym_col = None
    for col in delivery_data.columns:
        if "SYMBOL" in col:
            sym_col = col
            break

    if sym_col is None:
        features["DELIVERY_PCT"] = np.nan
        features["DELIVERY_PCT_5D_AVG"] = np.nan
        return features

    sym_data = delivery_data[delivery_data[sym_col].str.strip() == symbol].copy()

    if sym_data.empty or "DATE" not in sym_data.columns:
        features["DELIVERY_PCT"] = np.nan
        features["DELIVERY_PCT_5D_AVG"] = np.nan
        return features

    # Find the delivery percentage column
    deliv_col = None
    for col in sym_data.columns:
        if "DELIV" in col and "PER" in col:
            deliv_col = col
            break
        if "DELIV" in col and "PCT" in col:
            deliv_col = col
            break

    if deliv_col is None:
        features["DELIVERY_PCT"] = np.nan
        features["DELIVERY_PCT_5D_AVG"] = np.nan
        return features

    sym_data = sym_data.set_index("DATE")
    sym_data.index = pd.to_datetime(sym_data.index)
    deliv_series = pd.to_numeric(sym_data[deliv_col], errors="coerce")

    # Reindex to stock dates
    features["DELIVERY_PCT"] = deliv_series.reindex(stock_dates)
    features["DELIVERY_PCT_5D_AVG"] = features["DELIVERY_PCT"].rolling(window=5, min_periods=1).mean()

    return features


def compute_deal_features(
    stock_dates: pd.DatetimeIndex,
    symbol: str,
    lookback_days: int = 5,
) -> pd.DataFrame:
    """Compute bulk/block deal presence features.

    Args:
        stock_dates: DatetimeIndex of the stock's OHLCV data.
        symbol: NSE symbol (e.g., "RELIANCE").
        lookback_days: Number of days to look back for deal presence.

    Returns:
        DataFrame with binary deal flags.
    """
    features = pd.DataFrame(index=stock_dates)

    # Bulk deals
    bulk = _load_bulk_deals()
    if bulk is not None and "DATE" in bulk.columns:
        sym_col = None
        for col in bulk.columns:
            if "SYMBOL" in col:
                sym_col = col
                break

        if sym_col:
            sym_bulk = bulk[bulk[sym_col].str.strip() == symbol]
            bulk_dates = set(sym_bulk["DATE"].dropna().dt.normalize())

            # For each stock date, check if any bulk deal in last N days
            flags = []
            for dt in stock_dates:
                dt_norm = pd.Timestamp(dt).normalize()
                has_deal = any(
                    (dt_norm - pd.Timedelta(days=lookback_days)) <= d <= dt_norm
                    for d in bulk_dates
                )
                flags.append(int(has_deal))
            features["BULK_DEAL_FLAG"] = flags
        else:
            features["BULK_DEAL_FLAG"] = 0
    else:
        features["BULK_DEAL_FLAG"] = 0

    # Block deals
    block = _load_block_deals()
    if block is not None and "DATE" in block.columns:
        sym_col = None
        for col in block.columns:
            if "SYMBOL" in col:
                sym_col = col
                break

        if sym_col:
            sym_block = block[block[sym_col].str.strip() == symbol]
            block_dates = set(sym_block["DATE"].dropna().dt.normalize())

            flags = []
            for dt in stock_dates:
                dt_norm = pd.Timestamp(dt).normalize()
                has_deal = any(
                    (dt_norm - pd.Timedelta(days=lookback_days)) <= d <= dt_norm
                    for d in block_dates
                )
                flags.append(int(has_deal))
            features["BLOCK_DEAL_FLAG"] = flags
        else:
            features["BLOCK_DEAL_FLAG"] = 0
    else:
        features["BLOCK_DEAL_FLAG"] = 0

    return features


def compute_nse_features(
    df: pd.DataFrame,
    symbol: str,
) -> pd.DataFrame:
    """Compute all NSE-specific features for a stock.

    Args:
        df: OHLCV DataFrame with DatetimeIndex.
        symbol: NSE symbol (e.g., "RELIANCE").

    Returns:
        DataFrame with NSE features, same index as input.
    """
    dates = df.index

    delivery = compute_delivery_features(dates, symbol)
    deals = compute_deal_features(dates, symbol)

    result = pd.concat([delivery, deals], axis=1)
    logger.debug("Computed %d NSE features for %s", result.shape[1], symbol)
    return result


def clear_nse_cache() -> None:
    """Clear cached NSE supplementary data."""
    global _delivery_cache, _bulk_deals_cache, _block_deals_cache
    _delivery_cache = None
    _bulk_deals_cache = None
    _block_deals_cache = None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    from config import OHLCV_DIR

    symbol = "RELIANCE"
    filepath = OHLCV_DIR / f"{symbol}.parquet"
    if not filepath.exists():
        print(f"No data for {symbol}. Run fetch_ohlcv.py first.")
        sys.exit(1)

    df = pd.read_parquet(filepath)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    features = compute_nse_features(df, symbol)
    print(f"\n{symbol} NSE features:")
    print(f"  Shape: {features.shape}")
    print(f"  Columns: {list(features.columns)}")
    print(f"\nLast 5 rows:")
    print(features.tail(5).to_string())

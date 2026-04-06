"""Phase 2.3 — Fundamental Features.

Fetches PE, PB, market cap, 52-week return, and beta from yfinance.
Values are cached per-symbol since fundamentals update infrequently.

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import YFINANCE_SUFFIX

logger = logging.getLogger(__name__)

# Cache fundamental data per-symbol to avoid repeated yfinance API calls
_fundamental_cache: dict[str, dict] = {}


def _fetch_fundamentals(yf_symbol: str) -> dict:
    """Fetch fundamental data for a single stock from yfinance.

    Returns a dict with PE, PB, market_cap, market_cap_category, beta, 52w_return.
    """
    if yf_symbol in _fundamental_cache:
        return _fundamental_cache[yf_symbol]

    result: dict = {
        "PE_RATIO": np.nan,
        "PB_RATIO": np.nan,
        "MARKET_CAP": np.nan,
        "MARKET_CAP_CATEGORY": np.nan,
        "BETA": np.nan,
    }

    try:
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info

        result["PE_RATIO"] = info.get("trailingPE") or info.get("forwardPE") or np.nan
        result["PB_RATIO"] = info.get("priceToBook", np.nan)
        result["MARKET_CAP"] = info.get("marketCap", np.nan)
        result["BETA"] = info.get("beta", np.nan)

        # Categorize market cap (INR)
        mcap = result["MARKET_CAP"]
        if pd.notna(mcap):
            if mcap >= 200_000_000_000:  # 20,000 Cr+
                result["MARKET_CAP_CATEGORY"] = 3  # Large
            elif mcap >= 50_000_000_000:  # 5,000 Cr+
                result["MARKET_CAP_CATEGORY"] = 2  # Mid
            elif mcap >= 5_000_000_000:  # 500 Cr+
                result["MARKET_CAP_CATEGORY"] = 1  # Small
            else:
                result["MARKET_CAP_CATEGORY"] = 0  # Micro

    except Exception as e:
        logger.warning("Failed to fetch fundamentals for %s: %s", yf_symbol, e)

    _fundamental_cache[yf_symbol] = result
    return result


def compute_52w_return(close: pd.Series) -> pd.Series:
    """Compute rolling 252-day (52-week) return from Close prices."""
    return close.pct_change(periods=252)


def compute_fundamental_features(
    df: pd.DataFrame,
    symbol: str,
) -> pd.DataFrame:
    """Compute fundamental features for a stock.

    Args:
        df: OHLCV DataFrame with DatetimeIndex.
        symbol: NSE symbol (e.g., "RELIANCE") — will append .NS for yfinance.

    Returns:
        DataFrame with fundamental features, same index as input.
        Static values (PE, PB, etc.) are broadcast to all rows.
    """
    # Handle MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)

    yf_symbol = symbol + YFINANCE_SUFFIX if not symbol.endswith(YFINANCE_SUFFIX) else symbol

    features = pd.DataFrame(index=df.index)

    # Fetch static fundamentals
    fundamentals = _fetch_fundamentals(yf_symbol)
    features["PE_RATIO"] = fundamentals["PE_RATIO"]
    features["PB_RATIO"] = fundamentals["PB_RATIO"]
    features["MARKET_CAP"] = fundamentals["MARKET_CAP"]
    features["MARKET_CAP_CATEGORY"] = fundamentals["MARKET_CAP_CATEGORY"]
    features["BETA"] = fundamentals["BETA"]

    # Time-series fundamental: 52-week return
    features["RETURN_52W"] = compute_52w_return(df["Close"])

    logger.debug(
        "Fundamentals for %s: PE=%.1f PB=%.1f MCap=%s Beta=%.2f",
        symbol,
        fundamentals["PE_RATIO"],
        fundamentals["PB_RATIO"],
        f"{fundamentals['MARKET_CAP']:.0f}" if pd.notna(fundamentals["MARKET_CAP"]) else "N/A",
        fundamentals["BETA"],
    )

    return features


def clear_fundamental_cache() -> None:
    """Clear the cached fundamental data."""
    _fundamental_cache.clear()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    from config import OHLCV_DIR

    symbol = "RELIANCE"
    filepath = OHLCV_DIR / f"{symbol}.parquet"
    if not filepath.exists():
        print(f"No data for {symbol}. Run fetch_ohlcv.py first.")
        sys.exit(1)

    df = pd.read_parquet(filepath)
    features = compute_fundamental_features(df, symbol)
    print(f"\n{symbol} fundamental features:")
    print(f"  Shape: {features.shape}")
    print(f"  Columns: {list(features.columns)}")
    print(f"\nLast row:")
    print(features.iloc[-1].to_string())

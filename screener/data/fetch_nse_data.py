"""Step 1.3 + 1.4 — Supplementary NSE Data & Index Benchmarks.

Fetches delivery %, bulk/block deals, FII/DII activity from nselib,
and index benchmark data (NIFTY 50, SENSEX, BANK NIFTY, NIFTY IT) from yfinance.

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    INDEX_SYMBOLS,
    INDICES_DIR,
    NSE_REQUEST_DELAY,
    NSE_SUPP_DIR,
    OHLCV_HISTORY_YEARS,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ── Helper ────────────────────────────────────────────────────────────────────

def _nse_date(dt: datetime) -> str:
    """Format datetime as dd-mm-yyyy for nselib API."""
    return dt.strftime("%d-%m-%Y")


def _safe_nselib_call(func, *args, **kwargs) -> pd.DataFrame | None:
    """Wrap nselib call with error handling and rate-limit delay."""
    try:
        result = func(*args, **kwargs)
        time.sleep(NSE_REQUEST_DELAY)
        if isinstance(result, pd.DataFrame) and not result.empty:
            return result
        return None
    except Exception as e:
        logger.warning("nselib call %s failed: %s", func.__name__, e)
        time.sleep(NSE_REQUEST_DELAY)
        return None


# ── Step 1.3: Supplementary NSE Data ─────────────────────────────────────────

def fetch_delivery_data(from_date: str, to_date: str) -> pd.DataFrame | None:
    """Fetch delivery percentage data for a date range.

    Args:
        from_date: Start date in dd-mm-yyyy format.
        to_date: End date in dd-mm-yyyy format.
    """
    from nselib.capital_market import price_volume_and_deliverable_position_data

    logger.info("Fetching delivery pct data: %s to %s", from_date, to_date)
    # Try with positional args first, then keyword if that fails
    df = _safe_nselib_call(price_volume_and_deliverable_position_data, from_date, to_date)
    if df is None:
        # Some nselib versions require symbol param
        from nselib.capital_market import bhav_copy_with_delivery
        logger.info("Falling back to bhav_copy_with_delivery")
        df = _safe_nselib_call(bhav_copy_with_delivery, from_date)
    if df is not None:
        logger.info("Delivery data: %d rows", len(df))
    return df


def fetch_bulk_deals(from_date: str, to_date: str) -> pd.DataFrame | None:
    """Fetch bulk deal data."""
    from nselib.capital_market import bulk_deal_data

    logger.info("Fetching bulk deals: %s to %s", from_date, to_date)
    df = _safe_nselib_call(bulk_deal_data, from_date, to_date)
    if df is not None:
        logger.info("Bulk deals: %d rows", len(df))
    return df


def fetch_block_deals(from_date: str, to_date: str) -> pd.DataFrame | None:
    """Fetch block deal data."""
    from nselib.capital_market import block_deals_data

    logger.info("Fetching block deals: %s to %s", from_date, to_date)
    df = _safe_nselib_call(block_deals_data, from_date, to_date)
    if df is not None:
        logger.info("Block deals: %d rows", len(df))
    return df


def fetch_fii_dii_activity(from_date: str, to_date: str) -> pd.DataFrame | None:
    """Fetch FII/DII trading activity data.

    Note: nselib may not expose fii_dii_trading_activity in all versions.
    Falls back gracefully if unavailable.
    """
    try:
        from nselib.capital_market import fii_dii_trading_activity
    except ImportError:
        logger.warning(
            "fii_dii_trading_activity not available in this nselib version. "
            "Skipping FII/DII data. Consider using jugaad-data as fallback."
        )
        return None

    logger.info("Fetching FII/DII activity: %s to %s", from_date, to_date)
    df = _safe_nselib_call(fii_dii_trading_activity, from_date, to_date)
    if df is not None:
        logger.info("FII/DII data: %d rows", len(df))
    return df


def fetch_all_nse_supplementary(days_back: int = 30) -> dict[str, pd.DataFrame | None]:
    """Fetch all supplementary NSE data for the last N days.

    Args:
        days_back: Number of calendar days to look back.

    Returns:
        Dict mapping data type to DataFrame.
    """
    end = datetime.now()
    start = end - timedelta(days=days_back)
    from_date = _nse_date(start)
    to_date = _nse_date(end)

    results: dict[str, pd.DataFrame | None] = {}

    # Delivery %
    results["delivery"] = fetch_delivery_data(from_date, to_date)
    if results["delivery"] is not None:
        results["delivery"].to_csv(NSE_SUPP_DIR / "delivery_data.csv", index=False)
        logger.info("Saved delivery data")

    # Bulk deals
    results["bulk_deals"] = fetch_bulk_deals(from_date, to_date)
    if results["bulk_deals"] is not None:
        results["bulk_deals"].to_csv(NSE_SUPP_DIR / "bulk_deals.csv", index=False)
        logger.info("Saved bulk deals")

    # Block deals
    results["block_deals"] = fetch_block_deals(from_date, to_date)
    if results["block_deals"] is not None:
        results["block_deals"].to_csv(NSE_SUPP_DIR / "block_deals.csv", index=False)
        logger.info("Saved block deals")

    # FII/DII
    results["fii_dii"] = fetch_fii_dii_activity(from_date, to_date)
    if results["fii_dii"] is not None:
        results["fii_dii"].to_csv(NSE_SUPP_DIR / "fii_dii_activity.csv", index=False)
        logger.info("Saved FII/DII activity")

    return results


# ── Step 1.4: Index Benchmarks ───────────────────────────────────────────────

def fetch_index_data() -> dict[str, pd.DataFrame]:
    """Download historical OHLCV for benchmark indices.

    Returns dict mapping index name to DataFrame.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=OHLCV_HISTORY_YEARS * 365)

    results: dict[str, pd.DataFrame] = {}

    for name, symbol in INDEX_SYMBOLS.items():
        logger.info("Downloading index: %s (%s)", name, symbol)
        try:
            data = yf.download(
                symbol,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=False,
            )
            if not data.empty:
                filepath = INDICES_DIR / f"{name}.parquet"
                data.to_parquet(filepath, engine="pyarrow")
                results[name] = data
                logger.info("Saved %s: %d rows → %s", name, len(data), filepath)
            else:
                logger.warning("No data returned for %s", name)
        except Exception as e:
            logger.error("Failed to download %s: %s", name, e)

    return results


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch supplementary NSE data and index benchmarks")
    parser.add_argument("--indices-only", action="store_true",
                        help="Only download index benchmark data")
    parser.add_argument("--nse-only", action="store_true",
                        help="Only download supplementary NSE data")
    parser.add_argument("--days", type=int, default=30,
                        help="Days of NSE supplementary data to fetch (default: 30)")
    args = parser.parse_args()

    if args.indices_only:
        idx = fetch_index_data()
        print(f"\nDownloaded {len(idx)} indices: {list(idx.keys())}")
    elif args.nse_only:
        nse = fetch_all_nse_supplementary(days_back=args.days)
        fetched = [k for k, v in nse.items() if v is not None]
        print(f"\nFetched NSE data: {fetched}")
    else:
        # Fetch everything
        idx = fetch_index_data()
        print(f"\nIndices downloaded: {len(idx)} — {list(idx.keys())}")

        nse = fetch_all_nse_supplementary(days_back=args.days)
        fetched = [k for k, v in nse.items() if v is not None]
        print(f"NSE supplementary data fetched: {fetched}")

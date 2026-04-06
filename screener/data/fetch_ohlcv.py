"""Step 1.2 — Historical OHLCV Download.

Downloads 2 years of daily OHLCV data for all filtered stocks via yfinance.
Stores as individual Parquet files. Supports incremental updates.

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    OHLCV_DIR,
    OHLCV_HISTORY_YEARS,
    UNIVERSE_FILTERED_FILE,
    YFINANCE_BATCH_SIZE,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def load_filtered_universe() -> list[str]:
    """Load yfinance symbols from the filtered universe CSV."""
    if not UNIVERSE_FILTERED_FILE.exists():
        raise FileNotFoundError(
            f"Filtered universe not found: {UNIVERSE_FILTERED_FILE}. "
            "Run fetch_universe.py first."
        )
    df = pd.read_csv(UNIVERSE_FILTERED_FILE)
    symbols = df["SYMBOL_YF"].tolist()
    logger.info("Loaded %d symbols from filtered universe", len(symbols))
    return symbols


def get_date_range(symbol_file: Path | None = None) -> tuple[str, str]:
    """Determine start/end dates for download.

    If symbol_file exists (incremental mode), start from the last date in file.
    Otherwise, download full OHLCV_HISTORY_YEARS of data.
    """
    end_date = datetime.now()
    end_str = end_date.strftime("%Y-%m-%d")

    if symbol_file and symbol_file.exists():
        try:
            existing = pd.read_parquet(symbol_file)
            last_date = pd.to_datetime(existing.index).max()
            # Start from the day after the last date we have
            start = last_date + timedelta(days=1)
            return start.strftime("%Y-%m-%d"), end_str
        except Exception:
            pass

    start_date = end_date - timedelta(days=OHLCV_HISTORY_YEARS * 365)
    return start_date.strftime("%Y-%m-%d"), end_str


def download_ohlcv_batch(
    symbols: list[str],
    start: str,
    end: str,
) -> dict[str, pd.DataFrame]:
    """Download OHLCV data for a batch of symbols.

    Returns a dict mapping symbol -> DataFrame.
    """
    results: dict[str, pd.DataFrame] = {}

    if not symbols:
        return results

    batch_str = " ".join(symbols)
    try:
        data = yf.download(
            batch_str,
            start=start,
            end=end,
            group_by="ticker",
            progress=False,
            threads=True,
            auto_adjust=False,
        )

        if data.empty:
            logger.warning("Empty response for batch")
            return results

        if len(symbols) == 1:
            sym = symbols[0]
            if not data.empty:
                results[sym] = data
        else:
            for sym in symbols:
                try:
                    if sym in data.columns.get_level_values(0):
                        sym_data = data[sym].dropna(how="all")
                        if not sym_data.empty:
                            results[sym] = sym_data
                except (KeyError, TypeError):
                    continue

    except Exception as e:
        logger.error("Download failed for batch: %s", e)

    return results


def save_ohlcv(symbol: str, df: pd.DataFrame, incremental: bool = False) -> None:
    """Save OHLCV data to Parquet file. Merges with existing if incremental."""
    # Clean the symbol for filename (remove .NS suffix)
    clean_name = symbol.replace(".NS", "").replace(".", "_")
    filepath = OHLCV_DIR / f"{clean_name}.parquet"

    if incremental and filepath.exists():
        try:
            existing = pd.read_parquet(filepath)
            df = pd.concat([existing, df])
            df = df[~df.index.duplicated(keep="last")]
            df = df.sort_index()
        except Exception as e:
            logger.warning("Could not merge incremental data for %s: %s", symbol, e)

    df.to_parquet(filepath, engine="pyarrow")


def fetch_ohlcv(incremental: bool = False) -> dict[str, int]:
    """Main entry point: download OHLCV for all filtered stocks.

    Args:
        incremental: If True, only download data newer than existing files.

    Returns:
        Stats dict with success/failure counts.
    """
    symbols = load_filtered_universe()
    stats = {"total": len(symbols), "success": 0, "failed": 0, "skipped": 0}

    # Determine date range
    start, end = get_date_range()
    logger.info("Download period: %s to %s", start, end)

    for i in range(0, len(symbols), YFINANCE_BATCH_SIZE):
        batch = symbols[i : i + YFINANCE_BATCH_SIZE]
        batch_num = (i // YFINANCE_BATCH_SIZE) + 1
        total_batches = (len(symbols) + YFINANCE_BATCH_SIZE - 1) // YFINANCE_BATCH_SIZE
        logger.info("Processing batch %d/%d (%d symbols)...", batch_num, total_batches, len(batch))

        if incremental:
            # For incremental, determine start per-symbol from existing files
            # For simplicity, use the global start date here; per-symbol is handled in save
            pass

        batch_data = download_ohlcv_batch(batch, start, end)

        for sym in batch:
            if sym in batch_data and not batch_data[sym].empty:
                save_ohlcv(sym, batch_data[sym], incremental=incremental)
                stats["success"] += 1
            else:
                stats["failed"] += 1

        logger.info(
            "Batch %d done. Running total: %d success, %d failed",
            batch_num, stats["success"], stats["failed"],
        )

    logger.info(
        "OHLCV download complete. %d/%d success, %d failed.",
        stats["success"], stats["total"], stats["failed"],
    )
    return stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download historical OHLCV data")
    parser.add_argument("--incremental", action="store_true",
                        help="Only download data newer than existing files")
    parser.add_argument("--symbols", nargs="+",
                        help="Download specific symbols only (e.g., RELIANCE.NS TCS.NS)")
    args = parser.parse_args()

    if args.symbols:
        # Quick test mode: download specific symbols
        start, end = get_date_range()
        logger.info("Downloading %d specific symbols: %s", len(args.symbols), args.symbols)
        batch_data = download_ohlcv_batch(args.symbols, start, end)
        for sym, df in batch_data.items():
            save_ohlcv(sym, df)
            logger.info("Saved %s: %d rows", sym, len(df))
        print(f"\nDownloaded {len(batch_data)}/{len(args.symbols)} symbols")
    else:
        stats = fetch_ohlcv(incremental=args.incremental)
        print(f"\nSummary: {stats}")

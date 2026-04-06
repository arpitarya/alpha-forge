"""Step 1.1 — Stock Universe Fetcher.

Fetches all NSE-listed equities, filters to EQ series,
maps to yfinance format, applies volume filter, and saves CSVs.

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from nselib.capital_market import equity_list

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
from config import (
    MIN_AVG_VOLUME_90D,
    UNIVERSE_FILE,
    UNIVERSE_FILTERED_FILE,
    VALID_SERIES,
    YFINANCE_BATCH_SIZE,
    YFINANCE_SUFFIX,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def fetch_nse_equity_list() -> pd.DataFrame:
    """Fetch the full list of NSE-listed equities via nselib."""
    logger.info("Fetching NSE equity list...")
    df = equity_list()
    logger.info("Total NSE-listed securities: %d", len(df))
    return df


def filter_eq_series(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only regular equity (EQ) series."""
    # nselib columns may vary — find the series column
    series_col = None
    for col in df.columns:
        if "series" in col.lower():
            series_col = col
            break

    if series_col is None:
        logger.warning("No 'series' column found. Columns: %s. Keeping all rows.", list(df.columns))
        return df

    filtered = df[df[series_col].str.strip().isin(VALID_SERIES)].copy()
    logger.info("After EQ series filter: %d stocks", len(filtered))
    return filtered


def map_to_yfinance_symbols(df: pd.DataFrame) -> pd.DataFrame:
    """Add yfinance-compatible symbol column (SYMBOL.NS)."""
    symbol_col = None
    for col in df.columns:
        if "symbol" in col.lower():
            symbol_col = col
            break

    if symbol_col is None:
        raise ValueError(f"No 'symbol' column found. Columns: {list(df.columns)}")

    df = df.copy()
    df["SYMBOL_NSE"] = df[symbol_col].str.strip()
    df["SYMBOL_YF"] = df["SYMBOL_NSE"] + YFINANCE_SUFFIX
    return df


def apply_volume_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out stocks with avg daily volume < threshold over 90 days.

    Downloads recent volume data in batches via yfinance.
    """
    symbols = df["SYMBOL_YF"].tolist()
    logger.info("Checking 90-day avg volume for %d stocks (batch size: %d)...", len(symbols), YFINANCE_BATCH_SIZE)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=120)  # ~90 trading days

    avg_volumes: dict[str, float] = {}
    for i in range(0, len(symbols), YFINANCE_BATCH_SIZE):
        batch = symbols[i : i + YFINANCE_BATCH_SIZE]
        batch_str = " ".join(batch)
        logger.info("Downloading volume batch %d/%d (%d symbols)...",
                     (i // YFINANCE_BATCH_SIZE) + 1,
                     (len(symbols) + YFINANCE_BATCH_SIZE - 1) // YFINANCE_BATCH_SIZE,
                     len(batch))
        try:
            data = yf.download(
                batch_str,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                group_by="ticker",
                progress=False,
                threads=True,
            )
            if len(batch) == 1:
                # Single ticker: data columns are flat (Open, High, ..., Volume)
                sym = batch[0]
                if "Volume" in data.columns:
                    vol = data["Volume"].mean()
                    if pd.notna(vol):
                        avg_volumes[sym] = float(vol)
            else:
                # Multi-ticker: MultiIndex columns (ticker, field)
                for sym in batch:
                    try:
                        vol_series = data[sym]["Volume"] if sym in data.columns.get_level_values(0) else None
                        if vol_series is not None:
                            vol = vol_series.mean()
                            if pd.notna(vol):
                                avg_volumes[sym] = float(vol)
                    except (KeyError, TypeError):
                        continue
        except Exception as e:
            logger.warning("Volume download failed for batch starting at %d: %s", i, e)
            continue

    logger.info("Got volume data for %d / %d symbols", len(avg_volumes), len(symbols))

    df = df.copy()
    df["AVG_VOLUME_90D"] = df["SYMBOL_YF"].map(avg_volumes)

    # Keep stocks that pass the volume filter OR where we couldn't get volume data
    # (we'd rather include than exclude when data is missing)
    before = len(df)
    filtered = df[
        (df["AVG_VOLUME_90D"].isna()) | (df["AVG_VOLUME_90D"] >= MIN_AVG_VOLUME_90D)
    ].copy()
    logger.info(
        "Volume filter (>=%s): %d → %d stocks (%d removed)",
        f"{MIN_AVG_VOLUME_90D:,}",
        before,
        len(filtered),
        before - len(filtered),
    )
    return filtered


def fetch_universe(skip_volume_filter: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Main entry point: fetch, filter, and save stock universe.

    Returns (full_universe, filtered_universe) DataFrames.
    """
    # Step 1: Fetch all NSE equities
    raw = fetch_nse_equity_list()

    # Step 2: Filter to EQ series
    eq_only = filter_eq_series(raw)

    # Step 3: Map to yfinance symbols
    mapped = map_to_yfinance_symbols(eq_only)

    # Step 4: Save full universe
    mapped.to_csv(UNIVERSE_FILE, index=False)
    logger.info("Saved full universe: %s (%d stocks)", UNIVERSE_FILE, len(mapped))

    # Step 5: Apply volume filter
    if skip_volume_filter:
        filtered = mapped.copy()
        logger.info("Volume filter skipped.")
    else:
        filtered = apply_volume_filter(mapped)

    # Step 6: Save filtered universe
    filtered.to_csv(UNIVERSE_FILTERED_FILE, index=False)
    logger.info("Saved filtered universe: %s (%d stocks)", UNIVERSE_FILTERED_FILE, len(filtered))

    return mapped, filtered


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch and filter NSE stock universe")
    parser.add_argument("--skip-volume-filter", action="store_true",
                        help="Skip the 90-day volume filter (faster, for testing)")
    args = parser.parse_args()

    full, filtered = fetch_universe(skip_volume_filter=args.skip_volume_filter)
    print(f"\nSummary:")
    print(f"  Total NSE EQ stocks: {len(full)}")
    print(f"  After volume filter: {len(filtered)}")

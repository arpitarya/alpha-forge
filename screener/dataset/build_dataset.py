"""Phase 3.2 — Dataset Assembly.

Combines features (Phase 2) + labels (Phase 3.1) into a single ML-ready dataset.
One row per stock-day with all features, metadata, and target labels.

Data quality rules:
- Drop rows with >30% NaN features (indicator warmup period)
- No lookahead bias: features use data up to day T, labels use T+1 to T+5
- Survivorship bias acknowledged as limitation with free data sources
- Rows without valid labels (last 5 days per stock) are excluded

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    BASE_DIR,
    OHLCV_DIR,
    UNIVERSE_FILTERED_FILE,
)

logger = logging.getLogger(__name__)

# Output paths
DATASET_OUTPUT_DIR = BASE_DIR / "dataset" / "output"
DATASET_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATASET_FILE = DATASET_OUTPUT_DIR / "dataset.parquet"
DATASET_STATS_FILE = DATASET_OUTPUT_DIR / "dataset_stats.txt"

# Quality thresholds
MAX_NAN_FEATURE_PCT = 0.30  # Drop rows with >30% NaN features


def _get_available_symbols() -> list[str]:
    """Get symbols that have OHLCV parquet files downloaded."""
    parquet_files = list(OHLCV_DIR.glob("*.parquet"))
    symbols = [f.stem for f in parquet_files]
    logger.info("Found %d symbols with OHLCV data", len(symbols))
    return sorted(symbols)


def build_single_stock_dataset(
    symbol: str,
    include_fundamentals: bool = True,
    include_nse: bool = True,
) -> pd.DataFrame | None:
    """Build a complete feature + label row-set for one stock.

    Args:
        symbol: NSE symbol (e.g., "RELIANCE").
        include_fundamentals: Whether to fetch fundamentals from yfinance.
        include_nse: Whether to include NSE-specific features.

    Returns:
        DataFrame with features + labels + metadata, or None on failure.
    """
    # Import here to avoid circular imports at module level
    from features.build_features import build_features_for_symbol
    from dataset.labeler import compute_labels

    # Build features
    features = build_features_for_symbol(
        symbol,
        include_fundamentals=include_fundamentals,
        include_nse=include_nse,
    )
    if features is None:
        return None

    # Load OHLCV for labels
    filepath = OHLCV_DIR / f"{symbol}.parquet"
    ohlcv = pd.read_parquet(filepath)
    if isinstance(ohlcv.columns, pd.MultiIndex):
        ohlcv.columns = ohlcv.columns.get_level_values(0)

    # Compute labels
    labels = compute_labels(ohlcv)

    # Merge features + labels on index (Date)
    dataset = pd.concat([features, labels], axis=1)

    # Add metadata
    # SYMBOL column already added by build_features_for_symbol
    if "SYMBOL" not in dataset.columns:
        dataset["SYMBOL"] = symbol

    return dataset


def apply_quality_filters(
    df: pd.DataFrame,
    max_nan_pct: float = MAX_NAN_FEATURE_PCT,
) -> pd.DataFrame:
    """Apply data quality rules to the assembled dataset.

    Rules:
    1. Drop rows where the target label is NaN (last N days per stock)
    2. Drop rows with >max_nan_pct NaN across feature columns
    3. Log statistics about dropped rows

    Args:
        df: Raw assembled dataset.
        max_nan_pct: Maximum fraction of NaN features allowed per row.

    Returns:
        Cleaned dataset.
    """
    initial_rows = len(df)

    # Identify feature columns (everything except metadata and label columns)
    meta_cols = {"SYMBOL", "FORWARD_RETURN_5D", "TARGET_5PCT_5D"}
    feature_cols = [c for c in df.columns if c not in meta_cols]

    # Rule 1: Drop rows without valid labels
    before = len(df)
    df = df.dropna(subset=["TARGET_5PCT_5D"])
    dropped_no_label = before - len(df)
    logger.info("Dropped %d rows with no target label (last %d days per stock)",
                dropped_no_label, 5)

    # Rule 2: Drop rows with too many NaN features
    before = len(df)
    nan_frac = df[feature_cols].isna().sum(axis=1) / len(feature_cols)
    df = df[nan_frac <= max_nan_pct].copy()
    dropped_nan = before - len(df)
    logger.info("Dropped %d rows with >%.0f%% NaN features (warmup period)",
                dropped_nan, max_nan_pct * 100)

    logger.info(
        "Quality filter: %d → %d rows (dropped %d total: %d no-label, %d high-NaN)",
        initial_rows, len(df), initial_rows - len(df), dropped_no_label, dropped_nan,
    )

    return df


def compute_dataset_stats(df: pd.DataFrame) -> str:
    """Compute and format dataset statistics as a text report."""
    meta_cols = {"SYMBOL", "FORWARD_RETURN_5D", "TARGET_5PCT_5D"}
    feature_cols = [c for c in df.columns if c not in meta_cols]

    n_positive = (df["TARGET_5PCT_5D"] == 1).sum()
    n_negative = (df["TARGET_5PCT_5D"] == 0).sum()
    total = n_positive + n_negative

    lines = [
        "AlphaForge Screener — Dataset Statistics",
        "=" * 50,
        f"Total rows:          {len(df):,}",
        f"Unique symbols:      {df['SYMBOL'].nunique()}",
        f"Feature columns:     {len(feature_cols)}",
        f"Date range:          {df.index.min()} → {df.index.max()}",
        "",
        "Target Distribution:",
        f"  Positive (>5%%):    {n_positive:,} ({n_positive / total * 100:.1f}%)" if total else "  N/A",
        f"  Negative (<=5%%):   {n_negative:,} ({n_negative / total * 100:.1f}%)" if total else "  N/A",
        f"  Class ratio:       1:{n_negative / n_positive:.1f}" if n_positive > 0 else "  N/A",
        "",
        "Forward Return Stats:",
        f"  Mean:   {df['FORWARD_RETURN_5D'].mean():.4f}",
        f"  Median: {df['FORWARD_RETURN_5D'].median():.4f}",
        f"  Std:    {df['FORWARD_RETURN_5D'].std():.4f}",
        f"  Min:    {df['FORWARD_RETURN_5D'].min():.4f}",
        f"  Max:    {df['FORWARD_RETURN_5D'].max():.4f}",
        "",
        "NaN Coverage (per feature):",
    ]

    # NaN stats per feature
    nan_counts = df[feature_cols].isna().sum().sort_values(ascending=False)
    for col in nan_counts.head(15).index:
        pct = nan_counts[col] / len(df) * 100
        lines.append(f"  {col:35s} {nan_counts[col]:5d} ({pct:.1f}%)")
    if len(nan_counts) > 15:
        lines.append(f"  ... and {len(nan_counts) - 15} more features")

    overall_nan = df[feature_cols].isna().sum().sum() / (len(df) * len(feature_cols)) * 100
    lines.append(f"\n  Overall NaN rate:  {overall_nan:.2f}%")

    # Per-symbol stats
    lines.append("\nPer-Symbol Row Counts (top 10):")
    sym_counts = df["SYMBOL"].value_counts().head(10)
    for sym, count in sym_counts.items():
        lines.append(f"  {sym:20s} {count:5d} rows")

    return "\n".join(lines)


def build_dataset(
    symbols: list[str] | None = None,
    max_symbols: int | None = None,
    include_fundamentals: bool = True,
    include_nse: bool = True,
    save: bool = True,
) -> pd.DataFrame:
    """Build the full ML dataset for all available stocks.

    Args:
        symbols: Specific symbols to process. If None, uses all available.
        max_symbols: Limit number of symbols (for testing).
        include_fundamentals: Whether to fetch fundamentals.
        include_nse: Whether to include NSE features.
        save: Whether to save dataset to parquet and stats to txt.

    Returns:
        Cleaned, ML-ready DataFrame.
    """
    if symbols is None:
        symbols = _get_available_symbols()

    if max_symbols:
        symbols = symbols[:max_symbols]

    logger.info("Building dataset for %d symbols...", len(symbols))
    all_datasets: list[pd.DataFrame] = []
    success = 0
    failed = 0

    for i, symbol in enumerate(symbols):
        if (i + 1) % 50 == 0 or i == 0:
            logger.info("Progress: %d/%d (success: %d, failed: %d)",
                        i + 1, len(symbols), success, failed)

        result = build_single_stock_dataset(
            symbol,
            include_fundamentals=include_fundamentals,
            include_nse=include_nse,
        )
        if result is not None:
            all_datasets.append(result)
            success += 1
        else:
            failed += 1

    if not all_datasets:
        logger.error("No datasets built. Check data availability.")
        return pd.DataFrame()

    logger.info("Concatenating %d stock datasets...", len(all_datasets))
    raw_dataset = pd.concat(all_datasets, axis=0)
    logger.info("Raw dataset: %d rows × %d columns", raw_dataset.shape[0], raw_dataset.shape[1])

    # Apply quality filters
    dataset = apply_quality_filters(raw_dataset)

    # Sort by date then symbol for reproducibility
    dataset = dataset.sort_index()

    if save and not dataset.empty:
        # Save dataset
        dataset.to_parquet(DATASET_FILE, engine="pyarrow")
        logger.info("Saved dataset: %s (%d rows)", DATASET_FILE, len(dataset))

        # Save stats
        stats = compute_dataset_stats(dataset)
        DATASET_STATS_FILE.write_text(stats)
        logger.info("Saved stats: %s", DATASET_STATS_FILE)

    logger.info(
        "Dataset build complete. %d symbols, %d rows, %d columns.",
        dataset["SYMBOL"].nunique() if not dataset.empty else 0,
        len(dataset),
        dataset.shape[1],
    )

    return dataset


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Build ML dataset for screener")
    parser.add_argument("--symbols", nargs="+", help="Specific symbols to process")
    parser.add_argument("--max-symbols", type=int, help="Limit number of symbols")
    parser.add_argument("--no-fundamentals", action="store_true",
                        help="Skip yfinance fundamentals (faster)")
    parser.add_argument("--no-nse", action="store_true",
                        help="Skip NSE-specific features")
    parser.add_argument("--no-save", action="store_true",
                        help="Don't save to disk")
    args = parser.parse_args()

    dataset = build_dataset(
        symbols=args.symbols,
        max_symbols=args.max_symbols,
        include_fundamentals=not args.no_fundamentals,
        include_nse=not args.no_nse,
        save=not args.no_save,
    )

    if not dataset.empty:
        print(f"\nDataset Summary:")
        print(f"  Shape: {dataset.shape}")
        print(f"  Symbols: {dataset['SYMBOL'].nunique()}")
        print(f"  Date range: {dataset.index.min()} → {dataset.index.max()}")

        n_pos = (dataset["TARGET_5PCT_5D"] == 1).sum()
        n_neg = (dataset["TARGET_5PCT_5D"] == 0).sum()
        total = n_pos + n_neg
        print(f"  Positive: {n_pos} ({n_pos / total * 100:.1f}%)")
        print(f"  Negative: {n_neg} ({n_neg / total * 100:.1f}%)")
        print(f"  Saved to: {DATASET_FILE}")
    else:
        print("Dataset is empty. Check data availability.")

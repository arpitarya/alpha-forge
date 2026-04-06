"""Phase 3.1 — Target Variable Labeler.

Computes forward-looking labels for the ML model:
- Classification: Did the stock return >5% in the next 5 trading days? (binary 1/0)
- Regression: Actual 5-day forward return (for ranking)

Uses Adjusted Close to handle splits/dividends correctly.
Last N rows per stock are excluded since no future data is available.

⚠️ CRITICAL: Labels use FUTURE data — they must NEVER leak into features.
   Features use data up to day T; labels use data from day T+1 to T+5.

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import OHLCV_DIR, TARGET_FORWARD_DAYS, TARGET_RETURN_THRESHOLD

logger = logging.getLogger(__name__)


def compute_forward_return(
    adj_close: pd.Series,
    forward_days: int = TARGET_FORWARD_DAYS,
) -> pd.Series:
    """Compute the N-day forward return from Adjusted Close prices.

    Forward return at day T = (AdjClose[T + forward_days] - AdjClose[T]) / AdjClose[T]

    The last `forward_days` rows will be NaN (no future data).

    Args:
        adj_close: Adjusted Close price series with DatetimeIndex.
        forward_days: Number of trading days to look ahead.

    Returns:
        Series of forward returns (NaN for last N rows).
    """
    future_close = adj_close.shift(-forward_days)
    forward_return = (future_close - adj_close) / adj_close.replace(0, np.nan)
    return forward_return


def compute_classification_label(
    forward_return: pd.Series,
    threshold: float = TARGET_RETURN_THRESHOLD,
) -> pd.Series:
    """Convert forward return to binary classification label.

    1 = stock returned > threshold in forward period
    0 = stock returned <= threshold
    NaN = no forward data available

    Args:
        forward_return: Series of forward returns.
        threshold: Minimum return for positive label (default: 0.05 = 5%).

    Returns:
        Series of binary labels (0/1/NaN).
    """
    label = pd.Series(np.nan, index=forward_return.index, dtype="Float64")
    valid = forward_return.notna()
    label[valid] = (forward_return[valid] > threshold).astype(int)
    return label


def compute_labels(
    df: pd.DataFrame,
    forward_days: int = TARGET_FORWARD_DAYS,
    threshold: float = TARGET_RETURN_THRESHOLD,
) -> pd.DataFrame:
    """Compute all labels for a single stock's OHLCV DataFrame.

    Args:
        df: OHLCV DataFrame with 'Adj Close' column and DatetimeIndex.
        forward_days: Number of trading days to look ahead.
        threshold: Minimum return for positive classification label.

    Returns:
        DataFrame with columns:
        - FORWARD_RETURN_5D: actual 5-day forward return (float)
        - TARGET_5PCT_5D: binary label (1 if return > 5%, else 0)
    """
    # Handle MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)

    if "Adj Close" not in df.columns:
        raise ValueError("DataFrame must have 'Adj Close' column for label computation")

    adj_close = df["Adj Close"]

    labels = pd.DataFrame(index=df.index)
    labels["FORWARD_RETURN_5D"] = compute_forward_return(adj_close, forward_days)
    labels["TARGET_5PCT_5D"] = compute_classification_label(
        labels["FORWARD_RETURN_5D"], threshold
    )

    n_positive = (labels["TARGET_5PCT_5D"] == 1).sum()
    n_negative = (labels["TARGET_5PCT_5D"] == 0).sum()
    n_nan = labels["TARGET_5PCT_5D"].isna().sum()
    total_valid = n_positive + n_negative

    logger.debug(
        "Labels: %d positive (%.1f%%), %d negative, %d NaN (last %d rows)",
        n_positive,
        (n_positive / total_valid * 100) if total_valid > 0 else 0,
        n_negative,
        n_nan,
        forward_days,
    )

    return labels


def compute_labels_for_symbol(symbol: str) -> pd.DataFrame | None:
    """Compute labels for a single stock by loading its OHLCV parquet.

    Args:
        symbol: NSE symbol (e.g., "RELIANCE").

    Returns:
        DataFrame with label columns, or None if data not found.
    """
    filepath = OHLCV_DIR / f"{symbol}.parquet"
    if not filepath.exists():
        logger.warning("No OHLCV data for %s", symbol)
        return None

    df = pd.read_parquet(filepath)
    return compute_labels(df)


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Compute target labels for screener")
    parser.add_argument("--symbol", type=str, default="RELIANCE",
                        help="Symbol to compute labels for")
    args = parser.parse_args()

    labels = compute_labels_for_symbol(args.symbol)
    if labels is None:
        print(f"No data for {args.symbol}")
        sys.exit(1)

    print(f"\n{args.symbol} labels:")
    print(f"  Shape: {labels.shape}")
    print(f"  Forward days: {TARGET_FORWARD_DAYS}")
    print(f"  Return threshold: {TARGET_RETURN_THRESHOLD:.0%}")

    valid = labels["TARGET_5PCT_5D"].notna()
    n_pos = (labels.loc[valid, "TARGET_5PCT_5D"] == 1).sum()
    n_neg = (labels.loc[valid, "TARGET_5PCT_5D"] == 0).sum()
    total = n_pos + n_neg

    print(f"\n  Total valid rows: {total}")
    print(f"  Positive (>5%%): {n_pos} ({n_pos / total * 100:.1f}%)")
    print(f"  Negative (<=5%%): {n_neg} ({n_neg / total * 100:.1f}%)")
    print(f"  NaN (no future): {labels['TARGET_5PCT_5D'].isna().sum()}")

    print(f"\n  Forward return stats:")
    print(f"    Mean:   {labels['FORWARD_RETURN_5D'].mean():.4f}")
    print(f"    Median: {labels['FORWARD_RETURN_5D'].median():.4f}")
    print(f"    Std:    {labels['FORWARD_RETURN_5D'].std():.4f}")
    print(f"    Min:    {labels['FORWARD_RETURN_5D'].min():.4f}")
    print(f"    Max:    {labels['FORWARD_RETURN_5D'].max():.4f}")

    print(f"\n  Last 10 rows:")
    print(labels.tail(10).to_string())

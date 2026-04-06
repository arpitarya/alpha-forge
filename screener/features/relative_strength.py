"""Phase 2.2 — Relative Strength Features.

Computes stock returns relative to benchmark indices (NIFTY 50, sector indices)
over multiple time windows.

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import INDICES_DIR, INDEX_SYMBOLS

logger = logging.getLogger(__name__)

# Cache loaded index data to avoid re-reading parquet on every call
_index_cache: dict[str, pd.Series] = {}


def _load_index_close(index_name: str) -> pd.Series | None:
    """Load and cache the Close price series for a benchmark index."""
    if index_name in _index_cache:
        return _index_cache[index_name]

    filepath = INDICES_DIR / f"{index_name}.parquet"
    if not filepath.exists():
        logger.warning("Index data not found: %s", filepath)
        return None

    df = pd.read_parquet(filepath)

    # Handle MultiIndex columns from yfinance (e.g., ('Close', '^NSEI'))
    if isinstance(df.columns, pd.MultiIndex):
        # Find the Close column
        close_cols = [c for c in df.columns if c[0] == "Close"]
        if close_cols:
            close = df[close_cols[0]]
        else:
            logger.warning("No Close column in index %s", index_name)
            return None
    else:
        close = df["Close"]

    close = close.sort_index()
    _index_cache[index_name] = close
    return close


def _compute_returns(series: pd.Series, window: int) -> pd.Series:
    """Compute rolling percentage return over N days."""
    return series.pct_change(periods=window)


def compute_relative_strength(
    stock_close: pd.Series,
    benchmark_name: str = "NIFTY_50",
    windows: list[int] | None = None,
) -> pd.DataFrame:
    """Compute relative strength of a stock vs a benchmark index.

    Args:
        stock_close: Stock's Close price series with DatetimeIndex.
        benchmark_name: Key from INDEX_SYMBOLS (e.g., "NIFTY_50").
        windows: Return lookback windows in trading days.

    Returns:
        DataFrame with relative strength features.
    """
    if windows is None:
        windows = [5, 10, 20]

    benchmark_close = _load_index_close(benchmark_name)
    features = pd.DataFrame(index=stock_close.index)

    if benchmark_close is None:
        # Return NaN columns if benchmark not available
        for w in windows:
            features[f"RS_{benchmark_name}_{w}D"] = float("nan")
            features[f"EXCESS_RET_{benchmark_name}_{w}D"] = float("nan")
        return features

    # Align dates
    aligned = pd.DataFrame({
        "stock": stock_close,
        "benchmark": benchmark_close,
    }).dropna()

    if aligned.empty:
        for w in windows:
            features[f"RS_{benchmark_name}_{w}D"] = float("nan")
            features[f"EXCESS_RET_{benchmark_name}_{w}D"] = float("nan")
        return features

    for w in windows:
        stock_ret = _compute_returns(aligned["stock"], w)
        bench_ret = _compute_returns(aligned["benchmark"], w)

        # Excess return: stock return - benchmark return
        excess = stock_ret - bench_ret

        # Relative strength ratio: (1 + stock_ret) / (1 + bench_ret)
        rs = (1 + stock_ret) / (1 + bench_ret)

        # Map back to original index
        features[f"RS_{benchmark_name}_{w}D"] = rs.reindex(stock_close.index)
        features[f"EXCESS_RET_{benchmark_name}_{w}D"] = excess.reindex(stock_close.index)

    return features


def compute_all_relative_strength(
    stock_close: pd.Series,
    windows: list[int] | None = None,
) -> pd.DataFrame:
    """Compute relative strength vs all available benchmarks.

    Args:
        stock_close: Stock's Close price series with DatetimeIndex.
        windows: Return lookback windows in trading days.

    Returns:
        DataFrame with relative strength features for all benchmarks.
    """
    if windows is None:
        windows = [5, 10, 20]

    all_features = []

    # Primary benchmark: NIFTY 50
    all_features.append(compute_relative_strength(stock_close, "NIFTY_50", windows))

    # Additional benchmarks (only 5-day for brevity)
    for idx_name in INDEX_SYMBOLS:
        if idx_name == "NIFTY_50":
            continue
        all_features.append(compute_relative_strength(stock_close, idx_name, [5]))

    result = pd.concat(all_features, axis=1)
    logger.debug("Computed %d relative strength features", result.shape[1])
    return result


def clear_index_cache() -> None:
    """Clear the cached index data (e.g., between runs)."""
    _index_cache.clear()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    from config import OHLCV_DIR

    symbol = "RELIANCE"
    filepath = OHLCV_DIR / f"{symbol}.parquet"
    if not filepath.exists():
        print(f"No data for {symbol}. Run fetch_ohlcv.py first.")
        sys.exit(1)

    df = pd.read_parquet(filepath)
    # Handle MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    features = compute_all_relative_strength(df["Close"])
    print(f"\n{symbol} relative strength features:")
    print(f"  Shape: {features.shape}")
    print(f"  Columns: {list(features.columns)}")
    print(f"\nLast 3 rows:")
    print(features.tail(3).to_string())

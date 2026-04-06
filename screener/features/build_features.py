"""Phase 2.5 — Feature Orchestrator.

Combines all feature groups (technical, relative strength, fundamental, NSE-specific)
into a single feature DataFrame per stock. Also computes derived/interaction features.

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import OHLCV_DIR, UNIVERSE_FILTERED_FILE

from features.technical import compute_technical_features
from features.relative_strength import compute_all_relative_strength
from features.fundamental import compute_fundamental_features
from features.nse_features import compute_nse_features

logger = logging.getLogger(__name__)


def compute_interaction_features(features: pd.DataFrame) -> pd.DataFrame:
    """Compute derived/interaction features from existing features.

    These capture joint signals that individual indicators miss.

    Args:
        features: DataFrame with all base features already computed.

    Returns:
        DataFrame with only the new interaction features.
    """
    interactions = pd.DataFrame(index=features.index)

    # RSI × Volume ratio — momentum + volume confirmation
    if "RSI_14" in features.columns and "VOL_SMA_RATIO" in features.columns:
        interactions["RSI_VOL_CONFIRM"] = features["RSI_14"] * features["VOL_SMA_RATIO"]

    # Distance from 52w high × ADX — breakout + trend strength
    if "DIST_52W_HIGH_PCT" in features.columns and "ADX_14" in features.columns:
        interactions["BREAKOUT_TREND"] = features["DIST_52W_HIGH_PCT"] * features["ADX_14"]

    # Bollinger %B when bandwidth narrowing — squeeze signal
    if "BB_PCT_B" in features.columns and "BB_BANDWIDTH" in features.columns:
        bw_sma = features["BB_BANDWIDTH"].rolling(window=20, min_periods=5).mean()
        bw_narrowing = (features["BB_BANDWIDTH"] < bw_sma).astype(int)
        interactions["SQUEEZE_SIGNAL"] = features["BB_PCT_B"] * bw_narrowing

    # MACD histogram momentum (change in histogram)
    if "MACD_HIST" in features.columns:
        interactions["MACD_HIST_DELTA"] = features["MACD_HIST"].diff()

    # RSI divergence proxy: RSI direction vs price direction over 5 days
    if "RSI_14" in features.columns and "ROC_5" in features.columns:
        rsi_change = features["RSI_14"].diff(5)
        price_dir = np.sign(features["ROC_5"])
        rsi_dir = np.sign(rsi_change)
        # Divergence: 1 if price and RSI moving in opposite directions
        interactions["RSI_DIVERGENCE"] = (price_dir != rsi_dir).astype(int)

    # Volume-confirmed trend: ADX strong + volume above average
    if "ADX_14" in features.columns and "VOL_SMA_RATIO" in features.columns:
        interactions["VOL_CONFIRMED_TREND"] = (
            (features["ADX_14"] > 25).astype(int)
            * (features["VOL_SMA_RATIO"] > 1.0).astype(int)
        )

    return interactions


def build_features_for_symbol(
    symbol: str,
    include_fundamentals: bool = True,
    include_nse: bool = True,
) -> pd.DataFrame | None:
    """Build all features for a single stock.

    Args:
        symbol: NSE symbol (e.g., "RELIANCE").
        include_fundamentals: Whether to fetch fundamentals from yfinance (slower).
        include_nse: Whether to include NSE-specific features.

    Returns:
        DataFrame with all features, or None if OHLCV data not found.
    """
    filepath = OHLCV_DIR / f"{symbol}.parquet"
    if not filepath.exists():
        logger.warning("No OHLCV data for %s", symbol)
        return None

    df = pd.read_parquet(filepath)

    # Handle MultiIndex columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty or len(df) < 50:
        logger.warning("Insufficient data for %s (%d rows, need >=50)", symbol, len(df))
        return None

    all_features: list[pd.DataFrame] = []

    # 2.1 — Technical indicators (~30 features)
    try:
        tech = compute_technical_features(df)
        all_features.append(tech)
    except Exception as e:
        logger.error("Technical features failed for %s: %s", symbol, e)
        return None

    # 2.2 — Relative strength (~12 features)
    try:
        rs = compute_all_relative_strength(df["Close"])
        all_features.append(rs)
    except Exception as e:
        logger.warning("Relative strength failed for %s: %s", symbol, e)

    # 2.3 — Fundamentals (~6 features)
    if include_fundamentals:
        try:
            fund = compute_fundamental_features(df, symbol)
            all_features.append(fund)
        except Exception as e:
            logger.warning("Fundamentals failed for %s: %s", symbol, e)

    # 2.4 — NSE-specific features (~4 features)
    if include_nse:
        try:
            nse = compute_nse_features(df, symbol)
            all_features.append(nse)
        except Exception as e:
            logger.warning("NSE features failed for %s: %s", symbol, e)

    # Combine all base features
    combined = pd.concat(all_features, axis=1)

    # 2.5 — Interaction/derived features (~6 features)
    try:
        interactions = compute_interaction_features(combined)
        combined = pd.concat([combined, interactions], axis=1)
    except Exception as e:
        logger.warning("Interaction features failed for %s: %s", symbol, e)

    # Add metadata columns
    combined["SYMBOL"] = symbol

    logger.info("Built %d features for %s (%d rows)", combined.shape[1] - 1, symbol, len(combined))
    return combined


def build_features_for_universe(
    max_symbols: int | None = None,
    include_fundamentals: bool = True,
    include_nse: bool = True,
) -> pd.DataFrame:
    """Build features for all stocks in the filtered universe.

    Args:
        max_symbols: Limit number of stocks to process (for testing).
        include_fundamentals: Whether to fetch fundamentals from yfinance.
        include_nse: Whether to include NSE-specific features.

    Returns:
        DataFrame with features for all stocks, stacked.
    """
    if not UNIVERSE_FILTERED_FILE.exists():
        raise FileNotFoundError(
            f"Filtered universe not found: {UNIVERSE_FILTERED_FILE}. "
            "Run fetch_universe.py first."
        )

    universe = pd.read_csv(UNIVERSE_FILTERED_FILE)
    symbols = universe["SYMBOL_NSE"].tolist()

    if max_symbols:
        symbols = symbols[:max_symbols]

    logger.info("Building features for %d symbols...", len(symbols))
    all_stock_features: list[pd.DataFrame] = []
    success = 0
    failed = 0

    for i, symbol in enumerate(symbols):
        if (i + 1) % 50 == 0 or i == 0:
            logger.info("Progress: %d/%d (success: %d, failed: %d)", i + 1, len(symbols), success, failed)

        result = build_features_for_symbol(
            symbol,
            include_fundamentals=include_fundamentals,
            include_nse=include_nse,
        )
        if result is not None:
            all_stock_features.append(result)
            success += 1
        else:
            failed += 1

    logger.info(
        "Feature building complete. %d/%d success, %d failed.",
        success, len(symbols), failed,
    )

    if not all_stock_features:
        return pd.DataFrame()

    combined = pd.concat(all_stock_features, axis=0)
    logger.info("Combined feature matrix: %d rows × %d columns", combined.shape[0], combined.shape[1])
    return combined


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Build features for screener")
    parser.add_argument("--symbol", type=str, help="Build features for a single symbol")
    parser.add_argument("--max-symbols", type=int, help="Limit number of symbols to process")
    parser.add_argument("--no-fundamentals", action="store_true", help="Skip yfinance fundamentals")
    parser.add_argument("--no-nse", action="store_true", help="Skip NSE-specific features")
    args = parser.parse_args()

    if args.symbol:
        features = build_features_for_symbol(
            args.symbol,
            include_fundamentals=not args.no_fundamentals,
            include_nse=not args.no_nse,
        )
        if features is not None:
            print(f"\n{args.symbol} features:")
            print(f"  Shape: {features.shape}")
            print(f"  Feature columns ({features.shape[1] - 1}):")  # -1 for SYMBOL
            for col in features.columns:
                if col == "SYMBOL":
                    continue
                non_null = features[col].notna().sum()
                print(f"    {col:35s} — {non_null}/{len(features)} non-null")
            nan_pct = features.isna().sum().sum() / (features.shape[0] * features.shape[1]) * 100
            print(f"\n  Overall NaN: {nan_pct:.1f}%")
        else:
            print(f"Failed to build features for {args.symbol}")
    else:
        combined = build_features_for_universe(
            max_symbols=args.max_symbols,
            include_fundamentals=not args.no_fundamentals,
            include_nse=not args.no_nse,
        )
        print(f"\nCombined feature matrix: {combined.shape}")
        if not combined.empty:
            print(f"Symbols: {combined['SYMBOL'].nunique()}")
            print(f"Date range: {combined.index.min()} → {combined.index.max()}")

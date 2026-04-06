"""Phase 6.1 — Daily Stock Scan Script.

Run after market close (~3:45 PM IST) to scan all stocks and output top picks.

Workflow:
1. Fetch/update latest OHLCV for all stocks in universe
2. Compute features for most recent trading day
3. Load trained model (LightGBM or XGBoost)
4. Predict probability for all stocks
5. Rank and output top N picks with confidence scores

Output: picks/{date}_weekly_picks.csv

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    MODELS_DIR,
    OHLCV_DIR,
    PICKS_DIR,
    UNIVERSE_FILTERED_FILE,
)

logger = logging.getLogger(__name__)


def get_universe_symbols() -> list[str]:
    """Load the filtered universe of stock symbols.

    Returns:
        List of NSE symbols (without .NS suffix).
    """
    if not UNIVERSE_FILTERED_FILE.exists():
        logger.error("Universe file not found: %s", UNIVERSE_FILTERED_FILE)
        logger.info("Run screener/data/fetch_universe.py first")
        return []

    universe = pd.read_csv(UNIVERSE_FILTERED_FILE)
    # Try common column names
    for col in ["SYMBOL", "Symbol", "symbol"]:
        if col in universe.columns:
            return universe[col].tolist()

    # Fallback: first column
    return universe.iloc[:, 0].tolist()


def get_available_symbols() -> list[str]:
    """Get symbols that have OHLCV data downloaded."""
    return sorted(f.stem for f in OHLCV_DIR.glob("*.parquet"))


def compute_features_latest(
    symbols: list[str],
    include_fundamentals: bool = False,
    include_nse: bool = False,
) -> pd.DataFrame:
    """Compute features for the most recent trading day across all symbols.

    Args:
        symbols: List of NSE symbols to scan.
        include_fundamentals: Whether to fetch fundamentals (slower).
        include_nse: Whether to include NSE features.

    Returns:
        DataFrame with one row per symbol: all features + SYMBOL column.
    """
    from features.build_features import build_features_for_symbol

    latest_rows = []
    failed = []

    for i, symbol in enumerate(symbols):
        if (i + 1) % 100 == 0:
            logger.info("Computing features: %d/%d symbols...", i + 1, len(symbols))

        try:
            features = build_features_for_symbol(
                symbol,
                include_fundamentals=include_fundamentals,
                include_nse=include_nse,
            )
            if features is not None and not features.empty:
                # Take only the last row (most recent day)
                last_row = features.iloc[[-1]].copy()
                latest_rows.append(last_row)
            else:
                failed.append(symbol)
        except Exception as e:
            logger.warning("Feature computation failed for %s: %s", symbol, e)
            failed.append(symbol)

    if not latest_rows:
        logger.error("No features computed for any symbol")
        return pd.DataFrame()

    result = pd.concat(latest_rows, ignore_index=False)
    logger.info(
        "Computed features for %d/%d symbols (%d failed)",
        len(latest_rows), len(symbols), len(failed),
    )

    if failed:
        logger.debug("Failed symbols: %s", failed[:20])

    return result


def load_model(model_type: str = "lightgbm"):
    """Load a trained model and its metadata.

    Args:
        model_type: 'lightgbm' or 'xgboost'.

    Returns:
        Tuple of (model, metadata_dict).
    """
    if model_type == "lightgbm":
        from models.train_lightgbm import load_model as load_lgb
        return load_lgb()
    elif model_type == "xgboost":
        from models.train_xgboost import load_model as load_xgb
        return load_xgb()
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def predict_and_rank(
    features: pd.DataFrame,
    model,
    meta: dict,
    model_type: str = "lightgbm",
    top_n: int = 20,
) -> pd.DataFrame:
    """Predict probabilities and rank stocks.

    Args:
        features: DataFrame with features for all stocks (one row per stock).
        model: Trained model.
        meta: Model metadata (contains feature_cols, prob_threshold).
        model_type: 'lightgbm' or 'xgboost'.
        top_n: Number of top picks to return.

    Returns:
        DataFrame of top N picks with columns:
        SYMBOL, PROBABILITY, RANK, SIGNAL, and key feature values.
    """
    feature_cols = meta.get("feature_cols", [])
    prob_threshold = meta.get("prob_threshold", 0.5)

    # Filter to available features
    available = [c for c in feature_cols if c in features.columns]
    missing = set(feature_cols) - set(available)
    if missing:
        logger.warning("Missing %d features, filling with NaN: %s",
                        len(missing), list(missing)[:5])

    X = features[available].copy()
    # Add missing columns as NaN
    for col in feature_cols:
        if col not in X.columns:
            X[col] = np.nan
    X = X[feature_cols]  # Reorder to match training

    # Predict
    if model_type == "lightgbm":
        probabilities = model.predict(X)
    else:
        probabilities = model.predict_proba(X)[:, 1]

    # Build results DataFrame
    results = pd.DataFrame({
        "SYMBOL": features["SYMBOL"].values,
        "PROBABILITY": probabilities,
        "SIGNAL": (probabilities >= prob_threshold).astype(int),
    })

    # Add date from index
    results["DATE"] = features.index.strftime("%Y-%m-%d") if hasattr(features.index, "strftime") else ""

    # Add key feature values for context
    key_features = ["RSI_14", "VOL_SMA_RATIO", "MACD_HIST", "ADX_14",
                     "DIST_52W_HIGH_PCT", "ROC_5"]
    for feat in key_features:
        if feat in features.columns:
            results[feat] = features[feat].values

    # Rank by probability (descending)
    results = results.sort_values("PROBABILITY", ascending=False).reset_index(drop=True)
    results["RANK"] = range(1, len(results) + 1)

    # Return top N
    top_picks = results.head(top_n).copy()

    logger.info(
        "Top %d picks — highest prob: %.3f, lowest: %.3f, signals: %d/%d total",
        top_n, top_picks["PROBABILITY"].max(), top_picks["PROBABILITY"].min(),
        results["SIGNAL"].sum(), len(results),
    )

    return top_picks


def save_picks(
    picks: pd.DataFrame,
    scan_date: str | None = None,
    model_type: str = "lightgbm",
) -> Path:
    """Save picks to CSV in the picks directory.

    Args:
        picks: DataFrame of picks from predict_and_rank().
        scan_date: Date string for filename (default: today).
        model_type: Model type for filename.

    Returns:
        Path to saved CSV file.
    """
    if scan_date is None:
        scan_date = datetime.now().strftime("%Y-%m-%d")

    filename = f"{scan_date}_{model_type}_weekly_picks.csv"
    filepath = PICKS_DIR / filename

    PICKS_DIR.mkdir(parents=True, exist_ok=True)
    picks.to_csv(filepath, index=False)

    logger.info("Saved %d picks to %s", len(picks), filepath)
    return filepath


def run_daily_scan(
    model_type: str = "lightgbm",
    top_n: int = 20,
    symbols: list[str] | None = None,
    include_fundamentals: bool = False,
    include_nse: bool = False,
    save: bool = True,
) -> pd.DataFrame:
    """Run the full daily scan pipeline.

    Args:
        model_type: Which model to use ('lightgbm' or 'xgboost').
        top_n: Number of top picks.
        symbols: Specific symbols to scan. If None, uses all available.
        include_fundamentals: Whether to include fundamental features.
        include_nse: Whether to include NSE features.
        save: Whether to save picks to CSV.

    Returns:
        DataFrame of top picks.
    """
    logger.info("Starting daily scan with %s model...", model_type)

    # Get symbols
    if symbols is None:
        symbols = get_available_symbols()
    if not symbols:
        logger.error("No symbols available for scanning")
        return pd.DataFrame()

    logger.info("Scanning %d symbols...", len(symbols))

    # Load model
    try:
        model, meta = load_model(model_type)
        logger.info("Loaded %s model (trained: %s)", model_type, meta.get("trained_at", "unknown"))
    except FileNotFoundError as e:
        logger.error("Model not found: %s. Train first with train_%s.py", e, model_type)
        return pd.DataFrame()

    # Compute features
    features = compute_features_latest(
        symbols,
        include_fundamentals=include_fundamentals,
        include_nse=include_nse,
    )
    if features.empty:
        return pd.DataFrame()

    # Predict and rank
    picks = predict_and_rank(features, model, meta, model_type, top_n)

    # Save
    if save and not picks.empty:
        save_picks(picks, model_type=model_type)

    return picks


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Daily stock scanner")
    parser.add_argument("--model", type=str, default="lightgbm",
                        choices=["lightgbm", "xgboost"],
                        help="Model to use (default: lightgbm)")
    parser.add_argument("--top-n", type=int, default=20,
                        help="Number of top picks (default: 20)")
    parser.add_argument("--symbols", nargs="+", default=None,
                        help="Specific symbols to scan (default: all available)")
    parser.add_argument("--fundamentals", action="store_true",
                        help="Include fundamental features (slower)")
    parser.add_argument("--nse", action="store_true",
                        help="Include NSE features")
    parser.add_argument("--no-save", action="store_true",
                        help="Don't save picks to file")
    args = parser.parse_args()

    picks = run_daily_scan(
        model_type=args.model,
        top_n=args.top_n,
        symbols=args.symbols,
        include_fundamentals=args.fundamentals,
        include_nse=args.nse,
        save=not args.no_save,
    )

    if picks.empty:
        print("\nNo picks generated.")
    else:
        print(f"\n{'=' * 70}")
        print(f"  TOP {len(picks)} WEEKLY PICKS — {args.model.upper()}")
        print(f"  Disclaimer: NOT SEBI registered investment advice.")
        print(f"{'=' * 70}\n")

        # Display columns
        display_cols = ["RANK", "SYMBOL", "PROBABILITY", "SIGNAL"]
        key_feats = ["RSI_14", "VOL_SMA_RATIO", "MACD_HIST", "ADX_14",
                      "DIST_52W_HIGH_PCT", "ROC_5"]
        display_cols.extend([c for c in key_feats if c in picks.columns])

        pd.set_option("display.max_columns", 20)
        pd.set_option("display.width", 120)
        pd.set_option("display.float_format", lambda x: f"{x:.4f}")
        print(picks[display_cols].to_string(index=False))
        print()

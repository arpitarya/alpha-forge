"""Phase 6.2 — SHAP-Based Signal Explanation.

For each pick from the daily scan, generates human-readable explanations
of WHY the model selected that stock using SHAP feature attributions.

Example output:
  "RELIANCE: RSI oversold bounce (RSI=28→35), volume surge 3.2×,
   MACD bullish crossover, near 52-week low (−8.5%)"

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logger = logging.getLogger(__name__)


# ── Feature Interpretation Rules ───────────────────────────────────────────────
# Maps feature names to human-readable templates.
# {value} is replaced with the actual feature value.

FEATURE_DESCRIPTIONS: dict[str, dict[str, Any]] = {
    "RSI_14": {
        "name": "RSI(14)",
        "format": ".0f",
        "thresholds": [
            (lambda v: v < 30, "deeply oversold (RSI={value:.0f})"),
            (lambda v: v < 40, "approaching oversold (RSI={value:.0f})"),
            (lambda v: v > 70, "overbought (RSI={value:.0f})"),
            (lambda v: v > 60, "strong momentum (RSI={value:.0f})"),
        ],
        "default": "RSI={value:.0f}",
    },
    "RSI_7": {
        "name": "RSI(7)",
        "format": ".0f",
        "thresholds": [
            (lambda v: v < 25, "short-term deeply oversold"),
            (lambda v: v < 35, "short-term oversold"),
            (lambda v: v > 75, "short-term overbought"),
        ],
    },
    "VOL_SMA_RATIO": {
        "name": "Volume ratio",
        "format": ".1f",
        "thresholds": [
            (lambda v: v > 3.0, "massive volume surge {value:.1f}×"),
            (lambda v: v > 2.0, "volume surge {value:.1f}×"),
            (lambda v: v > 1.5, "above-average volume {value:.1f}×"),
            (lambda v: v < 0.5, "low volume {value:.1f}×"),
        ],
        "default": "volume {value:.1f}× avg",
    },
    "MACD_HIST": {
        "name": "MACD histogram",
        "format": ".3f",
        "thresholds": [
            (lambda v: v > 0, "MACD bullish ({value:+.3f})"),
            (lambda v: v < 0, "MACD bearish ({value:+.3f})"),
        ],
    },
    "ADX_14": {
        "name": "ADX",
        "format": ".0f",
        "thresholds": [
            (lambda v: v > 40, "very strong trend (ADX={value:.0f})"),
            (lambda v: v > 25, "trending (ADX={value:.0f})"),
            (lambda v: v < 15, "no trend (ADX={value:.0f})"),
        ],
        "default": "ADX={value:.0f}",
    },
    "DIST_52W_HIGH_PCT": {
        "name": "Dist from 52W high",
        "format": ".1f",
        "thresholds": [
            (lambda v: v > -2, "near 52-week high ({value:+.1f}%)"),
            (lambda v: v > -5, "close to 52-week high ({value:+.1f}%)"),
            (lambda v: v < -20, "far from 52-week high ({value:+.1f}%)"),
        ],
        "default": "{value:+.1f}% from 52W high",
    },
    "DIST_52W_LOW_PCT": {
        "name": "Dist from 52W low",
        "format": ".1f",
        "thresholds": [
            (lambda v: v < 5, "near 52-week low (+{value:.1f}%)"),
            (lambda v: v > 50, "well above 52-week low (+{value:.1f}%)"),
        ],
    },
    "ROC_5": {
        "name": "5-day ROC",
        "format": ".2f",
        "thresholds": [
            (lambda v: v > 5, "strong 5-day momentum (+{value:.1f}%)"),
            (lambda v: v > 2, "positive 5-day momentum (+{value:.1f}%)"),
            (lambda v: v < -5, "sharp 5-day decline ({value:.1f}%)"),
        ],
    },
    "BB_PCT_B": {
        "name": "Bollinger %B",
        "format": ".2f",
        "thresholds": [
            (lambda v: v < 0, "below lower Bollinger band"),
            (lambda v: v < 0.2, "near lower Bollinger band"),
            (lambda v: v > 1, "above upper Bollinger band"),
            (lambda v: v > 0.8, "near upper Bollinger band"),
        ],
    },
    "MFI_14": {
        "name": "Money Flow Index",
        "format": ".0f",
        "thresholds": [
            (lambda v: v < 20, "MFI oversold ({value:.0f})"),
            (lambda v: v > 80, "MFI overbought ({value:.0f})"),
        ],
    },
    "RSI_VOL_CONFIRM": {
        "name": "RSI+Volume confirmation",
        "format": ".1f",
        "thresholds": [
            (lambda v: v > 100, "strong RSI + volume confirmation"),
        ],
    },
    "SQUEEZE_SIGNAL": {
        "name": "Squeeze signal",
        "format": ".2f",
        "thresholds": [
            (lambda v: v > 0, "Bollinger squeeze detected"),
        ],
    },
}


def compute_shap_values(
    model,
    features: pd.DataFrame,
    feature_cols: list[str],
    model_type: str = "lightgbm",
) -> np.ndarray:
    """Compute SHAP values for the given features.

    Args:
        model: Trained model.
        features: DataFrame of features (one or more rows).
        feature_cols: Ordered list of feature column names.
        model_type: 'lightgbm' or 'xgboost'.

    Returns:
        SHAP values array (n_samples × n_features).
    """
    import shap

    X = features[feature_cols].copy()

    if model_type == "lightgbm":
        explainer = shap.TreeExplainer(model)
    else:
        explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(X)

    # For binary classification, shap_values may be a list [class0, class1]
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # class 1 = positive

    return shap_values


def describe_feature(feature_name: str, value: float) -> str | None:
    """Generate human-readable description for a feature value.

    Args:
        feature_name: Name of the feature.
        value: Feature value.

    Returns:
        Description string, or None if no notable description.
    """
    if pd.isna(value):
        return None

    desc_info = FEATURE_DESCRIPTIONS.get(feature_name)
    if desc_info is None:
        return None

    # Check thresholds
    for condition, template in desc_info.get("thresholds", []):
        try:
            if condition(value):
                return template.format(value=value)
        except (TypeError, ValueError):
            continue

    # Default description (only if explicitly defined)
    default = desc_info.get("default")
    if default:
        return default.format(value=value)

    return None


def explain_pick(
    symbol: str,
    features: pd.Series,
    shap_values: np.ndarray,
    feature_cols: list[str],
    top_k: int = 5,
) -> dict[str, Any]:
    """Generate explanation for a single stock pick.

    Args:
        symbol: Stock symbol.
        features: Feature values for this stock (Series).
        shap_values: SHAP values for this stock (1D array).
        feature_cols: Feature column names.
        top_k: Number of top contributing features to show.

    Returns:
        Dict with 'symbol', 'summary', 'details' (list of feature explanations).
    """
    # Get top contributing features (by absolute SHAP value)
    abs_shap = np.abs(shap_values)
    top_indices = np.argsort(abs_shap)[-top_k:][::-1]

    details = []
    descriptions = []

    for idx in top_indices:
        feat_name = feature_cols[idx]
        shap_val = float(shap_values[idx])
        feat_val = float(features.get(feat_name, np.nan))
        direction = "↑" if shap_val > 0 else "↓"

        # Human-readable description
        desc = describe_feature(feat_name, feat_val)
        if desc is None:
            desc = f"{feat_name}={feat_val:.3f}"

        detail = {
            "feature": feat_name,
            "value": feat_val,
            "shap_value": shap_val,
            "direction": direction,
            "description": desc,
        }
        details.append(detail)

        if desc:
            descriptions.append(f"{desc} ({direction})")

    summary = f"{symbol}: {', '.join(descriptions)}"

    return {
        "symbol": symbol,
        "summary": summary,
        "details": details,
    }


def explain_picks(
    picks: pd.DataFrame,
    model,
    meta: dict,
    features: pd.DataFrame,
    model_type: str = "lightgbm",
    top_k: int = 5,
) -> list[dict]:
    """Generate explanations for all picks.

    Args:
        picks: DataFrame of picks (from scan.py predict_and_rank).
        model: Trained model.
        meta: Model metadata.
        features: Full feature DataFrame (one row per symbol).
        model_type: 'lightgbm' or 'xgboost'.
        top_k: Number of top features per explanation.

    Returns:
        List of explanation dicts.
    """
    feature_cols = meta.get("feature_cols", [])

    # Filter features to only picked symbols, preserving pick rank order
    pick_symbols = picks["SYMBOL"].tolist()
    pick_features = features[features["SYMBOL"].isin(pick_symbols)].copy()

    # Reorder to match picks ranking
    symbol_order = {s: i for i, s in enumerate(pick_symbols)}
    pick_features["_rank"] = pick_features["SYMBOL"].map(symbol_order)
    pick_features = pick_features.sort_values("_rank").drop(columns=["_rank"])

    if pick_features.empty:
        logger.warning("No matching features for picked symbols")
        return []

    # Ensure feature columns match training order, fill missing with NaN
    for col in feature_cols:
        if col not in pick_features.columns:
            pick_features[col] = np.nan

    # Compute SHAP values
    try:
        shap_values = compute_shap_values(model, pick_features, feature_cols, model_type)
    except Exception as e:
        logger.error("SHAP computation failed: %s", e)
        logger.info("Falling back to feature-value-only explanations")
        return _explain_without_shap(pick_features, feature_cols, top_k)

    explanations = []
    for i, (_, row) in enumerate(pick_features.iterrows()):
        symbol = row["SYMBOL"]
        if i < len(shap_values):
            explanation = explain_pick(
                symbol, row, shap_values[i], feature_cols, top_k
            )
            explanations.append(explanation)

    return explanations


def _explain_without_shap(
    features: pd.DataFrame,
    feature_cols: list[str],
    top_k: int = 5,
) -> list[dict]:
    """Fallback explanations using feature values only (no SHAP)."""
    explanations = []

    for _, row in features.iterrows():
        symbol = row["SYMBOL"]
        descriptions = []
        details = []

        # Check all features with known descriptions
        for feat_name in feature_cols:
            if feat_name not in FEATURE_DESCRIPTIONS:
                continue
            val = row.get(feat_name, np.nan)
            desc = describe_feature(feat_name, val)
            if desc:
                details.append({
                    "feature": feat_name,
                    "value": float(val) if not pd.isna(val) else None,
                    "shap_value": None,
                    "direction": "",
                    "description": desc,
                })
                descriptions.append(desc)

        # Limit to top_k
        details = details[:top_k]
        descriptions = descriptions[:top_k]

        explanations.append({
            "symbol": symbol,
            "summary": f"{symbol}: {', '.join(descriptions)}" if descriptions else f"{symbol}: no notable signals",
            "details": details,
        })

    return explanations


def format_explanations(explanations: list[dict]) -> str:
    """Format explanations as human-readable text.

    Args:
        explanations: List of explanation dicts from explain_picks().

    Returns:
        Formatted multi-line string.
    """
    lines = []
    lines.append("=" * 70)
    lines.append("  SIGNAL EXPLANATIONS")
    lines.append("  Disclaimer: NOT SEBI registered investment advice.")
    lines.append("=" * 70)

    for exp in explanations:
        lines.append(f"\n  {exp['summary']}")
        if exp.get("details"):
            for d in exp["details"]:
                shap_str = f" (SHAP: {d['shap_value']:+.4f})" if d.get("shap_value") is not None else ""
                lines.append(f"    • {d['description']}{shap_str}")

    lines.append("")
    return "\n".join(lines)


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Explain stock picks via SHAP")
    parser.add_argument("--model", type=str, default="lightgbm",
                        choices=["lightgbm", "xgboost"],
                        help="Model type (default: lightgbm)")
    parser.add_argument("--symbols", nargs="+", default=None,
                        help="Symbols to explain (default: all available)")
    parser.add_argument("--top-n", type=int, default=10,
                        help="Number of top picks to explain (default: 10)")
    parser.add_argument("--top-k", type=int, default=5,
                        help="Features per explanation (default: 5)")
    parser.add_argument("--no-shap", action="store_true",
                        help="Skip SHAP (use feature values only)")
    args = parser.parse_args()

    from live.scan import run_daily_scan, compute_features_latest, get_available_symbols

    # Run scan to get picks and features
    symbols = args.symbols or get_available_symbols()
    print(f"Scanning {len(symbols)} symbols...")

    model, meta = None, None
    try:
        from live.scan import load_model
        model, meta = load_model(args.model)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    features = compute_features_latest(symbols, include_fundamentals=False, include_nse=False)
    if features.empty:
        print("No features computed")
        sys.exit(1)

    from live.scan import predict_and_rank
    picks = predict_and_rank(features, model, meta, args.model, args.top_n)

    if picks.empty:
        print("No picks generated")
        sys.exit(1)

    # Explain
    if args.no_shap:
        explanations = _explain_without_shap(
            features[features["SYMBOL"].isin(picks["SYMBOL"].tolist())],
            meta.get("feature_cols", []),
            args.top_k,
        )
    else:
        explanations = explain_picks(
            picks, model, meta, features, args.model, args.top_k
        )

    print(format_explanations(explanations))

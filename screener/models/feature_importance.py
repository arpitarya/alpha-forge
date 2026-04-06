"""Phase 4.5 — Feature Importance & Selection.

Analyzes feature importance from trained models and provides:
- LightGBM gain-based importance
- XGBoost gain-based importance
- SHAP values for interpretability
- Feature selection: drop near-zero importance features

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MODELS_DIR, REPORTS_DIR
from models.walk_forward import drop_all_nan_columns, get_feature_columns

logger = logging.getLogger(__name__)


def get_model_importance(model_dir: Path) -> pd.DataFrame | None:
    """Load feature importance CSV from a saved model directory."""
    path = model_dir / "feature_importance.csv"
    if not path.exists():
        return None
    return pd.read_csv(path)


def compare_model_importances(
    lgb_dir: Path | None = None,
    xgb_dir: Path | None = None,
) -> pd.DataFrame:
    """Compare feature importance across LightGBM and XGBoost.

    Returns:
        DataFrame with features and their importance in each model,
        sorted by average rank.
    """
    lgb_dir = lgb_dir or MODELS_DIR / "lightgbm"
    xgb_dir = xgb_dir or MODELS_DIR / "xgboost"

    lgb_imp = get_model_importance(lgb_dir)
    xgb_imp = get_model_importance(xgb_dir)

    if lgb_imp is None and xgb_imp is None:
        raise FileNotFoundError("No model importance files found. Train models first.")

    dfs = []
    if lgb_imp is not None:
        lgb_imp = lgb_imp.rename(columns={"importance_gain": "lgb_importance"})
        lgb_imp["lgb_rank"] = lgb_imp["lgb_importance"].rank(ascending=False).astype(int)
        dfs.append(lgb_imp)

    if xgb_imp is not None:
        xgb_imp = xgb_imp.rename(columns={"importance_gain": "xgb_importance"})
        xgb_imp["xgb_rank"] = xgb_imp["xgb_importance"].rank(ascending=False).astype(int)
        dfs.append(xgb_imp)

    if len(dfs) == 2:
        merged = pd.merge(dfs[0], dfs[1], on="feature", how="outer")
        merged["avg_rank"] = merged[["lgb_rank", "xgb_rank"]].mean(axis=1)
    else:
        merged = dfs[0]
        rank_col = "lgb_rank" if "lgb_rank" in merged.columns else "xgb_rank"
        merged["avg_rank"] = merged[rank_col]

    return merged.sort_values("avg_rank")


def compute_shap_importance(
    model,
    df: pd.DataFrame,
    feature_cols: list[str],
    max_samples: int = 500,
) -> pd.DataFrame:
    """Compute SHAP values for feature importance.

    Args:
        model: Trained model (LightGBM or XGBoost).
        df: Dataset.
        feature_cols: Feature columns.
        max_samples: Max samples for SHAP computation (for speed).

    Returns:
        DataFrame with feature names and mean absolute SHAP values.
    """
    import shap

    X = df[feature_cols]

    # Subsample for speed if needed
    if len(X) > max_samples:
        X = X.sample(n=max_samples, random_state=42)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # For binary classification, shap_values may be a list [neg_class, pos_class]
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # Use positive class

    mean_abs_shap = np.abs(shap_values).mean(axis=0)

    importance_df = pd.DataFrame({
        "feature": feature_cols,
        "shap_importance": mean_abs_shap,
    }).sort_values("shap_importance", ascending=False)

    return importance_df


def select_features(
    importance_df: pd.DataFrame,
    importance_col: str = "lgb_importance",
    min_importance_pct: float = 0.01,
) -> list[str]:
    """Select features above a minimum importance threshold.

    Args:
        importance_df: DataFrame with feature and importance columns.
        importance_col: Which importance column to use.
        min_importance_pct: Minimum importance as fraction of max (default: 1%).

    Returns:
        List of selected feature names.
    """
    if importance_col not in importance_df.columns:
        # Try any available importance column
        imp_cols = [c for c in importance_df.columns if "importance" in c.lower()]
        if not imp_cols:
            raise ValueError("No importance columns found")
        importance_col = imp_cols[0]

    max_imp = importance_df[importance_col].max()
    threshold = max_imp * min_importance_pct

    selected = importance_df[importance_df[importance_col] >= threshold]["feature"].tolist()
    dropped = len(importance_df) - len(selected)

    logger.info(
        "Feature selection: %d → %d features (dropped %d with importance < %.4f)",
        len(importance_df), len(selected), dropped, threshold,
    )

    return selected


def generate_report(
    comparison_df: pd.DataFrame,
    shap_df: pd.DataFrame | None = None,
    save_path: Path | None = None,
) -> str:
    """Generate a text report of feature importance analysis.

    Args:
        comparison_df: Output of compare_model_importances().
        shap_df: Optional SHAP importance DataFrame.
        save_path: Optional path to save the report.

    Returns:
        Report as string.
    """
    lines = [
        "AlphaForge Screener — Feature Importance Report",
        "=" * 60,
        f"Total features analyzed: {len(comparison_df)}",
        "",
    ]

    # Top features by average rank
    lines.append("Top 20 Features (by avg rank across models):")
    lines.append("-" * 60)
    top20 = comparison_df.head(20)
    for _, row in top20.iterrows():
        parts = [f"  {row['feature']:<30s}"]
        if "lgb_importance" in row and not pd.isna(row.get("lgb_importance")):
            parts.append(f"LGB={row['lgb_importance']:>8.0f} (#{int(row['lgb_rank'])})")
        if "xgb_importance" in row and not pd.isna(row.get("xgb_importance")):
            parts.append(f"XGB={row['xgb_importance']:>8.4f} (#{int(row['xgb_rank'])})")
        lines.append("  ".join(parts))

    # Bottom features (candidates for removal)
    lines.append("")
    lines.append("Bottom 10 Features (candidates for removal):")
    lines.append("-" * 60)
    bottom10 = comparison_df.tail(10)
    for _, row in bottom10.iterrows():
        parts = [f"  {row['feature']:<30s}"]
        if "lgb_importance" in row and not pd.isna(row.get("lgb_importance")):
            parts.append(f"LGB={row['lgb_importance']:>8.0f}")
        if "xgb_importance" in row and not pd.isna(row.get("xgb_importance")):
            parts.append(f"XGB={row['xgb_importance']:>8.4f}")
        lines.append("  ".join(parts))

    # SHAP if available
    if shap_df is not None:
        lines.append("")
        lines.append("Top 15 Features by SHAP Values:")
        lines.append("-" * 60)
        for _, row in shap_df.head(15).iterrows():
            lines.append(f"  {row['feature']:<30s} SHAP={row['shap_importance']:.6f}")

    lines.append("")
    lines.append("Disclaimer: NOT SEBI registered investment advice. For personal research only.")

    report = "\n".join(lines)

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            f.write(report)
        logger.info("Saved report to %s", save_path)

    return report


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Feature importance analysis")
    parser.add_argument("--dataset", type=str, default=None,
                        help="Path to dataset parquet (for SHAP)")
    parser.add_argument("--shap", action="store_true",
                        help="Compute SHAP values (requires trained model + dataset)")
    parser.add_argument("--select", action="store_true",
                        help="Run feature selection and print selected features")
    parser.add_argument("--min-importance-pct", type=float, default=0.01,
                        help="Min importance as pct of max for selection (default: 0.01)")
    parser.add_argument("--save-report", action="store_true",
                        help="Save report to reports/ directory")
    args = parser.parse_args()

    # Compare model importances
    try:
        comparison = compare_model_importances()
        report = generate_report(
            comparison,
            save_path=REPORTS_DIR / "feature_importance.txt" if args.save_report else None,
        )
        print(report)
    except FileNotFoundError as e:
        logger.warning("Could not compare models: %s", e)
        comparison = None

    # SHAP analysis
    if args.shap:
        dataset_path = args.dataset or str(
            Path(__file__).resolve().parent.parent / "dataset" / "output" / "dataset.parquet"
        )
        df = pd.read_parquet(dataset_path)
        feature_cols = get_feature_columns(df)
        feature_cols = drop_all_nan_columns(df, feature_cols)

        # Try LightGBM first
        lgb_model_path = MODELS_DIR / "lightgbm" / "model.txt"
        if lgb_model_path.exists():
            import lightgbm as lgb
            model = lgb.Booster(model_file=str(lgb_model_path))
            print("\nComputing SHAP values for LightGBM model...")
            shap_df = compute_shap_importance(model, df, feature_cols)
            print("\nTop 15 Features by SHAP:")
            for _, row in shap_df.head(15).iterrows():
                print(f"  {row['feature']:<30s} {row['shap_importance']:.6f}")
        else:
            logger.warning("No LightGBM model found for SHAP analysis")

    # Feature selection
    if args.select and comparison is not None:
        imp_col = "lgb_importance" if "lgb_importance" in comparison.columns else "xgb_importance"
        selected = select_features(comparison, imp_col, args.min_importance_pct)
        print(f"\nSelected {len(selected)} features (threshold: {args.min_importance_pct:.1%} of max):")
        for feat in selected:
            print(f"  {feat}")

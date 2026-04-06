"""Phase 4.3 — XGBoost Classifier for Stock Screener.

Comparison model against LightGBM. Same features, same walk-forward CV,
different gradient boosting implementation.

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MODELS_DIR, TARGET_FORWARD_DAYS, TARGET_RETURN_THRESHOLD
from models.walk_forward import (
    WalkForwardSplit,
    compute_fold_metrics,
    drop_all_nan_columns,
    evaluate_walk_forward,
    get_feature_columns,
)

logger = logging.getLogger(__name__)


# ── Default Hyperparameters ────────────────────────────────────────────────────

DEFAULT_PARAMS = {
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "n_estimators": 500,
    "max_depth": 6,
    "learning_rate": 0.05,
    "min_child_weight": 5,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "random_state": 42,
    "verbosity": 0,
    "n_jobs": -1,
    "tree_method": "hist",
}


def compute_scale_pos_weight(y: np.ndarray) -> float:
    """Compute scale_pos_weight for class imbalance."""
    n_pos = (y == 1).sum()
    n_neg = (y == 0).sum()
    if n_pos == 0:
        return 1.0
    return float(n_neg / n_pos)


def create_xgboost_model(params: dict | None = None, scale_pos_weight: float | None = None):
    """Create an XGBoost classifier instance."""
    import xgboost as xgb

    model_params = DEFAULT_PARAMS.copy()
    if params:
        model_params.update(params)
    if scale_pos_weight is not None:
        model_params["scale_pos_weight"] = scale_pos_weight

    return xgb.XGBClassifier(**model_params)


def train_xgboost(
    df: pd.DataFrame,
    feature_cols: list[str],
    params: dict | None = None,
    min_train_months: int = 12,
    test_months: int = 1,
    prob_threshold: float = 0.5,
    save: bool = True,
) -> dict:
    """Train XGBoost with walk-forward CV and optionally save final model.

    Args:
        df: Full dataset with features + target + returns.
        feature_cols: List of feature column names.
        params: Custom XGBoost parameters.
        min_train_months: Min training months for walk-forward.
        test_months: Test period per fold.
        prob_threshold: Signal threshold.
        save: Whether to save the final model.

    Returns:
        Dict with CV results, model, and metadata.
    """
    import xgboost as xgb

    target_col = "TARGET_5PCT_5D"
    return_col = "FORWARD_RETURN_5D"

    y_all = df[target_col].astype(float).values
    scale_pw = compute_scale_pos_weight(y_all)
    logger.info("Class imbalance: scale_pos_weight=%.2f", scale_pw)

    # Model factory for walk-forward CV
    model_params = DEFAULT_PARAMS.copy()
    if params:
        model_params.update(params)
    model_params["scale_pos_weight"] = scale_pw

    def model_factory():
        return xgb.XGBClassifier(**model_params)

    # Run walk-forward CV
    fold_results, agg_metrics = evaluate_walk_forward(
        df, model_factory, feature_cols,
        target_col=target_col,
        return_col=return_col,
        min_train_months=min_train_months,
        test_months=test_months,
        prob_threshold=prob_threshold,
    )

    # Train final model on ALL data for deployment
    logger.info("Training final model on full dataset (%d rows)", len(df))
    final_model = create_xgboost_model(params, scale_pos_weight=scale_pw)
    X_full = df[feature_cols]
    y_full = df[target_col].astype(float).values
    final_model.fit(X_full, y_full)

    # Feature importance
    importance = pd.DataFrame({
        "feature": feature_cols,
        "importance_gain": final_model.feature_importances_,
    }).sort_values("importance_gain", ascending=False)

    result = {
        "model_type": "xgboost",
        "model": final_model,
        "feature_cols": feature_cols,
        "params": model_params,
        "scale_pos_weight": scale_pw,
        "fold_results": fold_results,
        "agg_metrics": agg_metrics,
        "feature_importance": importance,
        "prob_threshold": prob_threshold,
        "trained_at": datetime.now().isoformat(),
        "n_rows": len(df),
        "n_features": len(feature_cols),
    }

    if save:
        save_model(result)

    return result


def save_model(result: dict) -> Path:
    """Save trained model + metadata to models/saved/xgboost/."""
    save_dir = MODELS_DIR / "xgboost"
    save_dir.mkdir(parents=True, exist_ok=True)

    # Save model in native JSON format
    model_path = save_dir / "model.json"
    result["model"].save_model(str(model_path))
    logger.info("Saved XGBoost model to %s", model_path)

    # Save feature importance
    importance_path = save_dir / "feature_importance.csv"
    result["feature_importance"].to_csv(importance_path, index=False)

    # Save metadata
    meta = {
        "model_type": "xgboost",
        "trained_at": result["trained_at"],
        "n_rows": result["n_rows"],
        "n_features": result["n_features"],
        "prob_threshold": result["prob_threshold"],
        "scale_pos_weight": result["scale_pos_weight"],
        "params": {k: v for k, v in result["params"].items()
                   if not callable(v)},
        "agg_metrics": result["agg_metrics"],
        "feature_cols": result["feature_cols"],
        "fold_summary": [
            {
                "fold": f.fold_id,
                "train": f"{f.train_start} → {f.train_end}",
                "test": f"{f.test_start} → {f.test_end}",
                "n_train": f.n_train,
                "n_test": f.n_test,
                "auc_roc": f.auc_roc,
                "precision": f.precision,
                "recall": f.recall,
                "n_signals": f.n_signals,
                "hit_rate": f.hit_rate,
            }
            for f in result["fold_results"]
        ],
    }
    meta_path = save_dir / "meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    logger.info("Saved metadata to %s", meta_path)

    return save_dir


def load_model(model_dir: Path | None = None):
    """Load a saved XGBoost model + metadata."""
    import xgboost as xgb

    if model_dir is None:
        model_dir = MODELS_DIR / "xgboost"

    model_path = model_dir / "model.json"
    meta_path = model_dir / "meta.json"

    model = xgb.XGBClassifier()
    model.load_model(str(model_path))

    with open(meta_path) as f:
        meta = json.load(f)

    return model, meta


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Train XGBoost classifier")
    parser.add_argument("--dataset", type=str, default=None,
                        help="Path to dataset parquet")
    parser.add_argument("--min-train-months", type=int, default=12,
                        help="Minimum training months (default: 12)")
    parser.add_argument("--test-months", type=int, default=1,
                        help="Test months per fold (default: 1)")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Probability threshold for signals (default: 0.5)")
    parser.add_argument("--no-save", action="store_true",
                        help="Don't save the trained model")
    parser.add_argument("--n-estimators", type=int, default=None,
                        help="Override number of trees")
    parser.add_argument("--learning-rate", type=float, default=None,
                        help="Override learning rate")
    args = parser.parse_args()

    # Load dataset
    dataset_path = args.dataset or str(
        Path(__file__).resolve().parent.parent / "dataset" / "output" / "dataset.parquet"
    )
    logger.info("Loading dataset from %s", dataset_path)
    df = pd.read_parquet(dataset_path)
    logger.info("Dataset: %d rows × %d columns", len(df), len(df.columns))

    # Get features
    feature_cols = get_feature_columns(df)
    feature_cols = drop_all_nan_columns(df, feature_cols)
    logger.info("Using %d features", len(feature_cols))

    # Custom params
    custom_params = {}
    if args.n_estimators:
        custom_params["n_estimators"] = args.n_estimators
    if args.learning_rate:
        custom_params["learning_rate"] = args.learning_rate

    # Train
    result = train_xgboost(
        df,
        feature_cols,
        params=custom_params or None,
        min_train_months=args.min_train_months,
        test_months=args.test_months,
        prob_threshold=args.threshold,
        save=not args.no_save,
    )

    # Print results
    agg = result["agg_metrics"]
    print(f"\nXGBoost Walk-Forward CV Results ({agg['n_folds']} folds, {agg['total_test_rows']:,} test rows)")
    print("=" * 70)

    for fr in result["fold_results"]:
        print(f"  Fold {fr.fold_id}: AUC={fr.auc_roc:.3f} Prec={fr.precision:.3f} "
              f"Recall={fr.recall:.3f} Signals={fr.n_signals} Hit={fr.hit_rate:.2%}")

    print(f"\nAggregated Metrics:")
    print("-" * 50)
    print(f"  AUC-ROC:       {agg['auc_roc']:.4f} (avg/fold: {agg['avg_auc_per_fold']:.4f} ± {agg['std_auc_per_fold']:.4f})")
    print(f"  Precision:     {agg['precision']:.4f}")
    print(f"  Recall:        {agg['recall']:.4f}")
    print(f"  F1:            {agg['f1']:.4f}")
    print(f"  Signals:       {agg['n_signals']}")
    print(f"  Hit rate:      {agg['hit_rate']:.2%}")
    print(f"  Avg return:    {agg['avg_return']:.4f} ({agg['avg_return'] * 100:.2f}%)")
    print(f"  Profit factor: {agg['profit_factor']:.2f}")

    # Top features
    print(f"\nTop 15 Features (by importance):")
    print("-" * 50)
    top = result["feature_importance"].head(15)
    for _, row in top.iterrows():
        print(f"  {row['feature']:<30s} {row['importance_gain']:.4f}")

    print("\nDisclaimer: NOT SEBI registered investment advice. For personal research only.")

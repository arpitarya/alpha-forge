"""Phase 4.4 — Walk-Forward Cross-Validation Engine.

⚠️ CRITICAL: Never use random train/test split for time-series data.
   Walk-forward ensures we always train on the past and predict the future.

Expanding window walk-forward:
  Fold 1:  Train [Month 1–12]  → Test [Month 13]
  Fold 2:  Train [Month 1–13]  → Test [Month 14]
  Fold 3:  Train [Month 1–14]  → Test [Month 15]
  ...
  Fold N:  Train [Month 1–(N+11)] → Test [Month N+12]

This module provides:
- WalkForwardSplit: generates (train_idx, test_idx) folds from a DatetimeIndex
- evaluate_walk_forward: runs a model through all folds and collects metrics
- Purge gap: configurable gap between train/test to prevent lookahead from labels

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import argparse
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import TARGET_FORWARD_DAYS

logger = logging.getLogger(__name__)


@dataclass
class FoldResult:
    """Results from a single walk-forward fold."""
    fold_id: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    n_train: int
    n_test: int
    n_train_pos: int
    n_test_pos: int
    # Classification metrics
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    auc_roc: float = 0.0
    # Trading metrics
    n_signals: int = 0
    hit_rate: float = 0.0
    avg_return: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    n_winners: int = 0
    n_losers: int = 0
    # Predictions
    predictions: np.ndarray = field(default_factory=lambda: np.array([]))
    probabilities: np.ndarray = field(default_factory=lambda: np.array([]))


class WalkForwardSplit:
    """Walk-forward cross-validation splitter for time-series data.

    Expanding window: training set grows each fold, test is next month.
    Includes a purge gap to prevent label lookahead.

    Args:
        min_train_months: Minimum training period in months (default: 12).
        test_months: Test period in months per fold (default: 1).
        purge_days: Gap in trading days between train end and test start
                    to prevent label lookahead (default: TARGET_FORWARD_DAYS).
    """

    def __init__(
        self,
        min_train_months: int = 12,
        test_months: int = 1,
        purge_days: int = TARGET_FORWARD_DAYS,
    ):
        self.min_train_months = min_train_months
        self.test_months = test_months
        self.purge_days = purge_days

    def split(
        self, df: pd.DataFrame
    ) -> list[tuple[np.ndarray, np.ndarray]]:
        """Generate walk-forward train/test index splits.

        Args:
            df: Dataset with DatetimeIndex (sorted).

        Returns:
            List of (train_indices, test_indices) tuples.
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must have a DatetimeIndex")

        dates = df.index.sort_values()
        min_date = dates.min()
        max_date = dates.max()

        # First test period starts after min_train_months
        first_test_start = min_date + pd.DateOffset(months=self.min_train_months)
        if first_test_start >= max_date:
            raise ValueError(
                f"Not enough data: need {self.min_train_months} months for training "
                f"but data only spans {min_date} to {max_date}"
            )

        folds = []
        test_start = first_test_start

        while test_start < max_date:
            test_end = test_start + pd.DateOffset(months=self.test_months)

            # Train: all data from start up to purge gap before test start
            purge_boundary = test_start - pd.Timedelta(days=self.purge_days)
            train_mask = dates < purge_boundary
            test_mask = (dates >= test_start) & (dates < test_end)

            train_idx = np.where(train_mask)[0]
            test_idx = np.where(test_mask)[0]

            if len(train_idx) > 0 and len(test_idx) > 0:
                folds.append((train_idx, test_idx))

            # Move to next test period
            test_start = test_end

        logger.info("Generated %d walk-forward folds", len(folds))
        return folds

    def get_fold_info(
        self, df: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]]
    ) -> list[dict]:
        """Get human-readable info about each fold."""
        info = []
        for i, (train_idx, test_idx) in enumerate(folds):
            train_dates = df.index[train_idx]
            test_dates = df.index[test_idx]
            info.append({
                "fold": i + 1,
                "train": f"{train_dates.min().date()} → {train_dates.max().date()}",
                "test": f"{test_dates.min().date()} → {test_dates.max().date()}",
                "n_train": len(train_idx),
                "n_test": len(test_idx),
            })
        return info


def compute_fold_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    forward_returns: np.ndarray,
    prob_threshold: float = 0.5,
) -> dict:
    """Compute classification + trading metrics for one fold.

    Args:
        y_true: True binary labels.
        y_pred: Predicted binary labels.
        y_prob: Predicted probabilities (for class 1).
        forward_returns: Actual forward returns for trading metrics.
        prob_threshold: Threshold for signal generation (default: 0.5).

    Returns:
        Dict of metric name → value.
    """
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    metrics = {}

    # Classification metrics
    metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
    metrics["precision"] = float(precision_score(y_true, y_pred, zero_division=0))
    metrics["recall"] = float(recall_score(y_true, y_pred, zero_division=0))
    metrics["f1"] = float(f1_score(y_true, y_pred, zero_division=0))

    # AUC-ROC (needs at least both classes present)
    if len(np.unique(y_true)) >= 2:
        metrics["auc_roc"] = float(roc_auc_score(y_true, y_prob))
    else:
        metrics["auc_roc"] = 0.0

    # Trading metrics — based on signals (y_pred == 1)
    signal_mask = y_pred == 1
    n_signals = signal_mask.sum()
    metrics["n_signals"] = int(n_signals)

    if n_signals > 0:
        signal_returns = forward_returns[signal_mask]
        signal_labels = y_true[signal_mask]
        hits = (signal_labels == 1).sum()

        metrics["hit_rate"] = float(hits / n_signals)
        metrics["avg_return"] = float(signal_returns.mean())

        winners = signal_returns[signal_returns > 0]
        losers = signal_returns[signal_returns <= 0]
        metrics["avg_win"] = float(winners.mean()) if len(winners) > 0 else 0.0
        metrics["avg_loss"] = float(losers.mean()) if len(losers) > 0 else 0.0

        gross_profit = winners.sum() if len(winners) > 0 else 0.0
        gross_loss = abs(losers.sum()) if len(losers) > 0 else 1e-9
        metrics["profit_factor"] = float(gross_profit / gross_loss)
        metrics["n_winners"] = int(len(winners))
        metrics["n_losers"] = int(len(losers))
    else:
        metrics["hit_rate"] = 0.0
        metrics["avg_return"] = 0.0
        metrics["avg_win"] = 0.0
        metrics["avg_loss"] = 0.0
        metrics["profit_factor"] = 0.0
        metrics["n_winners"] = 0
        metrics["n_losers"] = 0

    return metrics


def evaluate_walk_forward(
    df: pd.DataFrame,
    model_factory: Any,
    feature_cols: list[str],
    target_col: str = "TARGET_5PCT_5D",
    return_col: str = "FORWARD_RETURN_5D",
    min_train_months: int = 12,
    test_months: int = 1,
    purge_days: int = TARGET_FORWARD_DAYS,
    prob_threshold: float = 0.5,
) -> tuple[list[FoldResult], dict]:
    """Run walk-forward cross-validation with a model.

    Args:
        df: Full dataset with features, target, and forward returns.
        model_factory: Callable that returns a new (unfitted) model instance.
                       Must implement .fit(X, y) and .predict_proba(X).
        feature_cols: List of feature column names.
        target_col: Name of the target column.
        return_col: Name of the forward return column.
        min_train_months: Minimum training months.
        test_months: Test period per fold.
        purge_days: Purge gap in days.
        prob_threshold: Threshold for converting probabilities to signals.

    Returns:
        Tuple of (list of FoldResult, aggregated metrics dict).
    """
    splitter = WalkForwardSplit(min_train_months, test_months, purge_days)
    folds = splitter.split(df)

    if not folds:
        raise ValueError("No valid walk-forward folds could be generated")

    logger.info("Running walk-forward CV with %d folds", len(folds))

    fold_results = []
    all_preds = []
    all_probs = []
    all_true = []
    all_returns = []

    for fold_id, (train_idx, test_idx) in enumerate(folds, 1):
        X_train = df.iloc[train_idx][feature_cols]
        y_train = df.iloc[train_idx][target_col].astype(float).values
        X_test = df.iloc[test_idx][feature_cols]
        y_test = df.iloc[test_idx][target_col].astype(float).values
        returns_test = df.iloc[test_idx][return_col].values

        # Train model
        model = model_factory()
        model.fit(X_train, y_train)

        # Predict
        y_prob = model.predict_proba(X_test)[:, 1]
        y_pred = (y_prob >= prob_threshold).astype(int)

        # Compute fold metrics
        metrics = compute_fold_metrics(y_test, y_pred, y_prob, returns_test, prob_threshold)

        train_dates = df.index[train_idx]
        test_dates = df.index[test_idx]

        result = FoldResult(
            fold_id=fold_id,
            train_start=str(train_dates.min().date()),
            train_end=str(train_dates.max().date()),
            test_start=str(test_dates.min().date()),
            test_end=str(test_dates.max().date()),
            n_train=len(train_idx),
            n_test=len(test_idx),
            n_train_pos=int((y_train == 1).sum()),
            n_test_pos=int((y_test == 1).sum()),
            predictions=y_pred,
            probabilities=y_prob,
            **metrics,
        )
        fold_results.append(result)

        all_preds.extend(y_pred)
        all_probs.extend(y_prob)
        all_true.extend(y_test)
        all_returns.extend(returns_test)

        logger.info(
            "Fold %d: train=%d test=%d auc=%.3f prec=%.3f recall=%.3f signals=%d",
            fold_id, len(train_idx), len(test_idx),
            metrics["auc_roc"], metrics["precision"], metrics["recall"],
            metrics["n_signals"],
        )

    # Aggregate metrics across all folds
    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)
    all_true = np.array(all_true)
    all_returns = np.array(all_returns)

    agg = compute_fold_metrics(all_true, all_preds, all_probs, all_returns, prob_threshold)
    agg["n_folds"] = len(fold_results)
    agg["avg_auc_per_fold"] = float(np.mean([f.auc_roc for f in fold_results]))
    agg["std_auc_per_fold"] = float(np.std([f.auc_roc for f in fold_results]))
    agg["total_test_rows"] = int(len(all_true))

    return fold_results, agg


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Get feature column names from dataset (everything except metadata/target)."""
    exclude = {"SYMBOL", "FORWARD_RETURN_5D", "TARGET_5PCT_5D"}
    return [c for c in df.columns if c not in exclude]


def drop_all_nan_columns(df: pd.DataFrame, feature_cols: list[str]) -> list[str]:
    """Drop feature columns that are entirely NaN."""
    valid = [c for c in feature_cols if not df[c].isna().all()]
    dropped = set(feature_cols) - set(valid)
    if dropped:
        logger.info("Dropped %d all-NaN feature columns: %s", len(dropped), sorted(dropped))
    return valid


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from sklearn.ensemble import HistGradientBoostingClassifier

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Walk-forward CV demo")
    parser.add_argument("--dataset", type=str, default=None,
                        help="Path to dataset parquet")
    parser.add_argument("--min-train-months", type=int, default=12)
    parser.add_argument("--test-months", type=int, default=1)
    args = parser.parse_args()

    dataset_path = args.dataset or str(
        Path(__file__).resolve().parent.parent / "dataset" / "output" / "dataset.parquet"
    )
    df = pd.read_parquet(dataset_path)
    logger.info("Loaded dataset: %d rows × %d columns", len(df), len(df.columns))

    feature_cols = get_feature_columns(df)
    feature_cols = drop_all_nan_columns(df, feature_cols)
    logger.info("Using %d features", len(feature_cols))

    # Demo with sklearn HistGradientBoosting (handles NaN natively)
    def model_factory():
        return HistGradientBoostingClassifier(
            max_iter=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
        )

    splitter = WalkForwardSplit(args.min_train_months, args.test_months)
    folds = splitter.split(df)
    fold_info = splitter.get_fold_info(df, folds)

    print(f"\nWalk-Forward CV: {len(folds)} folds")
    print("=" * 70)
    for info in fold_info:
        print(f"  Fold {info['fold']}: Train {info['train']} ({info['n_train']:,}) "
              f"→ Test {info['test']} ({info['n_test']:,})")

    fold_results, agg = evaluate_walk_forward(
        df, model_factory, feature_cols,
        min_train_months=args.min_train_months,
        test_months=args.test_months,
    )

    print(f"\nAggregated Results ({agg['total_test_rows']:,} test rows):")
    print("-" * 50)
    print(f"  AUC-ROC:       {agg['auc_roc']:.4f} (avg/fold: {agg['avg_auc_per_fold']:.4f} ± {agg['std_auc_per_fold']:.4f})")
    print(f"  Precision:     {agg['precision']:.4f}")
    print(f"  Recall:        {agg['recall']:.4f}")
    print(f"  F1:            {agg['f1']:.4f}")
    print(f"  Signals:       {agg['n_signals']}")
    print(f"  Hit rate:      {agg['hit_rate']:.2%}")
    print(f"  Avg return:    {agg['avg_return']:.4f}")
    print(f"  Profit factor: {agg['profit_factor']:.2f}")
    print("\nDisclaimer: NOT SEBI registered investment advice. For personal research only.")

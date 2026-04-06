"""Phase 6.3 — Monthly Model Retraining with Drift Detection.

Automates model retraining on an expanding window and monitors for model drift.

Schedule:
- Retrain monthly (or on-demand) with all available data
- Compare new model vs current model on recent data
- Alert if live hit rate drops >10% below backtest rate

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MODELS_DIR, PICKS_DIR, REPORTS_DIR

logger = logging.getLogger(__name__)

# Drift detection thresholds
DRIFT_HIT_RATE_DROP = 0.10  # Alert if hit rate drops >10% vs backtest
DRIFT_AUC_DROP = 0.05       # Alert if AUC drops >5% vs backtest


def retrain_model(
    model_type: str = "lightgbm",
    dataset_path: str | Path | None = None,
    save: bool = True,
) -> dict[str, Any]:
    """Retrain model on latest dataset.

    Args:
        model_type: 'lightgbm' or 'xgboost'.
        dataset_path: Path to dataset. If None, uses default.
        save: Whether to save the retrained model.

    Returns:
        Training result dict (same format as train_lightgbm/train_xgboost).
    """
    if dataset_path is None:
        dataset_path = Path(__file__).resolve().parent.parent / "dataset" / "output" / "dataset.parquet"
    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    logger.info("Retraining %s model from %s", model_type, dataset_path)

    if model_type == "lightgbm":
        from models.train_lightgbm import train_lightgbm
        result = train_lightgbm(dataset_path=dataset_path, save=save)
    elif model_type == "xgboost":
        from models.train_xgboost import train_xgboost
        result = train_xgboost(dataset_path=dataset_path, save=save)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    logger.info(
        "Retraining complete: AUC=%.4f, %d folds",
        result["agg_metrics"].get("auc_roc", 0),
        len(result["fold_results"]),
    )

    # Save retrain log
    _log_retrain(model_type, result)

    return result


def _log_retrain(model_type: str, result: dict) -> None:
    """Append retrain event to retrain log."""
    log_path = REPORTS_DIR / "retrain_log.jsonl"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "model_type": model_type,
        "n_rows": result.get("n_rows", 0),
        "n_features": result.get("n_features", 0),
        "n_folds": len(result.get("fold_results", [])),
        "auc_roc": result["agg_metrics"].get("auc_roc", 0),
        "precision": result["agg_metrics"].get("precision", 0),
        "recall": result["agg_metrics"].get("recall", 0),
        "hit_rate": result["agg_metrics"].get("hit_rate", 0),
        "profit_factor": result["agg_metrics"].get("profit_factor", 0),
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    logger.info("Logged retrain event to %s", log_path)


def check_model_drift(
    model_type: str = "lightgbm",
) -> dict[str, Any]:
    """Check for model drift by comparing backtest metrics to live performance.

    Looks at saved picks files and compares predicted signals vs actual outcomes.

    Args:
        model_type: Model type to check.

    Returns:
        Dict with drift status, comparison metrics, and alerts.
    """
    # Load backtest metrics from model metadata
    meta_path = MODELS_DIR / model_type / "meta.json"
    if not meta_path.exists():
        logger.warning("No meta.json found for %s", model_type)
        return {"status": "unknown", "reason": "no model metadata"}

    with open(meta_path) as f:
        meta = json.load(f)

    backtest_metrics = meta.get("agg_metrics", {})
    backtest_auc = backtest_metrics.get("auc_roc", 0)
    backtest_hit_rate = backtest_metrics.get("hit_rate", 0)
    backtest_pf = backtest_metrics.get("profit_factor", 0)

    # Load recent picks and check actual outcomes
    picks_files = sorted(PICKS_DIR.glob(f"*_{model_type}_weekly_picks.csv"))

    if not picks_files:
        return {
            "status": "no_data",
            "reason": "no picks files found",
            "backtest_auc": backtest_auc,
            "backtest_hit_rate": backtest_hit_rate,
        }

    # Analyze recent picks (last 4 weeks)
    recent_picks = []
    for pf in picks_files[-4:]:
        try:
            df = pd.read_csv(pf)
            recent_picks.append(df)
        except Exception as e:
            logger.warning("Failed to read %s: %s", pf, e)

    if not recent_picks:
        return {"status": "no_data", "reason": "could not read picks files"}

    all_picks = pd.concat(recent_picks, ignore_index=True)

    # Check if we have SIGNAL column (predicted signals)
    n_signals = all_picks["SIGNAL"].sum() if "SIGNAL" in all_picks.columns else 0
    n_total = len(all_picks)
    signal_rate = n_signals / n_total if n_total > 0 else 0

    # Drift alerts
    alerts = []

    # Check retrain log for metric trends
    retrain_log = _load_retrain_log()
    if len(retrain_log) >= 2:
        latest = retrain_log[-1]
        previous = retrain_log[-2]

        auc_change = latest.get("auc_roc", 0) - previous.get("auc_roc", 0)
        hr_change = latest.get("hit_rate", 0) - previous.get("hit_rate", 0)

        if auc_change < -DRIFT_AUC_DROP:
            alerts.append(
                f"AUC dropped {auc_change:+.4f} vs previous retrain "
                f"({latest.get('auc_roc', 0):.4f} vs {previous.get('auc_roc', 0):.4f})"
            )

        if hr_change < -DRIFT_HIT_RATE_DROP:
            alerts.append(
                f"Hit rate dropped {hr_change:+.2%} vs previous retrain"
            )

    status = "ok" if not alerts else "drift_detected"

    return {
        "status": status,
        "alerts": alerts,
        "backtest_auc": backtest_auc,
        "backtest_hit_rate": backtest_hit_rate,
        "backtest_pf": backtest_pf,
        "recent_picks_count": n_total,
        "recent_signal_count": n_signals,
        "recent_signal_rate": signal_rate,
        "retrain_history_count": len(retrain_log),
    }


def _load_retrain_log() -> list[dict]:
    """Load retrain log entries."""
    log_path = REPORTS_DIR / "retrain_log.jsonl"
    if not log_path.exists():
        return []

    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def retrain_if_due(
    model_type: str = "lightgbm",
    retrain_interval_days: int = 30,
    force: bool = False,
) -> dict[str, Any]:
    """Retrain model if enough time has passed since last retrain.

    Args:
        model_type: Model type to retrain.
        retrain_interval_days: Days between retrains (default: 30).
        force: Force retrain regardless of schedule.

    Returns:
        Dict with action taken and result.
    """
    retrain_log = _load_retrain_log()
    model_entries = [e for e in retrain_log if e.get("model_type") == model_type]

    if model_entries and not force:
        last_retrain = datetime.fromisoformat(model_entries[-1]["timestamp"])
        days_since = (datetime.now() - last_retrain).days

        if days_since < retrain_interval_days:
            logger.info(
                "Last %s retrain was %d days ago (interval: %d). Skipping.",
                model_type, days_since, retrain_interval_days,
            )
            return {
                "action": "skipped",
                "reason": f"retrained {days_since} days ago",
                "next_retrain_in": retrain_interval_days - days_since,
            }

    logger.info("Retraining %s model...", model_type)
    result = retrain_model(model_type)

    # Check drift after retrain
    drift = check_model_drift(model_type)

    return {
        "action": "retrained",
        "auc_roc": result["agg_metrics"].get("auc_roc", 0),
        "hit_rate": result["agg_metrics"].get("hit_rate", 0),
        "drift_status": drift.get("status", "unknown"),
        "drift_alerts": drift.get("alerts", []),
    }


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Model retraining & drift detection")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command")

    # retrain sub-command
    retrain_parser = subparsers.add_parser("retrain", help="Retrain model")
    retrain_parser.add_argument("--model", default="lightgbm",
                                choices=["lightgbm", "xgboost", "all"],
                                help="Model to retrain")
    retrain_parser.add_argument("--dataset", type=str, default=None,
                                help="Path to dataset parquet")
    retrain_parser.add_argument("--force", action="store_true",
                                help="Force retrain regardless of schedule")

    # drift sub-command
    drift_parser = subparsers.add_parser("drift", help="Check model drift")
    drift_parser.add_argument("--model", default="lightgbm",
                              choices=["lightgbm", "xgboost", "all"],
                              help="Model to check")

    # schedule sub-command
    schedule_parser = subparsers.add_parser("schedule", help="Retrain if due")
    schedule_parser.add_argument("--model", default="lightgbm",
                                 choices=["lightgbm", "xgboost", "all"],
                                 help="Model to retrain")
    schedule_parser.add_argument("--interval", type=int, default=30,
                                 help="Days between retrains (default: 30)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    models = ["lightgbm", "xgboost"] if args.model == "all" else [args.model]

    if args.command == "retrain":
        for m in models:
            print(f"\n{'=' * 50}")
            print(f"  Retraining: {m}")
            print(f"{'=' * 50}")
            result = retrain_model(m, dataset_path=args.dataset)
            print(f"  AUC-ROC: {result['agg_metrics'].get('auc_roc', 0):.4f}")
            print(f"  Hit Rate: {result['agg_metrics'].get('hit_rate', 0):.2%}")
            print(f"  Profit Factor: {result['agg_metrics'].get('profit_factor', 0):.2f}")

    elif args.command == "drift":
        for m in models:
            print(f"\n{'=' * 50}")
            print(f"  Drift Check: {m}")
            print(f"{'=' * 50}")
            drift = check_model_drift(m)
            print(f"  Status: {drift['status']}")
            print(f"  Backtest AUC: {drift.get('backtest_auc', 0):.4f}")
            print(f"  Backtest Hit Rate: {drift.get('backtest_hit_rate', 0):.2%}")
            if drift.get("alerts"):
                print("  ALERTS:")
                for alert in drift["alerts"]:
                    print(f"    ⚠ {alert}")
            else:
                print("  No drift alerts.")

    elif args.command == "schedule":
        for m in models:
            result = retrain_if_due(m, retrain_interval_days=args.interval)
            print(f"\n{m}: {result['action']}")
            if result["action"] == "retrained":
                print(f"  AUC: {result.get('auc_roc', 0):.4f}")
                if result.get("drift_alerts"):
                    for alert in result["drift_alerts"]:
                        print(f"  ⚠ {alert}")
            elif result["action"] == "skipped":
                print(f"  {result['reason']}")

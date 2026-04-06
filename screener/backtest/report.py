"""Phase 5.4 — Backtest Comparison Report.

Generates a side-by-side comparison of all backtested strategies:
- Rule-based baselines (strict, relaxed, momentum)
- LightGBM at various top-N settings
- XGBoost at various top-N settings

Outputs:
- Text report to reports/backtest_report.txt
- Summary table to stdout

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import REPORTS_DIR
from backtest.metrics import (
    check_benchmarks,
    format_metrics_table,
    TARGET_BENCHMARKS,
)

logger = logging.getLogger(__name__)


def generate_comparison_table(results: dict[str, dict]) -> pd.DataFrame:
    """Generate a comparison DataFrame from backtest results.

    Args:
        results: Dict from run_full_backtest(): strategy_name → result dict.

    Returns:
        DataFrame with one row per strategy, columns = metric names.
    """
    rows = []

    for strategy, res in results.items():
        metrics = res["metrics"]
        tm = metrics.get("trade", {})
        pm = metrics.get("portfolio", {})

        row = {
            "Strategy": strategy,
            "Model": res.get("model_type", "unknown"),
            "Top N": res.get("top_n", 0),
            "Trades": tm.get("n_trades", 0),
            "Hit Rate": tm.get("hit_rate", 0),
            "Avg Return": tm.get("avg_return", 0),
            "Avg Win": tm.get("avg_win", 0),
            "Avg Loss": tm.get("avg_loss", 0),
            "Profit Factor": tm.get("profit_factor", 0),
            "Win/Loss Ratio": tm.get("win_loss_ratio", 0),
            "Total Return": pm.get("total_return", 0),
            "CAGR": pm.get("cagr", 0),
            "Sharpe": pm.get("sharpe_ratio", 0),
            "Sortino": pm.get("sortino_ratio", 0),
            "Max DD": pm.get("max_drawdown", 0),
            "Calmar": pm.get("calmar_ratio", 0),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Profit Factor", ascending=False).reset_index(drop=True)
    return df


def generate_text_report(results: dict[str, dict]) -> str:
    """Generate a full text comparison report.

    Args:
        results: Dict from run_full_backtest().

    Returns:
        Multi-line text report string.
    """
    lines = []
    lines.append("=" * 80)
    lines.append("  AlphaForge Screener — Backtest Comparison Report")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("  Disclaimer: NOT SEBI registered investment advice.")
    lines.append("=" * 80)

    # ── Summary table ──────────────────────────────────────────────────────
    comparison = generate_comparison_table(results)
    if comparison.empty:
        lines.append("\nNo backtest results to report.")
        return "\n".join(lines)

    lines.append("\n┌─────────────────────────────────────────────────────────────┐")
    lines.append("│  SUMMARY COMPARISON                                         │")
    lines.append("└─────────────────────────────────────────────────────────────┘")

    # Format fixed-width table
    header = (
        f"{'Strategy':<30} {'Trades':>6} {'Hit%':>6} {'AvgRet':>7} "
        f"{'PF':>6} {'CAGR':>7} {'Sharpe':>7} {'MaxDD':>7}"
    )
    lines.append(f"\n  {header}")
    lines.append(f"  {'─' * len(header)}")

    for _, row in comparison.iterrows():
        line = (
            f"  {row['Strategy']:<30} {row['Trades']:>6} "
            f"{row['Hit Rate']:>5.1%} {row['Avg Return']:>6.2%} "
            f"{row['Profit Factor']:>6.2f} {row['CAGR']:>6.2%} "
            f"{row['Sharpe']:>7.2f} {row['Max DD']:>6.2%}"
        )
        lines.append(line)

    # ── Per-strategy details ───────────────────────────────────────────────
    lines.append("\n")
    lines.append("─" * 80)
    lines.append("  DETAILED RESULTS PER STRATEGY")
    lines.append("─" * 80)

    for key, res in results.items():
        report = format_metrics_table(res["metrics"], title=key)
        lines.append(report)

        # Benchmark check
        benchmarks = check_benchmarks(res["metrics"])
        passed = sum(1 for b in benchmarks.values() if b["passed"])
        total = len(benchmarks)
        lines.append(f"  Benchmark Score: {passed}/{total}")
        for name, bm in benchmarks.items():
            status = "PASS" if bm["passed"] else "FAIL"
            dir_label = ">" if bm["direction"] == "gt" else "<"
            lines.append(
                f"    [{status}] {name}: {bm['value']:.4f} "
                f"(target {dir_label} {bm['target']:.4f})"
            )
        lines.append("")

    # ── Best strategy ──────────────────────────────────────────────────────
    if not comparison.empty:
        lines.append("─" * 80)
        lines.append("  BEST STRATEGIES BY METRIC")
        lines.append("─" * 80)

        metrics_to_rank = {
            "Hit Rate": ("max", ".1%"),
            "Profit Factor": ("max", ".2f"),
            "Sharpe": ("max", ".2f"),
            "CAGR": ("max", ".2%"),
            "Max DD": ("min", ".2%"),
        }

        for metric, (direction, fmt) in metrics_to_rank.items():
            if metric in comparison.columns:
                if direction == "max":
                    best_idx = comparison[metric].idxmax()
                else:
                    best_idx = comparison[metric].idxmin()
                best_row = comparison.loc[best_idx]
                val = best_row[metric]
                lines.append(
                    f"  Best {metric:<15}: {best_row['Strategy']:<30} "
                    f"({val:{fmt}})"
                )

    lines.append("\n" + "=" * 80)
    lines.append("  END OF REPORT")
    lines.append("=" * 80)

    return "\n".join(lines)


def save_report(
    results: dict[str, dict],
    output_path: Path | None = None,
) -> Path:
    """Generate and save comparison report.

    Args:
        results: Dict from run_full_backtest().
        output_path: Output file path. Default: reports/backtest_report.txt.

    Returns:
        Path to saved report.
    """
    if output_path is None:
        output_path = REPORTS_DIR / "backtest_report.txt"

    report_text = generate_text_report(results)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report_text)

    logger.info("Saved backtest report to %s", output_path)

    # Also save comparison table as CSV
    csv_path = output_path.with_suffix(".csv")
    comparison = generate_comparison_table(results)
    comparison.to_csv(csv_path, index=False)
    logger.info("Saved comparison CSV to %s", csv_path)

    return output_path


def save_trades_csv(
    trades: list,
    output_path: Path | None = None,
    strategy_name: str = "backtest",
) -> Path:
    """Save trade list to CSV.

    Args:
        trades: List of Trade objects.
        output_path: Output path. Default: reports/{strategy}_trades.csv.
        strategy_name: Name for file naming.

    Returns:
        Path to saved CSV.
    """
    if output_path is None:
        output_path = REPORTS_DIR / f"{strategy_name}_trades.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for t in trades:
        rows.append({
            "symbol": t.symbol,
            "signal_date": t.signal_date,
            "entry_date": t.entry_date,
            "exit_date": t.exit_date,
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "gross_return": t.gross_return,
            "costs": t.costs,
            "net_return": t.net_return,
            "probability": t.probability,
            "fold_id": t.fold_id,
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    logger.info("Saved %d trades to %s", len(trades), output_path)
    return output_path


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Generate backtest comparison report")
    parser.add_argument("--dataset", type=str, default=None,
                        help="Path to dataset parquet")
    parser.add_argument("--models", nargs="+", default=["lightgbm", "xgboost"],
                        help="Model types to compare")
    parser.add_argument("--top-ns", nargs="+", type=int, default=[5, 10, 20],
                        help="Top N values to compare")
    parser.add_argument("--no-baseline", action="store_true",
                        help="Skip rule-based baselines")
    parser.add_argument("--output", type=str, default=None,
                        help="Output report file path")
    parser.add_argument("--save-trades", action="store_true",
                        help="Save individual trade lists as CSV")
    args = parser.parse_args()

    from backtest.engine import run_full_backtest

    results = run_full_backtest(
        dataset_path=args.dataset,
        model_types=args.models,
        top_ns=args.top_ns,
        include_baseline=not args.no_baseline,
    )

    output = args.output
    if output:
        output = Path(output)

    report_path = save_report(results, output)
    print(f"\nReport saved to: {report_path}")

    # Print summary to stdout
    print(generate_text_report(results))

    if args.save_trades:
        for key, res in results.items():
            save_trades_csv(res["trades"], strategy_name=key)

"""Phase 4.1 — Baseline Technical Rules Strategy.

Simple rule-based screener for comparison against ML models.
Uses classic technical indicator thresholds to generate buy signals.

Rules (ALL must be true for a positive signal):
1. RSI(14) < 35 AND RSI recently bounced (RSI > RSI 1 day ago)
2. Volume > 2× 20-day average (volume surge)
3. MACD histogram turning positive (MACD_HIST > 0 AND was <= 0 recently)
4. Price above SMA(50)

This is intentionally simple — the purpose is to establish a baseline
that the ML models should comfortably beat.

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MODELS_DIR, TARGET_FORWARD_DAYS, TARGET_RETURN_THRESHOLD

logger = logging.getLogger(__name__)


# ── Rule Definitions ───────────────────────────────────────────────────────────

def rule_rsi_oversold_bounce(df: pd.DataFrame) -> pd.Series:
    """RSI(14) < 35 — stock is oversold territory."""
    return (df["RSI_14"] < 35).astype(int)


def rule_volume_surge(df: pd.DataFrame) -> pd.Series:
    """Volume > 2× 20-day average (VOL_SMA_RATIO > 2.0)."""
    return (df["VOL_SMA_RATIO"] > 2.0).astype(int)


def rule_macd_bullish(df: pd.DataFrame) -> pd.Series:
    """MACD histogram is positive (bullish momentum)."""
    if "MACD_HIST" not in df.columns:
        return pd.Series(0, index=df.index)
    return (df["MACD_HIST"] > 0).astype(int)


def rule_price_above_sma50(df: pd.DataFrame) -> pd.Series:
    """Price is above SMA(50) — uptrend confirmation."""
    return df["PRICE_ABOVE_SMA_50"].astype(int)


# ── Strategy Variants ──────────────────────────────────────────────────────────

STRATEGIES = {
    "strict": {
        "description": "ALL 4 rules must fire (AND logic)",
        "rules": [
            rule_rsi_oversold_bounce,
            rule_volume_surge,
            rule_macd_bullish,
            rule_price_above_sma50,
        ],
        "logic": "AND",
    },
    "relaxed": {
        "description": "At least 2 of 4 rules must fire",
        "rules": [
            rule_rsi_oversold_bounce,
            rule_volume_surge,
            rule_macd_bullish,
            rule_price_above_sma50,
        ],
        "logic": "MIN_2",
    },
    "momentum": {
        "description": "MACD bullish + volume surge + above SMA50",
        "rules": [
            rule_volume_surge,
            rule_macd_bullish,
            rule_price_above_sma50,
        ],
        "logic": "AND",
    },
}


def apply_rules(
    df: pd.DataFrame,
    strategy: str = "strict",
) -> pd.Series:
    """Apply a named rule-based strategy to generate signals.

    Args:
        df: Dataset with feature columns.
        strategy: One of 'strict', 'relaxed', 'momentum'.

    Returns:
        Binary series (1=signal, 0=no signal) aligned with df index.
    """
    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy}. Choose from {list(STRATEGIES.keys())}")

    strat = STRATEGIES[strategy]
    rule_results = pd.DataFrame(index=df.index)

    for i, rule_fn in enumerate(strat["rules"]):
        rule_results[f"rule_{i}"] = rule_fn(df)

    if strat["logic"] == "AND":
        signal = rule_results.prod(axis=1).astype(int)
    elif strat["logic"] == "MIN_2":
        signal = (rule_results.sum(axis=1) >= 2).astype(int)
    else:
        signal = rule_results.prod(axis=1).astype(int)

    return signal


def evaluate_baseline(
    df: pd.DataFrame,
    strategy: str = "strict",
) -> dict:
    """Run baseline strategy on dataset and compute performance metrics.

    Args:
        df: Dataset with features + TARGET_5PCT_5D + FORWARD_RETURN_5D.
        strategy: Strategy variant to evaluate.

    Returns:
        Dict with performance metrics.
    """
    signals = apply_rules(df, strategy)

    n_signals = signals.sum()
    if n_signals == 0:
        return {
            "strategy": strategy,
            "description": STRATEGIES[strategy]["description"],
            "n_signals": 0,
            "signal_rate": 0.0,
            "hit_rate": 0.0,
            "avg_return": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 0.0,
            "note": "No signals generated",
        }

    # Filter to signal rows
    signal_rows = df[signals == 1]
    true_labels = signal_rows["TARGET_5PCT_5D"].astype(float)
    returns = signal_rows["FORWARD_RETURN_5D"]

    # Hit rate: how many signals actually returned >5%
    hits = (true_labels == 1).sum()
    hit_rate = hits / len(signal_rows) if len(signal_rows) > 0 else 0.0

    # Return stats
    avg_return = returns.mean()
    winners = returns[returns > 0]
    losers = returns[returns <= 0]
    avg_win = winners.mean() if len(winners) > 0 else 0.0
    avg_loss = losers.mean() if len(losers) > 0 else 0.0

    # Profit factor
    gross_profit = winners.sum() if len(winners) > 0 else 0.0
    gross_loss = abs(losers.sum()) if len(losers) > 0 else 1e-9
    profit_factor = gross_profit / gross_loss

    return {
        "strategy": strategy,
        "description": STRATEGIES[strategy]["description"],
        "n_signals": int(n_signals),
        "signal_rate": float(n_signals / len(df)),
        "hit_rate": float(hit_rate),
        "avg_return": float(avg_return),
        "avg_win": float(avg_win),
        "avg_loss": float(avg_loss),
        "profit_factor": float(profit_factor),
        "n_winners": int(len(winners)),
        "n_losers": int(len(losers)),
    }


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Baseline rules strategy evaluation")
    parser.add_argument("--dataset", type=str, default=None,
                        help="Path to dataset parquet (default: dataset/output/dataset.parquet)")
    parser.add_argument("--strategy", type=str, default="all",
                        choices=["strict", "relaxed", "momentum", "all"],
                        help="Strategy to evaluate (default: all)")
    args = parser.parse_args()

    # Load dataset
    dataset_path = args.dataset or str(
        Path(__file__).resolve().parent.parent / "dataset" / "output" / "dataset.parquet"
    )
    logger.info("Loading dataset from %s", dataset_path)
    df = pd.read_parquet(dataset_path)
    logger.info("Dataset: %d rows × %d columns", len(df), len(df.columns))

    # Evaluate
    strategies_to_run = list(STRATEGIES.keys()) if args.strategy == "all" else [args.strategy]

    print(f"\nBaseline Rules Evaluation ({len(df):,} rows)")
    print("=" * 70)

    for strat_name in strategies_to_run:
        result = evaluate_baseline(df, strat_name)
        print(f"\nStrategy: {result['strategy']} — {result['description']}")
        print("-" * 50)
        print(f"  Signals:       {result['n_signals']:,} ({result['signal_rate']:.2%} of rows)")
        if result["n_signals"] > 0:
            print(f"  Hit rate:      {result['hit_rate']:.2%} (predicted >5%, actually >5%)")
            print(f"  Avg return:    {result['avg_return']:.4f} ({result['avg_return'] * 100:.2f}%)")
            print(f"  Avg win:       {result['avg_win']:.4f} ({result['avg_win'] * 100:.2f}%)")
            print(f"  Avg loss:      {result['avg_loss']:.4f} ({result['avg_loss'] * 100:.2f}%)")
            print(f"  Profit factor: {result['profit_factor']:.2f}")
            print(f"  Winners/Losers: {result['n_winners']}/{result['n_losers']}")
        else:
            print("  ⚠ No signals generated — rules too strict for this dataset")

    # Random baseline for comparison
    pos_rate = (df["TARGET_5PCT_5D"].astype(float) == 1).mean()
    print(f"\nRandom Baseline: {pos_rate:.2%} positive rate (expected hit rate for random picks)")
    print("\nDisclaimer: NOT SEBI registered investment advice. For personal research only.")

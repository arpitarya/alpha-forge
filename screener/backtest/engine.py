"""Phase 5.1 + 5.2 — Backtest Engine with Indian Market Cost Model.

Simulates trading based on model predictions from walk-forward CV:
1. For each test date, rank stocks by predicted probability
2. Select top N picks
3. Simulate: buy at next day's open, sell after 5 trading days at close
4. Apply realistic Indian market costs (brokerage, STT, exchange txn, GST, stamp duty)
5. Track equity curve and per-trade P&L

Cost Model (Indian Market — Delivery Trades):
  | Cost                | Rate              | Applied On   |
  |---------------------|-------------------|--------------|
  | Brokerage           | ₹20/order or 0.03%| Both sides   |
  | STT                 | 0.1%              | Sell side     |
  | Exchange txn        | 0.00345%          | Both sides   |
  | GST                 | 18%               | On brokerage + txn |
  | Stamp duty          | 0.015%            | Buy side     |
  | Total round-trip    | ~0.25-0.30%       |              |

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    MODELS_DIR,
    OHLCV_DIR,
    REPORTS_DIR,
    TARGET_FORWARD_DAYS,
)
from backtest.metrics import compute_all_metrics, format_metrics_table, check_benchmarks

logger = logging.getLogger(__name__)


# ── Indian Market Cost Model ───────────────────────────────────────────────────

@dataclass
class CostModel:
    """Indian equities delivery cost model.

    All rates as fractions (e.g., 0.001 = 0.1%).
    """
    brokerage_flat: float = 20.0            # ₹20 per order (flat fee brokers)
    brokerage_pct: float = 0.0003           # 0.03% (percentage-based brokers)
    use_flat_brokerage: bool = True          # Use flat (True) or percentage (False)
    stt_sell: float = 0.001                  # 0.1% on sell side (delivery)
    exchange_txn: float = 0.0000345          # 0.00345% each side
    gst_rate: float = 0.18                   # 18% on brokerage + exchange txn
    stamp_duty_buy: float = 0.00015          # 0.015% on buy side

    def compute_costs(
        self,
        entry_value: float,
        exit_value: float,
    ) -> dict[str, float]:
        """Compute detailed trading costs for a round-trip trade.

        Args:
            entry_value: Total buy value (price × quantity).
            exit_value: Total sell value (price × quantity).

        Returns:
            Dict with per-component costs and total.
        """
        # Buy-side brokerage
        if self.use_flat_brokerage:
            brokerage_buy = self.brokerage_flat
        else:
            brokerage_buy = entry_value * self.brokerage_pct

        # Sell-side brokerage
        if self.use_flat_brokerage:
            brokerage_sell = self.brokerage_flat
        else:
            brokerage_sell = exit_value * self.brokerage_pct

        # STT (sell side only for delivery)
        stt = exit_value * self.stt_sell

        # Exchange transaction charges (both sides)
        exchange_buy = entry_value * self.exchange_txn
        exchange_sell = exit_value * self.exchange_txn

        # GST on brokerage + exchange charges
        gst = (brokerage_buy + brokerage_sell + exchange_buy + exchange_sell) * self.gst_rate

        # Stamp duty (buy side only)
        stamp = entry_value * self.stamp_duty_buy

        total = brokerage_buy + brokerage_sell + stt + exchange_buy + exchange_sell + gst + stamp

        return {
            "brokerage_buy": brokerage_buy,
            "brokerage_sell": brokerage_sell,
            "stt": stt,
            "exchange_buy": exchange_buy,
            "exchange_sell": exchange_sell,
            "gst": gst,
            "stamp_duty": stamp,
            "total": total,
        }

    def compute_cost_pct(self, trade_value: float = 100_000.0) -> float:
        """Compute approximate round-trip cost as a percentage.

        Assumes entry_value ≈ exit_value for estimation.

        Args:
            trade_value: Approximate trade value for cost estimation.

        Returns:
            Round-trip cost as a fraction (e.g., 0.003 = 0.3%).
        """
        costs = self.compute_costs(trade_value, trade_value)
        return costs["total"] / trade_value


# ── Trade Record ───────────────────────────────────────────────────────────────

@dataclass
class Trade:
    """Record of a single simulated trade."""
    symbol: str
    signal_date: pd.Timestamp
    entry_date: pd.Timestamp | None = None
    exit_date: pd.Timestamp | None = None
    entry_price: float = 0.0
    exit_price: float = 0.0
    gross_return: float = 0.0
    costs: float = 0.0
    net_return: float = 0.0
    probability: float = 0.0
    fold_id: int = 0
    trade_value: float = 0.0


# ── Backtest Engine ────────────────────────────────────────────────────────────

class BacktestEngine:
    """Walk-forward backtest engine for stock screener strategies.

    Modes:
    1. ML models (LightGBM/XGBoost): rank by predicted probability → top N
    2. Rule-based strategies: take all signals on each date

    Uses FORWARD_RETURN_5D from dataset for quick backtesting, or can optionally
    load OHLCV for realistic open-to-close returns.
    """

    def __init__(
        self,
        top_n: int = 10,
        initial_capital: float = 1_000_000.0,
        capital_per_trade: float | None = None,
        cost_model: CostModel | None = None,
        use_ohlcv_prices: bool = False,
    ):
        """Initialize backtest engine.

        Args:
            top_n: Number of top picks per signal date.
            initial_capital: Starting portfolio value in INR.
            capital_per_trade: Capital allocated per trade. If None,
                               uses initial_capital / top_n.
            cost_model: Cost model to use. Default: Indian delivery costs.
            use_ohlcv_prices: If True, load OHLCV files for actual
                              open/close prices instead of using FORWARD_RETURN_5D.
        """
        self.top_n = top_n
        self.initial_capital = initial_capital
        self.capital_per_trade = capital_per_trade or (initial_capital / top_n)
        self.cost_model = cost_model or CostModel()
        self.use_ohlcv_prices = use_ohlcv_prices
        self._ohlcv_cache: dict[str, pd.DataFrame] = {}

    def _load_ohlcv(self, symbol: str) -> pd.DataFrame | None:
        """Load and cache OHLCV data for a symbol."""
        if symbol in self._ohlcv_cache:
            return self._ohlcv_cache[symbol]

        filepath = OHLCV_DIR / f"{symbol}.parquet"
        if not filepath.exists():
            logger.warning("No OHLCV file for %s", symbol)
            return None

        df = pd.read_parquet(filepath)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        self._ohlcv_cache[symbol] = df
        return df

    def _get_trade_return(
        self,
        symbol: str,
        signal_date: pd.Timestamp,
        forward_return: float,
    ) -> tuple[float, pd.Timestamp | None, pd.Timestamp | None, float, float]:
        """Get trade return, entry/exit dates and prices.

        Returns:
            (gross_return, entry_date, exit_date, entry_price, exit_price)
        """
        if not self.use_ohlcv_prices:
            # Use dataset's FORWARD_RETURN_5D (close-to-close)
            return forward_return, None, None, 0.0, 0.0

        # Load OHLCV for realistic open-to-close prices
        ohlcv = self._load_ohlcv(symbol)
        if ohlcv is None:
            return forward_return, None, None, 0.0, 0.0

        dates = ohlcv.index.sort_values()
        signal_loc = dates.get_indexer([signal_date], method="pad")[0]

        if signal_loc < 0 or signal_loc + 1 >= len(dates):
            return forward_return, None, None, 0.0, 0.0

        # Entry: open of next trading day (T+1)
        entry_idx = signal_loc + 1
        entry_date = dates[entry_idx]
        entry_price = float(ohlcv.iloc[entry_idx]["Open"])

        # Exit: close of T+5 (or last available)
        exit_idx = min(entry_idx + TARGET_FORWARD_DAYS, len(dates) - 1)
        exit_date = dates[exit_idx]
        exit_price = float(ohlcv.iloc[exit_idx]["Close"])

        if entry_price <= 0:
            return forward_return, None, None, 0.0, 0.0

        gross_return = (exit_price - entry_price) / entry_price
        return gross_return, entry_date, exit_date, entry_price, exit_price

    def run_from_predictions(
        self,
        dataset: pd.DataFrame,
        predictions: dict[int, tuple[np.ndarray, np.ndarray]],
        fold_test_indices: dict[int, np.ndarray],
    ) -> tuple[list[Trade], np.ndarray, dict]:
        """Run backtest from pre-computed predictions.

        Args:
            dataset: Full dataset with SYMBOL, FORWARD_RETURN_5D columns.
            predictions: Dict of fold_id → (probabilities, predictions) arrays.
            fold_test_indices: Dict of fold_id → test row indices.

        Returns:
            Tuple of (trades list, equity curve, metrics dict).
        """
        all_trades: list[Trade] = []

        for fold_id in sorted(predictions.keys()):
            probs, preds = predictions[fold_id]
            test_idx = fold_test_indices[fold_id]
            test_data = dataset.iloc[test_idx].copy()
            test_data["_prob"] = probs
            test_data["_pred"] = preds

            # Group by date, pick top N by probability
            for date, group in test_data.groupby(test_data.index):
                # Only consider positive predictions (or top N by prob)
                candidates = group.sort_values("_prob", ascending=False)
                picks = candidates.head(self.top_n)

                for _, row in picks.iterrows():
                    symbol = row["SYMBOL"]
                    fwd_ret = row["FORWARD_RETURN_5D"]
                    prob = row["_prob"]

                    if pd.isna(fwd_ret):
                        continue

                    gross_ret, entry_dt, exit_dt, entry_px, exit_px = (
                        self._get_trade_return(symbol, date, fwd_ret)
                    )

                    # Compute costs
                    trade_val = self.capital_per_trade
                    cost_detail = self.cost_model.compute_costs(
                        trade_val, trade_val * (1 + gross_ret)
                    )
                    cost_pct = cost_detail["total"] / trade_val if trade_val > 0 else 0.0
                    net_ret = gross_ret - cost_pct

                    trade = Trade(
                        symbol=symbol,
                        signal_date=date,
                        entry_date=entry_dt or date,
                        exit_date=exit_dt,
                        entry_price=entry_px,
                        exit_price=exit_px,
                        gross_return=gross_ret,
                        costs=cost_pct,
                        net_return=net_ret,
                        probability=prob,
                        fold_id=fold_id,
                        trade_value=trade_val,
                    )
                    all_trades.append(trade)

        return self._finalize(all_trades)

    def run_from_walk_forward(
        self,
        dataset: pd.DataFrame,
        fold_results: list,
        fold_test_indices: list[np.ndarray],
    ) -> tuple[list[Trade], np.ndarray, dict]:
        """Run backtest using FoldResult objects from walk-forward CV.

        Args:
            dataset: Full dataset.
            fold_results: List of FoldResult objects.
            fold_test_indices: List of test index arrays (one per fold).

        Returns:
            Tuple of (trades, equity_curve, metrics).
        """
        predictions = {}
        indices = {}

        for i, fr in enumerate(fold_results):
            predictions[fr.fold_id] = (fr.probabilities, fr.predictions)
            indices[fr.fold_id] = fold_test_indices[i]

        return self.run_from_predictions(dataset, predictions, indices)

    def run_baseline(
        self,
        dataset: pd.DataFrame,
        signals: pd.Series,
    ) -> tuple[list[Trade], np.ndarray, dict]:
        """Run backtest for a rule-based strategy.

        Args:
            dataset: Full dataset with SYMBOL, FORWARD_RETURN_5D.
            signals: Binary series (1=signal) aligned with dataset index.

        Returns:
            Tuple of (trades, equity_curve, metrics).
        """
        signal_rows = dataset[signals == 1]
        all_trades: list[Trade] = []

        for date, group in signal_rows.groupby(signal_rows.index):
            # Take all signals (no probability ranking for rule-based)
            picks = group.head(self.top_n) if len(group) > self.top_n else group

            for _, row in picks.iterrows():
                symbol = row["SYMBOL"]
                fwd_ret = row["FORWARD_RETURN_5D"]

                if pd.isna(fwd_ret):
                    continue

                gross_ret, entry_dt, exit_dt, entry_px, exit_px = (
                    self._get_trade_return(symbol, date, fwd_ret)
                )

                trade_val = self.capital_per_trade
                cost_detail = self.cost_model.compute_costs(
                    trade_val, trade_val * (1 + gross_ret)
                )
                cost_pct = cost_detail["total"] / trade_val if trade_val > 0 else 0.0
                net_ret = gross_ret - cost_pct

                trade = Trade(
                    symbol=symbol,
                    signal_date=date,
                    entry_date=entry_dt or date,
                    exit_date=exit_dt,
                    entry_price=entry_px,
                    exit_price=exit_px,
                    gross_return=gross_ret,
                    costs=cost_pct,
                    net_return=net_ret,
                    probability=0.0,
                    fold_id=0,
                    trade_value=trade_val,
                )
                all_trades.append(trade)

        return self._finalize(all_trades)

    def _finalize(
        self, trades: list[Trade]
    ) -> tuple[list[Trade], np.ndarray, dict]:
        """Build equity curve and compute metrics from trade list.

        Returns:
            Tuple of (trades, equity_curve, metrics_dict).
        """
        if not trades:
            logger.warning("No trades generated in backtest")
            equity = np.array([self.initial_capital])
            metrics = compute_all_metrics(pd.DataFrame(), equity)
            return trades, equity, metrics

        # Sort trades by signal date
        trades.sort(key=lambda t: t.signal_date)

        # Build equity curve
        equity = [self.initial_capital]
        current = self.initial_capital

        # Group trades by signal date to compute daily portfolio return
        trades_df = pd.DataFrame([
            {
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
                "trade_value": t.trade_value,
            }
            for t in trades
        ])

        # Group by signal date → compute period return
        for date, group in trades_df.groupby("signal_date"):
            n_trades = len(group)
            # Equal weight across trades in this period
            period_return = group["net_return"].mean()
            # Apply to capital (fraction invested = n_trades * capital_per_trade / current)
            fraction_invested = min(
                n_trades * self.capital_per_trade / current, 1.0
            ) if current > 0 else 0
            portfolio_return = fraction_invested * period_return
            current *= (1 + portfolio_return)
            equity.append(current)

        equity_curve = np.array(equity)

        # Date span for CAGR calculation
        first_date = trades_df["signal_date"].min()
        last_date = trades_df["signal_date"].max()
        total_days = (last_date - first_date).days if first_date != last_date else 365

        metrics = compute_all_metrics(trades_df, equity_curve, total_days)

        return trades, equity_curve, metrics


# ── Convenience Functions ──────────────────────────────────────────────────────

def run_full_backtest(
    dataset_path: str | Path | None = None,
    model_types: list[str] | None = None,
    top_ns: list[int] | None = None,
    include_baseline: bool = True,
) -> dict[str, dict]:
    """Run complete backtest for all models and configurations.

    Args:
        dataset_path: Path to dataset parquet. If None, uses default.
        model_types: List of model types to test (default: ['lightgbm', 'xgboost']).
        top_ns: List of top-N values to test (default: [5, 10, 20]).
        include_baseline: Whether to include rule-based baseline.

    Returns:
        Nested dict: {strategy_name → {top_n → {trades, equity, metrics}}}.
    """
    from models.walk_forward import (
        WalkForwardSplit,
        get_feature_columns,
        drop_all_nan_columns,
    )
    from models.baseline_rules import apply_rules, STRATEGIES

    if model_types is None:
        model_types = ["lightgbm", "xgboost"]
    if top_ns is None:
        top_ns = [5, 10, 20]

    # Load dataset
    if dataset_path is None:
        dataset_path = Path(__file__).resolve().parent.parent / "dataset" / "output" / "dataset.parquet"
    dataset = pd.read_parquet(dataset_path)
    if not isinstance(dataset.index, pd.DatetimeIndex):
        if "Date" in dataset.columns:
            dataset = dataset.set_index("Date")
        dataset.index = pd.to_datetime(dataset.index)
    dataset = dataset.sort_index()

    logger.info("Loaded dataset: %d rows × %d cols", *dataset.shape)

    feature_cols = get_feature_columns(dataset)
    feature_cols = drop_all_nan_columns(dataset, feature_cols)

    results = {}

    # ── ML Models ──────────────────────────────────────────────────────────
    for model_type in model_types:
        logger.info("Backtesting %s model...", model_type)

        # Load trained model
        try:
            model, meta = _load_model(model_type)
        except FileNotFoundError:
            logger.warning("No saved %s model found, skipping", model_type)
            continue

        # Get feature columns from model metadata
        model_features = meta.get("feature_cols", feature_cols)
        # Keep only features that exist in dataset
        model_features = [f for f in model_features if f in dataset.columns]
        prob_threshold = meta.get("prob_threshold", 0.5)

        # Run walk-forward to get predictions
        splitter = WalkForwardSplit()
        folds = splitter.split(dataset)

        fold_predictions = {}
        fold_indices = {}

        for fold_id, (train_idx, test_idx) in enumerate(folds, 1):
            X_test = dataset.iloc[test_idx][model_features]

            # Predict
            if model_type == "lightgbm":
                probs = model.predict(X_test)
            else:
                probs = model.predict_proba(X_test)[:, 1]

            preds = (probs >= prob_threshold).astype(int)
            fold_predictions[fold_id] = (probs, preds)
            fold_indices[fold_id] = test_idx

        # Run backtest at each top_n
        for top_n in top_ns:
            engine = BacktestEngine(top_n=top_n)
            trades, equity, metrics = engine.run_from_predictions(
                dataset, fold_predictions, fold_indices
            )
            key = f"{model_type}_top{top_n}"
            results[key] = {
                "trades": trades,
                "equity": equity,
                "metrics": metrics,
                "model_type": model_type,
                "top_n": top_n,
            }
            tm = metrics["trade"]
            logger.info(
                "%s: %d trades, hit_rate=%.1f%%, pf=%.2f, total_return=%.2f%%",
                key, tm["n_trades"], tm["hit_rate"] * 100,
                tm["profit_factor"], metrics["portfolio"]["total_return"] * 100,
            )

    # ── Rule-Based Baselines ───────────────────────────────────────────────
    if include_baseline:
        for strategy_name in STRATEGIES:
            logger.info("Backtesting baseline '%s'...", strategy_name)
            signals = apply_rules(dataset, strategy_name)
            n_signals = signals.sum()

            if n_signals == 0:
                logger.info("Strategy '%s' produced 0 signals, skipping", strategy_name)
                continue

            for top_n in top_ns:
                engine = BacktestEngine(top_n=top_n)
                trades, equity, metrics = engine.run_baseline(dataset, signals)
                key = f"baseline_{strategy_name}_top{top_n}"
                results[key] = {
                    "trades": trades,
                    "equity": equity,
                    "metrics": metrics,
                    "model_type": f"baseline_{strategy_name}",
                    "top_n": top_n,
                }
                tm = metrics["trade"]
                logger.info(
                    "%s: %d trades, hit_rate=%.1f%%, pf=%.2f",
                    key, tm["n_trades"], tm["hit_rate"] * 100,
                    tm["profit_factor"],
                )

    return results


def _load_model(model_type: str):
    """Load a saved model by type."""
    if model_type == "lightgbm":
        from models.train_lightgbm import load_model
        return load_model()
    elif model_type == "xgboost":
        from models.train_xgboost import load_model
        return load_model()
    else:
        raise ValueError(f"Unknown model type: {model_type}")


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Run backtest engine")
    parser.add_argument("--dataset", type=str, default=None,
                        help="Path to dataset parquet")
    parser.add_argument("--models", nargs="+", default=["lightgbm", "xgboost"],
                        help="Model types to test (default: lightgbm xgboost)")
    parser.add_argument("--top-ns", nargs="+", type=int, default=[5, 10, 20],
                        help="Top N values to test (default: 5 10 20)")
    parser.add_argument("--no-baseline", action="store_true",
                        help="Skip rule-based baselines")
    parser.add_argument("--use-ohlcv", action="store_true",
                        help="Use OHLCV files for actual open/close prices")
    args = parser.parse_args()

    results = run_full_backtest(
        dataset_path=args.dataset,
        model_types=args.models,
        top_ns=args.top_ns,
        include_baseline=not args.no_baseline,
    )

    print("\n" + "=" * 70)
    print("  BACKTEST RESULTS SUMMARY")
    print("=" * 70)

    for key, res in results.items():
        report = format_metrics_table(res["metrics"], title=key)
        print(report)

        # Check benchmarks
        benchmarks = check_benchmarks(res["metrics"])
        passed = sum(1 for b in benchmarks.values() if b["passed"])
        total = len(benchmarks)
        print(f"  Benchmarks: {passed}/{total} passed")
        for name, bm in benchmarks.items():
            status = "✓" if bm["passed"] else "✗"
            dir_label = ">" if bm["direction"] == "gt" else "<"
            print(f"    {status} {name}: {bm['value']:.4f} (target {dir_label} {bm['target']:.4f})")
        print()

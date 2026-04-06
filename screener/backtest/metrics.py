"""Phase 5.3 — Portfolio & Trading Performance Metrics.

Computes comprehensive performance metrics for backtest results:
- Trade-level: hit rate, avg win/loss, profit factor, win/loss ratio
- Portfolio-level: Sharpe ratio (annualized), CAGR, max drawdown, Calmar ratio

Target benchmarks (from PLAN.md):
  Hit Rate > 55%, Avg Win > 5%, Avg Loss < 3%, Profit Factor > 1.5,
  Sharpe Ratio > 1.5, Max Drawdown < 20%, CAGR > 25%, Win/Loss Ratio > 1.5

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Indian market: ~250 trading days per year
TRADING_DAYS_PER_YEAR = 250


# ── Trade-Level Metrics ────────────────────────────────────────────────────────

def compute_trade_metrics(trades: pd.DataFrame) -> dict[str, Any]:
    """Compute trade-level performance metrics.

    Args:
        trades: DataFrame with at least 'net_return' column (fractional returns).
                Optional: 'gross_return', 'costs' columns.

    Returns:
        Dict of metric name → value.
    """
    if trades.empty:
        logger.warning("No trades to compute metrics for")
        return _empty_trade_metrics()

    returns = trades["net_return"].values
    n_trades = len(returns)
    winners = returns[returns > 0]
    losers = returns[returns <= 0]
    n_winners = len(winners)
    n_losers = len(losers)

    # Hit rate
    hit_rate = n_winners / n_trades if n_trades > 0 else 0.0

    # Average returns
    avg_return = float(np.mean(returns))
    avg_win = float(np.mean(winners)) if n_winners > 0 else 0.0
    avg_loss = float(np.mean(losers)) if n_losers > 0 else 0.0

    # Profit factor = gross profits / gross losses
    gross_profit = float(np.sum(winners)) if n_winners > 0 else 0.0
    gross_loss = float(np.abs(np.sum(losers))) if n_losers > 0 else 1e-9
    profit_factor = gross_profit / gross_loss

    # Win/loss ratio (avg win / |avg loss|)
    win_loss_ratio = avg_win / abs(avg_loss) if avg_loss != 0 else float("inf")

    # Expectancy: avg profit per trade
    expectancy = avg_return

    # Best/worst trade
    best_trade = float(np.max(returns))
    worst_trade = float(np.min(returns))

    # Median return
    median_return = float(np.median(returns))

    # Gross returns (if available)
    total_costs = 0.0
    if "costs" in trades.columns:
        total_costs = float(trades["costs"].sum())

    metrics = {
        "n_trades": n_trades,
        "n_winners": n_winners,
        "n_losers": n_losers,
        "hit_rate": float(hit_rate),
        "avg_return": avg_return,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "median_return": median_return,
        "profit_factor": float(profit_factor),
        "win_loss_ratio": float(win_loss_ratio),
        "expectancy": float(expectancy),
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "total_profit": float(np.sum(returns)),
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "total_costs": total_costs,
    }

    return metrics


def _empty_trade_metrics() -> dict[str, Any]:
    """Return zeroed trade metrics when no trades exist."""
    return {
        "n_trades": 0,
        "n_winners": 0,
        "n_losers": 0,
        "hit_rate": 0.0,
        "avg_return": 0.0,
        "avg_win": 0.0,
        "avg_loss": 0.0,
        "median_return": 0.0,
        "profit_factor": 0.0,
        "win_loss_ratio": 0.0,
        "expectancy": 0.0,
        "best_trade": 0.0,
        "worst_trade": 0.0,
        "total_profit": 0.0,
        "gross_profit": 0.0,
        "gross_loss": 0.0,
        "total_costs": 0.0,
    }


# ── Portfolio-Level Metrics ────────────────────────────────────────────────────

def compute_sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.065,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Compute annualized Sharpe ratio.

    Args:
        returns: Array of periodic returns (per-trade or per-period).
        risk_free_rate: Annual risk-free rate (default: 6.5% for India).
        periods_per_year: Number of trading periods per year.

    Returns:
        Annualized Sharpe ratio.
    """
    if len(returns) < 2:
        return 0.0

    excess_returns = returns - (risk_free_rate / periods_per_year)
    mean_excess = np.mean(excess_returns)
    std_excess = np.std(excess_returns, ddof=1)

    if std_excess == 0 or np.isnan(std_excess):
        return 0.0

    sharpe = (mean_excess / std_excess) * np.sqrt(periods_per_year)
    return float(sharpe)


def compute_max_drawdown(equity_curve: np.ndarray) -> dict[str, float]:
    """Compute maximum drawdown from an equity curve.

    Args:
        equity_curve: Array of portfolio values over time.

    Returns:
        Dict with max_drawdown (fraction), peak_value, trough_value,
        peak_idx, trough_idx.
    """
    if len(equity_curve) < 2:
        return {"max_drawdown": 0.0, "peak_value": 0.0, "trough_value": 0.0,
                "peak_idx": 0, "trough_idx": 0}

    peak = equity_curve[0]
    max_dd = 0.0
    peak_idx = 0
    trough_idx = 0
    peak_at_max_dd = equity_curve[0]
    trough_at_max_dd = equity_curve[0]

    for i, val in enumerate(equity_curve):
        if val > peak:
            peak = val
            peak_idx_candidate = i
        dd = (peak - val) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd
            peak_idx = peak_idx_candidate
            trough_idx = i
            peak_at_max_dd = peak
            trough_at_max_dd = val

    return {
        "max_drawdown": float(max_dd),
        "peak_value": float(peak_at_max_dd),
        "trough_value": float(trough_at_max_dd),
        "peak_idx": int(peak_idx),
        "trough_idx": int(trough_idx),
    }


def compute_cagr(
    initial_value: float,
    final_value: float,
    n_years: float,
) -> float:
    """Compute Compound Annual Growth Rate.

    Args:
        initial_value: Starting portfolio value.
        final_value: Ending portfolio value.
        n_years: Number of years.

    Returns:
        CAGR as a fraction (e.g., 0.25 for 25%).
    """
    if initial_value <= 0 or final_value <= 0 or n_years <= 0:
        return 0.0

    cagr = (final_value / initial_value) ** (1.0 / n_years) - 1.0
    return float(cagr)


def compute_calmar_ratio(cagr: float, max_drawdown: float) -> float:
    """Compute Calmar ratio (CAGR / Max Drawdown).

    Args:
        cagr: Compound annual growth rate (fraction).
        max_drawdown: Maximum drawdown (fraction, positive).

    Returns:
        Calmar ratio.
    """
    if max_drawdown == 0:
        return 0.0 if cagr <= 0 else float("inf")
    return float(cagr / max_drawdown)


def compute_portfolio_metrics(
    equity_curve: np.ndarray,
    trade_returns: np.ndarray,
    total_days: int | None = None,
    risk_free_rate: float = 0.065,
) -> dict[str, Any]:
    """Compute portfolio-level performance metrics from equity curve.

    Args:
        equity_curve: Array of portfolio values (starting from initial capital).
        trade_returns: Array of per-trade returns (fractional).
        total_days: Total calendar days of backtest (for CAGR).
                    If None, estimated from equity curve length.
        risk_free_rate: Annual risk-free rate (default: 6.5% India).

    Returns:
        Dict of portfolio metric name → value.
    """
    if len(equity_curve) < 2:
        return _empty_portfolio_metrics()

    initial_value = equity_curve[0]
    final_value = equity_curve[-1]

    # Time span
    if total_days is None:
        # Estimate: assume each equity point is ~1 week (5 trading days / trade cycle)
        total_days = len(equity_curve) * 7
    n_years = total_days / 365.25

    # Total return
    total_return = (final_value - initial_value) / initial_value if initial_value > 0 else 0.0

    # CAGR
    cagr = compute_cagr(initial_value, final_value, n_years)

    # Sharpe (using per-trade returns, annualized assuming ~50 trades/year)
    trades_per_year = len(trade_returns) / n_years if n_years > 0 else 50
    sharpe = compute_sharpe_ratio(trade_returns, risk_free_rate,
                                  int(max(trades_per_year, 1)))

    # Max drawdown
    dd_info = compute_max_drawdown(equity_curve)

    # Calmar ratio
    calmar = compute_calmar_ratio(cagr, dd_info["max_drawdown"])

    # Sortino ratio (downside deviation only)
    sortino = _compute_sortino(trade_returns, risk_free_rate, trades_per_year)

    return {
        "total_return": float(total_return),
        "cagr": float(cagr),
        "sharpe_ratio": float(sharpe),
        "sortino_ratio": float(sortino),
        "max_drawdown": dd_info["max_drawdown"],
        "calmar_ratio": float(calmar),
        "initial_value": float(initial_value),
        "final_value": float(final_value),
        "n_years": float(n_years),
    }


def _compute_sortino(
    returns: np.ndarray,
    risk_free_rate: float,
    periods_per_year: float,
) -> float:
    """Compute Sortino ratio (like Sharpe but only downside volatility)."""
    if len(returns) < 2:
        return 0.0

    excess = returns - (risk_free_rate / periods_per_year)
    downside = excess[excess < 0]

    if len(downside) == 0:
        return float("inf") if np.mean(excess) > 0 else 0.0

    downside_std = np.std(downside, ddof=1)
    if downside_std == 0:
        return 0.0

    sortino = (np.mean(excess) / downside_std) * np.sqrt(periods_per_year)
    return float(sortino)


def _empty_portfolio_metrics() -> dict[str, Any]:
    """Return zeroed portfolio metrics."""
    return {
        "total_return": 0.0,
        "cagr": 0.0,
        "sharpe_ratio": 0.0,
        "sortino_ratio": 0.0,
        "max_drawdown": 0.0,
        "calmar_ratio": 0.0,
        "initial_value": 0.0,
        "final_value": 0.0,
        "n_years": 0.0,
    }


# ── Combined Metrics ───────────────────────────────────────────────────────────

def compute_all_metrics(
    trades: pd.DataFrame,
    equity_curve: np.ndarray,
    total_days: int | None = None,
    risk_free_rate: float = 0.065,
) -> dict[str, Any]:
    """Compute all trade-level + portfolio-level metrics.

    Args:
        trades: DataFrame with at least 'net_return' column.
        equity_curve: Array of portfolio values.
        total_days: Total calendar days of backtest.
        risk_free_rate: Annual risk-free rate.

    Returns:
        Combined dict: trade metrics + portfolio metrics under 'trade' and 'portfolio' keys.
    """
    trade_metrics = compute_trade_metrics(trades)
    portfolio_metrics = compute_portfolio_metrics(
        equity_curve,
        trades["net_return"].values if not trades.empty else np.array([]),
        total_days,
        risk_free_rate,
    )

    return {
        "trade": trade_metrics,
        "portfolio": portfolio_metrics,
    }


def format_metrics_table(metrics: dict[str, Any], title: str = "") -> str:
    """Format metrics dict as a human-readable text table.

    Args:
        metrics: Output from compute_all_metrics().
        title: Optional title for the table.

    Returns:
        Formatted string.
    """
    lines = []
    if title:
        lines.append(f"\n{'=' * 60}")
        lines.append(f"  {title}")
        lines.append(f"{'=' * 60}")

    if "trade" in metrics:
        tm = metrics["trade"]
        lines.append("\n  Trade Metrics")
        lines.append(f"  {'─' * 40}")
        lines.append(f"  Total Trades:       {tm['n_trades']}")
        lines.append(f"  Winners / Losers:   {tm['n_winners']} / {tm['n_losers']}")
        lines.append(f"  Hit Rate:           {tm['hit_rate']:.1%}")
        lines.append(f"  Avg Return:         {tm['avg_return']:.2%}")
        lines.append(f"  Avg Win:            {tm['avg_win']:.2%}")
        lines.append(f"  Avg Loss:           {tm['avg_loss']:.2%}")
        lines.append(f"  Median Return:      {tm['median_return']:.2%}")
        lines.append(f"  Profit Factor:      {tm['profit_factor']:.2f}")
        lines.append(f"  Win/Loss Ratio:     {tm['win_loss_ratio']:.2f}")
        lines.append(f"  Best Trade:         {tm['best_trade']:.2%}")
        lines.append(f"  Worst Trade:        {tm['worst_trade']:.2%}")
        lines.append(f"  Total Costs:        {tm['total_costs']:.4%}")

    if "portfolio" in metrics:
        pm = metrics["portfolio"]
        lines.append("\n  Portfolio Metrics")
        lines.append(f"  {'─' * 40}")
        lines.append(f"  Total Return:       {pm['total_return']:.2%}")
        lines.append(f"  CAGR:               {pm['cagr']:.2%}")
        lines.append(f"  Sharpe Ratio:       {pm['sharpe_ratio']:.2f}")
        lines.append(f"  Sortino Ratio:      {pm['sortino_ratio']:.2f}")
        lines.append(f"  Max Drawdown:       {pm['max_drawdown']:.2%}")
        lines.append(f"  Calmar Ratio:       {pm['calmar_ratio']:.2f}")
        lines.append(f"  Duration:           {pm['n_years']:.1f} years")

    lines.append("")
    return "\n".join(lines)


# ── Benchmark Comparison ───────────────────────────────────────────────────────

TARGET_BENCHMARKS = {
    "hit_rate": (0.55, "gt"),       # > 55%
    "avg_win": (0.05, "gt"),        # > 5%
    "avg_loss": (-0.03, "gt"),      # > -3% (loss less than 3%)
    "profit_factor": (1.5, "gt"),   # > 1.5
    "sharpe_ratio": (1.5, "gt"),    # > 1.5
    "max_drawdown": (0.20, "lt"),   # < 20%
    "cagr": (0.25, "gt"),           # > 25%
    "win_loss_ratio": (1.5, "gt"),  # > 1.5
}


def check_benchmarks(metrics: dict[str, Any]) -> dict[str, dict]:
    """Check metrics against target benchmarks.

    Args:
        metrics: Output from compute_all_metrics().

    Returns:
        Dict of metric → {value, target, passed, direction}.
    """
    results = {}
    flat = {}
    if "trade" in metrics:
        flat.update(metrics["trade"])
    if "portfolio" in metrics:
        flat.update(metrics["portfolio"])

    for metric_name, (target, direction) in TARGET_BENCHMARKS.items():
        value = flat.get(metric_name, None)
        if value is None:
            continue

        if direction == "gt":
            passed = value > target
        else:  # lt
            passed = value < target

        results[metric_name] = {
            "value": value,
            "target": target,
            "direction": direction,
            "passed": passed,
        }

    return results

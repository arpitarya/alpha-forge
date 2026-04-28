"""Pure helpers for memory pick parsing."""

from __future__ import annotations

_FEATURE_KEYS = (
    "rsi_14", "RSI_14", "vol_sma_ratio", "VOL_SMA_RATIO",
    "macd_hist", "MACD_HIST", "adx_14", "ADX_14",
    "dist_52w_high_pct", "DIST_52W_HIGH_PCT", "roc_5", "ROC_5",
)


def extract_pick_fields(pick: dict) -> tuple[str, float, int | None, dict]:
    """Pull symbol, probability, rank, raw_features from a pick dict (case-tolerant)."""
    symbol = str(pick.get("symbol", pick.get("SYMBOL", ""))).upper()
    prob = float(pick.get("probability", pick.get("PROBABILITY", 0.0)))
    rank_val = pick.get("rank", pick.get("RANK"))
    rank = int(rank_val) if rank_val is not None else None
    raw_features = {k: pick[k] for k in _FEATURE_KEYS if k in pick}
    return symbol, prob, rank, raw_features

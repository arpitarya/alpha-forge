"""Pure helper for building screener-pick explanation strings."""

from __future__ import annotations


def build_pick_explanation_text(pick: dict) -> str:
    """Build a rich, embeddable text description of a screener pick (case-tolerant)."""
    symbol = pick.get("symbol", pick.get("SYMBOL", "UNKNOWN"))
    date = pick.get("scan_date", pick.get("DATE", ""))
    model = pick.get("model_type", "ml")
    prob = pick.get("probability", pick.get("PROBABILITY", 0.0))
    rank = pick.get("rank", pick.get("RANK", ""))

    parts = [f"{symbol} screener pick"]
    if date:
        parts.append(date)
    parts.append(f"{model}: probability={float(prob):.3f}")
    if rank:
        parts.append(f"rank={rank}")
    parts.extend(_feature_phrases(pick))
    return ", ".join(parts)


def _feature_phrases(pick: dict) -> list[str]:
    out: list[str] = []
    rsi = pick.get("rsi_14", pick.get("RSI_14", ""))
    vol = pick.get("vol_sma_ratio", pick.get("VOL_SMA_RATIO", ""))
    macd = pick.get("macd_hist", pick.get("MACD_HIST", ""))
    adx = pick.get("adx_14", pick.get("ADX_14", ""))
    dist_52w = pick.get("dist_52w_high_pct", pick.get("DIST_52W_HIGH_PCT", ""))
    roc = pick.get("roc_5", pick.get("ROC_5", ""))
    if rsi != "":
        out.append(f"RSI={float(rsi):.1f}")
    if vol != "":
        out.append(f"volume ratio={float(vol):.2f}x average")
    if macd != "":
        out.append(f"MACD histogram={'+' if float(macd) >= 0 else ''}{float(macd):.2f}")
    if adx != "":
        out.append(f"ADX={float(adx):.1f} (trend strength)")
    if dist_52w != "":
        out.append(f"distance from 52-week high={float(dist_52w):.1f}%")
    if roc != "":
        out.append(f"5-day ROC={'+' if float(roc) >= 0 else ''}{float(roc):.2f}%")
    return out

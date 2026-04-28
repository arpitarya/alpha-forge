"""Pure formatting helpers for AI prompt context."""

from __future__ import annotations


def format_picks_context(picks: list[dict]) -> str:
    if not picks:
        return "No relevant screener picks found."
    return "\n".join(
        f"- {p['symbol']} ({p['scan_date']}, {p['model_type']}): "
        f"probability={p['probability']:.3f}, rank={p.get('rank', 'N/A')}, "
        f"signal: {p['explanation_text']}"
        for p in picks
    )


def format_memory_context(turns: list[dict]) -> str:
    if not turns:
        return ""
    lines = ["Relevant past analysis:"]
    lines.extend(f"  [{t['role']}] {t['content'][:200]}" for t in turns)
    return "\n".join(lines)


def format_portfolio_context(portfolio: list[dict]) -> str:
    if not portfolio:
        return "Not provided."
    return "\n".join(
        f"- {h.get('symbol')}: {h.get('quantity')} shares @ avg ₹{h.get('avg_price')}"
        for h in portfolio
    )


def build_system_prompt(picks_ctx: str, portfolio_ctx: str, mem_ctx: str, symbol: str) -> str:
    out = (
        f"== SCREENER CONTEXT (most relevant ML picks) ==\n{picks_ctx}\n\n"
        f"== PORTFOLIO CONTEXT ==\n{portfolio_ctx}\n"
    )
    if symbol:
        out += f"\n== CURRENT SYMBOL == {symbol}\n"
    if mem_ctx:
        out += f"\n{mem_ctx}\n"
    return out

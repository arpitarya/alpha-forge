"""Holdings aggregator + treemap layout + simple rebalance suggestions.

The aggregator walks all configured BrokerSource caches and merges their
holdings into one portfolio. We don't dedupe across sources by ISIN
because the same security held in two brokers is a real allocation
choice, not a duplicate. Consumers that want a deduped view can group by
ISIN themselves.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.brokers.base import AssetClass, Holding
from app.services.brokers.registry import SOURCES


@dataclass
class TreemapCell:
    symbol: str
    sublabel: str
    value: float
    pct: float
    pnl: float
    pnl_pct: float
    asset_class: AssetClass
    # Layout (computed by `_squarify`): % of width/height in 0..1 units.
    left_pct: float
    top_pct: float
    width_pct: float
    height_pct: float


@dataclass
class AllocationSlice:
    asset_class: AssetClass
    value: float
    pct: float


@dataclass
class RebalanceDrift:
    asset_class: AssetClass
    target_pct: float
    actual_pct: float
    drift_pct: float


@dataclass
class RebalanceSuggestion:
    action: str  # "trim X" or "add Y"


# Default target allocation. Editable via settings later; for now just a
# sensible balanced template.
DEFAULT_TARGETS: dict[AssetClass, float] = {
    AssetClass.EQUITY: 60.0,
    AssetClass.MUTUAL_FUND: 15.0,
    AssetClass.BOND: 15.0,
    AssetClass.GOLD: 5.0,
    AssetClass.CRYPTO: 3.0,
    AssetClass.CASH: 2.0,
}


class HoldingsAggregator:
    """Read-only roll-up over the registered BrokerSource instances."""

    def __init__(self, targets: dict[AssetClass, float] | None = None) -> None:
        self.targets = targets or DEFAULT_TARGETS

    # ── Core data ────────────────────────────────────────────────────────

    def all_holdings(self, source: str | None = None) -> list[Holding]:
        if source:
            return list(SOURCES[source].cached) if source in SOURCES else []
        merged: list[Holding] = []
        for s in SOURCES.values():
            merged.extend(s.cached)
        return merged

    def totals(self, source: str | None = None) -> dict[str, float]:
        h = self.all_holdings(source)
        invested = sum(x.invested for x in h)
        current = sum(x.current_value for x in h)
        pnl = current - invested
        pnl_pct = (pnl / invested * 100) if invested else 0.0
        return {
            "invested": round(invested, 2),
            "current_value": round(current, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "count": len(h),
        }

    # ── Allocation pie ──────────────────────────────────────────────────

    def allocation(self, source: str | None = None) -> list[AllocationSlice]:
        h = self.all_holdings(source)
        total = sum(x.current_value for x in h) or 1.0
        buckets: dict[AssetClass, float] = {}
        for x in h:
            buckets[x.asset_class] = buckets.get(x.asset_class, 0.0) + x.current_value
        return [
            AllocationSlice(asset_class=c, value=round(v, 2), pct=round(v / total * 100, 2))
            for c, v in sorted(buckets.items(), key=lambda kv: -kv[1])
        ]

    # ── Treemap (squarified-ish) ────────────────────────────────────────

    def treemap(self, source: str | None = None, max_cells: int = 24) -> list[TreemapCell]:
        h = sorted(self.all_holdings(source), key=lambda x: -x.current_value)[:max_cells]
        total = sum(x.current_value for x in h) or 1.0
        rects = _squarify([x.current_value / total for x in h], 0, 0, 1, 1)
        cells: list[TreemapCell] = []
        for hold, (lx, ly, lw, lh) in zip(h, rects, strict=False):
            sub = (
                f"{hold.asset_class.value} · ₹{round(hold.current_value):,}"
                if hold.current_value
                else hold.asset_class.value
            )
            cells.append(
                TreemapCell(
                    symbol=hold.symbol,
                    sublabel=sub,
                    value=hold.current_value,
                    pct=round(hold.current_value / total * 100, 2),
                    pnl=hold.pnl,
                    pnl_pct=hold.pnl_pct,
                    asset_class=hold.asset_class,
                    left_pct=round(lx * 100, 4),
                    top_pct=round(ly * 100, 4),
                    width_pct=round(lw * 100, 4),
                    height_pct=round(lh * 100, 4),
                )
            )
        return cells

    # ── Rebalance ───────────────────────────────────────────────────────

    def rebalance(self) -> tuple[list[RebalanceDrift], list[RebalanceSuggestion]]:
        alloc = {a.asset_class: a.pct for a in self.allocation()}
        drift: list[RebalanceDrift] = []
        for cls, target in self.targets.items():
            actual = alloc.get(cls, 0.0)
            drift.append(
                RebalanceDrift(
                    asset_class=cls,
                    target_pct=target,
                    actual_pct=round(actual, 2),
                    drift_pct=round(actual - target, 2),
                )
            )
        suggestions: list[RebalanceSuggestion] = []
        for d in drift:
            if d.drift_pct > 5:
                suggestions.append(RebalanceSuggestion(action=f"Trim {d.asset_class.value} ~{d.drift_pct:.0f}%"))
            elif d.drift_pct < -5:
                suggestions.append(RebalanceSuggestion(action=f"Add {d.asset_class.value} ~{abs(d.drift_pct):.0f}%"))
        return drift, suggestions


# ── Squarified treemap layout ─────────────────────────────────────────────────


def _squarify(values: list[float], x: float, y: float, w: float, h: float) -> list[tuple[float, float, float, float]]:
    """Tiny squarified-treemap layout — good enough for ≤24 cells.

    Splits the box along the longer dimension proportionally to a row of
    cells whose sizes sum to a target slice; recurses on the remainder.
    Doesn't guarantee perfect aspect ratios but produces visually sensible
    layouts for portfolio sizes we care about.
    """
    if not values or w <= 0 or h <= 0:
        return []
    if len(values) == 1:
        return [(x, y, w, h)]

    total = sum(values)
    if total <= 0:
        return [(x, y, 0, 0) for _ in values]

    # Take rows of cells until the next addition worsens the worst aspect
    # ratio; lay that row out along the shorter side.
    along_w = w >= h
    short_side = h if along_w else w
    long_side = w if along_w else h

    row: list[float] = []
    remaining = values[:]
    while remaining:
        candidate = row + [remaining[0]]
        if not row or _worst(candidate, short_side, total) >= _worst(row, short_side, total):
            row = candidate
            remaining.pop(0)
        else:
            break

    row_total = sum(row)
    row_long = (row_total / total) * long_side
    rects: list[tuple[float, float, float, float]] = []
    cursor = 0.0
    for v in row:
        size = (v / row_total) * short_side if row_total else 0.0
        if along_w:
            rects.append((x, y + cursor, row_long, size))
        else:
            rects.append((x + cursor, y, size, row_long))
        cursor += size

    if remaining:
        if along_w:
            rects.extend(_squarify(remaining, x + row_long, y, w - row_long, h))
        else:
            rects.extend(_squarify(remaining, x, y + row_long, w, h - row_long))
    return rects


def _worst(row: list[float], short_side: float, total: float) -> float:
    if not row:
        return float("inf")
    s = sum(row) or 1e-9
    long_side = s / total if total else 0.0
    cells_short = [v / s * short_side for v in row] if s else []
    if not cells_short or short_side <= 0:
        return float("inf")
    max_short = max(cells_short)
    min_short = min(cells_short)
    if min_short <= 0:
        return float("inf")
    return max(long_side / min_short, max_short / long_side)

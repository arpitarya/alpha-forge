"""Holdings aggregator — read-only roll-up over registered BrokerSource caches.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from app.modules.brokers.aggregator_types import (
    DEFAULT_TARGETS,
    AllocationSlice,
    RebalanceDrift,
    RebalanceSuggestion,
    TreemapCell,
)
from app.modules.brokers.base import AssetClass, Holding
from app.modules.brokers.registry import SOURCES
from app.modules.brokers.treemap_helper import squarify


class HoldingsAggregator:
    def __init__(self, targets: dict[AssetClass, float] | None = None) -> None:
        self.targets = targets or DEFAULT_TARGETS

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
        return {
            "invested": round(invested, 2),
            "current_value": round(current, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round((pnl / invested * 100) if invested else 0.0, 2),
            "count": len(h),
        }

    def allocation(self, source: str | None = None) -> list[AllocationSlice]:
        h = self.all_holdings(source)
        total = sum(x.current_value for x in h) or 1.0
        buckets: dict[AssetClass, float] = {}
        for x in h:
            buckets[x.asset_class] = buckets.get(x.asset_class, 0.0) + x.current_value
        return [
            AllocationSlice(
                asset_class=c, value=round(v, 2), pct=round(v / total * 100, 2)
            )
            for c, v in sorted(buckets.items(), key=lambda kv: -kv[1])
        ]

    def treemap(self, source: str | None = None, max_cells: int = 24) -> list[TreemapCell]:
        h = sorted(self.all_holdings(source), key=lambda x: -x.current_value)[:max_cells]
        total = sum(x.current_value for x in h) or 1.0
        rects = squarify([x.current_value / total for x in h], 0, 0, 1, 1)
        cells: list[TreemapCell] = []
        for hold, (lx, ly, lw, lh) in zip(h, rects, strict=False):
            sub = (
                f"{hold.asset_class.value} · ₹{round(hold.current_value):,}"
                if hold.current_value
                else hold.asset_class.value
            )
            cells.append(
                TreemapCell(
                    symbol=hold.symbol, sublabel=sub,
                    value=hold.current_value,
                    pct=round(hold.current_value / total * 100, 2),
                    pnl=hold.pnl, pnl_pct=hold.pnl_pct,
                    asset_class=hold.asset_class,
                    left_pct=round(lx * 100, 4), top_pct=round(ly * 100, 4),
                    width_pct=round(lw * 100, 4), height_pct=round(lh * 100, 4),
                )
            )
        return cells

    def rebalance(self) -> tuple[list[RebalanceDrift], list[RebalanceSuggestion]]:
        alloc = {a.asset_class: a.pct for a in self.allocation()}
        drift = [
            RebalanceDrift(
                asset_class=cls, target_pct=target,
                actual_pct=round(alloc.get(cls, 0.0), 2),
                drift_pct=round(alloc.get(cls, 0.0) - target, 2),
            )
            for cls, target in self.targets.items()
        ]
        suggestions: list[RebalanceSuggestion] = []
        for d in drift:
            if d.drift_pct > 5:
                suggestions.append(RebalanceSuggestion(
                    action=f"Trim {d.asset_class.value} ~{d.drift_pct:.0f}%"))
            elif d.drift_pct < -5:
                suggestions.append(RebalanceSuggestion(
                    action=f"Add {d.asset_class.value} ~{abs(d.drift_pct):.0f}%"))
        return drift, suggestions

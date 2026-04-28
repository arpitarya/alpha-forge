"""Aggregator response dataclasses + default rebalance targets."""

from __future__ import annotations

from dataclasses import dataclass

from app.modules.brokers.base import AssetClass


@dataclass
class TreemapCell:
    symbol: str
    sublabel: str
    value: float
    pct: float
    pnl: float
    pnl_pct: float
    asset_class: AssetClass
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
    action: str


DEFAULT_TARGETS: dict[AssetClass, float] = {
    AssetClass.EQUITY: 60.0,
    AssetClass.MUTUAL_FUND: 15.0,
    AssetClass.BOND: 15.0,
    AssetClass.GOLD: 5.0,
    AssetClass.CRYPTO: 3.0,
    AssetClass.CASH: 2.0,
}

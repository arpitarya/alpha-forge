"""Pydantic schemas for terminal dashboard payloads."""

from __future__ import annotations

from pydantic import BaseModel

DISCLAIMER = "Not SEBI registered investment advice."


class TickerItem(BaseModel):
    symbol: str
    price: str
    change: str
    tone: str  # "up" | "dn"


class WatchlistItem(BaseModel):
    symbol: str
    sublabel: str
    price: str
    change: str
    tone: str  # "up" | "dn"


class RiskMeter(BaseModel):
    bars: list[float]
    active_index: int
    confidence: float


class BriefBlock(BaseModel):
    title: str
    body: str
    cta: str
    accent: bool = False


class TerminalBrief(BaseModel):
    blocks: list[BriefBlock]
    generated_at: str
    disclaimer: str = DISCLAIMER


class StatCard(BaseModel):
    label: str
    value: float
    delta: str
    delta_tone: str  # "up" | "dn" | "neutral" | "accent"
    sparkline: list[float] | None = None


class DashboardStats(BaseModel):
    net_worth: StatCard
    pnl_today: StatCard
    confidence: StatCard
    disclaimer: str = DISCLAIMER

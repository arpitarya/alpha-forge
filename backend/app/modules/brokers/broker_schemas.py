"""Broker domain enums + Pydantic schemas (Holding, SourceInfo)."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    EQUITY = "equity"
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
    BOND = "bond"
    GOLD = "gold"
    CRYPTO = "crypto"
    CASH = "cash"
    OTHER = "other"


class SourceKind(str, Enum):
    API = "api"
    CSV = "csv"


class SourceStatus(str, Enum):
    UNCONFIGURED = "unconfigured"
    READY = "ready"
    SYNCING = "syncing"
    ERROR = "error"


class Holding(BaseModel):
    source: str
    asset_class: AssetClass
    symbol: str
    name: str | None = None
    isin: str | None = None
    quantity: float
    avg_price: float
    last_price: float
    invested: float
    current_value: float
    pnl: float
    pnl_pct: float
    sector: str | None = None
    exchange: str | None = None
    as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SourceInfo(BaseModel):
    slug: str
    label: str
    kind: SourceKind
    status: SourceStatus
    holdings_count: int = 0
    last_synced_at: datetime | None = None
    error_message: str | None = None
    notes: str | None = None

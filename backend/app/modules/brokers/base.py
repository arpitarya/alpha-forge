"""Broker source ABC + unified Holding model."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import IO

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
    """Two integration paths: pull via API, or accept user-uploaded CSV."""

    API = "api"
    CSV = "csv"


class SourceStatus(str, Enum):
    UNCONFIGURED = "unconfigured"
    READY = "ready"
    SYNCING = "syncing"
    ERROR = "error"


class Holding(BaseModel):
    """Unified holding shape across all sources."""

    source: str  # e.g. "zerodha", "groww"
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


class BrokerSource(ABC):
    """Adapter for one holdings provider.

    Two integration paths:
      - kind=API:  override `fetch()` (e.g. Angel One SmartAPI).
      - kind=CSV:  override `parse(stream)` (e.g. Zerodha console export).

    The aggregator never branches on source identity — it iterates over
    BrokerSource instances and merges their Holding lists.
    """

    slug: str
    label: str
    kind: SourceKind

    def __init__(self) -> None:
        self._cached: list[Holding] | None = None
        self._last_synced_at: datetime | None = None
        self._status: SourceStatus = SourceStatus.UNCONFIGURED
        self._error: str | None = None

    # ── Override one of these ────────────────────────────────────────────

    async def fetch(self) -> list[Holding]:
        """API-driven sources override this."""
        raise NotImplementedError(f"{self.slug}: override fetch() or use parse()")

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        """CSV-driven sources override this."""
        raise NotImplementedError(f"{self.slug}: override parse() or use fetch()")

    # ── Shared lifecycle ────────────────────────────────────────────────

    async def sync(self) -> list[Holding]:
        """Refresh from upstream (API only)."""
        if self.kind != SourceKind.API:
            raise RuntimeError(f"{self.slug}: sync() only valid for API sources")
        self._status = SourceStatus.SYNCING
        try:
            holdings = await self.fetch()
            self._cached = holdings
            self._last_synced_at = datetime.now(timezone.utc)
            self._status = SourceStatus.READY
            self._error = None
            return holdings
        except Exception as e:  # noqa: BLE001
            self._status = SourceStatus.ERROR
            self._error = str(e)
            raise

    def ingest_csv(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        """Apply uploaded CSV (CSV sources only)."""
        if self.kind != SourceKind.CSV:
            raise RuntimeError(f"{self.slug}: ingest_csv() only valid for CSV sources")
        self._status = SourceStatus.SYNCING
        try:
            holdings = self.parse(stream, filename)
            self._cached = holdings
            self._last_synced_at = datetime.now(timezone.utc)
            self._status = SourceStatus.READY
            self._error = None
            return holdings
        except Exception as e:  # noqa: BLE001
            self._status = SourceStatus.ERROR
            self._error = str(e)
            raise

    # ── Read-side helpers ───────────────────────────────────────────────

    @property
    def cached(self) -> list[Holding]:
        return self._cached or []

    def info(self) -> SourceInfo:
        return SourceInfo(
            slug=self.slug,
            label=self.label,
            kind=self.kind,
            status=self._status,
            holdings_count=len(self.cached),
            last_synced_at=self._last_synced_at,
            error_message=self._error,
            notes=getattr(self, "notes", None),
        )

    def reset(self) -> None:
        self._cached = None
        self._last_synced_at = None
        self._status = SourceStatus.UNCONFIGURED
        self._error = None

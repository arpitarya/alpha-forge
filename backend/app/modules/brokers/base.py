"""BrokerSource ABC + lifecycle (sync, ingest_csv, info, reset).

Schemas live in `broker_schemas.py` and are re-exported here for convenience.
"""

from __future__ import annotations

from abc import ABC
from datetime import datetime, timezone
from typing import IO

from app.modules.brokers.broker_schemas import (
    AssetClass,
    Holding,
    SourceInfo,
    SourceKind,
    SourceStatus,
)

__all__ = [
    "AssetClass", "BrokerSource", "Holding",
    "SourceInfo", "SourceKind", "SourceStatus",
]


class BrokerSource(ABC):
    """Adapter for one holdings provider — override `fetch()` (API) or `parse()` (CSV)."""

    slug: str
    label: str
    kind: SourceKind

    def __init__(self) -> None:
        self._cached: list[Holding] | None = None
        self._last_synced_at: datetime | None = None
        self._status: SourceStatus = SourceStatus.UNCONFIGURED
        self._error: str | None = None

    async def fetch(self) -> list[Holding]:
        raise NotImplementedError(f"{self.slug}: override fetch() or use parse()")

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        raise NotImplementedError(f"{self.slug}: override parse() or use fetch()")

    async def sync(self) -> list[Holding]:
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

    @property
    def cached(self) -> list[Holding]:
        return self._cached or []

    def info(self) -> SourceInfo:
        return SourceInfo(
            slug=self.slug, label=self.label, kind=self.kind,
            status=self._status, holdings_count=len(self.cached),
            last_synced_at=self._last_synced_at,
            error_message=self._error, notes=getattr(self, "notes", None),
        )

    def reset(self) -> None:
        self._cached = None
        self._last_synced_at = None
        self._status = SourceStatus.UNCONFIGURED
        self._error = None

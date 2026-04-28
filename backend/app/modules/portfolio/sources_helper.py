"""Helpers for source-management routes — sync orchestration + upload state mutation."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.modules.brokers import SOURCES, HoldingsAggregator, SourceKind
from app.modules.brokers.base import SourceStatus

logger = get_logger("routes.portfolio.sources_helper")


def apply_uploaded(src, holdings: list) -> None:
    """Persist a fresh CSV-parsed list onto a BrokerSource."""
    src._cached = holdings  # noqa: SLF001
    src._last_synced_at = datetime.now(timezone.utc)  # noqa: SLF001
    src._status = SourceStatus.READY  # noqa: SLF001
    src._error = None  # noqa: SLF001


async def _sync_one(slug: str, src, results: dict[str, dict]) -> None:
    if src.kind != SourceKind.API:
        return
    try:
        holdings = await src.sync()
        results[slug] = {"ok": True, "count": len(holdings)}
    except Exception as e:  # noqa: BLE001
        logger.exception("sync-all: %s failed", slug)
        results[slug] = {"ok": False, "error": str(e)}


async def sync_all() -> dict:
    aggregator = HoldingsAggregator()
    results: dict[str, dict] = {}
    await asyncio.gather(*[_sync_one(slug, src, results) for slug, src in SOURCES.items()])
    return {
        "results": results,
        "totals": aggregator.totals(),
        "disclaimer": "Not SEBI registered investment advice.",
    }

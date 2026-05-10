"""Aggregated portfolio endpoints — holdings, treemap, rebalance, plus mounted broker routes.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.core.logging import get_logger
from app.modules.brokers import SOURCES, HoldingsAggregator
from app.modules.brokers.base import SourceKind
from app.modules.brokers.brokers_routes import router as sources_router

router = APIRouter()
aggregator = HoldingsAggregator()
logger = get_logger("routes.portfolio")

_STALE_SECONDS = 3600


async def _maybe_sync(source: str | None) -> None:
    """Sync any API source whose cached data is missing or older than _STALE_SECONDS."""
    now = datetime.now(timezone.utc)
    targets = [SOURCES[source]] if source else list(SOURCES.values())
    for src in targets:
        if src.kind != SourceKind.API:
            continue
        age = (
            (now - src._last_synced_at).total_seconds()  # noqa: SLF001
            if src._last_synced_at else float("inf")
        )
        if age > _STALE_SECONDS:
            try:
                await src.sync()
            except Exception:  # noqa: BLE001
                logger.warning("Auto-sync failed for %s — returning cached data", src.slug)


@router.get("/holdings")
async def get_holdings(source: str | None = None):
    if source and source not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {source}")
    await _maybe_sync(source)
    return {
        "totals": aggregator.totals(source),
        "allocation": [a.__dict__ for a in aggregator.allocation(source)],
        "holdings": [h.model_dump(mode="json") for h in aggregator.all_holdings(source)],
        "disclaimer": "Not SEBI registered investment advice.",
    }


@router.get("/treemap")
async def get_treemap(source: str | None = None):
    if source and source not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {source}")
    return {
        "totals": aggregator.totals(source),
        "cells": [c.__dict__ for c in aggregator.treemap(source)],
        "disclaimer": "Not SEBI registered investment advice.",
    }


@router.get("/rebalance")
async def get_rebalance():
    drift, suggestions = aggregator.rebalance()
    return {
        "drift": [d.__dict__ for d in drift],
        "suggestions": [s.__dict__ for s in suggestions],
        "targets": {k.value: v for k, v in aggregator.targets.items()},
        "disclaimer": "Not SEBI registered investment advice.",
    }


router.include_router(sources_router, prefix="/sources")

"""Broker source management endpoints — list/sync. Mounted under /sources/*."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, status

from app.core.logging import get_logger
from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.brokers.base import SourceKind
from app.modules.brokers.registry import SOURCES, get_source

router = APIRouter()
logger = get_logger("routes.brokers")


@router.get("")
async def list_sources():
    return {"sources": [s.info().model_dump(mode="json") for s in SOURCES.values()]}


@router.get("/{slug}")
async def get_source_info(slug: str):
    if slug not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {slug}")
    return SOURCES[slug].info().model_dump(mode="json")


@router.post("/{slug}/sync")
async def sync_source(slug: str):
    try:
        src = get_source(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    if src.kind != SourceKind.API:
        raise HTTPException(400, f"{slug} is a CSV source — only API sources support sync.")
    try:
        holdings = await src.sync()
    except Exception as e:  # noqa: BLE001
        logger.exception("Sync failed for %s", slug)
        raise HTTPException(400, f"Sync failed: {e}") from e
    return {
        "source": slug,
        "holdings_count": len(holdings),
        "holdings": [h.model_dump(mode="json") for h in holdings],
        "info": src.info().model_dump(mode="json"),
    }


@router.post("/sync-all")
async def sync_all_sources():
    results: dict[str, dict] = {}

    async def _sync_one(slug: str, src) -> None:  # type: ignore[no-untyped-def]
        if src.kind != SourceKind.API:
            return
        try:
            h = await src.sync()
            results[slug] = {"ok": True, "count": len(h)}
        except Exception as e:  # noqa: BLE001
            logger.exception("sync-all: %s failed", slug)
            results[slug] = {"ok": False, "error": str(e)}

    await asyncio.gather(*[_sync_one(slug, src) for slug, src in SOURCES.items()])
    return {
        "results": results,
        "totals": HoldingsAggregator().totals(),
        "disclaimer": "Not SEBI registered investment advice.",
    }

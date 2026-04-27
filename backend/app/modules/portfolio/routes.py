"""Portfolio management endpoints.

Aggregates holdings across all configured broker sources (Zerodha, Coin,
Groww, Dezerv, Wint Wealth, Angel One). Each source is either CSV-driven
(user uploads an export) or API-driven (Angel One SmartAPI free tier).

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.logging import get_logger
from app.modules.brokers import (
    SOURCES,
    HoldingsAggregator,
    SourceKind,
    get_source,
)

router = APIRouter()
logger = get_logger("routes.portfolio")
aggregator = HoldingsAggregator()


# ── Aggregated holdings ──────────────────────────────────────────────────────


@router.get("/holdings")
async def get_holdings(source: str | None = None):
    """Return every holding across (or filtered to one) source."""
    if source and source not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {source}")
    holdings = aggregator.all_holdings(source)
    return {
        "totals": aggregator.totals(source),
        "allocation": [a.__dict__ for a in aggregator.allocation(source)],
        "holdings": [h.model_dump(mode="json") for h in holdings],
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


# ── Source management ────────────────────────────────────────────────────────


@router.get("/sources")
async def list_sources():
    return {"sources": [s.info().model_dump(mode="json") for s in SOURCES.values()]}


@router.get("/sources/{slug}")
async def get_source_info(slug: str):
    if slug not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {slug}")
    return SOURCES[slug].info().model_dump(mode="json")


@router.post("/sources/{slug}/upload")
async def upload_csv(slug: str, file: UploadFile):
    """Ingest an exported CSV from any source (manual fallback)."""
    try:
        src = get_source(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    # Force CSV ingestion path regardless of declared kind (every source
    # implements parse() either natively or via a CSV adapter).
    try:
        holdings = src.parse(file.file, filename=file.filename)
        src._cached = holdings  # noqa: SLF001
        from datetime import datetime, timezone

        from app.modules.brokers.base import SourceStatus

        src._last_synced_at = datetime.now(timezone.utc)  # noqa: SLF001
        src._status = SourceStatus.READY  # noqa: SLF001
        src._error = None  # noqa: SLF001
    except NotImplementedError as e:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{slug} does not support CSV upload.",
        ) from e
    except Exception as e:  # noqa: BLE001
        logger.exception("CSV ingest failed for %s", slug)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Ingest failed: {e}") from e
    logger.info("Ingested %d holdings from %s (%s)", len(holdings), slug, file.filename)
    return {
        "source": slug,
        "filename": file.filename,
        "holdings_count": len(holdings),
        "info": src.info().model_dump(mode="json"),
    }


@router.post("/sources/{slug}/sync")
async def sync_source(slug: str):
    """Pull from upstream (API sources only)."""
    try:
        src = get_source(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    if src.kind != SourceKind.API:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{slug} is a CSV source — use /sources/{slug}/upload instead.",
        )
    try:
        holdings = await src.sync()
    except Exception as e:  # noqa: BLE001
        logger.exception("Sync failed for %s", slug)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Sync failed: {e}") from e
    return {
        "source": slug,
        "holdings_count": len(holdings),
        "info": src.info().model_dump(mode="json"),
    }


@router.post("/sources/sync-all")
async def sync_all_sources():
    """Fan-out sync across every API source. Returns per-source result."""
    results: dict[str, dict] = {}

    async def _one(slug: str, src) -> None:
        if src.kind != SourceKind.API:
            return
        try:
            holdings = await src.sync()
            results[slug] = {"ok": True, "count": len(holdings)}
        except Exception as e:  # noqa: BLE001
            logger.exception("sync-all: %s failed", slug)
            results[slug] = {"ok": False, "error": str(e)}

    await asyncio.gather(*[_one(slug, src) for slug, src in SOURCES.items()])
    return {
        "results": results,
        "totals": aggregator.totals(),
        "disclaimer": "Not SEBI registered investment advice.",
    }


# ── OTP flow (Wint Wealth and any future OTP-bound source) ───────────────────


class OTPSubmit(BaseModel):
    code: str


@router.post("/sources/{slug}/start-login")
async def start_login(slug: str):
    """Trigger an OTP send for sources whose login is OTP-bound."""
    try:
        src = get_source(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    fn = getattr(src, "start_login", None)
    if not callable(fn):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{slug} does not use OTP login.",
        )
    try:
        return await fn()
    except Exception as e:  # noqa: BLE001
        logger.exception("start-login failed for %s", slug)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"start-login failed: {e}") from e


@router.post("/sources/{slug}/otp")
async def submit_otp(slug: str, body: OTPSubmit):
    """Submit OTP for sources whose login is OTP-bound. Caches the JWT."""
    try:
        src = get_source(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    fn = getattr(src, "submit_otp", None)
    if not callable(fn):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{slug} does not use OTP login.",
        )
    try:
        return await fn(body.code)
    except Exception as e:  # noqa: BLE001
        logger.exception("submit-otp failed for %s", slug)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"submit-otp failed: {e}") from e


@router.post("/sources/{slug}/reset")
async def reset_source(slug: str):
    """Clear cached holdings for a source (lets you re-upload a CSV)."""
    if slug not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {slug}")
    SOURCES[slug].reset()
    return {"source": slug, "info": SOURCES[slug].info().model_dump(mode="json")}

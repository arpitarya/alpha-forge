"""Portfolio management endpoints.

Aggregates holdings across all configured broker sources (Zerodha, Coin,
Groww, Dezerv, Wint Wealth, Angel One). Each source is either CSV-driven
(user uploads an export) or API-driven (Angel One SmartAPI free tier).

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.brokers import (
    SOURCES,
    HoldingsAggregator,
    SourceKind,
    get_source,
)

router = APIRouter()
logger = get_logger("routes.portfolio")
aggregator = HoldingsAggregator()


# ── Legacy-shape models kept for backward compat ──────────────────────────────


class Holding(BaseModel):
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    pnl: float
    pnl_pct: float


class PortfolioSummary(BaseModel):
    total_invested: float
    current_value: float
    total_pnl: float
    total_pnl_pct: float
    holdings: list[Holding]


# ── Summary / positions / orders ──────────────────────────────────────────────


@router.get("/summary", response_model=PortfolioSummary)
async def portfolio_summary():
    t = aggregator.totals()
    holdings = [
        Holding(
            symbol=h.symbol,
            quantity=int(h.quantity),
            avg_price=h.avg_price,
            current_price=h.last_price,
            pnl=h.pnl,
            pnl_pct=h.pnl_pct,
        )
        for h in aggregator.all_holdings()
    ]
    return PortfolioSummary(
        total_invested=t["invested"],
        current_value=t["current_value"],
        total_pnl=t["pnl"],
        total_pnl_pct=t["pnl_pct"],
        holdings=holdings,
    )


@router.get("/positions")
async def open_positions():
    return {"positions": []}


@router.get("/orders")
async def order_history():
    return {"orders": []}


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
    """Ingest an exported CSV from a CSV-kind source."""
    try:
        src = get_source(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    if src.kind != SourceKind.CSV:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{slug} is an API source — use /sources/{slug}/sync instead.",
        )
    try:
        holdings = src.ingest_csv(file.file, filename=file.filename)
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


@router.post("/sources/{slug}/reset")
async def reset_source(slug: str):
    """Clear cached holdings for a source (lets you re-upload a CSV)."""
    if slug not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {slug}")
    SOURCES[slug].reset()
    return {"source": slug, "info": SOURCES[slug].info().model_dump(mode="json")}

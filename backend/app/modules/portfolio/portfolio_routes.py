"""Aggregated portfolio endpoints — holdings, treemap, rebalance, plus mounted source routes.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.modules.brokers import SOURCES, HoldingsAggregator
from app.modules.portfolio.sources_routes import router as sources_router

router = APIRouter()
aggregator = HoldingsAggregator()


@router.get("/holdings")
async def get_holdings(source: str | None = None):
    if source and source not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {source}")
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

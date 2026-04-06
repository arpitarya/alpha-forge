"""Screener endpoints — push/pull ML screener picks."""

from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.screener import ScreenerService

router = APIRouter()
logger = get_logger("routes.screener")

screener_service = ScreenerService()


# ── Request / Response Models ─────────────────────────────────────────────────

class ScreenerPick(BaseModel):
    symbol: str
    probability: float
    rank: int
    rsi_14: float | None = None
    macd_hist: float | None = None
    adx_14: float | None = None
    vol_sma_ratio: float | None = None
    dist_52w_high_pct: float | None = None


class PushPicksRequest(BaseModel):
    scan_date: str
    model_type: str = "lightgbm"
    picks: list[ScreenerPick]


class PicksResponse(BaseModel):
    scan_date: str
    model_type: str | None = None
    count: int
    picks: list[dict]


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/picks", response_model=dict)
async def push_picks(request: PushPicksRequest):
    """Receive screener picks from the notebook/CLI pipeline.

    Disclaimer: Not SEBI registered investment advice.
    """
    logger.info(
        "Receiving %d picks for %s (%s)",
        len(request.picks), request.scan_date, request.model_type,
    )
    picks_dicts = [p.model_dump(exclude_none=True) for p in request.picks]
    result = await screener_service.save_picks(request.scan_date, request.model_type, picks_dicts)
    return result


@router.get("/picks", response_model=PicksResponse)
async def get_picks(date: str | None = Query(None, description="Scan date (YYYY-MM-DD)")):
    """Retrieve screener picks for a given date (or latest).

    Disclaimer: Not SEBI registered investment advice.
    """
    logger.info("Fetching picks for date=%s", date or "latest")
    result = await screener_service.get_picks(scan_date=date)
    return PicksResponse(
        scan_date=result.get("scan_date", ""),
        model_type=result.get("model_type"),
        count=result.get("count", 0),
        picks=result.get("picks", []),
    )


@router.get("/dates", response_model=list[str])
async def list_scan_dates():
    """List all available scan dates."""
    return await screener_service.list_scan_dates()

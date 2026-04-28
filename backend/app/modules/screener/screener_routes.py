"""Screener endpoints — push/pull ML screener picks.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Query

from app.core.logging import get_logger
from app.modules.screener.screener_helper import backfill_all_picks, embed_picks_background
from app.modules.screener.screener_schemas import (
    PicksResponse,
    PushPicksRequest,
)
from app.modules.screener.screener_service import ScreenerService

router = APIRouter()
logger = get_logger("routes.screener")
screener_service = ScreenerService()


@router.post("/picks", response_model=dict)
async def push_picks(request: PushPicksRequest, background_tasks: BackgroundTasks):
    logger.info(
        "Receiving %d picks for %s (%s)",
        len(request.picks), request.scan_date, request.model_type,
    )
    picks_dicts = [p.model_dump(exclude_none=True) for p in request.picks]
    result = await screener_service.save_picks(
        request.scan_date, request.model_type, picks_dicts
    )
    background_tasks.add_task(
        embed_picks_background, picks_dicts, request.scan_date, request.model_type
    )
    return result


@router.post("/picks/embed-backfill", response_model=dict)
async def backfill_embeddings(background_tasks: BackgroundTasks):
    background_tasks.add_task(backfill_all_picks)
    return {"message": "Backfill started — check logs for progress."}


@router.get("/picks", response_model=PicksResponse)
async def get_picks(date: str | None = Query(None, description="Scan date (YYYY-MM-DD)")):
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
    return await screener_service.list_scan_dates()

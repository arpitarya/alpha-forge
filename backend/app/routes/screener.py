"""Screener endpoints — push/pull ML screener picks."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session, get_db
from app.core.logging import get_logger
from app.services.embedding import get_embedding_service
from app.services.memory import MemoryService
from app.services.screener import ScreenerService, PICKS_DIR

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


# ── Background embed helper ───────────────────────────────────────────────────

async def _embed_picks_background(
    picks: list[dict], scan_date: str, model_type: str
) -> None:
    """Background task: embed picks and store in screener_pick_embeddings."""
    async with async_session() as db:
        async with db.begin():
            mem = MemoryService(db=db, embedding_svc=get_embedding_service())
            count = await mem.index_picks_batch(picks, scan_date, model_type)
            logger.info("Background embed: %d/%d picks for %s/%s", count, len(picks), scan_date, model_type)


async def _backfill_all_picks() -> None:
    """Re-embed all existing picks JSON files that haven't been indexed yet."""
    files = sorted(PICKS_DIR.glob("*_picks.json"))
    total = 0
    for f in files:
        try:
            data = json.loads(f.read_text())
            picks = data.get("picks", [])
            scan_date = data.get("scan_date", "")
            model_type = data.get("model_type", "unknown")
            if picks and scan_date:
                await _embed_picks_background(picks, scan_date, model_type)
                total += len(picks)
        except Exception as e:
            logger.warning("Backfill failed for %s: %s", f.name, e)
    logger.info("Backfill complete — processed %d total picks from %d files", total, len(files))


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/picks", response_model=dict)
async def push_picks(
    request: PushPicksRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Receive screener picks from the notebook/CLI pipeline.

    Disclaimer: Not SEBI registered investment advice.
    """
    logger.info(
        "Receiving %d picks for %s (%s)",
        len(request.picks), request.scan_date, request.model_type,
    )
    picks_dicts = [p.model_dump(exclude_none=True) for p in request.picks]
    result = await screener_service.save_picks(request.scan_date, request.model_type, picks_dicts)

    background_tasks.add_task(
        _embed_picks_background, picks_dicts, request.scan_date, request.model_type
    )
    return result


@router.post("/picks/embed-backfill", response_model=dict)
async def backfill_embeddings(background_tasks: BackgroundTasks):
    """Re-embed all existing picks JSON files that haven't been indexed yet."""
    background_tasks.add_task(_backfill_all_picks)
    return {"message": "Backfill started — check logs for progress."}


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

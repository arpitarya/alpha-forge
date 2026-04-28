"""Background tasks for screener: embed pushed picks + backfill from disk."""

from __future__ import annotations

import json

from app.core.database import async_session
from app.core.logging import get_logger
from app.modules.memory.embedding_service import get_embedding_service
from app.modules.memory.memory_service import MemoryService
from app.modules.screener.screener_service import PICKS_DIR

logger = get_logger("services.screener_helper")


async def embed_picks_background(
    picks: list[dict], scan_date: str, model_type: str
) -> None:
    async with async_session() as db, db.begin():
        mem = MemoryService(db=db, embedding_svc=get_embedding_service())
        count = await mem.index_picks_batch(picks, scan_date, model_type)
        logger.info(
            "Background embed: %d/%d picks for %s/%s",
            count, len(picks), scan_date, model_type,
        )


async def backfill_all_picks() -> None:
    files = sorted(PICKS_DIR.glob("*_picks.json"))
    total = 0
    for f in files:
        try:
            data = json.loads(f.read_text())
            picks = data.get("picks", [])
            scan_date = data.get("scan_date", "")
            model_type = data.get("model_type", "unknown")
            if picks and scan_date:
                await embed_picks_background(picks, scan_date, model_type)
                total += len(picks)
        except Exception as e:
            logger.warning("Backfill failed for %s: %s", f.name, e)
    logger.info("Backfill complete — %d picks across %d files", total, len(files))

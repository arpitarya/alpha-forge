"""Indexing helpers — pick → ScreenerPickEmbedding record builder."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.memory.embedding_service import EmbeddingService
from app.modules.memory.memory_models import ScreenerPickEmbedding
from app.modules.memory.memory_utils import extract_pick_fields


async def upsert_pick(
    db: AsyncSession,
    embed: EmbeddingService,
    pick: dict,
    scan_date: str,
    model_type: str,
) -> ScreenerPickEmbedding | None:
    symbol, prob, rank, raw_features = extract_pick_fields(pick)
    if not symbol:
        return None

    existing = await db.scalar(
        select(ScreenerPickEmbedding).where(
            ScreenerPickEmbedding.symbol == symbol,
            ScreenerPickEmbedding.scan_date == scan_date,
            ScreenerPickEmbedding.model_type == model_type,
        )
    )
    if existing:
        return existing

    explanation = embed.build_pick_explanation_text(
        {**pick, "scan_date": scan_date, "model_type": model_type}
    )
    embedding = await embed.embed_text(explanation, task_type="RETRIEVAL_DOCUMENT")

    record = ScreenerPickEmbedding(
        symbol=symbol,
        scan_date=scan_date,
        model_type=model_type,
        probability=prob,
        rank=rank,
        explanation_text=explanation,
        embedding=embedding,
        raw_features=raw_features,
        embedded_at=datetime.now(timezone.utc),
    )
    db.add(record)
    await db.flush()
    return record

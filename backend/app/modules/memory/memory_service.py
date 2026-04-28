"""Memory service — vector store interface for picks and conversation history."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.memory.embedding_service import EmbeddingService
from app.modules.memory.memory_helper import upsert_pick
from app.modules.memory.memory_models import ConversationMemory, ScreenerPickEmbedding
from app.modules.memory.memory_repo import (
    search_conversations_by_vector,
    search_picks_by_vector,
)

logger = logging.getLogger("services.memory")


class MemoryService:
    def __init__(self, db: AsyncSession, embedding_svc: EmbeddingService) -> None:
        self._db = db
        self._embed = embedding_svc

    async def index_pick(
        self, pick: dict, scan_date: str, model_type: str
    ) -> ScreenerPickEmbedding | None:
        return await upsert_pick(self._db, self._embed, pick, scan_date, model_type)

    async def index_picks_batch(
        self, picks: list[dict], scan_date: str, model_type: str
    ) -> int:
        count = 0
        for i, pick in enumerate(picks):
            result = await self.index_pick(pick, scan_date, model_type)
            if result and result.id:
                count += 1
            if i < len(picks) - 1:
                await asyncio.sleep(1.1)  # Gemini free tier: 1 RPM
        await self._db.commit()
        logger.info("Indexed %d/%d picks for %s/%s", count, len(picks), scan_date, model_type)
        return count

    async def search_picks(
        self, query: str, top_k: int | None = None, symbol_filter: str | None = None
    ) -> list[dict]:
        k = top_k or settings.memory_top_k
        vec = await self._embed.embed_text(query, task_type="RETRIEVAL_QUERY")
        return await search_picks_by_vector(self._db, vec, k, symbol_filter)

    async def save_turn(
        self, session_id: str, role: str, content: str, turn_index: int,
        user_id: uuid.UUID | None = None, context_snapshot: dict | None = None,
    ) -> ConversationMemory:
        embedding = await self._embed.embed_text(content, task_type="RETRIEVAL_DOCUMENT")
        record = ConversationMemory(
            user_id=user_id, session_id=session_id, role=role, content=content,
            embedding=embedding, context_snapshot=context_snapshot, turn_index=turn_index,
        )
        self._db.add(record)
        await self._db.flush()
        return record

    async def get_session_history(self, session_id: str, limit: int = 20) -> list[dict]:
        result = await self._db.execute(
            select(ConversationMemory)
            .where(ConversationMemory.session_id == session_id)
            .order_by(ConversationMemory.turn_index.asc())
            .limit(limit)
        )
        return [
            {"role": r.role, "content": r.content, "turn_index": r.turn_index}
            for r in result.scalars().all()
        ]

    async def search_memory(
        self, query: str, user_id: uuid.UUID | None,
        top_k: int = 3, exclude_session: str | None = None,
    ) -> list[dict]:
        vec = await self._embed.embed_text(query, task_type="RETRIEVAL_QUERY")
        return await search_conversations_by_vector(
            self._db, vec, top_k, user_id, exclude_session
        )

    async def prune_old_memories(self, max_age_days: int | None = None) -> int:
        days = max_age_days or settings.memory_max_age_days
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._db.execute(
            delete(ConversationMemory).where(ConversationMemory.created_at < cutoff)
        )
        await self._db.commit()
        return result.rowcount

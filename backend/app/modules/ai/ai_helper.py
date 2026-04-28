"""Memory retrieval + persistence helpers for AIService.chat."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.memory.memory_service import MemoryService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.modules.memory.embedding_service import EmbeddingService

logger = get_logger("services.ai_helper")


async def fetch_chat_context(
    db: AsyncSession,
    embed_svc: EmbeddingService,
    user_query: str,
    session_id: str,
    user_id: uuid.UUID | None,
    symbol: str,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Returns (relevant_picks, past_turns, session_history) — lenient on errors."""
    try:
        mem = MemoryService(db=db, embedding_svc=embed_svc)
        picks = await mem.search_picks(
            user_query, top_k=settings.memory_top_k, symbol_filter=symbol or None
        )
        past_turns = await mem.search_memory(
            user_query, user_id=user_id, top_k=3, exclude_session=session_id
        )
        history = await mem.get_session_history(session_id, limit=10)
        return picks, past_turns, history
    except Exception as e:
        logger.warning("Memory retrieval failed: %s", e)
        return [], [], []


async def persist_turn_pair(
    db: AsyncSession,
    embed_svc: EmbeddingService,
    session_id: str,
    user_query: str,
    reply: str,
    turn_index: int,
    user_id: uuid.UUID | None,
    ctx: dict,
) -> None:
    try:
        mem = MemoryService(db=db, embedding_svc=embed_svc)
        await mem.save_turn(
            session_id=session_id, role="user", content=user_query,
            turn_index=turn_index, user_id=user_id, context_snapshot=ctx,
        )
        await mem.save_turn(
            session_id=session_id, role="assistant", content=reply,
            turn_index=turn_index + 1, user_id=user_id,
        )
        await db.commit()
    except Exception as e:
        logger.warning("Memory persistence failed: %s", e)

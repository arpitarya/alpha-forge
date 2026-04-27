"""Memory service — vector store interface for screener picks and conversation history."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.memory.models import ConversationMemory, ScreenerPickEmbedding
from app.modules.memory.embedding import EmbeddingService

logger = logging.getLogger("services.memory")


class MemoryService:
    """Unified interface for storing and retrieving vector memories."""

    def __init__(self, db: AsyncSession, embedding_svc: EmbeddingService) -> None:
        self._db = db
        self._embed = embedding_svc

    # ── Screener pick methods ─────────────────────────────────────────────────

    async def index_pick(
        self, pick: dict, scan_date: str, model_type: str
    ) -> ScreenerPickEmbedding | None:
        """Embed and store a single screener pick. Idempotent — skips if already indexed."""
        symbol = str(pick.get("symbol", pick.get("SYMBOL", ""))).upper()
        if not symbol:
            return None

        existing = await self._db.scalar(
            select(ScreenerPickEmbedding).where(
                ScreenerPickEmbedding.symbol == symbol,
                ScreenerPickEmbedding.scan_date == scan_date,
                ScreenerPickEmbedding.model_type == model_type,
            )
        )
        if existing:
            return existing

        explanation = self._embed.build_pick_explanation_text({**pick, "scan_date": scan_date, "model_type": model_type})
        embedding = await self._embed.embed_text(explanation, task_type="RETRIEVAL_DOCUMENT")

        prob = float(pick.get("probability", pick.get("PROBABILITY", 0.0)))
        rank_val = pick.get("rank", pick.get("RANK"))
        rank = int(rank_val) if rank_val is not None else None

        feature_keys = ["rsi_14", "RSI_14", "vol_sma_ratio", "VOL_SMA_RATIO", "macd_hist",
                        "MACD_HIST", "adx_14", "ADX_14", "dist_52w_high_pct", "DIST_52W_HIGH_PCT",
                        "roc_5", "ROC_5"]
        raw_features = {k: pick[k] for k in feature_keys if k in pick}

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
        self._db.add(record)
        await self._db.flush()
        return record

    async def index_picks_batch(
        self, picks: list[dict], scan_date: str, model_type: str
    ) -> int:
        """Embed and store a batch of picks. Returns count of newly indexed picks."""
        count = 0
        for i, pick in enumerate(picks):
            result = await self.index_pick(pick, scan_date, model_type)
            if result and result.id:
                count += 1
            if i < len(picks) - 1:
                await asyncio.sleep(1.1)  # Gemini free tier: 1 RPM embedding
        await self._db.commit()
        logger.info("Indexed %d/%d picks for %s/%s", count, len(picks), scan_date, model_type)
        return count

    async def search_picks(
        self,
        query: str,
        top_k: int | None = None,
        symbol_filter: str | None = None,
    ) -> list[dict]:
        """Semantic search over screener picks using cosine distance."""
        k = top_k or settings.memory_top_k
        query_vec = await self._embed.embed_text(query, task_type="RETRIEVAL_QUERY")

        if symbol_filter:
            sql = text("""
                SELECT id, symbol, scan_date, model_type, probability, rank,
                       explanation_text, raw_features,
                       embedding <=> CAST(:vec AS vector) AS distance
                FROM screener_pick_embeddings
                WHERE symbol = :symbol AND embedding IS NOT NULL
                ORDER BY distance ASC
                LIMIT :top_k
            """)
            params = {"vec": str(query_vec), "symbol": symbol_filter.upper(), "top_k": k}
        else:
            sql = text("""
                SELECT id, symbol, scan_date, model_type, probability, rank,
                       explanation_text, raw_features,
                       embedding <=> CAST(:vec AS vector) AS distance
                FROM screener_pick_embeddings
                WHERE embedding IS NOT NULL
                ORDER BY distance ASC
                LIMIT :top_k
            """)
            params = {"vec": str(query_vec), "top_k": k}

        result = await self._db.execute(sql, params)
        rows = result.fetchall()
        return [
            {
                "symbol": r.symbol,
                "scan_date": r.scan_date,
                "model_type": r.model_type,
                "probability": r.probability,
                "rank": r.rank,
                "explanation_text": r.explanation_text,
                "raw_features": r.raw_features,
                "distance": float(r.distance),
            }
            for r in rows
        ]

    # ── Conversation memory methods ───────────────────────────────────────────

    async def save_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        turn_index: int,
        user_id: uuid.UUID | None = None,
        context_snapshot: dict | None = None,
    ) -> ConversationMemory:
        """Embed and persist a conversation turn."""
        embedding = await self._embed.embed_text(content, task_type="RETRIEVAL_DOCUMENT")
        record = ConversationMemory(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            embedding=embedding,
            context_snapshot=context_snapshot,
            turn_index=turn_index,
        )
        self._db.add(record)
        await self._db.flush()
        return record

    async def get_session_history(
        self, session_id: str, limit: int = 20
    ) -> list[dict]:
        """Return ordered conversation turns for a session (no vector search)."""
        result = await self._db.execute(
            select(ConversationMemory)
            .where(ConversationMemory.session_id == session_id)
            .order_by(ConversationMemory.turn_index.asc())
            .limit(limit)
        )
        rows = result.scalars().all()
        return [{"role": r.role, "content": r.content, "turn_index": r.turn_index} for r in rows]

    async def search_memory(
        self,
        query: str,
        user_id: uuid.UUID | None,
        top_k: int = 3,
        exclude_session: str | None = None,
    ) -> list[dict]:
        """Semantic search across past conversation turns."""
        query_vec = await self._embed.embed_text(query, task_type="RETRIEVAL_QUERY")

        if user_id and exclude_session:
            sql = text("""
                SELECT session_id, role, content, created_at,
                       embedding <=> CAST(:vec AS vector) AS distance
                FROM conversation_memories
                WHERE user_id = :user_id AND session_id != :excl AND embedding IS NOT NULL
                ORDER BY distance ASC
                LIMIT :top_k
            """)
            params = {"vec": str(query_vec), "user_id": str(user_id), "excl": exclude_session, "top_k": top_k}
        elif user_id:
            sql = text("""
                SELECT session_id, role, content, created_at,
                       embedding <=> CAST(:vec AS vector) AS distance
                FROM conversation_memories
                WHERE user_id = :user_id AND embedding IS NOT NULL
                ORDER BY distance ASC
                LIMIT :top_k
            """)
            params = {"vec": str(query_vec), "user_id": str(user_id), "top_k": top_k}
        elif exclude_session:
            sql = text("""
                SELECT session_id, role, content, created_at,
                       embedding <=> CAST(:vec AS vector) AS distance
                FROM conversation_memories
                WHERE session_id != :excl AND embedding IS NOT NULL
                ORDER BY distance ASC
                LIMIT :top_k
            """)
            params = {"vec": str(query_vec), "excl": exclude_session, "top_k": top_k}
        else:
            sql = text("""
                SELECT session_id, role, content, created_at,
                       embedding <=> CAST(:vec AS vector) AS distance
                FROM conversation_memories
                WHERE embedding IS NOT NULL
                ORDER BY distance ASC
                LIMIT :top_k
            """)
            params = {"vec": str(query_vec), "top_k": top_k}

        result = await self._db.execute(sql, params)
        rows = result.fetchall()
        return [
            {
                "session_id": r.session_id,
                "role": r.role,
                "content": r.content,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "distance": float(r.distance),
            }
            for r in rows
        ]

    async def prune_old_memories(self, max_age_days: int | None = None) -> int:
        """Delete conversation memories older than max_age_days. Returns deleted count."""
        days = max_age_days or settings.memory_max_age_days
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._db.execute(
            delete(ConversationMemory).where(ConversationMemory.created_at < cutoff)
        )
        await self._db.commit()
        return result.rowcount

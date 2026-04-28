"""Raw pgvector SQL for semantic search — picks + conversation memory."""

from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def search_picks_by_vector(
    db: AsyncSession,
    vec: list[float],
    top_k: int,
    symbol_filter: str | None,
) -> list[dict]:
    if symbol_filter:
        sql = text(
            """
            SELECT id, symbol, scan_date, model_type, probability, rank,
                   explanation_text, raw_features,
                   embedding <=> CAST(:vec AS vector) AS distance
            FROM screener_pick_embeddings
            WHERE symbol = :symbol AND embedding IS NOT NULL
            ORDER BY distance ASC
            LIMIT :top_k
            """
        )
        params: dict = {"vec": str(vec), "symbol": symbol_filter.upper(), "top_k": top_k}
    else:
        sql = text(
            """
            SELECT id, symbol, scan_date, model_type, probability, rank,
                   explanation_text, raw_features,
                   embedding <=> CAST(:vec AS vector) AS distance
            FROM screener_pick_embeddings
            WHERE embedding IS NOT NULL
            ORDER BY distance ASC
            LIMIT :top_k
            """
        )
        params = {"vec": str(vec), "top_k": top_k}

    rows = (await db.execute(sql, params)).fetchall()
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


async def search_conversations_by_vector(
    db: AsyncSession,
    vec: list[float],
    top_k: int,
    user_id: uuid.UUID | None,
    exclude_session: str | None,
) -> list[dict]:
    where = ["embedding IS NOT NULL"]
    params: dict = {"vec": str(vec), "top_k": top_k}
    if user_id:
        where.append("user_id = :user_id")
        params["user_id"] = str(user_id)
    if exclude_session:
        where.append("session_id != :excl")
        params["excl"] = exclude_session

    sql = text(
        f"""
        SELECT session_id, role, content, created_at,
               embedding <=> CAST(:vec AS vector) AS distance
        FROM conversation_memories
        WHERE {" AND ".join(where)}
        ORDER BY distance ASC
        LIMIT :top_k
        """
    )
    rows = (await db.execute(sql, params)).fetchall()
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

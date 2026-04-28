"""AI service — orchestrates RAG chat, analysis, screener, sentiment."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from alphaforge_llm_gateway.types import QueryType

from app.core.logging import get_logger
from app.modules.ai.ai_helper import fetch_chat_context, persist_turn_pair
from app.modules.ai.ai_utils import (
    build_system_prompt,
    format_memory_context,
    format_picks_context,
    format_portfolio_context,
)
from app.modules.llm.llm_service import get_gateway
from app.modules.memory.embedding_service import get_embedding_service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("services.ai")


class AIService:
    def __init__(self) -> None:
        self._gateway = get_gateway()
        self._embed_svc = get_embedding_service()

    async def chat(
        self,
        messages: list[dict],
        context: dict | None = None,
        db: AsyncSession | None = None,
    ) -> dict:
        ctx = context or {}
        user_query = messages[-1].get("content", "") if messages else ""
        session_id = ctx.get("session_id") or str(uuid.uuid4())
        user_id_str = ctx.get("user_id")
        user_id = uuid.UUID(user_id_str) if user_id_str else None
        turn_index = int(ctx.get("turn_index", 0))
        symbol = ctx.get("symbol", "")
        portfolio = ctx.get("portfolio", [])

        picks, past_turns, history = (
            await fetch_chat_context(db, self._embed_svc, user_query, session_id, user_id, symbol)
            if (db and user_query) else ([], [], [])
        )

        system_content = build_system_prompt(
            format_picks_context(picks), format_portfolio_context(portfolio),
            format_memory_context(past_turns), symbol,
        )
        llm_messages: list[dict] = [{"role": "system", "content": system_content}]
        llm_messages.extend({"role": t["role"], "content": t["content"]} for t in history)
        llm_messages.extend(
            {"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages
        )
        query_type = QueryType.RAG_CHAT if (picks or past_turns) else QueryType.CHAT
        try:
            response = await self._gateway.complete(
                query_type, llm_messages, temperature=0.7, max_tokens=2048
            )
            reply = response.content
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            reply = "AI service is temporarily unavailable. Please try again."

        if db and user_query:
            await persist_turn_pair(
                db, self._embed_svc, session_id, user_query, reply, turn_index, user_id, ctx
            )

        return {
            "reply": reply,
            "sources": [p["explanation_text"] for p in picks],
            "suggested_actions": [],
            "session_id": session_id,
        }

    async def analyze_stock(self, symbol: str, analysis_type: str = "comprehensive") -> dict:
        return {
            "symbol": symbol,
            "summary": "Analysis engine not connected.",
            "technical_signals": {},
            "fundamental_metrics": {},
            "ai_recommendation": "",
            "confidence": 0.0,
        }

    async def run_screener(self, strategy: str) -> list[dict]:
        return []

    async def sentiment_analysis(self, symbol: str) -> dict:
        return {"symbol": symbol, "sentiment": "neutral", "score": 0.0}

"""AI analysis service — LLM integration for market analysis and chat."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from alphaforge_llm_gateway.types import QueryType

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.memory.embedding import get_embedding_service
from app.modules.llm.service import get_gateway
from app.modules.memory.service import MemoryService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("services.ai")


def _format_picks_context(picks: list[dict]) -> str:
    if not picks:
        return "No relevant screener picks found."
    lines = []
    for p in picks:
        lines.append(
            f"- {p['symbol']} ({p['scan_date']}, {p['model_type']}): "
            f"probability={p['probability']:.3f}, rank={p.get('rank', 'N/A')}, "
            f"signal: {p['explanation_text']}"
        )
    return "\n".join(lines)


def _format_memory_context(turns: list[dict]) -> str:
    if not turns:
        return ""
    lines = ["Relevant past analysis:"]
    for t in turns:
        lines.append(f"  [{t['role']}] {t['content'][:200]}")
    return "\n".join(lines)


class AIService:
    """Orchestrates AI-powered features: chat, analysis, screener, sentiment."""

    def __init__(self) -> None:
        self._gateway = get_gateway()
        self._embed_svc = get_embedding_service()

    async def chat(
        self,
        messages: list[dict],
        context: dict | None = None,
        db: AsyncSession | None = None,
    ) -> dict:
        """RAG-powered conversational AI for market queries.

        Retrieves relevant screener picks and past conversation turns before calling the LLM.
        Persists both the user turn and assistant reply to vector memory.
        """
        ctx = context or {}
        user_query = messages[-1].get("content", "") if messages else ""
        session_id = ctx.get("session_id") or str(uuid.uuid4())
        user_id_str = ctx.get("user_id")
        user_id = uuid.UUID(user_id_str) if user_id_str else None
        turn_index = int(ctx.get("turn_index", 0))
        symbol = ctx.get("symbol", "")
        portfolio = ctx.get("portfolio", [])

        relevant_picks: list[dict] = []
        past_turns: list[dict] = []
        session_history: list[dict] = []

        if db and user_query:
            try:
                mem = MemoryService(db=db, embedding_svc=self._embed_svc)
                relevant_picks = await mem.search_picks(
                    user_query,
                    top_k=settings.memory_top_k,
                    symbol_filter=symbol or None,
                )
                past_turns = await mem.search_memory(
                    user_query,
                    user_id=user_id,
                    top_k=3,
                    exclude_session=session_id,
                )
                session_history = await mem.get_session_history(session_id, limit=10)
            except Exception as e:
                logger.warning("Memory retrieval failed: %s", e)

        picks_ctx = _format_picks_context(relevant_picks)
        mem_ctx = _format_memory_context(past_turns)
        portfolio_ctx = (
            "\n".join(f"- {h.get('symbol')}: {h.get('quantity')} shares @ avg ₹{h.get('avg_price')}"
                      for h in portfolio)
            if portfolio else "Not provided."
        )

        system_content = (
            f"== SCREENER CONTEXT (most relevant ML picks) ==\n{picks_ctx}\n\n"
            f"== PORTFOLIO CONTEXT ==\n{portfolio_ctx}\n"
        )
        if symbol:
            system_content += f"\n== CURRENT SYMBOL == {symbol}\n"
        if mem_ctx:
            system_content += f"\n{mem_ctx}\n"

        llm_messages: list[dict] = [{"role": "system", "content": system_content}]
        for turn in session_history:
            llm_messages.append({"role": turn["role"], "content": turn["content"]})
        for msg in messages:
            llm_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        query_type = QueryType.RAG_CHAT if (relevant_picks or past_turns) else QueryType.CHAT
        try:
            response = await self._gateway.complete(
                query_type,
                llm_messages,
                temperature=0.7,
                max_tokens=2048,
            )
            reply = response.content
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            reply = "AI service is temporarily unavailable. Please try again."

        if db and user_query:
            try:
                mem = MemoryService(db=db, embedding_svc=self._embed_svc)
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

        return {
            "reply": reply,
            "sources": [p["explanation_text"] for p in relevant_picks],
            "suggested_actions": [],
            "session_id": session_id,
        }

    async def analyze_stock(self, symbol: str, analysis_type: str = "comprehensive") -> dict:
        """Run comprehensive stock analysis combining technical + fundamental + AI."""
        return {
            "symbol": symbol,
            "summary": "Analysis engine not connected.",
            "technical_signals": {},
            "fundamental_metrics": {},
            "ai_recommendation": "",
            "confidence": 0.0,
        }

    async def run_screener(self, strategy: str) -> list[dict]:
        """AI-driven stock screener."""
        return []

    async def sentiment_analysis(self, symbol: str) -> dict:
        """Analyse news & social media sentiment for a stock."""
        return {"symbol": symbol, "sentiment": "neutral", "score": 0.0}

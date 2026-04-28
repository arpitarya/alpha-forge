"""AI-powered endpoints — chat, analysis, screener, sentiment, memory search.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.modules.ai.ai_schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ChatRequest,
    ChatResponse,
)
from app.modules.ai.ai_service import AIService
from app.modules.memory.embedding_service import get_embedding_service
from app.modules.memory.memory_service import MemoryService
from app.modules.screener.screener_service import ScreenerService

router = APIRouter()
logger = get_logger("routes.ai")
screener_service = ScreenerService()


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    result = await AIService().chat(
        messages=[m.model_dump() for m in body.messages],
        context=body.context,
        db=db,
    )
    return ChatResponse(**result)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(body: AnalysisRequest):
    result = await AIService().analyze_stock(body.symbol.upper(), body.analysis_type)
    return AnalysisResponse(**result)


@router.get("/screener")
async def ai_screener(strategy: str = "momentum"):
    logger.info("Screener requested with strategy=%s", strategy)
    data = await screener_service.get_picks()
    picks = data.get("picks", [])
    return {
        "strategy": strategy,
        "scan_date": data.get("scan_date", ""),
        "model_type": data.get("model_type"),
        "count": len(picks),
        "results": picks,
        "disclaimer": "Not SEBI registered investment advice. For personal research only.",
    }


@router.get("/sentiment/{symbol}")
async def sentiment_analysis(symbol: str):
    return {"symbol": symbol.upper(), "sentiment": "neutral", "score": 0.0, "articles": []}


@router.get("/memory/search")
async def search_memory(
    q: str = Query(..., description="Natural language query"),
    symbol: str | None = Query(None, description="Filter picks by symbol"),
    top_k: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    mem = MemoryService(db=db, embedding_svc=get_embedding_service())
    return {
        "query": q,
        "screener_picks": await mem.search_picks(q, top_k=top_k, symbol_filter=symbol),
        "conversation_turns": await mem.search_memory(q, user_id=None, top_k=top_k),
    }

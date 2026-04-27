"""AI-powered analysis endpoints — chat, recommendations, screeners."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.modules.ai.service import AIService
from app.modules.memory.embedding import get_embedding_service
from app.modules.memory.service import MemoryService
from app.modules.screener.service import ScreenerService

router = APIRouter()
logger = get_logger("routes.ai")

screener_service = ScreenerService()


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: dict | None = None
    # context keys: session_id (str), turn_index (int), user_id (str|None),
    #               symbol (str|None), portfolio (list[dict]|None)


class ChatResponse(BaseModel):
    reply: str
    sources: list[str] = []
    suggested_actions: list[dict] = []
    session_id: str = ""


class AnalysisRequest(BaseModel):
    symbol: str
    analysis_type: str = "comprehensive"


class AnalysisResponse(BaseModel):
    symbol: str
    summary: str
    technical_signals: dict = {}
    fundamental_metrics: dict = {}
    ai_recommendation: str = ""
    confidence: float = 0.0


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """RAG-powered conversational AI assistant for market analysis and portfolio advice."""
    ai_svc = AIService()
    result = await ai_svc.chat(
        messages=[m.model_dump() for m in body.messages],
        context=body.context,
        db=db,
    )
    return ChatResponse(**result)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(body: AnalysisRequest):
    """Run AI-powered comprehensive analysis on a stock."""
    ai_svc = AIService()
    result = await ai_svc.analyze_stock(body.symbol.upper(), body.analysis_type)
    return AnalysisResponse(**result)


@router.get("/screener")
async def ai_screener(strategy: str = "momentum"):
    """AI-driven stock screener — finds opportunities based on strategy.

    Disclaimer: Not SEBI registered investment advice.
    """
    logger.info("Screener requested with strategy=%s", strategy)
    data = await screener_service.get_picks()
    picks = data.get("picks", [])
    return {
        "strategy": strategy,
        "scan_date": data.get("scan_date", ""),
        "model_type": data.get("model_type"),
        "count": len(picks),
        "results": picks,
        "disclaimer": (
            "Not SEBI registered investment advice. "
            "For personal research and educational use only."
        ),
    }


@router.get("/sentiment/{symbol}")
async def sentiment_analysis(symbol: str):
    """Analyse news & social sentiment for a stock."""
    return {"symbol": symbol.upper(), "sentiment": "neutral", "score": 0.0, "articles": []}


@router.get("/memory/search")
async def search_memory(
    q: str = Query(..., description="Natural language query"),
    symbol: str | None = Query(None, description="Filter picks by symbol"),
    top_k: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Semantic search over screener picks and past AI conversations."""
    embed_svc = get_embedding_service()
    mem = MemoryService(db=db, embedding_svc=embed_svc)
    picks = await mem.search_picks(q, top_k=top_k, symbol_filter=symbol)
    conversations = await mem.search_memory(q, user_id=None, top_k=top_k)
    return {
        "query": q,
        "screener_picks": picks,
        "conversation_turns": conversations,
    }

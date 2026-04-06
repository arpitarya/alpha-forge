"""AI-powered analysis endpoints — chat, recommendations, screeners."""

from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.core.logging import get_logger
from app.services.screener import ScreenerService

router = APIRouter()
logger = get_logger("routes.ai")

screener_service = ScreenerService()


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: dict | None = None  # optional: current symbol, portfolio, etc.


class ChatResponse(BaseModel):
    reply: str
    sources: list[str] = []
    suggested_actions: list[dict] = []


class AnalysisRequest(BaseModel):
    symbol: str
    analysis_type: str = "comprehensive"  # technical | fundamental | comprehensive


class AnalysisResponse(BaseModel):
    symbol: str
    summary: str
    technical_signals: dict = {}
    fundamental_metrics: dict = {}
    ai_recommendation: str = ""
    confidence: float = 0.0


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(body: ChatRequest):
    """Conversational AI assistant for market analysis, portfolio advice, and trade ideas."""
    # TODO: integrate with LLM service
    return ChatResponse(
        reply="AI chat is not yet connected. This will provide market analysis, "
        "portfolio insights, and trade recommendations.",
        sources=[],
        suggested_actions=[],
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(body: AnalysisRequest):
    """Run AI-powered comprehensive analysis on a stock."""
    # TODO: integrate with AI service
    return AnalysisResponse(
        symbol=body.symbol.upper(),
        summary="Analysis engine not yet connected.",
    )


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
    # TODO: NLP sentiment pipeline
    return {"symbol": symbol.upper(), "sentiment": "neutral", "score": 0.0, "articles": []}

"""Pydantic schemas for AI endpoints."""

from __future__ import annotations

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: dict | None = None
    # context keys: session_id, turn_index, user_id, symbol, portfolio


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

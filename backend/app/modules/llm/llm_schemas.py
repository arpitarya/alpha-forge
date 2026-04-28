"""Pydantic schemas for LLM Gateway routes."""

from __future__ import annotations

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class CompleteRequest(BaseModel):
    query_type: str = "chat"
    messages: list[ChatMessage]
    provider: str | None = None
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 2048


class AnalyzeRequest(BaseModel):
    raw_output: str


class LLMResponseModel(BaseModel):
    content: str
    model: str
    provider: str
    tokens_used: int
    latency_ms: float
    cost: float

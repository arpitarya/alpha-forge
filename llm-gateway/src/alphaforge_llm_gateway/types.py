"""Core type definitions for the LLM gateway."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    GEMINI = "gemini"
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"


class QueryType(str, Enum):
    """Categories of queries for smart routing."""

    SCREENER_ANALYSIS = "screener_analysis"
    STOCK_EXPLANATION = "stock_explanation"
    CHAT = "chat"
    SENTIMENT = "sentiment"
    TECHNICAL_SUMMARY = "technical_summary"


@dataclass
class RateLimits:
    """Rate limit configuration for a provider."""

    rpm: int = 0  # requests per minute (0 = unlimited)
    tpm: int = 0  # tokens per minute (0 = unlimited)
    rpd: int = 0  # requests per day (0 = unlimited)
    tpd: int = 0  # tokens per day (0 = unlimited)


@dataclass
class ProviderConfig:
    """Configuration for a single LLM provider."""

    name: LLMProvider
    base_url: str
    api_key: str = ""
    models: list[str] = field(default_factory=list)
    rate_limits: RateLimits = field(default_factory=RateLimits)
    is_local: bool = False


@dataclass
class LLMResponse:
    """Unified response from any LLM provider."""

    content: str
    model: str
    provider: LLMProvider
    tokens_used: int = 0
    latency_ms: float = 0.0
    cost: float = 0.0  # Always 0.0 — free tier only


class CostGuardError(Exception):
    """Raised when a request would incur cost (non-free model or tier)."""

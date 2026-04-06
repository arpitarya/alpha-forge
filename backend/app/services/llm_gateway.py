"""Thin wrapper around alphaforge-llm-gateway for backend use.

Follows the same pattern as ``app.core.logging`` wrapping ``alphaforge-logger``.
"""

from __future__ import annotations

from alphaforge_llm_gateway import LLMGateway

from app.core.config import settings

_gateway: LLMGateway | None = None


def get_gateway() -> LLMGateway:
    """Return the singleton LLMGateway instance, initialized from settings."""
    global _gateway  # noqa: PLW0603
    if _gateway is None:
        _gateway = LLMGateway(
            gemini_key=settings.gemini_api_key,
            groq_key=settings.groq_api_key,
            hf_key=settings.huggingface_api_key,
            openrouter_key=settings.openrouter_api_key,
            ollama_url=settings.ollama_base_url,
        )
    return _gateway

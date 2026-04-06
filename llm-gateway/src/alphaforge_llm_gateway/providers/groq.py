"""Groq provider — free tier with ultra-fast inference."""

from __future__ import annotations

import logging

from alphaforge_llm_gateway.base import BaseLLMProvider
from alphaforge_llm_gateway.types import LLMProvider, LLMResponse, ProviderConfig, RateLimits

logger = logging.getLogger("alphaforge.llm.providers.groq")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "qwen/qwen3-32b",
    "moonshotai/kimi-k2-instruct",
]
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"


class GroqProvider(BaseLLMProvider):
    """Groq free tier — fastest inference for open-source models."""

    def __init__(self, api_key: str) -> None:
        config = ProviderConfig(
            name=LLMProvider.GROQ,
            base_url=GROQ_BASE_URL,
            api_key=api_key,
            models=list(GROQ_MODELS),
            rate_limits=RateLimits(rpm=30, rpd=1000, tpm=12_000, tpd=100_000),
        )
        super().__init__(config)
        self._dynamic_limits: dict[str, int] = {}

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        model = model or GROQ_DEFAULT_MODEL
        logger.debug("Groq completion: model=%s", model)
        response = await self._call_openai(messages, model, temperature, max_tokens)
        # Groq returns rate limit headers — parse them if available via raw response
        # The openai SDK doesn't directly expose headers, but we track what we can
        return response

    async def health_check(self) -> bool:
        try:
            response = await self._call_openai(
                messages=[{"role": "user", "content": "ping"}],
                model=GROQ_DEFAULT_MODEL,
                max_tokens=5,
            )
            return bool(response.content)
        except Exception:
            logger.warning("Groq health check failed", exc_info=True)
            return False

    def available_models(self) -> list[str]:
        return list(GROQ_MODELS)

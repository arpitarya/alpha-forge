"""Google Gemini provider — free tier via OpenAI-compatible endpoint."""

from __future__ import annotations

import logging

from alphaforge_llm_gateway.base import BaseLLMProvider
from alphaforge_llm_gateway.types import LLMProvider, LLMResponse, ProviderConfig, RateLimits

logger = logging.getLogger("alphaforge.llm.providers.gemini")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemma-4",
]
GEMINI_DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiProvider(BaseLLMProvider):
    """Google Gemini free tier via the generativelanguage OpenAI-compatible endpoint."""

    def __init__(self, api_key: str) -> None:
        config = ProviderConfig(
            name=LLMProvider.GEMINI,
            base_url=GEMINI_BASE_URL,
            api_key=api_key,
            models=list(GEMINI_MODELS),
            rate_limits=RateLimits(rpm=15, rpd=1500, tpm=1_000_000, tpd=50_000_000),
        )
        super().__init__(config)

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        model = model or GEMINI_DEFAULT_MODEL
        logger.debug("Gemini completion: model=%s", model)
        return await self._call_openai(messages, model, temperature, max_tokens)

    async def health_check(self) -> bool:
        try:
            response = await self._call_openai(
                messages=[{"role": "user", "content": "ping"}],
                model=GEMINI_DEFAULT_MODEL,
                max_tokens=5,
            )
            return bool(response.content)
        except Exception:
            logger.warning("Gemini health check failed", exc_info=True)
            return False

    def available_models(self) -> list[str]:
        return list(GEMINI_MODELS)

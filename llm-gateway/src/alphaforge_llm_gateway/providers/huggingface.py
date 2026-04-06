"""HuggingFace provider — serverless inference free tier."""

from __future__ import annotations

import logging

from alphaforge_llm_gateway.base import BaseLLMProvider
from alphaforge_llm_gateway.types import LLMProvider, LLMResponse, ProviderConfig, RateLimits

logger = logging.getLogger("alphaforge.llm.providers.huggingface")

HF_BASE_URL = "https://router.huggingface.co/v1"
HF_MODELS = [
    "Qwen/Qwen2.5-72B-Instruct",
]
HF_DEFAULT_MODEL = "Qwen/Qwen2.5-72B-Instruct"


class HuggingFaceProvider(BaseLLMProvider):
    """HuggingFace serverless inference — free tier with large open models."""

    def __init__(self, api_key: str) -> None:
        config = ProviderConfig(
            name=LLMProvider.HUGGINGFACE,
            base_url=HF_BASE_URL,
            api_key=api_key,
            models=list(HF_MODELS),
            rate_limits=RateLimits(rpm=10, rpd=1000),
        )
        super().__init__(config)

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        model = model or HF_DEFAULT_MODEL
        logger.debug("HuggingFace completion: model=%s", model)
        return await self._call_openai(messages, model, temperature, max_tokens)

    async def health_check(self) -> bool:
        try:
            response = await self._call_openai(
                messages=[{"role": "user", "content": "ping"}],
                model=HF_DEFAULT_MODEL,
                max_tokens=5,
            )
            return bool(response.content)
        except Exception:
            logger.warning("HuggingFace health check failed", exc_info=True)
            return False

    def available_models(self) -> list[str]:
        return list(HF_MODELS)

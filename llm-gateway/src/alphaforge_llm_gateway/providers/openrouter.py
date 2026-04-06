"""OpenRouter provider — aggregator with strict free-model-only enforcement."""

from __future__ import annotations

import logging
import time

import httpx

from alphaforge_llm_gateway.base import BaseLLMProvider
from alphaforge_llm_gateway.types import (
    CostGuardError,
    LLMProvider,
    LLMResponse,
    ProviderConfig,
    RateLimits,
)

logger = logging.getLogger("alphaforge.llm.providers.openrouter")

OR_BASE_URL = "https://openrouter.ai/api/v1"
OR_REFRESH_INTERVAL = 86400  # 24 hours in seconds


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter with hard filter to $0 models only — never incurs cost."""

    def __init__(self, api_key: str) -> None:
        config = ProviderConfig(
            name=LLMProvider.OPENROUTER,
            base_url=OR_BASE_URL,
            api_key=api_key,
            models=[],  # populated by _refresh_free_models
            rate_limits=RateLimits(rpm=10, rpd=200),
        )
        super().__init__(config)
        self._free_models: set[str] = set()
        self._last_refresh: float = 0.0

    async def _refresh_free_models(self) -> None:
        """Fetch model list from OpenRouter and filter to strictly $0 models."""
        now = time.monotonic()
        if self._free_models and (now - self._last_refresh) < OR_REFRESH_INTERVAL:
            return

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{OR_BASE_URL}/models",
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                    timeout=15.0,
                )
                resp.raise_for_status()
                data = resp.json()

            free = set()
            for model in data.get("data", []):
                pricing = model.get("pricing", {})
                prompt_cost = str(pricing.get("prompt", "1"))
                completion_cost = str(pricing.get("completion", "1"))
                if prompt_cost == "0" and completion_cost == "0":
                    free.add(model["id"])

            self._free_models = free
            self.config.models = sorted(free)
            self._last_refresh = now
            logger.info("OpenRouter: refreshed free models, found %d", len(free))
        except Exception:
            logger.warning("OpenRouter: failed to refresh free model list", exc_info=True)
            if not self._free_models:
                # Fallback defaults if we've never successfully fetched
                self._free_models = {
                    "google/gemma-3-1b-it:free",
                    "qwen/qwen3-0.6b:free",
                }
                self.config.models = sorted(self._free_models)

    def _assert_free(self, model: str) -> None:
        """Raise CostGuardError if the requested model is not in the free list."""
        if self._free_models and model not in self._free_models:
            raise CostGuardError(
                f"OpenRouter model '{model}' is not in the free model list. "
                "Request rejected to prevent cost."
            )

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        await self._refresh_free_models()
        model = model or (sorted(self._free_models)[0] if self._free_models else "")
        self._assert_free(model)
        logger.debug("OpenRouter completion: model=%s", model)
        return await self._call_openai(
            messages,
            model,
            temperature,
            max_tokens,
            extra_headers={
                "HTTP-Referer": "https://github.com/alphaforge",
                "X-Title": "AlphaForge LLM Gateway",
            },
        )

    async def health_check(self) -> bool:
        try:
            await self._refresh_free_models()
            return len(self._free_models) > 0
        except Exception:
            logger.warning("OpenRouter health check failed", exc_info=True)
            return False

    def available_models(self) -> list[str]:
        return sorted(self._free_models)

    def is_free_model(self, model: str) -> bool:
        """Check if a model is in the verified free list."""
        return model in self._free_models

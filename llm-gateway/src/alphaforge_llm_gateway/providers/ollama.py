"""Ollama provider — local, private, unlimited inference."""

from __future__ import annotations

import logging

import httpx

from alphaforge_llm_gateway.base import BaseLLMProvider
from alphaforge_llm_gateway.types import LLMProvider, LLMResponse, ProviderConfig, RateLimits

logger = logging.getLogger("alphaforge.llm.providers.ollama")

OLLAMA_DEFAULT_URL = "http://localhost:11434/v1"
OLLAMA_RECOMMENDED_MODELS = [
    "qwen2.5:7b",
    "llama3.1:8b",
    "mistral-nemo:12b",
]


class OllamaProvider(BaseLLMProvider):
    """Local Ollama — private, unlimited, works offline."""

    def __init__(self, base_url: str | None = None) -> None:
        url = base_url or OLLAMA_DEFAULT_URL
        config = ProviderConfig(
            name=LLMProvider.OLLAMA,
            base_url=url,
            api_key="not-needed",
            models=list(OLLAMA_RECOMMENDED_MODELS),
            rate_limits=RateLimits(),  # unlimited
            is_local=True,
        )
        super().__init__(config)
        self._detected_models: list[str] = []

    async def _detect_models(self) -> list[str]:
        """Auto-detect available models via Ollama's /api/tags endpoint."""
        # Ollama's API tags endpoint is at the root, not /v1
        base = self.config.base_url.rstrip("/")
        if base.endswith("/v1"):
            base = base[:-3]

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{base}/api/tags", timeout=5.0)
                resp.raise_for_status()
                data = resp.json()

            models = [m["name"] for m in data.get("models", [])]
            self._detected_models = models
            if models:
                self.config.models = models
                logger.info("Ollama: detected %d local models", len(models))
            return models
        except Exception:
            logger.debug("Ollama: could not detect models (is Ollama running?)")
            return []

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        if not self._detected_models:
            await self._detect_models()

        model = model or (self._detected_models[0] if self._detected_models else "qwen2.5:7b")
        logger.debug("Ollama completion: model=%s", model)
        return await self._call_openai(messages, model, temperature, max_tokens)

    async def health_check(self) -> bool:
        try:
            models = await self._detect_models()
            return len(models) > 0
        except Exception:
            logger.debug("Ollama health check failed — not running")
            return False

    def available_models(self) -> list[str]:
        return self._detected_models or list(OLLAMA_RECOMMENDED_MODELS)

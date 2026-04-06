"""Abstract base class for LLM providers — all providers implement this."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from alphaforge_llm_gateway.types import LLMProvider, LLMResponse, ProviderConfig


class BaseLLMProvider(ABC):
    """Interface every LLM provider adapter must implement."""

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self._client = AsyncOpenAI(
            api_key=config.api_key or "not-needed",
            base_url=config.base_url,
        )

    @property
    def name(self) -> LLMProvider:
        return self.config.name

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...

    @abstractmethod
    def available_models(self) -> list[str]:
        ...

    def default_model(self) -> str:
        """Return the provider's default model."""
        return self.config.models[0] if self.config.models else ""

    async def _call_openai(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        extra_headers: dict[str, str] | None = None,
    ) -> LLMResponse:
        """Shared OpenAI-compatible completion call used by all providers."""
        start = time.monotonic()
        kwargs: dict = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if extra_headers:
            kwargs["extra_headers"] = extra_headers

        response = await self._client.chat.completions.create(**kwargs)

        latency_ms = (time.monotonic() - start) * 1000
        choice = response.choices[0]
        usage = response.usage

        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            provider=self.config.name,
            tokens_used=usage.total_tokens if usage else 0,
            latency_ms=round(latency_ms, 2),
            cost=0.0,
        )

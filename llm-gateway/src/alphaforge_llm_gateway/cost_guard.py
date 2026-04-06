"""Zero-cost enforcement — ensures all requests stay within free tier."""

from __future__ import annotations

import logging

from alphaforge_llm_gateway.rate_limiter import RateLimiter
from alphaforge_llm_gateway.types import CostGuardError, LLMProvider

logger = logging.getLogger("alphaforge.llm.cost_guard")

# Models known to be free on each provider
_FREE_GEMINI_MODELS = {
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemma-4",
}

_FREE_GROQ_MODELS = {
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "qwen/qwen3-32b",
    "moonshotai/kimi-k2-instruct",
}


class CostGuard:
    """Pre-request validation to ensure $0 cost.

    Raises CostGuardError if a request would incur cost. Logs warnings
    when approaching rate limits (>80% utilization).
    """

    def __init__(
        self,
        rate_limiter: RateLimiter,
        openrouter_free_models: set[str] | None = None,
    ) -> None:
        self._rate_limiter = rate_limiter
        self._openrouter_free_models = openrouter_free_models or set()

    def update_openrouter_free_models(self, models: set[str]) -> None:
        """Update the cached set of free OpenRouter models."""
        self._openrouter_free_models = models

    def validate_request(self, provider: LLMProvider, model: str) -> bool:
        """Pre-request check. Raises CostGuardError if request would incur cost."""
        # Provider-specific free model checks
        if provider == LLMProvider.GEMINI and model not in _FREE_GEMINI_MODELS:
            raise CostGuardError(
                f"Gemini model '{model}' is not in the verified free model list."
            )

        if provider == LLMProvider.GROQ and model not in _FREE_GROQ_MODELS:
            raise CostGuardError(
                f"Groq model '{model}' is not in the verified free model list."
            )

        if provider == LLMProvider.OPENROUTER:
            if self._openrouter_free_models and model not in self._openrouter_free_models:
                raise CostGuardError(
                    f"OpenRouter model '{model}' is not in the free model list."
                )

        # Ollama is always free (local) — no check needed
        # HuggingFace serverless inference is free tier — no model-level check

        # Warn at >80% utilization
        utilization = self._rate_limiter.utilization_pct(provider)
        if utilization > 80:
            logger.warning(
                "%s at %.0f%% rate limit utilization — consider throttling",
                provider.value,
                utilization,
            )

        return True

    def check_rate_limit(self, provider: LLMProvider, estimated_tokens: int = 0) -> bool:
        """Check if the request would be within rate limits."""
        return self._rate_limiter.acquire(provider, estimated_tokens)

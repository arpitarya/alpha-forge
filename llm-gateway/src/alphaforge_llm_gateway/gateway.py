"""LLMGateway — main entry point that ties providers, router, rate limiter, and cost guard."""

from __future__ import annotations

import logging
import os

from alphaforge_llm_gateway.base import BaseLLMProvider
from alphaforge_llm_gateway.cost_guard import CostGuard
from alphaforge_llm_gateway.prompts import DISCLAIMER, SYSTEM_PROMPTS
from alphaforge_llm_gateway.rate_limiter import RateLimiter
from alphaforge_llm_gateway.router import QueryRouter
from alphaforge_llm_gateway.types import CostGuardError, LLMProvider, LLMResponse, QueryType

logger = logging.getLogger("alphaforge.llm.gateway")


class LLMGateway:
    """Unified async gateway to multiple free LLM providers.

    Usage::

        gateway = LLMGateway.from_env()
        response = await gateway.complete(QueryType.CHAT, [
            {"role": "user", "content": "What is RSI?"}
        ])
        print(response.content)
    """

    def __init__(
        self,
        gemini_key: str = "",
        groq_key: str = "",
        hf_key: str = "",
        openrouter_key: str = "",
        ollama_url: str = "",
    ) -> None:
        self._providers: dict[LLMProvider, BaseLLMProvider] = {}
        self._rate_limiter = RateLimiter()
        self._cost_guard = CostGuard(self._rate_limiter)

        # Register providers based on provided keys
        if gemini_key:
            from alphaforge_llm_gateway.providers.gemini import GeminiProvider

            self._providers[LLMProvider.GEMINI] = GeminiProvider(gemini_key)

        if groq_key:
            from alphaforge_llm_gateway.providers.groq import GroqProvider

            self._providers[LLMProvider.GROQ] = GroqProvider(groq_key)

        if hf_key:
            from alphaforge_llm_gateway.providers.huggingface import HuggingFaceProvider

            self._providers[LLMProvider.HUGGINGFACE] = HuggingFaceProvider(hf_key)

        if openrouter_key:
            from alphaforge_llm_gateway.providers.openrouter import OpenRouterProvider

            self._providers[LLMProvider.OPENROUTER] = OpenRouterProvider(openrouter_key)

        if ollama_url or not any([gemini_key, groq_key, hf_key, openrouter_key]):
            # Always try Ollama as fallback if no cloud keys, or if explicitly configured
            from alphaforge_llm_gateway.providers.ollama import OllamaProvider

            self._providers[LLMProvider.OLLAMA] = OllamaProvider(ollama_url or None)

        self._router = QueryRouter(set(self._providers.keys()))
        logger.info(
            "LLMGateway initialized with providers: %s",
            [p.value for p in self._providers],
        )

    @classmethod
    def from_env(cls, env_file: str | None = None) -> LLMGateway:
        """Create a gateway instance from environment variables.

        Reads: GEMINI_API_KEY, GROQ_API_KEY, HUGGINGFACE_API_KEY,
               OPENROUTER_API_KEY, OLLAMA_BASE_URL
        """
        if env_file:
            _load_dotenv(env_file)

        return cls(
            gemini_key=os.environ.get("GEMINI_API_KEY", ""),
            groq_key=os.environ.get("GROQ_API_KEY", ""),
            hf_key=os.environ.get("HUGGINGFACE_API_KEY", ""),
            openrouter_key=os.environ.get("OPENROUTER_API_KEY", ""),
            ollama_url=os.environ.get("OLLAMA_BASE_URL", ""),
        )

    async def complete(
        self,
        query_type: QueryType,
        messages: list[dict[str, str]],
        *,
        provider: LLMProvider | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Send a completion request, with smart routing and automatic fallback.

        Args:
            query_type: Category of query (determines routing).
            messages: Chat messages in OpenAI format.
            provider: Force a specific provider (skip router).
            model: Force a specific model.
            temperature: Sampling temperature.
            max_tokens: Max tokens in response.

        Returns:
            LLMResponse with content, model, provider, and metadata.

        Raises:
            CostGuardError: If request would incur cost.
            RuntimeError: If all providers fail or are exhausted.
        """
        # Inject system prompt if one exists for this query type
        system_prompt = SYSTEM_PROMPTS.get(query_type, "")
        if system_prompt and not any(m.get("role") == "system" for m in messages):
            messages = [{"role": "system", "content": system_prompt}, *messages]

        # Build the attempt chain
        if provider:
            chain = [(provider, model or "")]
        else:
            chain = self._router.get_fallback_chain(query_type)
            if model:
                # Override model in the first entry
                chain = [(chain[0][0], model)] + chain[1:] if chain else chain

        if not chain:
            raise RuntimeError(
                "No providers available. Configure at least one API key or start Ollama."
            )

        last_error: Exception | None = None
        for attempt_provider, attempt_model in chain:
            prov = self._providers.get(attempt_provider)
            if not prov:
                continue

            resolved_model = attempt_model or prov.default_model()

            # Cost guard check
            try:
                self._cost_guard.validate_request(attempt_provider, resolved_model)
            except CostGuardError:
                logger.warning(
                    "Cost guard blocked %s/%s", attempt_provider.value, resolved_model
                )
                continue

            # Rate limit check
            if not self._cost_guard.check_rate_limit(attempt_provider):
                logger.info(
                    "Rate limited on %s, falling back", attempt_provider.value
                )
                continue

            # Attempt completion
            try:
                response = await prov.complete(
                    messages, resolved_model, temperature, max_tokens
                )
                logger.info(
                    "Completed via %s/%s in %.0fms (%d tokens)",
                    response.provider.value,
                    response.model,
                    response.latency_ms,
                    response.tokens_used,
                )
                return response
            except Exception as e:
                last_error = e
                logger.warning(
                    "Provider %s failed: %s — cascading to next",
                    attempt_provider.value,
                    e,
                )
                continue

        raise RuntimeError(
            f"All providers exhausted for {query_type.value}. "
            f"Last error: {last_error}"
        )

    async def analyze_screener(self, raw_output: str) -> LLMResponse:
        """Convenience method: analyze screener scan output."""
        return await self.complete(
            QueryType.SCREENER_ANALYSIS,
            [{"role": "user", "content": raw_output}],
        )

    async def explain_picks(self, raw_output: str) -> LLMResponse:
        """Convenience method: translate SHAP explanations to plain English."""
        return await self.complete(
            QueryType.STOCK_EXPLANATION,
            [{"role": "user", "content": raw_output}],
        )

    async def providers_status(self) -> list[dict]:
        """Return health and remaining quota per registered provider."""
        statuses = []
        for name, prov in self._providers.items():
            healthy = False
            try:
                healthy = await prov.health_check()
            except Exception:
                pass

            remaining = self._rate_limiter.remaining(name)
            utilization = self._rate_limiter.utilization_pct(name)

            statuses.append({
                "provider": name.value,
                "healthy": healthy,
                "models": prov.available_models(),
                "default_model": prov.default_model(),
                "remaining": remaining,
                "utilization_pct": round(utilization, 1),
                "is_local": prov.config.is_local,
            })

        return statuses


def _load_dotenv(path: str) -> None:
    """Minimal .env file loader — no external dependency."""
    from pathlib import Path

    env_path = Path(path)
    if not env_path.is_file():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        os.environ.setdefault(key, value)

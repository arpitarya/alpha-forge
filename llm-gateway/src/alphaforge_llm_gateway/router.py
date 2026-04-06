"""Smart query router — maps QueryType to provider fallback chains."""

from __future__ import annotations

import logging

from alphaforge_llm_gateway.types import LLMProvider, QueryType

logger = logging.getLogger("alphaforge.llm.router")

# (provider, model) tuples — ordered by priority
RoutingEntry = tuple[LLMProvider, str]

# Default routing table — can be overridden by benchmark results
ROUTING_TABLE: dict[QueryType, list[RoutingEntry]] = {
    QueryType.SCREENER_ANALYSIS: [
        (LLMProvider.GEMINI, "gemini-2.5-flash"),
        (LLMProvider.GROQ, "llama-3.3-70b-versatile"),
        (LLMProvider.OLLAMA, ""),  # empty = use whatever is available locally
    ],
    QueryType.STOCK_EXPLANATION: [
        (LLMProvider.GEMINI, "gemini-2.5-pro"),
        (LLMProvider.GROQ, "qwen/qwen3-32b"),
        (LLMProvider.HUGGINGFACE, "Qwen/Qwen2.5-72B-Instruct"),
    ],
    QueryType.CHAT: [
        (LLMProvider.GROQ, "llama-3.3-70b-versatile"),
        (LLMProvider.GEMINI, "gemini-2.5-flash"),
        (LLMProvider.OLLAMA, ""),
    ],
    QueryType.SENTIMENT: [
        (LLMProvider.GEMINI, "gemini-2.5-flash-lite"),
        (LLMProvider.GROQ, "meta-llama/llama-4-scout-17b-16e-instruct"),
        (LLMProvider.HUGGINGFACE, "Qwen/Qwen2.5-72B-Instruct"),
    ],
    QueryType.TECHNICAL_SUMMARY: [
        (LLMProvider.GEMINI, "gemini-2.5-flash"),
        (LLMProvider.GROQ, "qwen/qwen3-32b"),
        (LLMProvider.OLLAMA, ""),
    ],
}


class QueryRouter:
    """Routes queries to the best available provider with automatic fallback."""

    def __init__(
        self,
        available_providers: set[LLMProvider],
        routing_table: dict[QueryType, list[RoutingEntry]] | None = None,
    ) -> None:
        self._available = available_providers
        self._table = routing_table or dict(ROUTING_TABLE)

    def get_fallback_chain(self, query_type: QueryType) -> list[RoutingEntry]:
        """Return the ordered fallback chain for a query type, filtered to available providers."""
        chain = self._table.get(query_type, [])
        return [(p, m) for p, m in chain if p in self._available]

    def update_routing(self, query_type: QueryType, chain: list[RoutingEntry]) -> None:
        """Override the routing chain for a query type (e.g., from benchmark results)."""
        self._table[query_type] = chain
        logger.info("Updated routing for %s: %s", query_type.value, chain)

    def add_provider(self, provider: LLMProvider) -> None:
        """Register a provider as available."""
        self._available.add(provider)

    def remove_provider(self, provider: LLMProvider) -> None:
        """Mark a provider as unavailable."""
        self._available.discard(provider)

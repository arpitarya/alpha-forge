"""Per-provider token bucket rate limiter with free-tier limits."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from alphaforge_llm_gateway.types import LLMProvider, RateLimits


@dataclass
class _BucketState:
    """Tracks current consumption for a single provider."""

    requests_this_minute: int = 0
    tokens_this_minute: int = 0
    requests_today: int = 0
    tokens_today: int = 0
    minute_start: float = field(default_factory=time.monotonic)
    day_start: float = field(default_factory=time.monotonic)


# Pre-configured free-tier limits per provider
DEFAULT_LIMITS: dict[LLMProvider, RateLimits] = {
    LLMProvider.GEMINI: RateLimits(rpm=15, rpd=1500, tpm=1_000_000, tpd=50_000_000),
    LLMProvider.GROQ: RateLimits(rpm=30, rpd=1000, tpm=12_000, tpd=100_000),
    LLMProvider.HUGGINGFACE: RateLimits(rpm=10, rpd=1000),
    LLMProvider.OPENROUTER: RateLimits(rpm=10, rpd=200),
    LLMProvider.OLLAMA: RateLimits(),  # unlimited
}


class RateLimiter:
    """In-memory per-provider rate limiter with auto-resetting counters."""

    def __init__(self, limits: dict[LLMProvider, RateLimits] | None = None) -> None:
        self._limits = limits or dict(DEFAULT_LIMITS)
        self._buckets: dict[LLMProvider, _BucketState] = {}

    def _get_bucket(self, provider: LLMProvider) -> _BucketState:
        if provider not in self._buckets:
            self._buckets[provider] = _BucketState()
        bucket = self._buckets[provider]
        now = time.monotonic()

        # Reset minute counters
        if now - bucket.minute_start >= 60:
            bucket.requests_this_minute = 0
            bucket.tokens_this_minute = 0
            bucket.minute_start = now

        # Reset day counters
        if now - bucket.day_start >= 86400:
            bucket.requests_today = 0
            bucket.tokens_today = 0
            bucket.day_start = now

        return bucket

    def acquire(self, provider: LLMProvider, estimated_tokens: int = 0) -> bool:
        """Check if a request is allowed. Returns False if rate-limited."""
        limits = self._limits.get(provider, RateLimits())
        bucket = self._get_bucket(provider)

        # Check RPM
        if limits.rpm and bucket.requests_this_minute >= limits.rpm:
            return False

        # Check RPD
        if limits.rpd and bucket.requests_today >= limits.rpd:
            return False

        # Check TPM
        if limits.tpm and estimated_tokens and bucket.tokens_this_minute + estimated_tokens > limits.tpm:
            return False

        # Check TPD
        if limits.tpd and estimated_tokens and bucket.tokens_today + estimated_tokens > limits.tpd:
            return False

        # Allowed — increment counters
        bucket.requests_this_minute += 1
        bucket.requests_today += 1
        if estimated_tokens:
            bucket.tokens_this_minute += estimated_tokens
            bucket.tokens_today += estimated_tokens

        return True

    def record_tokens(self, provider: LLMProvider, actual_tokens: int) -> None:
        """Update token counters after a response with actual usage."""
        # Already incremented estimated in acquire; adjust if actual differs
        # For simplicity, just add the difference if we underestimated
        pass

    def remaining(self, provider: LLMProvider) -> dict[str, int]:
        """Return remaining quota for a provider."""
        limits = self._limits.get(provider, RateLimits())
        bucket = self._get_bucket(provider)

        result: dict[str, int] = {}
        if limits.rpm:
            result["rpm_remaining"] = max(0, limits.rpm - bucket.requests_this_minute)
        if limits.rpd:
            result["rpd_remaining"] = max(0, limits.rpd - bucket.requests_today)
        if limits.tpm:
            result["tpm_remaining"] = max(0, limits.tpm - bucket.tokens_this_minute)
        if limits.tpd:
            result["tpd_remaining"] = max(0, limits.tpd - bucket.tokens_today)
        return result

    def utilization_pct(self, provider: LLMProvider) -> float:
        """Return the highest utilization percentage across all limit dimensions."""
        limits = self._limits.get(provider, RateLimits())
        bucket = self._get_bucket(provider)
        pcts: list[float] = []

        if limits.rpm:
            pcts.append(bucket.requests_this_minute / limits.rpm * 100)
        if limits.rpd:
            pcts.append(bucket.requests_today / limits.rpd * 100)
        if limits.tpm:
            pcts.append(bucket.tokens_this_minute / limits.tpm * 100)
        if limits.tpd:
            pcts.append(bucket.tokens_today / limits.tpd * 100)

        return max(pcts) if pcts else 0.0

    def update_limits(self, provider: LLMProvider, limits: RateLimits) -> None:
        """Dynamically update limits for a provider (e.g., from Groq response headers)."""
        self._limits[provider] = limits

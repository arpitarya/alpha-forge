# LLM Gateway — Variable Conventions

> Same Python rules as the backend, with a few additions for the gateway-specific concerns: provider slugs, query types, budgets.

---

## 1. Carry-overs from `structure/backend/variables.md`

Apply everything from the backend doc — casing, naming patterns, type-hint rules, async conventions. The points below are **additions** that are gateway-specific.

---

## 2. Domain vocabulary

Use these names consistently across providers, router, CLI, and tests:

| Concept | Variable | Example |
|---------|----------|---------|
| Provider identifier (URL-safe) | `provider_slug` (str) | `"gemini"`, `"groq"`, `"ollama"` |
| Provider human label | `provider_label` (str) | `"Google Gemini"` |
| Query category that drives routing | `query_type` (`QueryType` enum) | `QueryType.SCREENER_ANALYSIS` |
| Token counts | `prompt_tokens`, `completion_tokens`, `total_tokens` | always int |
| Time | `latency_ms` (int) | request duration in milliseconds |
| Money | `cost_usd` (float), `monthly_budget_usd`, `cost_per_1k_input_usd` | always USD, suffix `_usd` |
| Free-tier remaining | `quota_remaining` (dict[str, int]) | `{"requests_per_day": 1450}` |
| Utilization | `utilization_pct` (float) | 0..100 |
| Health | `is_healthy` (bool) | matches the `is_*` pattern |
| Local provider | `is_local` (bool) | true for Ollama |

---

## 3. Enums

```python
class QueryType(str, Enum):
    GENERAL = "general"
    SCREENER_ANALYSIS = "screener_analysis"
    EXPLAIN_PICKS = "explain_picks"
    PORTFOLIO_BRIEF = "portfolio_brief"
    SUMMARIZE = "summarize"


class ProviderHealth(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    DOWN = "down"
```

Routing policy keys are `QueryType` members — never magic strings:

```python
ROUTING_DEFAULTS: dict[QueryType, list[str]] = {
    QueryType.SCREENER_ANALYSIS: ["gemini", "groq", "ollama"],
    QueryType.EXPLAIN_PICKS:     ["groq", "gemini", "ollama"],
    QueryType.GENERAL:           ["groq", "gemini", "openrouter", "ollama"],
}
```

---

## 4. Dataclasses & response shapes

Always frozen, always typed, always derive equality:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_used: int
    latency_ms: int
    cost: float = 0.0


@dataclass(frozen=True)
class BenchmarkResult:
    provider: str
    model: str
    latency_ms: int
    tokens_used: int
    success: bool
    error: str | None = None
```

Frozen so the cost guard / rate limiter can hash + cache them. Mutability is a bug source.

---

## 5. Routing variables

```python
# Healthy providers ranked by p50 latency, then by quota headroom.
ranked: list[Provider] = await self._rank(query_type)
chosen: Provider = ranked[0]
fallback_chain: list[Provider] = ranked[1:]

# Per-call budget check
est_input_tokens = sum(len(m.content) // 4 for m in messages)   # rough
est_cost_usd = chosen.estimate_cost(est_input_tokens, max_tokens or 1024)
self._cost_guard.check(chosen, est_cost_usd)
```

Names like `chosen`, `ranked`, `fallback_chain` consistently describe the **role** a provider plays in this call — much clearer than `provider1`, `next_provider`.

---

## 6. Rate-limit math

```python
@dataclass
class QuotaWindow:
    requests_per_minute: int
    requests_per_day: int
    tokens_per_minute: int
    tokens_per_day: int


@dataclass
class QuotaUsage:
    requests_used_today: int = 0
    tokens_used_today: int = 0
    last_request_at: datetime | None = None


def remaining(self, slug: str) -> dict[str, int]:
    win, used = self._windows[slug], self._usage[slug]
    return {
        "requests_per_day": win.requests_per_day - used.requests_used_today,
        "tokens_per_day":   win.tokens_per_day   - used.tokens_used_today,
    }
```

Names track the time bucket explicitly (`_today`, `_per_day`, `_per_minute`) so a maintainer never has to guess what window applies.

---

## 7. CLI flags

argparse flag names mirror the underlying parameter, kebab-cased:

```bash
python -m alphaforge_llm_gateway chat --query-type screener-analysis --max-tokens 512
python -m alphaforge_llm_gateway analyze-screener -f picks.txt
python -m alphaforge_llm_gateway benchmark --providers gemini,groq
```

Inside argparse:

```python
parser.add_argument("--query-type", dest="query_type", type=QueryType, default=QueryType.GENERAL)
parser.add_argument("-f", "--file", dest="path", type=Path, required=True)
```

`dest=` always matches the Python variable name (snake_case).

---

## 8. Constants

```python
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TIMEOUT_SEC = 30
DEFAULT_MONTHLY_BUDGET_USD = 0.0      # the whole point: free tier only

QUOTA_WARNING_PCT = 80.0
HEALTH_CHECK_TTL_SEC = 60

PROVIDER_SLUGS: tuple[str, ...] = ("gemini", "groq", "huggingface", "openrouter", "ollama")
```

Underscore-grouped numerics:

```python
DEFAULT_QUOTA_RPD = 1_500          # requests per day
DEFAULT_QUOTA_TPD = 1_000_000      # tokens per day
```

---

## 9. Exceptions

Always end in `Error`, hierarchy rooted at `LLMGatewayError`:

```python
class LLMGatewayError(Exception):
    """Base — caller sees this only if they catch broadly."""


class ProviderUnavailable(LLMGatewayError):
    def __init__(self, slug: str, reason: str) -> None:
        super().__init__(f"{slug}: {reason}")
        self.slug = slug
        self.reason = reason


class QuotaExceeded(LLMGatewayError): ...
class BudgetExceeded(LLMGatewayError): ...
class AllProvidersFailed(LLMGatewayError):
    """Raised when every provider in the fallback chain has been tried."""
    def __init__(self, errors: dict[str, Exception]) -> None:
        super().__init__("all providers failed: " + ", ".join(errors))
        self.errors = errors
```

The `errors` map keys are slugs (so callers can log them).

---

## 10. Logging

The gateway must **never** log prompt/response bodies — they contain user data and may include personally identifying information. Log the metadata only:

```python
logger.info(
    "llm call slug=%s model=%s tokens=%d latency_ms=%d cost=%.4f",
    response.provider, response.model, response.tokens_used,
    response.latency_ms, response.cost,
)
```

Use structured logging when fields proliferate:

```python
logger.info("llm call complete", extra={
    "slug": response.provider,
    "model": response.model,
    "tokens": response.tokens_used,
    "latency_ms": response.latency_ms,
    "cost_usd": response.cost,
})
```

---

## 11. Testing variable patterns

Mock fixtures live under `tests/fixtures/<provider>/<scenario>.json`:

```python
@pytest.fixture
def mock_gemini_success():
    return _load("gemini/success.json")


@pytest.fixture
def mock_gemini_quota_exceeded():
    return _load("gemini/429_quota.json")
```

Test names spell out the scenario — never `test_1`, `test_works`:

```python
def test_router_falls_back_when_primary_returns_5xx(...): ...
def test_cost_guard_rejects_when_budget_would_overflow(...): ...
def test_rate_limiter_persists_across_restart(tmp_path): ...
```

---

## 12. Quick reference card (gateway-specific)

```
Provider slug         "gemini" | "groq" | "huggingface" | "openrouter" | "ollama"
Query type            QueryType.SCREENER_ANALYSIS  (str enum, lower-snake values)
Money                 *_usd suffix                 cost_usd, monthly_budget_usd
Tokens                prompt_tokens / completion_tokens / total_tokens
Latency               latency_ms (int)             — never seconds
Health                is_healthy (bool), ProviderHealth enum
Quota                 quota_remaining: dict[str, int]
Utilization           utilization_pct (0..100, float)
Errors                LLMGatewayError → ProviderUnavailable | QuotaExceeded | BudgetExceeded
Constants             DEFAULT_TIMEOUT_SEC, QUOTA_WARNING_PCT, ROUTING_DEFAULTS
CLI                   --kebab-case → snake_case dest
Log redaction         metadata only — never prompt/response content
```

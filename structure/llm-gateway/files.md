# LLM Gateway — Application Structure

> **Core principle**: a gateway, not a wrapper. We unify five free providers (Gemini, Groq, HuggingFace, OpenRouter, Ollama) behind one async API with smart routing, rate limiting, and a hard $0 cost wall.
> Soft caps: 200 lines per provider · 300 lines per orchestration module.

---

## What this package is

`@alphaforge/llm-gateway` (Python: `alphaforge-llm-gateway`) is a **publishable package** with three hats:

1. **Library** — `from alphaforge_llm_gateway import LLMGateway`. Used by `backend/app/services/llm_gateway.py`.
2. **CLI** — `python -m alphaforge_llm_gateway chat | analyze-screener | benchmark | providers`.
3. **Notebook playground** — `notebooks/llm_gateway_playground.ipynb` for interactive provider comparison.

It must work standalone — no dependency on `backend/app/*`.

---

## Directory layout

```
llm-gateway/
├── pyproject.toml                         packaged as alphaforge-llm-gateway
├── README.md
├── src/alphaforge_llm_gateway/
│   ├── __init__.py                        barrel: LLMGateway, LLMResponse, QueryType
│   ├── gateway.py                         main entrypoint — from_env(), complete(), analyze_screener()
│   ├── router.py                          provider selection: by query_type, latency, cost, fallback
│   ├── rate_limiter.py                    per-provider quota tracker (in-memory + on-disk persistence)
│   ├── cost_guard.py                      hard cost wall — refuses requests that would exceed $0/day
│   ├── cli.py                             argparse CLI
│   ├── types.py                           QueryType, LLMResponse, ProviderStatus dataclasses/Pydantic
│   ├── exceptions.py                      LLMGatewayError, ProviderUnavailable, BudgetExceeded
│   ├── providers/
│   │   ├── __init__.py                    PROVIDERS registry
│   │   ├── base.py                        Provider ABC + capabilities
│   │   ├── gemini.py                      Gemini provider (free tier — Google AI Studio)
│   │   ├── groq.py                        Groq provider (free tier)
│   │   ├── huggingface.py                 HF Inference API
│   │   ├── openrouter.py                  OpenRouter (free models only)
│   │   └── ollama.py                      Local Ollama (always-free fallback)
│   └── prompts/
│       ├── analyze_screener.py            built-in prompt for screener analysis
│       └── explain_picks.py
├── tests/
│   ├── conftest.py                        mock httpx transport + recorded responses
│   ├── test_router.py
│   ├── test_rate_limiter.py
│   ├── test_cost_guard.py
│   └── providers/
│       ├── test_gemini.py
│       └── ...
├── notebooks/
│   └── llm_gateway_playground.ipynb       compare providers on the same prompt
└── docs/
    └── PROVIDERS.md                       per-provider setup + free-tier limits
```

---

## Layered architecture

```
                     ┌──────────────────────────┐
                     │    LLMGateway            │  ← public API
                     │  (gateway.py)            │
                     └────────┬─────────────────┘
                              ▼
                     ┌──────────────────────────┐
                     │    Router                │  pick provider per request
                     │  (router.py)             │
                     └──────┬─────────┬─────────┘
                            ▼         ▼
              ┌──────────────────┐  ┌──────────────────┐
              │  RateLimiter     │  │  CostGuard       │
              │  (per-provider)  │  │  ($0 hard wall)  │
              └────────┬─────────┘  └─────────┬────────┘
                       ▼                       ▼
                       └─────────┬────────────┘
                                 ▼
                       ┌──────────────────┐
                       │  Provider        │  thin async HTTP wrapper
                       │  (Gemini/Groq…)  │
                       └──────────────────┘
```

**Rule**: providers know nothing about routing or budgeting. The router calls them. The cost guard inspects responses (token counts) and rejects future requests if the rolling budget tips over.

---

## Module responsibilities

### `gateway.py` — the public API

Single entry point. The rest of the package is internal.

```python
class LLMGateway:
    @classmethod
    def from_env(cls) -> "LLMGateway":
        """Construct from env vars. Reads GEMINI_API_KEY, GROQ_API_KEY, etc."""

    async def complete(
        self,
        messages: list[Message],
        *,
        query_type: QueryType = QueryType.GENERAL,
        max_tokens: int | None = None,
    ) -> LLMResponse: ...

    async def analyze_screener(self, raw_output: str) -> LLMResponse: ...
    async def explain_picks(self, raw_output: str) -> LLMResponse: ...

    async def list_providers(self) -> list[ProviderStatus]: ...
    async def benchmark(self, prompt: str) -> list[BenchmarkResult]: ...
```

Rules:
- Every public method is `async`. Sync helpers live in `types.py`.
- Returns are dataclasses or Pydantic models — never plain dicts.
- No retries here — that's the router's job.

### `router.py` — provider selection

Routing strategy is data-driven, not hard-coded:

| Strategy | When |
|----------|------|
| `query_type → provider` map | Different providers excel at different tasks (Groq for fast / Gemini for context / Ollama for offline) |
| Health check | Skip providers returning 5xx in last 60 s |
| Quota | Skip providers over 80% of free-tier quota |
| Latency-aware | Among healthy providers, prefer the one with lowest p50 latency |
| Fallback chain | If primary fails, try next in fallback list |

```python
class Router:
    def __init__(self, providers: dict[str, Provider], policy: RoutingPolicy): ...

    async def pick(self, query_type: QueryType) -> Provider: ...
    async def execute(self, request: LLMRequest) -> LLMResponse: ...   # picks + retries
```

### `rate_limiter.py` — per-provider quota

In-memory counter with on-disk persistence (so quota survives process restart). One row per provider per day.

```python
class RateLimiter:
    def __init__(self, persistence_path: Path = Path(".llm_gateway/quota.json")): ...

    async def can_call(self, provider_slug: str) -> bool: ...
    async def record_call(self, provider_slug: str, tokens: int) -> None: ...
    async def remaining(self, provider_slug: str) -> dict[str, int]: ...
```

### `cost_guard.py` — the $0 wall

The reason this gateway exists. **Every** provider must declare its free tier; the gateway refuses to route any request whose accumulated cost (from response token counts × provider price) would push total monthly spend above zero.

```python
class CostGuard:
    def __init__(self, monthly_budget_usd: float = 0.0): ...

    def check(self, provider: Provider, est_tokens: int) -> None:
        """Raises BudgetExceeded if this call would tip the rolling budget."""

    def record(self, response: LLMResponse) -> None: ...
```

> If you ever want to allow a paid provider, raise the budget — never bypass the guard.

### `providers/`

One module per provider, all extending `Provider` ABC:

```python
class Provider(ABC):
    slug: str
    label: str
    is_local: bool
    cost_per_1k_input_usd: float    # 0.0 for free-tier
    cost_per_1k_output_usd: float

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse: ...

    @abstractmethod
    async def health(self) -> ProviderHealth: ...
```

Concrete providers **only** translate the request shape, call upstream, and translate the response. No business logic.

### `cli.py`

Argparse, one subcommand per top-level operation. Mirrors the public API of `LLMGateway` 1:1 so the CLI is a thin shell.

```bash
python -m alphaforge_llm_gateway providers
python -m alphaforge_llm_gateway chat
python -m alphaforge_llm_gateway analyze-screener -f picks.txt
python -m alphaforge_llm_gateway benchmark
```

### `prompts/`

Prompt templates as Python modules (not raw strings) so they're testable and version-controlled. Each module exports a `build(...)` function.

```python
# prompts/analyze_screener.py
def build(raw_output: str) -> list[Message]: ...
```

---

## Cross-cutting conventions

### No paid SDKs

`httpx.AsyncClient` only. No `openai`, no `anthropic`, no `google-cloud-aiplatform`. We hit the free REST surface directly so the gateway has no path to silently drift onto a paid plan.

### Dependency on `alphaforge-logger`

Use `from alphaforge_logger import get_logger`. Module names mirror the dotted path (`gateway`, `router`, `providers.gemini`).

### Response shape

Always:

```python
@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_used: int
    latency_ms: int
    cost: float                # USD; 0.0 on free tier
```

The `cost` field is non-negotiable — it's how `CostGuard` does its accounting.

### Errors

```python
class LLMGatewayError(Exception): ...
class ProviderUnavailable(LLMGatewayError): ...
class BudgetExceeded(LLMGatewayError): ...
class QuotaExceeded(LLMGatewayError): ...
```

Backend route handlers translate these into HTTP responses (`502`, `429`, `402`).

---

## Testing

```
tests/
├── conftest.py            # mock httpx transport, recorded fixtures
├── test_router.py         # routing decisions for every query_type
├── test_rate_limiter.py   # quota math + persistence
├── test_cost_guard.py     # budget tripwire scenarios
└── providers/
    ├── test_gemini.py     # request shape, response parsing, error mapping
    └── …
```

- **No live network calls.** Use `httpx.MockTransport` with recorded fixtures (`tests/fixtures/<provider>/<scenario>.json`).
- Tests for free tier limits assert that the right provider is **avoided** at 80%+ utilisation.
- One test file per provider, mirroring the source layout.

---

## Anti-patterns

- ❌ Calling a provider directly from `gateway.py` — always go through the router.
- ❌ Importing a provider's SDK (paid or free). Stick to `httpx`.
- ❌ Returning plain dicts from public methods.
- ❌ Mutable module-level provider instances. The gateway owns them; tests construct their own.
- ❌ Logging full request/response bodies. They contain user prompts. Log the slug + token count + latency only.

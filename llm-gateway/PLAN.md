# LLM Gateway: Free Multi-Provider LLM Integration

> **Disclaimer: NOT SEBI registered investment advice. All AI-generated financial analysis is for personal research only.**

## TL;DR

Build a **standalone, publishable Python package** (`alphaforge-llm-gateway`) at the repo root — independent of the backend, usable in **three modes**: (1) **standalone CLI** for direct terminal execution (analyze screener output, benchmark models, check provider status), (2) **library import** consumed by any Python consumer (backend FastAPI routes, screener CLI, future services), and (3) **interactive Jupyter notebook** for exploratory analysis, provider comparison, and step-by-step financial research. Integrates **5 free LLM providers** (Google Gemini, Groq, HuggingFace, OpenRouter, Ollama) through a unified async interface, with smart query routing, automatic fallback chains, per-provider rate limiting, zero-cost guardrails, and an auto-benchmarking system to rank which model performs best for each query type.

**Key insight**: All 5 providers support OpenAI-compatible chat completions API → use the `openai` Python SDK with `base_url` override as the single unified client. No provider-specific SDKs needed.

**Architecture — three execution paths, one codebase**:
- **CLI mode**: `python -m alphaforge_llm_gateway <command>` — standalone scripts for terminal use, piping (`scan.py | llm-gateway analyze-screener`), and cron automation. No backend or server required.
- **Library mode**: `llm-gateway/` → consumed by `backend/` as `file:///` path dep → thin wrapper wires to Pydantic settings → FastAPI routes expose to frontend. Screener also imports directly as a library.
- **Notebook mode**: `llm-gateway/notebooks/llm_gateway_playground.ipynb` — interactive Jupyter notebook for hands-on provider testing, side-by-side model comparison, screener output analysis, and benchmarking with inline visualizations. Follows `screener/notebooks/screener_pipeline.ipynb` pattern.

---

## Free Providers ($0 Forever, No Credit Card Required)

| Provider | Best Free Models | Rate Limits (Free Tier) | Key Required | OpenAI-compatible |
|----------|-----------------|------------------------|--------------|-------------------|
| **Google Gemini** | Gemini 2.5 Pro, 2.5 Flash, 2.5 Flash-Lite, Gemma 4 | ~15 RPM, varies by model | Yes (free from aistudio.google.com) | Yes (via generativelanguage endpoint) |
| **Groq** | Llama 3.3 70B, Llama 4 Scout 17B, Qwen3 32B, Kimi K2 | 30–60 RPM, 1K–14K RPD | Yes (free account at console.groq.com) | Yes |
| **HuggingFace** | Qwen 2.5 72B, Mistral, Llama (serverless inference) | Rate-limited, generous free tier | Yes (free token from huggingface.co) | Yes (via /v1/chat/completions) |
| **OpenRouter** | Models tagged `:free` (Gemma, Qwen, Llama variants) | Varies per model | Yes (free key for $0 models) | Yes |
| **Ollama** (local) | Any model user downloads (Qwen 2.5 7B, Llama 3.1 8B, etc.) | Unlimited (runs locally) | No | Yes (localhost:11434/v1) |

### Provider Selection Rationale

- **Gemini**: Best free quality — 2.5 Pro/Flash are frontier-class with generous free tier. Excellent at structured data and tables (screener output).
- **Groq**: Fastest inference (~10× faster than cloud). Llama 3.3 70B and Qwen3 32B are strong for financial reasoning.
- **HuggingFace**: Access to largest open model catalog. Serverless inference means no infrastructure.
- **OpenRouter**: Aggregator with transparent pricing — easy to filter strictly to $0 models.
- **Ollama**: Local fallback — unlimited, private, works offline. User controls model selection.

### Free Tier Data Note

Gemini and Groq free tiers may use request data to improve their products. Acceptable for personal use. Ollama is fully private (local execution).

---

## Phase 1: Package Scaffold & Core Types

**Directory**: `llm-gateway/`

### 1.1 — Package Configuration (`pyproject.toml`)

- Follows `packages/logger-py/pyproject.toml` pattern exactly
- `name = "alphaforge-llm-gateway"`, `requires-python = ">=3.14"`
- PDM backend with `distribution = true` for publishability
- Runtime dependencies: `openai>=1.50.0`, `httpx>=0.27.0`
- Dev dependencies: `pytest>=8.3.0`, `pytest-asyncio>=0.24.0`, `ruff>=0.6.0`

### 1.2 — Type Definitions (`types.py`)

Core enums and dataclasses used throughout the package:

| Type | Kind | Fields / Values |
|------|------|-----------------|
| `LLMProvider` | Enum | GEMINI, GROQ, HUGGINGFACE, OPENROUTER, OLLAMA |
| `QueryType` | Enum | SCREENER_ANALYSIS, STOCK_EXPLANATION, CHAT, SENTIMENT, TECHNICAL_SUMMARY |
| `LLMResponse` | Dataclass | content, model, provider, tokens_used, latency_ms, cost (always 0.0) |
| `ProviderConfig` | Dataclass | name, base_url, api_key, models, rate_limits, is_local |
| `RateLimits` | Dataclass | rpm, tpm, rpd, tpd |
| `CostGuardError` | Exception | Raised when a request would incur cost |

### 1.3 — Abstract Provider Interface (`base.py`)

Follows `backend/app/services/broker_base.py` ABC pattern:

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages, model, temperature, max_tokens) -> LLMResponse: ...

    @abstractmethod
    async def health_check(self) -> bool: ...

    @abstractmethod
    def available_models(self) -> list[str]: ...
```

Includes concrete `_call_openai()` helper method — shared by all providers — that wraps the `openai.AsyncOpenAI` client with the provider's `base_url` and `api_key`. This is the key unification point.

---

## Phase 2: Provider Implementations

**Directory**: `llm-gateway/src/alphaforge_llm_gateway/providers/`

### 2.1 — Google Gemini (`gemini.py`)

- `base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"`
- Default model: `gemini-2.5-flash` (best free speed/quality ratio)
- Available models: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemma-4`
- Free-tier enforcement: uses standard tier endpoint only (no billing account needed)
- Configurable via `GEMINI_API_KEY` env var or constructor arg

### 2.2 — Groq (`groq.py`)

- `base_url = "https://api.groq.com/openai/v1"`
- Default model: `llama-3.3-70b-versatile`
- Available models: `llama-3.3-70b-versatile`, `meta-llama/llama-4-scout-17b-16e-instruct`, `qwen/qwen3-32b`, `moonshotai/kimi-k2-instruct`
- Parses `x-ratelimit-remaining-requests` and `x-ratelimit-remaining-tokens` response headers to update rate limiter in real-time
- Configurable via `GROQ_API_KEY` env var

### 2.3 — HuggingFace (`huggingface.py`)

- `base_url = "https://router.huggingface.co/v1"`
- Default model: `Qwen/Qwen2.5-72B-Instruct`
- Serverless inference — no infrastructure to manage
- Configurable via `HUGGINGFACE_API_KEY` env var

### 2.4 — OpenRouter (`openrouter.py`)

- `base_url = "https://openrouter.ai/api/v1"`
- On initialization: fetches model list via `GET /api/v1/models`, hard-filters to models where `pricing.prompt == "0"` AND `pricing.completion == "0"`
- Caches the free model list; refreshes every 24 hours
- **Rejects any non-free model at request time** — never incurs cost
- Includes `HTTP-Referer` and `X-Title` headers per OpenRouter requirements
- Configurable via `OPENROUTER_API_KEY` env var

### 2.5 — Ollama (`ollama.py`)

- `base_url` configurable (default: `http://localhost:11434/v1`)
- Auto-detects available models via `GET /api/tags` at startup
- `health_check()` returns `False` gracefully if Ollama is not running (no crash)
- Recommended models for 16GB Mac: Qwen 2.5 7B, Llama 3.1 8B, Mistral Nemo 12B
- Configurable via `OLLAMA_BASE_URL` env var

---

## Phase 3: Rate Limiting & Cost Guardrails

### 3.1 — Rate Limiter (`rate_limiter.py`)

Per-provider token bucket with pre-configured free-tier limits:

| Provider | RPM | RPD | TPM | TPD |
|----------|-----|-----|-----|-----|
| Gemini (2.5 Flash) | 15 | 1,500 | 1,000,000 | 50,000,000 |
| Groq (Llama 3.3 70B) | 30 | 1,000 | 12,000 | 100,000 |
| HuggingFace | 10 | 1,000 | — | — |
| OpenRouter (free models) | 10 | 200 | — | — |
| Ollama | ∞ | ∞ | ∞ | ∞ |

Key features:
- `async def acquire(provider, estimated_tokens) -> bool` — returns `False` if request would exceed limit
- `def remaining(provider) -> dict[str, int]` — expose remaining quota for status endpoint
- Auto-resets counters on minute/day boundaries
- In-memory by default (dict-based); constructor accepts optional Redis client for future scaling
- Groq: dynamically updates limits from `x-ratelimit-*` response headers

### 3.2 — Cost Guard (`cost_guard.py`)

Ensures absolutely $0 cost:

- `def validate_request(provider, model) -> bool` — pre-request check before every LLM call
- **OpenRouter**: verifies model exists in the cached free model list
- **Gemini**: confirms using standard (free) tier endpoint, not paid
- **All providers**: confirms within rate limits (exceeding limits ≠ cost, but signals degraded service)
- Raises `CostGuardError` if a request would incur cost
- Logs warning at >80% rate limit consumption

**Zero-cost wall**: If all free providers are exhausted (rate-limited), the gateway returns an error — it **never** falls through to a paid tier.

---

## Phase 4: Smart Router & Prompts

### 4.1 — Intelligent Query Router (`router.py`)

Maps `QueryType` → ranked fallback chain of `(LLMProvider, model_name)`:

| QueryType | Priority 1 | Priority 2 | Priority 3 | Rationale |
|-----------|-----------|-----------|-----------|-----------|
| `SCREENER_ANALYSIS` | Gemini 2.5 Flash | Groq Llama 3.3 70B | Ollama | Gemini excels at tabular data interpretation |
| `STOCK_EXPLANATION` | Gemini 2.5 Pro | Groq Qwen3 32B | HuggingFace Qwen 72B | Pro-tier reasoning for SHAP explanation translation |
| `CHAT` | Groq Llama 3.3 70B | Gemini 2.5 Flash | Ollama | Groq's speed advantage for conversational use |
| `SENTIMENT` | Gemini 2.5 Flash-Lite | Groq Llama 4 Scout | HuggingFace | Flash-Lite is fastest for simple classification |
| `TECHNICAL_SUMMARY` | Gemini 2.5 Flash | Groq Qwen3 32B | Ollama | Good balance of speed and quality for summaries |

**Fallback behavior**: If the primary provider is rate-limited or unreachable, the router automatically cascades to the next provider in the chain. No user intervention needed.

The routing table is a plain `dict` — can be overridden programmatically or updated by the auto-benchmarking system.

### 4.2 — Domain-Specific Prompt Templates (`prompts.py`)

| Prompt | Use Case | Key Instructions |
|--------|----------|------------------|
| `SCREENER_SYSTEM_PROMPT` | Analyzing `scan.py` output (picks table) | "Interpret this screener output. Identify strongest signals. Reference specific numbers." |
| `EXPLAIN_SYSTEM_PROMPT` | Interpreting SHAP explanations from `explain.py` | "Translate these SHAP-based signal explanations into plain English. Highlight highest-conviction picks." |
| `STOCK_ANALYSIS_PROMPT` | Comprehensive stock analysis | "Provide technical + fundamental analysis. Cover trend, momentum, volume, support/resistance." |
| `SENTIMENT_PROMPT` | Market/stock sentiment analysis | "Analyze sentiment. Classify as bullish/bearish/neutral with confidence." |

All prompts include the mandatory disclaimer: **"NOT SEBI registered investment advice. For personal research only."**

All prompts are importable constants — consumers can use them directly or override with custom prompts.

---

## Phase 5: Gateway Class & Public API (Library Mode)

### 5.1 — LLMGateway (`gateway.py`)

The main entry point — a single class that ties everything together:

```python
class LLMGateway:
    def __init__(self, gemini_key=None, groq_key=None, hf_key=None,
                 openrouter_key=None, ollama_url=None): ...

    @classmethod
    def from_env(cls) -> "LLMGateway": ...

    async def complete(self, query_type, messages, **kwargs) -> LLMResponse: ...
    async def analyze_screener(self, raw_output: str) -> LLMResponse: ...
    async def explain_picks(self, raw_output: str) -> LLMResponse: ...
    async def providers_status(self) -> list[dict]: ...
```

- Auto-registers providers based on which API keys are provided (skip providers without keys)
- `from_env()` reads env vars: `GEMINI_API_KEY`, `GROQ_API_KEY`, `HUGGINGFACE_API_KEY`, `OPENROUTER_API_KEY`, `OLLAMA_BASE_URL`
- `complete()` delegates to the router which handles fallback logic
- `analyze_screener()` / `explain_picks()` are convenience methods that inject the appropriate system prompt from `prompts.py`
- `providers_status()` returns health + remaining quota per registered provider

### 5.2 — Public API (`__init__.py`)

Clean barrel export:

```python
from alphaforge_llm_gateway.gateway import LLMGateway
from alphaforge_llm_gateway.types import LLMResponse, LLMProvider, QueryType, CostGuardError

__all__ = ["LLMGateway", "LLMResponse", "LLMProvider", "QueryType", "CostGuardError"]
```

Consumer usage:

```python
from alphaforge_llm_gateway import LLMGateway, QueryType

gateway = LLMGateway.from_env()
response = await gateway.complete(QueryType.SCREENER_ANALYSIS, [
    {"role": "user", "content": raw_screener_output}
])
print(response.content)  # Structured analysis
print(response.provider)  # Which provider handled it
print(response.cost)      # Always 0.0
```

---

## Phase 6: CLI Interface (Standalone Mode)

The gateway ships with a full CLI — runnable as `python -m alphaforge_llm_gateway` — for standalone terminal use without requiring the backend, FastAPI, or any server.

### 6.1 — Entry Point (`__main__.py`)

```python
"""Allow `python -m alphaforge_llm_gateway <command>` invocation."""
from alphaforge_llm_gateway.cli import main

if __name__ == "__main__":
    main()
```

### 6.2 — CLI Application (`cli.py`)

Uses `argparse` (stdlib — no extra dependency) with subcommands:

| Subcommand | Description | Example |
|------------|-------------|---------|
| `analyze-screener` | Analyze screener output (stdin or file) | `python -m alphaforge_llm_gateway analyze-screener < picks.txt` |
| `explain-picks` | Translate SHAP explanations to plain English | `python -m alphaforge_llm_gateway explain-picks -f shap_output.txt` |
| `chat` | Interactive single-turn or piped chat | `echo "What is RSI?" \| python -m alphaforge_llm_gateway chat` |
| `benchmark` | Run auto-benchmark across all providers | `python -m alphaforge_llm_gateway benchmark` |
| `providers` | Show provider health & remaining quota | `python -m alphaforge_llm_gateway providers` |
| `complete` | Raw completion with explicit query type | `python -m alphaforge_llm_gateway complete --type SENTIMENT "RELIANCE is breaking out"` |

**Common flags** (all subcommands):

| Flag | Description | Default |
|------|-------------|---------|
| `--provider` | Force a specific provider (skip router) | Auto-routed |
| `--model` | Force a specific model | Provider default |
| `--json` | Output raw JSON (`LLMResponse` dict) | Human-readable text |
| `--no-disclaimer` | Suppress disclaimer in output | Disclaimer shown |
| `--env-file` | Path to `.env` file for API keys | Auto-detect `.env` in cwd / repo root |

### 6.3 — stdin / File Input

All analysis subcommands accept input via stdin (for piping) or `-f <file>` flag:

```bash
# Pipe from screener scan
cd screener && python -m live.scan 2>/dev/null | python -m alphaforge_llm_gateway analyze-screener

# Pipe from explain
python -m live.explain 2>/dev/null | python -m alphaforge_llm_gateway explain-picks

# From file
python -m alphaforge_llm_gateway analyze-screener -f screener/live/picks/weekly_picks.txt

# Interactive chat
python -m alphaforge_llm_gateway chat
> What does high RSI with low volume mean?
```

### 6.4 — Output Formatting

- **Human mode** (default): Formatted Markdown output to terminal with disclaimer footer
- **JSON mode** (`--json`): Full `LLMResponse` as JSON — machine-parseable, suitable for further piping

```bash
# Human-readable
python -m alphaforge_llm_gateway analyze-screener < picks.txt
# → Formatted analysis with disclaimer

# JSON for scripting
python -m alphaforge_llm_gateway analyze-screener --json < picks.txt | jq '.content'
```

### 6.5 — Async Execution

The CLI internally uses `asyncio.run()` to bridge sync CLI entry → async gateway:

```python
def main():
    args = parse_args()
    asyncio.run(_run(args))

async def _run(args):
    gateway = LLMGateway.from_env(env_file=args.env_file)
    # dispatch to subcommand handler...
```

### 6.6 — Shell Aliases (Convenience)

Suggested aliases for `~/.zshrc` (documented in README.md):

```bash
alias llm='python -m alphaforge_llm_gateway'
alias llm-screener='python -m alphaforge_llm_gateway analyze-screener'
alias llm-explain='python -m alphaforge_llm_gateway explain-picks'
alias llm-chat='python -m alphaforge_llm_gateway chat'
alias llm-providers='python -m alphaforge_llm_gateway providers'
```

---

## Phase 7: Interactive Notebook (Notebook Mode)

**Directory**: `llm-gateway/notebooks/`

Follows the `screener/notebooks/screener_pipeline.ipynb` pattern — a single interactive notebook that exposes the full gateway functionality for exploratory use.

### 7.1 — Notebook: `llm_gateway_playground.ipynb`

Narrative flow with interleaved markdown + code cells:

| Section | Cells | Description |
|---------|-------|-------------|
| **Title + Disclaimer** | 1 md | Title, description, SEBI disclaimer |
| **Setup & Imports** | 1 md + 1 code | `sys.path` setup, import `LLMGateway`, `QueryType`, configure env |
| **1 — Provider Status** | 1 md + 1 code | Initialize gateway, display provider health + remaining quota as table |
| **2 — Single Completion** | 1 md + 2 code | Pick a query type, send a prompt, display formatted response with metadata (provider, model, latency, tokens) |
| **3 — Analyze Screener Output** | 1 md + 2 code | Load `screener/live/picks/weekly_picks.txt` (or paste inline), run `gateway.analyze_screener()`, display analysis |
| **4 — Explain SHAP Picks** | 1 md + 2 code | Load SHAP explanation output, run `gateway.explain_picks()`, display plain-English translation |
| **5 — Side-by-Side Provider Comparison** | 1 md + 2 code | Same prompt sent to all available providers, results displayed in a comparison table (content preview, latency, tokens, model) |
| **6 — Interactive Chat** | 1 md + 1 code | Cell with input prompt widget — type a question, get a response, run cell again for next question |
| **7 — Run Benchmark** | 1 md + 2 code | Execute full benchmark suite, display per-QueryType rankings as formatted table + bar chart (matplotlib) |
| **8 — Rate Limit Dashboard** | 1 md + 1 code | Show remaining quota per provider after all above calls — visual gauge of free tier consumption |
| **9 — Custom Prompt Playground** | 1 md + 1 code | Editable system prompt + user message — test any prompt against any provider/model with `--provider` and `--model` overrides |
| **Quick Run** | 1 md + 1 code | Single cell that runs: provider check → analyze latest screener picks → explain picks → comparison table |
| **Total** | **~30 cells** | |

### 7.2 — Async in Notebook

Jupyter natively supports `await` in cells (via `IPython.core.async_helpers`). The notebook uses `await` directly — no `asyncio.run()` wrapper needed:

```python
# Cell — works directly in Jupyter
from alphaforge_llm_gateway import LLMGateway, QueryType

gateway = LLMGateway.from_env()
response = await gateway.analyze_screener(open("../screener/live/picks/weekly_picks.txt").read())
print(response.content)
```

### 7.3 — Visualization Helpers

The notebook includes inline helper functions (not part of the package — notebook-only) for:
- **Comparison table**: Side-by-side provider responses using `IPython.display.HTML`
- **Latency bar chart**: `matplotlib` bar chart comparing response times per provider
- **Benchmark heatmap**: QueryType × Provider score matrix using `matplotlib` + colors
- **Quota gauges**: Simple progress bars showing remaining rate limits per provider

These use only `matplotlib` (already in `.venv` via screener deps) and `IPython.display` (comes with Jupyter).

### 7.4 — Dev Dependencies

Add to `llm-gateway/pyproject.toml` dev dependencies:
```toml
[tool.pdm.dev-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.6.0",
]
notebook = [
    "jupyter>=1.0.0",
    "matplotlib>=3.9.0",
]
```

Note: `jupyter` and `matplotlib` are **dev-only / notebook-only** — not required for CLI or library mode.

---

## Phase 8: Auto-Benchmarking System

### 8.1 — Benchmark Engine (`benchmark.py`)

Evaluates all available providers against predefined test cases per `QueryType`:

**Test cases** (stored in `benchmark_data/`):
- `screener_output.txt` — snapshot of real `scan.py` output (top 10 picks table)
- `shap_explanation.txt` — snapshot of real `explain.py` output (SHAP attributions)
- `rubrics.json` — evaluation criteria per query type

**Scoring method** (hybrid):

| Method | Weight | What It Checks |
|--------|--------|----------------|
| LLM-as-judge | 60% | Gemini 2.5 Pro scores other models' responses on quality, accuracy, helpfulness |
| Heuristic checks | 40% | Disclaimer present? Numbers referenced correctly? Response length appropriate? Financial terms used correctly? |

**Output**: `BenchmarkReport` with per-provider, per-query-type scores. Auto-updates the routing table in `router.py` to reflect actual measured performance.

**CLI**: `python -m alphaforge_llm_gateway benchmark` (uses the CLI from Phase 6)

### 8.2 — Test Fixtures (`benchmark_data/`)

| File | Content |
|------|---------|
| `screener_output.txt` | Sample weekly picks table with RANK, SYMBOL, PROBABILITY, SIGNAL, RSI, volume, MACD, ADX, etc. |
| `shap_explanation.txt` | Sample SHAP signal explanations for 5 picks with feature attributions |
| `rubrics.json` | Evaluation rubrics: `{"SCREENER_ANALYSIS": {"must_reference_numbers": true, "must_include_disclaimer": true, "min_length": 200, ...}}` |

---

## Phase 9: Backend Integration (Thin Wrapper)

The backend consumes the gateway package via a thin wrapper — identical to how `backend/app/core/logging.py` wraps the `alphaforge-logger` package.

### 9.1 — Dependency Declaration (`backend/pyproject.toml`)

```toml
"alphaforge-llm-gateway @ file:///${PROJECT_ROOT}/../llm-gateway",
```

### 9.2 — Thin Wrapper (`backend/app/services/llm_gateway.py`)

```python
from alphaforge_llm_gateway import LLMGateway
from app.core.config import settings

_gateway: LLMGateway | None = None

def get_gateway() -> LLMGateway:
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway(
            gemini_key=settings.gemini_api_key,
            groq_key=settings.groq_api_key,
            # ... other keys from settings
        )
    return _gateway
```

### 9.3 — Configuration (`backend/app/core/config.py`)

New settings (all with empty defaults — providers without keys are skipped):

| Setting | Env Var | Default |
|---------|---------|---------|
| `gemini_api_key` | `GEMINI_API_KEY` | `""` |
| `groq_api_key` | `GROQ_API_KEY` | `""` |
| `huggingface_api_key` | `HUGGINGFACE_API_KEY` | `""` |
| `openrouter_api_key` | `OPENROUTER_API_KEY` | `""` |
| `ollama_base_url` | `OLLAMA_BASE_URL` | `"http://localhost:11434"` |

### 9.4 — FastAPI Routes (`backend/app/routes/llm.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/llm/complete` | Generic completion — accepts `query_type` + `messages` |
| `POST` | `/llm/analyze-screener` | Accepts raw screener output, returns analysis |
| `POST` | `/llm/explain-picks` | Accepts SHAP explanation output, returns plain English |
| `GET` | `/llm/providers` | List providers with health status + remaining quota |
| `GET` | `/llm/benchmark` | Get latest benchmark results |
| `POST` | `/llm/benchmark/run` | Trigger benchmark run (FastAPI background task) |

### 9.5 — Wire Existing AI Service  (`backend/app/services/ai_service.py`)

Replace existing TODO stubs:
- `chat()` → `gateway.complete(QueryType.CHAT, messages)`
- `analyze_stock()` → `gateway.complete(QueryType.STOCK_EXPLANATION, ...)`
- `sentiment_analysis()` → `gateway.complete(QueryType.SENTIMENT, ...)`

---

## Phase 10: Frontend Integration

### 10.1 — API Client (`frontend/src/lib/api.ts`)

```typescript
export const llmApi = {
    complete: (queryType: string, messages: { role: string; content: string }[]) =>
        api.post("/llm/complete", { query_type: queryType, messages }),
    analyzeScreener: (output: string) =>
        api.post("/llm/analyze-screener", { raw_output: output }),
    explainPicks: (output: string) =>
        api.post("/llm/explain-picks", { raw_output: output }),
    getProviders: () => api.get("/llm/providers"),
    getBenchmark: () => api.get("/llm/benchmark"),
};
```

### 10.2 — React Query Hooks (`frontend/src/lib/queries.ts`)

| Hook | Type | Endpoint |
|------|------|----------|
| `useAnalyzeScreener()` | Mutation | `/llm/analyze-screener` |
| `useExplainPicks()` | Mutation | `/llm/explain-picks` |
| `useLLMProviders()` | Query | `/llm/providers` |
| `useBenchmarkResults()` | Query | `/llm/benchmark` |

---

## Phase 11: Screener Direct Integration

The screener can use the gateway in **two ways** — CLI piping or library import:

### CLI Piping (no code changes needed)

```bash
# Pipe scan output directly to LLM analysis
cd screener && python -m live.scan 2>/dev/null | python -m alphaforge_llm_gateway analyze-screener

# Pipe SHAP explanations to LLM translation
python -m live.explain 2>/dev/null | python -m alphaforge_llm_gateway explain-picks

# JSON output for further processing
python -m live.scan | python -m alphaforge_llm_gateway analyze-screener --json | jq '.content'

# Analyze saved picks file
python -m alphaforge_llm_gateway analyze-screener -f screener/live/picks/weekly_picks.txt
```

### Library Import (for programmatic use)

```python
# In screener/live/explain.py
from alphaforge_llm_gateway import LLMGateway

gateway = LLMGateway.from_env()
response = await gateway.explain_picks(format_explanations(explanations))
```

Add to `screener/requirements.txt`:
```
alphaforge-llm-gateway @ file:///path/to/llm-gateway
```

---

## Phase 12: Makefile & Setup Integration

New Makefile targets:
- `llm-gateway-install` — install llm-gateway package into .venv via PDM
- `llm-gateway-test` — run llm-gateway test suite
- `llm-providers` — shortcut for `python -m alphaforge_llm_gateway providers`
- `llm-benchmark` — shortcut for `python -m alphaforge_llm_gateway benchmark`

Update `setup.sh` with `--llm-gateway` flag.

---

## Module Structure

```
llm-gateway/                                  # Root-level, alongside screener/, backend/
├── pyproject.toml                            # PDM publishable package config
├── README.md                                 # Usage docs + disclaimer
├── PLAN.md                                   # This file
├── implement.txt                             # Implementation tracker
├── notebooks/
│   └── llm_gateway_playground.ipynb           # Interactive notebook (provider comparison, analysis, benchmarks)
├── src/
│   └── alphaforge_llm_gateway/
│       ├── __init__.py                       # Public API: LLMGateway, LLMResponse, QueryType
│       ├── __main__.py                       # `python -m alphaforge_llm_gateway` entry point
│       ├── cli.py                            # argparse CLI: subcommands, stdin/file input, JSON output
│       ├── types.py                          # Enums + dataclasses
│       ├── base.py                           # BaseLLMProvider ABC + shared _call_openai()
│       ├── gateway.py                        # Main LLMGateway class — entry point
│       ├── router.py                         # Smart routing + fallback chains
│       ├── rate_limiter.py                   # Per-provider token bucket rate limiter
│       ├── cost_guard.py                     # Zero-cost enforcement ($0 wall)
│       ├── prompts.py                        # Financial domain prompt templates
│       ├── benchmark.py                      # Auto-benchmarking + routing table update
│       ├── benchmark_data/                   # Test fixtures for benchmarking
│       │   ├── screener_output.txt           # Sample scan.py output snapshot
│       │   ├── shap_explanation.txt          # Sample explain.py output snapshot
│       │   └── rubrics.json                  # Evaluation criteria per query type
│       └── providers/
│           ├── __init__.py                   # Barrel export: all provider classes
│           ├── gemini.py                     # Google Gemini free tier
│           ├── groq.py                       # Groq free tier (fastest inference)
│           ├── huggingface.py                # HuggingFace serverless inference
│           ├── openrouter.py                 # OpenRouter free-only models
│           └── ollama.py                     # Local Ollama (private, unlimited)
└── tests/
    ├── test_gateway.py                       # Gateway class + from_env() + provider registration
    ├── test_providers.py                     # Mock openai client, test each provider
    ├── test_router.py                        # Fallback chain + cascade behavior
    ├── test_rate_limiter.py                  # Token bucket + counter reset
    └── test_cost_guard.py                    # CostGuardError on paid models
```

---

## Integration with AlphaForge

| Existing File | Action |
|---|---|
| `backend/pyproject.toml` | Add `alphaforge-llm-gateway @ file:///` dependency |
| `backend/app/core/config.py` | Add 5 new env vars for API keys |
| `backend/app/services/ai_service.py` | Wire TODO stubs to gateway |
| `backend/app/routes/__init__.py` | Register new `llm_router` at `/llm` |
| `backend/.env.example` | Add env var templates |
| `frontend/src/lib/api.ts` | Add `llmApi` namespace |
| `frontend/src/lib/queries.ts` | Add React Query hooks |
| `screener/requirements.txt` | Add path dependency |
| `Makefile` | Add `llm-gateway-install`, `llm-gateway-test` targets |

---

## Verification Checklist

- [ ] `cd llm-gateway && pdm run pytest -v` — all mock-based tests pass
- [ ] `cd backend && pdm install` — gateway installs as local dependency
- [ ] `python -c "from alphaforge_llm_gateway import LLMGateway, QueryType, LLMResponse"` — import works
- [ ] `python -m alphaforge_llm_gateway providers` — CLI lists provider health + quota
- [ ] `echo "test" | python -m alphaforge_llm_gateway chat` — CLI piped input works
- [ ] `python -m alphaforge_llm_gateway analyze-screener -f picks.txt` — CLI file input works
- [ ] `python -m alphaforge_llm_gateway analyze-screener --json < picks.txt | jq .` — JSON output valid
- [ ] `python -m alphaforge_llm_gateway benchmark` — produces per-QueryType ranking
- [ ] `curl http://localhost:8000/api/v1/llm/providers` — lists providers with health status
- [ ] Set one API key → `POST /api/v1/llm/complete` → response with `cost=0.0` + disclaimer
- [ ] Configure OpenRouter with paid model → `CostGuardError` raised
- [ ] Mock Gemini as rate-limited → verify auto-cascade to Groq
- [ ] `cd screener && python -m live.scan | python -m alphaforge_llm_gateway analyze-screener` — piping works
- [ ] `cd screener && python -c "from alphaforge_llm_gateway import LLMGateway"` — works independently
- [ ] Open `llm-gateway/notebooks/llm_gateway_playground.ipynb` in Jupyter — all cells run without error
- [ ] Notebook: provider status cell shows table of available providers
- [ ] Notebook: side-by-side comparison cell shows responses from multiple providers
- [ ] Notebook: benchmark cell produces ranking table + bar chart
- [ ] `cd llm-gateway && pdm run ruff check .` — no lint errors
- [ ] `cd frontend && pnpm type-check` — no type errors
- [ ] All AI responses include "NOT SEBI registered investment advice" disclaimer
- [ ] `cost` field in every `LLMResponse` is `0.0`

---

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Location | Root-level `llm-gateway/` (not `packages/` or `backend/`) | Same level as `screener/` — standalone module, not a UI package or backend submodule |
| Dual-mode execution | CLI (`python -m`) + library import | CLI for terminal/piping/cron; library for backend API + screener programmatic use |
| Notebook mode | Interactive Jupyter notebook in `notebooks/` | Follows screener notebook pattern; exploratory analysis, provider comparison, inline viz |
| Notebook deps | `jupyter` + `matplotlib` as dev-only deps | Not required for CLI or library mode — keeps core package lightweight |
| CLI framework | `argparse` (stdlib) | Zero extra dependencies; sufficient for subcommands + flags |
| Package pattern | Publishable Python package (PDM) | Follows `alphaforge-logger` pattern — reusable by any consumer |
| Client library | Single `openai` SDK for all providers | All 5 providers are OpenAI-compatible — no provider-specific SDKs needed |
| Backend consumption | Thin wrapper (same as `logging.py` wrapping `alphaforge-logger`) | Keeps package independent, backend just wires to settings |
| Rate limiter | In-memory (dict-based), Redis-upgradable | Sufficient for personal use; constructor accepts optional Redis client |
| Cost enforcement | Hard $0 wall (`CostGuardError`) | If all providers exhausted, return error — never fall to paid tier |
| Routing strategy | Heuristic defaults + benchmark-updated | Smart defaults out of the box, automatically refined by measured performance |
| Benchmarking | LLM-as-judge (Gemini Pro) + heuristic checks | Gemini Pro is free and capable; bias acknowledged for personal ranking |
| Screener integration | Direct import (no backend required) | `screener/` can use the gateway independently for CLI workflows |

---

## Scope

### Included
- 5 free LLM providers with unified interface
- **CLI mode**: `python -m alphaforge_llm_gateway <command>` with subcommands (analyze-screener, explain-picks, chat, benchmark, providers, complete)
- **Library mode**: async Python API for programmatic use (backend, screener, scripts)
- **Notebook mode**: `llm_gateway_playground.ipynb` for interactive exploration, provider comparison, benchmarking with inline visualizations
- stdin/file piping for Unix-style composition (`scan.py | llm-gateway analyze-screener`)
- Smart query routing with automatic fallback chains
- Per-provider rate limiting with free-tier enforcement
- Zero-cost guardrails (hard $0 wall)
- Auto-benchmarking system for model ranking
- FastAPI routes + frontend hooks
- Screener direct integration (CLI piping + library import)
- Domain-specific financial prompt templates

### Excluded (Future Iterations)
- Streaming responses (v2 — requires SSE/WebSocket)
- Conversation memory / RAG (separate feature)
- Fine-tuning / LoRA inference
- WebSocket live chat
- Embedding models
- Image/multimodal capabilities

---

## Disclaimers

- **Not SEBI registered investment advice** — all AI outputs must carry this disclaimer
- AI-generated analysis may contain errors, hallucinations, or outdated information
- LLM outputs should never be the sole basis for trading decisions
- Free tier providers may use request data to improve their products (except Ollama)
- Rate limits and free tier availability may change without notice — the gateway handles this gracefully via fallback chains
- The auto-benchmarking system provides relative rankings, not absolute quality guarantees

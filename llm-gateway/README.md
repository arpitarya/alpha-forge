# alphaforge-llm-gateway

Free multi-provider LLM gateway for AlphaForge — unified async interface with smart routing, automatic fallback, and zero-cost guardrails.

> **⚠️ NOT SEBI registered investment advice. All AI-generated financial analysis is for personal research only.**

## Providers (All Free, No Credit Card)

| Provider | Best Models | Rate Limits |
|----------|-------------|-------------|
| **Google Gemini** | Gemini 2.5 Flash/Pro, Gemma 4 | 15 RPM |
| **Groq** | Llama 3.3 70B, Qwen3 32B | 30 RPM |
| **HuggingFace** | Qwen 2.5 72B | 10 RPM |
| **OpenRouter** | Free-tagged models only | 10 RPM |
| **Ollama** | Local models (unlimited) | ∞ |

## Usage

### Library Mode

```python
from alphaforge_llm_gateway import LLMGateway, QueryType

gateway = LLMGateway.from_env()
response = await gateway.complete(QueryType.CHAT, [
    {"role": "user", "content": "What is RSI?"}
])
print(response.content)   # Analysis text
print(response.provider)  # Which provider handled it
print(response.cost)      # Always 0.0
```

### CLI Mode

```bash
# Provider status
python -m alphaforge_llm_gateway providers

# Analyze screener output
python -m alphaforge_llm_gateway analyze-screener -f picks.txt

# Pipe from screener
python -m live.scan | python -m alphaforge_llm_gateway analyze-screener

# Interactive chat
python -m alphaforge_llm_gateway chat

# Benchmark all providers
python -m alphaforge_llm_gateway benchmark
```

### Notebook Mode

Open `notebooks/llm_gateway_playground.ipynb` for interactive exploration.

## Environment Variables

```bash
GEMINI_API_KEY=       # From aistudio.google.com
GROQ_API_KEY=         # From console.groq.com
HUGGINGFACE_API_KEY=  # From huggingface.co
OPENROUTER_API_KEY=   # From openrouter.ai
OLLAMA_BASE_URL=      # Default: http://localhost:11434
```

## Install

```bash
# As library (backend consumes via pyproject.toml)
pip install -e ./llm-gateway

# Or via Makefile
just llm-gateway-install
```

## Architecture

- Single `openai` SDK for all providers (OpenAI-compatible APIs)
- Smart query routing with automatic provider fallback
- Per-provider rate limiting with free-tier enforcement
- Hard $0 cost wall — `CostGuardError` if any paid model requested
- Auto-benchmarking system for model ranking

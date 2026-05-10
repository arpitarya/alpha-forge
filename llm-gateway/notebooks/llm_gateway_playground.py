# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
# ---

# %% [markdown]
# # LLM Gateway Playground
#
# Interactive notebook for testing the AlphaForge LLM Gateway — explore providers, compare models, analyze screener output, and run benchmarks.
#
# **⚠️ Disclaimer**: NOT SEBI registered investment advice. All AI-generated financial analysis is for personal research only.

# %% [markdown]
# ## Setup & Imports

# %%
import sys
from pathlib import Path

# Add llm-gateway src to path
ROOT = Path.cwd().parent
sys.path.insert(0, str(ROOT / "src"))

from alphaforge_llm_gateway import LLMGateway, QueryType, LLMResponse

# Initialize from env
gateway = LLMGateway.from_env()
print("Gateway initialized")

# %% [markdown]
# ## 1 — Provider Status

# %%
statuses = await gateway.providers_status()
for s in statuses:
    health = "✅" if s["healthy"] else "❌"
    local = " (local)" if s["is_local"] else ""
    print(f"{health} {s['provider']}{local} — {s['default_model']} — {len(s['models'])} models — {s['utilization_pct']}% used")

# %% [markdown]
# ## 2 — Single Completion

# %%
query_type = QueryType.CHAT
prompt = "What does a high RSI with declining volume typically indicate for Indian equities?"

# %%
response = await gateway.complete(query_type, [{"role": "user", "content": prompt}])
print(f"Provider: {response.provider.value} | Model: {response.model}")
print(f"Latency: {response.latency_ms:.0f}ms | Tokens: {response.tokens_used} | Cost: ${response.cost}")
print("---")
print(response.content)

# %% [markdown]
# ## 3 — Analyze Screener Output

# %%
# Load screener picks (from file or paste inline)
picks_path = Path("../../screener/live/picks")
picks_files = sorted(picks_path.glob("*.txt")) if picks_path.exists() else []

if picks_files:
    screener_text = picks_files[-1].read_text()
    print(f"Loaded: {picks_files[-1].name}")
else:
    # Fallback to benchmark data
    screener_text = (ROOT / "src" / "alphaforge_llm_gateway" / "benchmark_data" / "screener_output.txt").read_text()
    print("Using benchmark sample data")
print(screener_text[:500])

# %%
analysis = await gateway.analyze_screener(screener_text)
print(f"[{analysis.provider.value}/{analysis.model}] {analysis.latency_ms:.0f}ms")
print("---")
print(analysis.content)

# %% [markdown]
# ## 4 — Explain SHAP Picks

# %%
shap_text = (ROOT / "src" / "alphaforge_llm_gateway" / "benchmark_data" / "shap_explanation.txt").read_text()
print(shap_text[:500])

# %%
explanation = await gateway.explain_picks(shap_text)
print(f"[{explanation.provider.value}/{explanation.model}] {explanation.latency_ms:.0f}ms")
print("---")
print(explanation.content)

# %% [markdown]
# ## 5 — Side-by-Side Provider Comparison

# %%
from alphaforge_llm_gateway.types import LLMProvider

comparison_prompt = "Analyze RELIANCE: RSI 62.3, MACD +2.15, ADX 28.4, Volume 1.52x avg. Is this a buy?"
results = []

for provider_name, prov in gateway._providers.items():
    try:
        r = await gateway.complete(
            QueryType.TECHNICAL_SUMMARY,
            [{"role": "user", "content": comparison_prompt}],
            provider=provider_name,
        )
        results.append(r)
    except Exception as e:
        print(f"  {provider_name.value}: FAILED — {e}")

for r in results:
    print(f"\n{'='*60}")
    print(f"{r.provider.value}/{r.model} — {r.latency_ms:.0f}ms — {r.tokens_used} tokens")
    print(f"{'='*60}")
    print(r.content[:500])

# %% [markdown]
# ## 6 — Interactive Chat

# %%
# Type your question below and run this cell
question = "What sectors look strong in the current Indian market?"

chat_response = await gateway.complete(QueryType.CHAT, [{"role": "user", "content": question}])
print(f"[{chat_response.provider.value}] {chat_response.latency_ms:.0f}ms")
print(chat_response.content)

# %% [markdown]
# ## 7 — Run Benchmark

# %%
from alphaforge_llm_gateway.benchmark import run_benchmark

report_text = await run_benchmark(gateway)
print(report_text)

# %%
# Benchmark as JSON for further analysis
import json
report_json = await run_benchmark(gateway, json_output=True)
report_data = json.loads(report_json)

# Bar chart of scores
try:
    import matplotlib.pyplot as plt
    labels = [f"{r['provider']}/{r['query_type']}" for r in report_data['results']]
    scores = [r['heuristic_score'] for r in report_data['results']]
    plt.figure(figsize=(12, 6))
    plt.barh(labels, scores, color='#22d3ee')
    plt.xlabel('Score')
    plt.title('LLM Gateway Benchmark Results')
    plt.tight_layout()
    plt.show()
except ImportError:
    print("matplotlib not installed — skipping chart")

# %% [markdown]
# ## 8 — Rate Limit Dashboard

# %%
statuses = await gateway.providers_status()
print("Rate Limit Status After All Calls")
print("=" * 50)
for s in statuses:
    print(f"\n{s['provider']} — Utilization: {s['utilization_pct']}%")
    for k, v in s['remaining'].items():
        print(f"  {k}: {v}")

# %% [markdown]
# ## 9 — Custom Prompt Playground

# %%
# Edit these and run
custom_system = "You are a quant researcher analyzing Indian equity momentum strategies."
custom_message = "Compare RSI and MACD as momentum indicators for NIFTY 50 stocks."

response = await gateway.complete(
    QueryType.CHAT,
    [
        {"role": "system", "content": custom_system},
        {"role": "user", "content": custom_message},
    ],
)
print(f"[{response.provider.value}/{response.model}] {response.latency_ms:.0f}ms")
print(response.content)

# %% [markdown]
# ## Quick Run
# Single cell: provider check → analyze screener → explain picks → comparison

# %%
print("1. Provider Status")
for s in await gateway.providers_status():
    h = "✅" if s["healthy"] else "❌"
    print(f"  {h} {s['provider']}")

print("\n2. Screener Analysis")
sample = (ROOT / "src" / "alphaforge_llm_gateway" / "benchmark_data" / "screener_output.txt").read_text()
a = await gateway.analyze_screener(sample)
print(f"  [{a.provider.value}] {a.latency_ms:.0f}ms — {a.content[:200]}...")

print("\n3. SHAP Explanation")
shap = (ROOT / "src" / "alphaforge_llm_gateway" / "benchmark_data" / "shap_explanation.txt").read_text()
e = await gateway.explain_picks(shap)
print(f"  [{e.provider.value}] {e.latency_ms:.0f}ms — {e.content[:200]}...")

print("\nDone! ⚠️ NOT SEBI registered investment advice.")

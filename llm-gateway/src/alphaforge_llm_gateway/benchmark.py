"""Auto-benchmarking system — evaluates providers per QueryType."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

from alphaforge_llm_gateway.types import LLMProvider, LLMResponse, QueryType

logger = logging.getLogger("alphaforge.llm.benchmark")

BENCHMARK_DATA_DIR = Path(__file__).parent / "benchmark_data"


@dataclass
class BenchmarkResult:
    """Result for a single provider/query_type evaluation."""

    provider: LLMProvider
    model: str
    query_type: QueryType
    latency_ms: float
    tokens_used: int
    heuristic_score: float  # 0-100
    content_preview: str = ""


@dataclass
class BenchmarkReport:
    """Full benchmark report across all providers and query types."""

    results: list[BenchmarkResult] = field(default_factory=list)
    timestamp: str = ""

    def rankings(self, query_type: QueryType) -> list[BenchmarkResult]:
        """Return results for a query type, sorted by score descending."""
        filtered = [r for r in self.results if r.query_type == query_type]
        return sorted(filtered, key=lambda r: r.heuristic_score, reverse=True)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "results": [
                {
                    "provider": r.provider.value,
                    "model": r.model,
                    "query_type": r.query_type.value,
                    "latency_ms": r.latency_ms,
                    "tokens_used": r.tokens_used,
                    "heuristic_score": r.heuristic_score,
                    "content_preview": r.content_preview[:200],
                }
                for r in self.results
            ],
        }


def _load_test_data() -> dict[str, str]:
    """Load benchmark test fixtures."""
    data: dict[str, str] = {}

    screener_file = BENCHMARK_DATA_DIR / "screener_output.txt"
    if screener_file.exists():
        data["screener"] = screener_file.read_text()

    shap_file = BENCHMARK_DATA_DIR / "shap_explanation.txt"
    if shap_file.exists():
        data["shap"] = shap_file.read_text()

    return data


def _load_rubrics() -> dict:
    """Load evaluation rubrics."""
    rubrics_file = BENCHMARK_DATA_DIR / "rubrics.json"
    if rubrics_file.exists():
        return json.loads(rubrics_file.read_text())
    return {}


def _score_response(response: LLMResponse, query_type: QueryType, rubrics: dict) -> float:
    """Heuristic scoring of a response (0-100)."""
    score = 0.0
    content = response.content.lower()

    # Base score for non-empty response
    if len(response.content) > 50:
        score += 20

    # Length appropriateness
    min_len = rubrics.get(query_type.value, {}).get("min_length", 100)
    if len(response.content) >= min_len:
        score += 15

    # Disclaimer present
    if rubrics.get(query_type.value, {}).get("must_include_disclaimer", True):
        if "not sebi" in content or "disclaimer" in content or "personal research" in content:
            score += 15

    # References numbers (for analysis types)
    if rubrics.get(query_type.value, {}).get("must_reference_numbers", False):
        import re

        numbers = re.findall(r"\d+\.?\d*", response.content)
        if len(numbers) >= 3:
            score += 15

    # Financial terms used
    financial_terms = ["rsi", "macd", "adx", "volume", "momentum", "trend", "support", "resistance"]
    term_count = sum(1 for t in financial_terms if t in content)
    score += min(term_count * 5, 20)

    # Latency bonus (faster = better)
    if response.latency_ms < 2000:
        score += 15
    elif response.latency_ms < 5000:
        score += 10
    elif response.latency_ms < 10000:
        score += 5

    return min(score, 100)


async def run_benchmark(
    gateway: object,  # LLMGateway — avoid circular import
    json_output: bool = False,
) -> str:
    """Run benchmark across all available providers."""
    from alphaforge_llm_gateway.gateway import LLMGateway

    if not isinstance(gateway, LLMGateway):
        return "Error: Invalid gateway instance"

    test_data = _load_test_data()
    rubrics = _load_rubrics()

    report = BenchmarkReport(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
    )

    # Test prompts per query type
    test_prompts: dict[QueryType, str] = {
        QueryType.SCREENER_ANALYSIS: test_data.get(
            "screener",
            "Analyze: RELIANCE RSI=65, MACD=2.1, ADX=28, Volume 1.5x avg. "
            "INFY RSI=42, MACD=-0.5, ADX=15, Volume 0.8x avg.",
        ),
        QueryType.STOCK_EXPLANATION: test_data.get(
            "shap",
            "SHAP explanation for RELIANCE: RSI_14 contribution=+0.15, "
            "MACD_hist=+0.08, Vol_SMA_ratio=+0.12, dist_52w_high=-0.05.",
        ),
        QueryType.CHAT: "What does a high RSI with declining volume typically indicate?",
        QueryType.SENTIMENT: "NIFTY up 1.2%, banking sector leads. FII buying $200M.",
        QueryType.TECHNICAL_SUMMARY: (
            "TCS: Price 3850, RSI 58, MACD +3.2, ADX 22, "
            "Volume 1.1x avg, 52W high 4100, 52W low 3200."
        ),
    }

    for query_type, prompt in test_prompts.items():
        chain = gateway._router.get_fallback_chain(query_type)

        for provider_enum, model in chain:
            prov = gateway._providers.get(provider_enum)
            if not prov:
                continue

            resolved_model = model or prov.default_model()
            try:
                response = await gateway.complete(
                    query_type,
                    [{"role": "user", "content": prompt}],
                    provider=provider_enum,
                    model=resolved_model,
                )
                score = _score_response(response, query_type, rubrics)
                report.results.append(BenchmarkResult(
                    provider=provider_enum,
                    model=response.model,
                    query_type=query_type,
                    latency_ms=response.latency_ms,
                    tokens_used=response.tokens_used,
                    heuristic_score=score,
                    content_preview=response.content[:200],
                ))
                logger.info(
                    "Benchmark %s/%s on %s: score=%.0f, latency=%.0fms",
                    provider_enum.value, resolved_model, query_type.value,
                    score, response.latency_ms,
                )
            except Exception as e:
                logger.warning(
                    "Benchmark failed for %s/%s on %s: %s",
                    provider_enum.value, resolved_model, query_type.value, e,
                )
                report.results.append(BenchmarkResult(
                    provider=provider_enum,
                    model=resolved_model,
                    query_type=query_type,
                    latency_ms=0,
                    tokens_used=0,
                    heuristic_score=0,
                    content_preview=f"ERROR: {e}",
                ))

    if json_output:
        return json.dumps(report.to_dict(), indent=2)

    # Format as table
    lines = [
        f"LLM Gateway Benchmark Report — {report.timestamp}",
        "=" * 70,
    ]
    for qt in QueryType:
        rankings = report.rankings(qt)
        if not rankings:
            continue
        lines.append(f"\n{qt.value}")
        lines.append("-" * 50)
        for i, r in enumerate(rankings, 1):
            lines.append(
                f"  {i}. {r.provider.value}/{r.model} — "
                f"Score: {r.heuristic_score:.0f} | "
                f"Latency: {r.latency_ms:.0f}ms | "
                f"Tokens: {r.tokens_used}"
            )

    return "\n".join(lines)

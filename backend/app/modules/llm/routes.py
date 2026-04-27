"""LLM Gateway endpoints — multi-provider AI completion for financial analysis."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.core.logging import get_logger
from app.modules.llm.service import get_gateway

router = APIRouter()
logger = get_logger("routes.llm")


# ── Request / Response Models ─────────────────────────────────────────────────


class ChatMessage(BaseModel):
    role: str
    content: str


class CompleteRequest(BaseModel):
    query_type: str = "chat"
    messages: list[ChatMessage]
    provider: str | None = None
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 2048


class AnalyzeRequest(BaseModel):
    raw_output: str


class LLMResponseModel(BaseModel):
    content: str
    model: str
    provider: str
    tokens_used: int
    latency_ms: float
    cost: float


# ── Benchmark state ───────────────────────────────────────────────────────────

_latest_benchmark: dict | None = None


# ── Routes ────────────────────────────────────────────────────────────────────


@router.post("/complete", response_model=LLMResponseModel)
async def complete(request: CompleteRequest):
    """Generic LLM completion with smart routing.

    Disclaimer: Not SEBI registered investment advice.
    """
    from alphaforge_llm_gateway.types import LLMProvider, QueryType

    gateway = get_gateway()
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    provider = LLMProvider(request.provider) if request.provider else None
    query_type = QueryType(request.query_type)

    logger.info("LLM complete: type=%s, provider=%s", request.query_type, request.provider)

    response = await gateway.complete(
        query_type,
        messages,
        provider=provider,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )

    return LLMResponseModel(
        content=response.content,
        model=response.model,
        provider=response.provider.value,
        tokens_used=response.tokens_used,
        latency_ms=response.latency_ms,
        cost=response.cost,
    )


@router.post("/analyze-screener", response_model=LLMResponseModel)
async def analyze_screener(request: AnalyzeRequest):
    """Analyze screener output using the best available LLM.

    Disclaimer: Not SEBI registered investment advice.
    """
    gateway = get_gateway()
    logger.info("LLM analyze-screener: %d chars", len(request.raw_output))
    response = await gateway.analyze_screener(request.raw_output)

    return LLMResponseModel(
        content=response.content,
        model=response.model,
        provider=response.provider.value,
        tokens_used=response.tokens_used,
        latency_ms=response.latency_ms,
        cost=response.cost,
    )


@router.post("/explain-picks", response_model=LLMResponseModel)
async def explain_picks(request: AnalyzeRequest):
    """Translate SHAP explanations to plain English.

    Disclaimer: Not SEBI registered investment advice.
    """
    gateway = get_gateway()
    logger.info("LLM explain-picks: %d chars", len(request.raw_output))
    response = await gateway.explain_picks(request.raw_output)

    return LLMResponseModel(
        content=response.content,
        model=response.model,
        provider=response.provider.value,
        tokens_used=response.tokens_used,
        latency_ms=response.latency_ms,
        cost=response.cost,
    )


@router.get("/providers")
async def list_providers():
    """List all configured providers with health status and remaining quota."""
    gateway = get_gateway()
    return await gateway.providers_status()


@router.get("/benchmark")
async def get_benchmark():
    """Get the latest benchmark results."""
    if _latest_benchmark is None:
        return {"message": "No benchmark run yet. POST /llm/benchmark/run to start one."}
    return _latest_benchmark


@router.post("/benchmark/run")
async def run_benchmark_endpoint(background_tasks: BackgroundTasks):
    """Trigger a benchmark run in the background."""
    background_tasks.add_task(_run_benchmark)
    return {"message": "Benchmark started in background. GET /llm/benchmark for results."}


async def _run_benchmark() -> None:
    """Background task to run the benchmark."""
    global _latest_benchmark  # noqa: PLW0603
    from alphaforge_llm_gateway.benchmark import run_benchmark

    gateway = get_gateway()
    import json

    result = await run_benchmark(gateway, json_output=True)
    _latest_benchmark = json.loads(result)
    logger.info("Benchmark completed: %d results", len(_latest_benchmark.get("results", [])))

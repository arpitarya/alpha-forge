"""Benchmark endpoints — kicks off a background run, exposes the latest result."""

from __future__ import annotations

import json

from fastapi import APIRouter, BackgroundTasks

from app.core.logging import get_logger
from app.modules.llm.llm_service import get_gateway

router = APIRouter()
logger = get_logger("routes.llm.benchmark")

_latest: dict | None = None


@router.get("")
async def get_benchmark():
    if _latest is None:
        return {"message": "No benchmark run yet. POST /llm/benchmark/run to start one."}
    return _latest


@router.post("/run")
async def run_benchmark_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_benchmark)
    return {"message": "Benchmark started in background. GET /llm/benchmark for results."}


async def _run_benchmark() -> None:
    global _latest  # noqa: PLW0603
    from alphaforge_llm_gateway.benchmark import run_benchmark

    result = await run_benchmark(get_gateway(), json_output=True)
    _latest = json.loads(result)
    logger.info("Benchmark completed: %d results", len(_latest.get("results", [])))

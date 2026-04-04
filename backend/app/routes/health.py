"""Health check endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("routes.health")


@router.get("/health")
async def health_check():
    logger.debug("Health check hit")
    return {"status": "healthy", "service": "alphaforge-api"}

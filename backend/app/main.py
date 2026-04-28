"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.modules import api_router

logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("AlphaForge starting up (env=%s)", settings.app_env)

    from app.modules.memory.embedding_service import get_embedding_service
    embed_svc = get_embedding_service()
    logger.info("Embedding service ready (model=%s)", settings.embedding_model)

    yield

    await embed_svc.close()
    logger.info("AlphaForge shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AI-powered financial analysis & trading platform for Indian markets",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()

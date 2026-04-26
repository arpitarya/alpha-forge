"""Central route registry — all API routers are mounted here."""

from __future__ import annotations

from fastapi import APIRouter

from app.routes.ai import router as ai_router
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.health import router as health_router
from app.routes.llm import router as llm_router
from app.routes.market import router as market_router
from app.routes.portfolio import router as portfolio_router
from app.routes.screener import router as screener_router
from app.routes.trade import router as trade_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(market_router, prefix="/market", tags=["market"])
api_router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(trade_router, prefix="/trade", tags=["trade"])
api_router.include_router(screener_router, prefix="/screener", tags=["screener"])
api_router.include_router(llm_router, prefix="/llm", tags=["llm"])

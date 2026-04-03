"""Portfolio management endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Holding(BaseModel):
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    pnl: float
    pnl_pct: float


class PortfolioSummary(BaseModel):
    total_invested: float
    current_value: float
    total_pnl: float
    total_pnl_pct: float
    holdings: list[Holding]


@router.get("/summary", response_model=PortfolioSummary)
async def portfolio_summary():
    """Get aggregated portfolio summary with all holdings."""
    # TODO: fetch from DB + broker sync
    return PortfolioSummary(
        total_invested=0,
        current_value=0,
        total_pnl=0,
        total_pnl_pct=0,
        holdings=[],
    )


@router.get("/positions")
async def open_positions():
    """List all open intraday and delivery positions."""
    # TODO: fetch from broker API
    return {"positions": []}


@router.get("/orders")
async def order_history():
    """List recent order history."""
    # TODO: fetch from broker API
    return {"orders": []}

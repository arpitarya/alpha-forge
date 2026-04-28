"""Pydantic schemas for screener endpoints."""

from __future__ import annotations

from pydantic import BaseModel


class ScreenerPick(BaseModel):
    symbol: str
    probability: float
    rank: int
    rsi_14: float | None = None
    macd_hist: float | None = None
    adx_14: float | None = None
    vol_sma_ratio: float | None = None
    dist_52w_high_pct: float | None = None


class PushPicksRequest(BaseModel):
    scan_date: str
    model_type: str = "lightgbm"
    picks: list[ScreenerPick]


class PicksResponse(BaseModel):
    scan_date: str
    model_type: str | None = None
    count: int
    picks: list[dict]

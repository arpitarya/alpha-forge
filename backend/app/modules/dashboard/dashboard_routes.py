"""Dashboard read-only feeds for the terminal home screen.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone

from fastapi import APIRouter

from app.modules.dashboard.dashboard_schemas import (
    BriefBlock,
    DashboardStats,
    RiskMeter,
    StatCard,
    TerminalBrief,
    TickerItem,
    WatchlistItem,
)
from app.modules.dashboard.dashboard_seed import BRIEF_SEED, TICKER_SEED, WATCHLIST_SEED

router = APIRouter()


@router.get("/ticker", response_model=list[TickerItem])
async def get_ticker():
    return [TickerItem(symbol=s, price=p, change=c, tone=t) for s, p, c, t in TICKER_SEED]


@router.get("/watchlist", response_model=list[WatchlistItem])
async def get_watchlist():
    return [
        WatchlistItem(symbol=s, sublabel=sub, price=p, change=c, tone=t)
        for s, sub, p, c, t in WATCHLIST_SEED
    ]


@router.get("/risk", response_model=RiskMeter)
async def get_risk():
    rng = random.Random(int(datetime.now().timestamp()) // 5)
    bars = [
        round(max(20.0, min(95.0, base + rng.uniform(-jit, jit))), 1)
        for base, jit in [(30, 8), (55, 8), (90, 4), (42, 8), (68, 8)]
    ]
    return RiskMeter(bars=bars, active_index=2, confidence=88.4)


@router.get("/brief", response_model=TerminalBrief)
async def get_brief():
    blocks = [BriefBlock(**b) for b in BRIEF_SEED]
    return TerminalBrief(blocks=blocks, generated_at=datetime.now(timezone.utc).isoformat())


@router.get("/stats", response_model=DashboardStats)
async def get_stats():
    return DashboardStats(
        net_worth=StatCard(
            label="Net Worth",
            value=12_845_000,
            delta="▲ 1.24% TODAY · +₹1,52,330",
            delta_tone="up",
            sparkline=[30, 28, 32, 25, 18, 22, 15, 8, 18, 10, 5],
        ),
        pnl_today=StatCard(
            label="Today's P&L",
            value=14_821,
            delta="12 positions · 8 up / 4 dn",
            delta_tone="up",
        ),
        confidence=StatCard(
            label="Confidence",
            value=88.4,
            delta="Orb pulse strong",
            delta_tone="accent",
        ),
    )

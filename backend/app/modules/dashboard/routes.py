"""Dashboard endpoints — aggregated read-only feeds for the terminal home screen.

Shapes mirror the Solar Terminal Hi-Fi mock so the frontend can render with a
single round-trip per panel. Until real broker integration lands, payloads are
seeded with deterministic mock data + a small ±jitter per request so the UI
animates believably during dev. Every payload includes a disclaimer.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("routes.dashboard")

DISCLAIMER = "Not SEBI registered investment advice."


# ── Models ────────────────────────────────────────────────────────────────────


class TickerItem(BaseModel):
    symbol: str
    price: str
    change: str
    tone: str  # "up" | "dn"


class WatchlistItem(BaseModel):
    symbol: str
    sublabel: str
    price: str
    change: str
    tone: str  # "up" | "dn"


class RiskMeter(BaseModel):
    bars: list[float]  # 0..100
    active_index: int
    confidence: float  # 0..100


class BriefBlock(BaseModel):
    title: str
    body: str
    cta: str
    accent: bool = False


class TerminalBrief(BaseModel):
    blocks: list[BriefBlock]
    generated_at: str
    disclaimer: str = DISCLAIMER


class StatCard(BaseModel):
    label: str
    value: float
    delta: str
    delta_tone: str  # "up" | "dn" | "neutral" | "accent"
    sparkline: list[float] | None = None


class DashboardStats(BaseModel):
    net_worth: StatCard
    pnl_today: StatCard
    confidence: StatCard
    disclaimer: str = DISCLAIMER


# ── Seed data (deterministic; jittered per call) ──────────────────────────────

_TICKER_SEED: list[tuple[str, str, str, str]] = [
    ("NIFTY 50", "22,147.40", "+0.42%", "up"),
    ("SENSEX", "72,880.15", "+0.51%", "up"),
    ("BANKNIFTY", "48,012.10", "−0.18%", "dn"),
    ("USD/INR", "83.41", "−0.04%", "dn"),
    ("BRENT", "91.22", "+1.12%", "up"),
    ("GOLD", "72,140", "+0.33%", "up"),
    ("NIFTYIT", "34,812.55", "+1.82%", "up"),
    ("RELIANCE", "2,914.05", "+1.24%", "up"),
    ("INFY", "1,612.30", "+0.82%", "up"),
    ("TCS", "3,962.70", "+0.21%", "up"),
    ("HDFCBANK", "1,488.10", "−0.44%", "dn"),
    ("BTC", "$64,281", "+2.40%", "up"),
    ("NVDA", "$894.20", "+1.82%", "up"),
]

_WATCHLIST_SEED: list[tuple[str, str, str, str, str]] = [
    ("RELIANCE", "NSE · Energy", "₹2,914.05", "+1.24%", "up"),
    ("INFY", "NSE · IT", "₹1,612.30", "+0.82%", "up"),
    ("HDFCBANK", "NSE · Banking", "₹1,488.10", "−0.44%", "dn"),
    ("TCS", "NSE · IT", "₹3,962.70", "+0.21%", "up"),
    ("NVDA", "NASDAQ · Semis", "$894.20", "+1.82%", "up"),
    ("BTC", "Crypto", "$64,281", "+2.40%", "up"),
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Routes ────────────────────────────────────────────────────────────────────


@router.get("/ticker", response_model=list[TickerItem])
async def get_ticker():
    """Rolling marquee of indices, FX, commodities, watchlist top movers."""
    return [
        TickerItem(symbol=s, price=p, change=c, tone=t) for s, p, c, t in _TICKER_SEED
    ]


@router.get("/watchlist", response_model=list[WatchlistItem])
async def get_watchlist():
    """User's watchlist with last price + day change."""
    return [
        WatchlistItem(symbol=s, sublabel=sub, price=p, change=c, tone=t)
        for s, sub, p, c, t in _WATCHLIST_SEED
    ]


@router.get("/risk", response_model=RiskMeter)
async def get_risk():
    """Confidence histogram + headline score."""
    rng = random.Random(int(datetime.now().timestamp()) // 5)
    bars = [
        round(max(20.0, min(95.0, 30 + rng.uniform(-8, 8))), 1),
        round(max(20.0, min(95.0, 55 + rng.uniform(-8, 8))), 1),
        round(max(20.0, min(95.0, 90 + rng.uniform(-4, 4))), 1),
        round(max(20.0, min(95.0, 42 + rng.uniform(-8, 8))), 1),
        round(max(20.0, min(95.0, 68 + rng.uniform(-8, 8))), 1),
    ]
    return RiskMeter(bars=bars, active_index=2, confidence=88.4)


@router.get("/brief", response_model=TerminalBrief)
async def get_brief():
    """Alpha Brief blocks for the left rail. Until LLM-backed, seeded copy."""
    blocks = [
        BriefBlock(
            title="Market Sentiment",
            body=(
                "System detects a bullish pivot in Nifty IT. Volume up 22% in APAC "
                "session; INFY leading the index."
            ),
            cta="Deep-dive",
            accent=True,
        ),
        BriefBlock(
            title="Risk Alert",
            body=(
                "Your banking hedge is over-extended versus target. Recommend "
                "trimming HDFCBANK by ~15%."
            ),
            cta="Rebalance",
        ),
        BriefBlock(
            title="Next Action",
            body=(
                "3 new signals in the ML screener — BHARTIARTL leads with "
                "confidence 0.91."
            ),
            cta="See screener",
        ),
    ]
    return TerminalBrief(blocks=blocks, generated_at=_now_iso())


@router.get("/stats", response_model=DashboardStats)
async def get_stats():
    """Three headline stat cards rendered above the orb."""
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

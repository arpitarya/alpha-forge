"""Deterministic seed data for the terminal dashboard panels.

Replaced by real broker integration once that lands.
"""

from __future__ import annotations

TICKER_SEED: list[tuple[str, str, str, str]] = [
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

WATCHLIST_SEED: list[tuple[str, str, str, str, str]] = [
    ("RELIANCE", "NSE · Energy", "₹2,914.05", "+1.24%", "up"),
    ("INFY", "NSE · IT", "₹1,612.30", "+0.82%", "up"),
    ("HDFCBANK", "NSE · Banking", "₹1,488.10", "−0.44%", "dn"),
    ("TCS", "NSE · IT", "₹3,962.70", "+0.21%", "up"),
    ("NVDA", "NASDAQ · Semis", "$894.20", "+1.82%", "up"),
    ("BTC", "Crypto", "$64,281", "+2.40%", "up"),
]

BRIEF_SEED = [
    {
        "title": "Market Sentiment",
        "body": (
            "System detects a bullish pivot in Nifty IT. Volume up 22% in APAC "
            "session; INFY leading the index."
        ),
        "cta": "Deep-dive",
        "accent": True,
    },
    {
        "title": "Risk Alert",
        "body": (
            "Your banking hedge is over-extended versus target. Recommend "
            "trimming HDFCBANK by ~15%."
        ),
        "cta": "Rebalance",
        "accent": False,
    },
    {
        "title": "Next Action",
        "body": (
            "3 new signals in the ML screener — BHARTIARTL leads with "
            "confidence 0.91."
        ),
        "cta": "See screener",
        "accent": False,
    },
]

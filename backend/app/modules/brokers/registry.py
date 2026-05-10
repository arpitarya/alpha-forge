"""Process-wide registry of broker sources.

Holds one BrokerSource instance per slug. State (cached holdings + last
sync timestamp) is in-memory; persistence to disk/DB is a layer above.

Each slug has a single primary source — preferring API where free, falling
back to CSV upload (the new API sources also implement `parse()` so the
`/sources/{slug}/upload` endpoint still works as a manual fallback).
"""

from __future__ import annotations

from app.modules.brokers.base import BrokerSource
from app.modules.brokers.zerodha_kite import ZerodhaKiteSource


def _build_sources() -> dict[str, BrokerSource]:
    instances: list[BrokerSource] = [
        ZerodhaKiteSource(),    # slug: zerodha
    ]
    return {s.slug: s for s in instances}


SOURCES: dict[str, BrokerSource] = _build_sources()


def get_source(slug: str) -> BrokerSource:
    src = SOURCES.get(slug)
    if not src:
        raise KeyError(f"Unknown broker source: {slug!r}")
    return src

"""Process-wide registry of broker sources.

Holds one BrokerSource instance per slug. State (cached holdings + last
sync timestamp) is in-memory; persistence to disk/DB is a layer above.
"""

from __future__ import annotations

from app.services.brokers.angel_one import AngelOneSource
from app.services.brokers.base import BrokerSource
from app.services.brokers.csv_sources import (
    DezervCSVSource,
    GrowwCSVSource,
    WintWealthCSVSource,
    ZerodhaCoinCSVSource,
    ZerodhaCSVSource,
)


def _build_sources() -> dict[str, BrokerSource]:
    instances: list[BrokerSource] = [
        ZerodhaCSVSource(),
        ZerodhaCoinCSVSource(),
        GrowwCSVSource(),
        DezervCSVSource(),
        WintWealthCSVSource(),
        AngelOneSource(),
    ]
    return {s.slug: s for s in instances}


SOURCES: dict[str, BrokerSource] = _build_sources()


def get_source(slug: str) -> BrokerSource:
    src = SOURCES.get(slug)
    if not src:
        raise KeyError(f"Unknown broker source: {slug!r}")
    return src

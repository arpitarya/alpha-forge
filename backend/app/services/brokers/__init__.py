"""Broker source plugins — pluggable adapters for each holdings provider.

Free-tier reality (as of 2026-04):

| Source         | Path        | Notes                                                |
|----------------|-------------|------------------------------------------------------|
| Zerodha        | CSV upload  | Console → Holdings → Download CSV. No free REST API. |
| Zerodha Coin   | CSV upload  | Coin → Statements → Holdings. Same constraint.       |
| Groww          | CSV upload  | Reports → Holdings → Export. No public API.          |
| Dezerv         | CSV upload  | App → Statements → Export holdings.                  |
| Wint Wealth    | CSV upload  | App → Investments → Export.                          |
| Angel One      | SmartAPI    | Free REST; needs API key + TOTP.                     |

Pluggable via the BrokerSource ABC so paid providers (Kite Connect, etc.)
slot in later without changing the aggregator or routes.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from app.services.brokers.aggregator import HoldingsAggregator
from app.services.brokers.angel_one import AngelOneSource
from app.services.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
)
from app.services.brokers.csv_sources import (
    DezervCSVSource,
    GrowwCSVSource,
    WintWealthCSVSource,
    ZerodhaCoinCSVSource,
    ZerodhaCSVSource,
)
from app.services.brokers.registry import SOURCES, get_source

__all__ = [
    "SOURCES",
    "AngelOneSource",
    "AssetClass",
    "BrokerSource",
    "DezervCSVSource",
    "GrowwCSVSource",
    "Holding",
    "HoldingsAggregator",
    "SourceKind",
    "SourceStatus",
    "WintWealthCSVSource",
    "ZerodhaCSVSource",
    "ZerodhaCoinCSVSource",
    "get_source",
]

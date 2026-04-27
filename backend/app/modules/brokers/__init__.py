"""Broker source plugins — pluggable adapters for each holdings provider.

Free-tier reality (as of 2026-04):

| Source         | Path                  | Notes                                              |
|----------------|-----------------------|----------------------------------------------------|
| Zerodha        | Web-login API         | Unofficial enctoken flow (Kite Connect is paid).   |
| Zerodha Coin   | Web-login API         | Reuses the Kite session.                           |
| Groww          | Reverse-engineered API| `/v1/api/...` bearer token after login.            |
| Angel One      | SmartAPI              | Free official REST; needs API key + TOTP.          |
| Wint Wealth    | OTP-bound API         | OTP-only login; cached JWT.                        |
| Dezerv         | CSV upload            | No public API.                                     |

CSV upload (`/sources/{slug}/upload`) remains as a manual fallback for every
source. Pluggable via the BrokerSource ABC so paid providers (Kite Connect,
etc.) slot in later without changing the aggregator or routes.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.brokers.angel_one import AngelOneSource
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
)
from app.modules.brokers.csv_sources import (
    DezervCSVSource,
    GrowwCSVSource,
    WintWealthCSVSource,
    ZerodhaCoinCSVSource,
    ZerodhaCSVSource,
)
from app.modules.brokers.groww import GrowwSource
from app.modules.brokers.registry import SOURCES, get_source
from app.modules.brokers.wint_wealth import WintWealthSource
from app.modules.brokers.zerodha_coin import ZerodhaCoinSource
from app.modules.brokers.zerodha_kite import ZerodhaKiteSource

__all__ = [
    "SOURCES",
    "AngelOneSource",
    "AssetClass",
    "BrokerSource",
    "DezervCSVSource",
    "GrowwCSVSource",
    "GrowwSource",
    "Holding",
    "HoldingsAggregator",
    "SourceKind",
    "SourceStatus",
    "WintWealthCSVSource",
    "WintWealthSource",
    "ZerodhaCSVSource",
    "ZerodhaCoinCSVSource",
    "ZerodhaCoinSource",
    "ZerodhaKiteSource",
    "get_source",
]

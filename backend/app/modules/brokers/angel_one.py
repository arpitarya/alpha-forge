"""Angel One SmartAPI — BrokerSource impl over the helper module.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.modules.brokers.angel_one_helper import (
    REQUIRED_ENV,
    env,
    login_and_fetch_holdings,
    map_holding,
)
from app.modules.brokers.base import BrokerSource, Holding, SourceKind, SourceStatus

logger = get_logger("brokers.angel_one")


class AngelOneSource(BrokerSource):
    slug = "angel-one"
    label = "Angel One (SmartAPI)"
    kind = SourceKind.API
    notes = (
        "Free SmartAPI tier — register at smartapi.angelbroking.com and set "
        "ANGEL_ONE_API_KEY / CLIENT_CODE / PASSWORD / TOTP_SECRET in .env"
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY

    async def fetch(self) -> list[Holding]:
        rows = await login_and_fetch_holdings()
        out = [map_holding(r, self.slug) for r in rows]
        logger.info("Angel One: fetched %d holdings", len(out))
        return out

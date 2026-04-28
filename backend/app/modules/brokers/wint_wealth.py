"""Wint Wealth — bond holdings via OTP-bound web/PWA API.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._http import load_session
from app.modules.brokers.base import BrokerSource, Holding, SourceKind, SourceStatus
from app.modules.brokers.wint_wealth_csv import WintWealthCSVSource as _WintCSV
from app.modules.brokers.wint_wealth_helper import (
    env,
    fetch_holdings_json,
    map_holding,
    send_otp,
    verify_otp,
)

logger = get_logger("brokers.wint_wealth")


class WintWealthSource(BrokerSource):
    slug = "wint-wealth"
    label = "Wint Wealth"
    kind = SourceKind.API
    notes = (
        "OTP-bound login. Call /sources/wint-wealth/start-login, then "
        "/sources/wint-wealth/otp with the code received."
    )

    def __init__(self) -> None:
        super().__init__()
        cached = load_session(self.slug)
        if cached.get("jwt"):
            self._status = SourceStatus.READY
        elif env("WINT_USER_ID"):
            self._status = SourceStatus.UNCONFIGURED

    async def start_login(self) -> dict[str, Any]:
        return await send_otp(self.slug)

    async def submit_otp(self, code: str) -> dict[str, Any]:
        await verify_otp(self.slug, code)
        self._status = SourceStatus.READY
        return {"verified": True}

    def parse(self, stream, filename=None):  # type: ignore[override]
        holdings = _WintCSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        jwt = load_session(self.slug).get("jwt")
        if not jwt:
            raise RuntimeError(
                "Wint Wealth not authenticated — POST /sources/wint-wealth/start-login first"
            )
        try:
            rows = await fetch_holdings_json(jwt, self.slug)
        except RuntimeError:
            self._status = SourceStatus.UNCONFIGURED
            raise
        out = [map_holding(r, self.slug) for r in rows]
        logger.info("Wint Wealth: fetched %d holdings", len(out))
        return out

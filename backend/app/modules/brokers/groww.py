"""Groww — equity + MF holdings via the reverse-engineered web API.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import httpx

from app.core.logging import get_logger
from app.modules.brokers._http import clear_session
from app.modules.brokers.base import BrokerSource, Holding, SourceKind, SourceStatus
from app.modules.brokers.groww_csv import GrowwCSVSource as _GrowwCSV
from app.modules.brokers.groww_helper import (
    MF_PATH,
    REQUIRED_ENV,
    STOCKS_PATH,
    acquire_token,
    env,
    get_with_auth,
)
from app.modules.brokers.groww_mapper import map_mf, map_stock

logger = get_logger("brokers.groww")


class GrowwSource(BrokerSource):
    slug = "groww"
    label = "Groww"
    kind = SourceKind.API
    notes = (
        "Reverse-engineered web API (free). Set GROWW_USER_ID / GROWW_PASSWORD "
        "(and GROWW_TOTP_SECRET if your account has MFA) in .env.cred."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY

    def parse(self, stream, filename=None):  # type: ignore[override]
        holdings = _GrowwCSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        async def _pull(token: str) -> list[Holding]:
            stocks = (await get_with_auth(STOCKS_PATH, token)).get("data") or []
            mfs = (await get_with_auth(MF_PATH, token)).get("data") or []
            return [map_stock(r) for r in stocks] + [map_mf(r) for r in mfs]

        try:
            token = await acquire_token()
            holdings = await _pull(token)
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 401:
                logger.warning("Groww: token expired, re-logging in")
                clear_session("groww")
                token = await acquire_token(force=True)
                holdings = await _pull(token)
            else:
                raise

        logger.info("Groww: fetched %d holdings", len(holdings))
        return holdings

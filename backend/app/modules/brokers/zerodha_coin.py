"""Zerodha Coin — mutual fund holdings.

Coin shares the Kite web session, so we reuse `acquire_enctoken()` from
zerodha_kite.py. The Coin web app calls `coin.zerodha.com/api/...` with the
same enctoken cookie.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.core.logging import get_logger
from app.modules.brokers._http import clear_session, make_client
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
)
from app.modules.brokers.csv_sources import ZerodhaCoinCSVSource as _CoinCSV
from app.modules.brokers.zerodha_kite import _REQUIRED, _env, acquire_enctoken

logger = get_logger("brokers.zerodha_coin")


_COIN_BASE = "https://coin.zerodha.com"
_HOLDINGS_PATH = "/api/dashboard/holdings"


async def _fetch_coin_holdings(enctoken: str) -> list[dict[str, Any]]:
    headers = {"Authorization": f"enctoken {enctoken}"}
    async with make_client(base_url=_COIN_BASE, headers=headers) as client:
        client.cookies.set("enctoken", enctoken, domain="coin.zerodha.com")
        res = await client.get(_HOLDINGS_PATH)
        if res.status_code == 401:
            raise httpx.HTTPStatusError("enctoken expired", request=res.request, response=res)
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    if payload.get("status") != "success":
        raise RuntimeError(f"Coin holdings failed: {payload.get('message') or payload}")
    data = payload.get("data") or {}
    if isinstance(data, dict):
        return list(data.get("holdings") or data.get("funds") or [])
    return list(data) if isinstance(data, list) else []


class ZerodhaCoinSource(BrokerSource):
    slug = "zerodha-coin"
    label = "Zerodha Coin"
    kind = SourceKind.API
    notes = "Reuses the Zerodha Kite session — same ZERODHA_* credentials."

    def __init__(self) -> None:
        super().__init__()
        if all(_env(k) for k in _REQUIRED):
            self._status = SourceStatus.READY

    def parse(self, stream, filename=None):  # type: ignore[override]
        holdings = _CoinCSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        try:
            enctoken = await acquire_enctoken()
            rows = await _fetch_coin_holdings(enctoken)
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 401:
                logger.warning("Coin: enctoken expired, re-logging in")
                clear_session("zerodha")
                enctoken = await acquire_enctoken(force=True)
                rows = await _fetch_coin_holdings(enctoken)
            else:
                raise

        out: list[Holding] = []
        for r in rows:
            units = float(r.get("units") or r.get("quantity") or 0)
            avg_nav = float(r.get("average_price") or r.get("avg_nav") or 0)
            ltp_nav = float(r.get("last_price") or r.get("nav") or 0)
            invested = units * avg_nav
            current = units * ltp_nav
            pnl = current - invested
            scheme = r.get("fund") or r.get("scheme") or r.get("name") or ""
            out.append(
                Holding(
                    source=self.slug,
                    asset_class=AssetClass.MUTUAL_FUND,
                    symbol=str(r.get("isin") or scheme[:24]),
                    name=scheme or None,
                    isin=r.get("isin"),
                    quantity=units,
                    avg_price=avg_nav,
                    last_price=ltp_nav,
                    invested=invested,
                    current_value=current,
                    pnl=pnl,
                    pnl_pct=(pnl / invested * 100) if invested else 0.0,
                )
            )
        logger.info("Zerodha Coin: fetched %d holdings", len(out))
        return out

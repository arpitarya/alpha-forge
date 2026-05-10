"""Zerodha Kite equity holdings — BrokerSource impl over the Playwright helper.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import httpx

from app.core.logging import get_logger
from app.modules.brokers._http import clear_session
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind, SourceStatus
from app.modules.brokers.zerodha_csv import ZerodhaCSVSource as _ZerodhaCSV
from app.modules.brokers.zerodha_dump import is_csv_fresh, live_csv_path, read_csv, write_csv
from app.modules.brokers.zerodha_kite_helper import (
    REQUIRED_ENV,
    acquire_enctoken,
    env,
    fetch_holdings_json,
)

logger = get_logger("brokers.zerodha_kite")

# Re-exports for sibling Zerodha sources (Coin) that want to share the session.
__all__ = ["ZerodhaKiteSource", "acquire_enctoken", "env", "REQUIRED_ENV"]


def _holding_from_row(r: dict, slug: str) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    invested = qty * avg
    current = qty * ltp
    pnl = current - invested
    return Holding(
        source=slug,
        asset_class=AssetClass.EQUITY,
        symbol=str(r.get("tradingsymbol") or "").upper(),
        isin=r.get("isin"),
        quantity=qty,
        avg_price=avg,
        last_price=ltp,
        invested=invested,
        current_value=current,
        pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
        exchange=r.get("exchange"),
    )


def _holding_from_csv(r: dict[str, str], slug: str) -> Holding:
    g = r.get
    return Holding(
        source=slug, asset_class=AssetClass.EQUITY,
        symbol=str(g("tradingsymbol") or "").upper(), isin=g("isin") or None,
        quantity=float(g("quantity") or 0), avg_price=float(g("average_price") or 0),
        last_price=float(g("last_price") or 0), invested=float(g("invested") or 0),
        current_value=float(g("current_value") or 0), pnl=float(g("pnl") or 0),
        pnl_pct=float(g("pnl_pct") or 0), exchange=g("exchange") or None,
    )


class ZerodhaKiteSource(BrokerSource):
    slug = "zerodha"
    label = "Zerodha (Kite)"
    kind = SourceKind.API
    notes = (
        "Manual login: log in to kite.zerodha.com inside the AlphaForge "
        "Chrome (started with --remote-debugging-port=9299). AlphaForge never "
        "stores your password or TOTP. Set ZERODHA_USER_ID in .env.cred.local."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(env(k) for k in REQUIRED_ENV):
            self._status = SourceStatus.READY

    def parse(self, stream, filename=None):  # type: ignore[override]
        holdings = _ZerodhaCSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        if is_csv_fresh():
            rows = read_csv()
            logger.info("Zerodha Kite: %d holdings from CSV cache", len(rows))
            return [_holding_from_csv(r, self.slug) for r in rows]
        try:
            enctoken = await acquire_enctoken()
            rows = await fetch_holdings_json(enctoken)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else None
            if status in (401, 403):
                logger.warning(
                    "Zerodha: auth rejected (%s) — clearing session, re-logging via Chrome CDP. "
                    "Ensure kite.zerodha.com is open and logged in.",
                    status,
                )
                clear_session("zerodha")
                enctoken = await acquire_enctoken(force=True)
                rows = await fetch_holdings_json(enctoken)
            else:
                raise
        write_csv(rows, live_csv_path())
        out = [_holding_from_row(r, self.slug) for r in rows]
        logger.info("Zerodha Kite: fetched %d holdings → cached to CSV", len(out))
        return out

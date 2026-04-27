"""Groww — equity + mutual fund holdings via the reverse-engineered web API.

Groww has no advertised public API, but its web app calls
`groww.in/v1/api/...` with a bearer access token issued at login. We hit
the same endpoints directly:

  POST  /v1/api/auth/v3/users/login          (email, password)            → access_token
  POST  /v1/api/auth/v3/users/login/mfa      (twofa)                      (if required)
  GET   /v1/api/stocks_data/v2/stocks/portfolio                           → equity holdings
  GET   /v1/api/mutual_funds/v1/portfolio                                 → MF holdings

The access token is cached on disk so subsequent syncs skip login.

Credentials (.env.cred):
  GROWW_USER_ID         (registered email)
  GROWW_PASSWORD
  GROWW_TOTP_SECRET     (optional; only if your account has TOTP MFA)

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.core.logging import get_logger
from app.modules.brokers._http import (
    clear_session,
    load_session,
    make_client,
    save_session,
)
from app.modules.brokers._otp import generate_totp
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
)
from app.modules.brokers.csv_sources import GrowwCSVSource as _GrowwCSV

logger = get_logger("brokers.groww")


_GROWW_BASE = "https://groww.in"
_LOGIN_PATH = "/v1/api/auth/v3/users/login"
_MFA_PATH = "/v1/api/auth/v3/users/login/mfa"
_STOCKS_PATH = "/v1/api/stocks_data/v2/stocks/portfolio"
_MF_PATH = "/v1/api/mutual_funds/v1/portfolio"

_REQUIRED = ("GROWW_USER_ID", "GROWW_PASSWORD")


def _env(key: str) -> str:
    return os.getenv(key, "").strip()


async def _login() -> str:
    email = _env("GROWW_USER_ID")
    password = _env("GROWW_PASSWORD")
    totp_secret = _env("GROWW_TOTP_SECRET")

    missing = [k for k in _REQUIRED if not _env(k)]
    if missing:
        raise RuntimeError(f"Groww credentials missing: {', '.join(missing)}")

    async with make_client(base_url=_GROWW_BASE) as client:
        r1 = await client.post(
            _LOGIN_PATH,
            json={"username": email, "password": password},
        )
        r1.raise_for_status()
        d1: dict[str, Any] = r1.json()

        token = d1.get("access_token") or d1.get("authToken")
        mfa_token = d1.get("mfa_token") or d1.get("mfaToken")
        if token:
            return str(token)

        if not mfa_token:
            raise RuntimeError(f"Groww login response unrecognised: {d1}")
        if not totp_secret:
            raise RuntimeError("Groww requires MFA but GROWW_TOTP_SECRET is not set")

        r2 = await client.post(
            _MFA_PATH,
            json={"mfa_token": mfa_token, "twofa_value": generate_totp(totp_secret)},
        )
        r2.raise_for_status()
        d2: dict[str, Any] = r2.json()
        token = d2.get("access_token") or d2.get("authToken")
        if not token:
            raise RuntimeError(f"Groww MFA failed: {d2}")
        return str(token)


async def _acquire_token(force: bool = False) -> str:
    cached = load_session("groww")
    if not force and cached.get("access_token"):
        return str(cached["access_token"])
    token = await _login()
    save_session("groww", {"access_token": token})
    logger.info("Groww: acquired new access token")
    return token


async def _get_with_auth(path: str, token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    async with make_client(base_url=_GROWW_BASE, headers=headers) as client:
        res = await client.get(path)
        if res.status_code == 401:
            raise httpx.HTTPStatusError("token expired", request=res.request, response=res)
        res.raise_for_status()
        return res.json()


def _map_stock(r: dict[str, Any]) -> Holding:
    qty = float(r.get("quantity") or r.get("holding_quantity") or 0)
    avg = float(r.get("average_price") or r.get("avg_price") or 0)
    ltp = float(r.get("ltp") or r.get("current_price") or 0)
    invested = qty * avg
    current = qty * ltp
    pnl = current - invested
    sym = str(r.get("nse_scrip_code") or r.get("symbol") or r.get("trading_symbol") or "").upper()
    return Holding(
        source="groww",
        asset_class=AssetClass.EQUITY,
        symbol=sym,
        name=r.get("company_name") or r.get("name"),
        isin=r.get("isin"),
        quantity=qty,
        avg_price=avg,
        last_price=ltp,
        invested=invested,
        current_value=current,
        pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
        exchange=r.get("exchange") or "NSE",
    )


def _map_mf(r: dict[str, Any]) -> Holding:
    units = float(r.get("units") or r.get("total_units") or 0)
    avg_nav = float(r.get("average_nav") or r.get("avg_nav") or 0)
    ltp_nav = float(r.get("nav") or r.get("current_nav") or 0)
    invested = float(r.get("invested_amount") or units * avg_nav)
    current = float(r.get("current_value") or units * ltp_nav)
    pnl = current - invested
    scheme = r.get("scheme_name") or r.get("name") or ""
    return Holding(
        source="groww",
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
        if all(_env(k) for k in _REQUIRED):
            self._status = SourceStatus.READY

    def parse(self, stream, filename=None):  # type: ignore[override]
        holdings = _GrowwCSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        async def _pull(token: str) -> list[Holding]:
            stocks_payload = await _get_with_auth(_STOCKS_PATH, token)
            mf_payload = await _get_with_auth(_MF_PATH, token)
            stock_rows = stocks_payload.get("data") or stocks_payload.get("holdings") or []
            mf_rows = mf_payload.get("data") or mf_payload.get("holdings") or []
            return [_map_stock(r) for r in stock_rows] + [_map_mf(r) for r in mf_rows]

        try:
            token = await _acquire_token()
            holdings = await _pull(token)
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 401:
                logger.warning("Groww: token expired, re-logging in")
                clear_session("groww")
                token = await _acquire_token(force=True)
                holdings = await _pull(token)
            else:
                raise

        logger.info("Groww: fetched %d holdings", len(holdings))
        return holdings

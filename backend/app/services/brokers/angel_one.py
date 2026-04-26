"""Angel One SmartAPI source.

SmartAPI is the only genuinely free REST API among the Indian brokers we
target. Auth flow:

  1. Register at https://smartapi.angelbroking.com/ → get API key.
  2. Generate a TOTP secret in your Angel One profile.
  3. POST /rest/auth/angelbroking/user/v1/loginByPassword
        {clientcode, password, totp}
     → returns jwtToken + refreshToken + feedToken.
  4. GET /rest/secure/angelbroking/portfolio/v1/getHolding
     with `Authorization: Bearer <jwtToken>` and the standard
     `X-PrivateKey`, `X-ClientLocalIP`, `X-MACAddress`, `X-UserType`,
     `X-SourceID`, `Accept` headers.

We hit the documented JSON endpoints with httpx; no third-party SDK is
required (the official `smartapi-python` is fine, but adds a heavy WS dep
we don't need for read-only holdings).

Credentials come from environment / Settings:

  ANGEL_ONE_API_KEY       (the SmartAPI app key)
  ANGEL_ONE_CLIENT_CODE   (your trading client ID, e.g. ABCD12345)
  ANGEL_ONE_PASSWORD      (login PIN/MPIN)
  ANGEL_ONE_TOTP_SECRET   (base32 secret for TOTP, used to compute the OTP)

If `pyotp` is missing or any cred is empty, the source is left in
UNCONFIGURED status and sync() raises a clear error.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.core.logging import get_logger
from app.services.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
)

logger = get_logger("brokers.angel_one")


_BASE_URL = "https://apiconnect.angelbroking.com"
_LOGIN_PATH = "/rest/auth/angelbroking/user/v1/loginByPassword"
_HOLDING_PATH = "/rest/secure/angelbroking/portfolio/v1/getHolding"


def _env(key: str) -> str:
    return os.getenv(key, "").strip()


def _common_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": _env("ANGEL_ONE_CLIENT_IP") or "127.0.0.1",
        "X-ClientPublicIP": _env("ANGEL_ONE_CLIENT_PUBLIC_IP") or "127.0.0.1",
        "X-MACAddress": _env("ANGEL_ONE_MAC") or "00:00:00:00:00:00",
        "X-PrivateKey": api_key,
    }


def _generate_totp(secret: str) -> str:
    try:
        import pyotp  # type: ignore[import-not-found]
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "pyotp not installed — run `pdm add pyotp` to enable Angel One auth"
        ) from e
    return pyotp.TOTP(secret).now()


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
        if all(
            _env(k)
            for k in (
                "ANGEL_ONE_API_KEY",
                "ANGEL_ONE_CLIENT_CODE",
                "ANGEL_ONE_PASSWORD",
                "ANGEL_ONE_TOTP_SECRET",
            )
        ):
            self._status = SourceStatus.READY

    async def fetch(self) -> list[Holding]:
        api_key = _env("ANGEL_ONE_API_KEY")
        client_code = _env("ANGEL_ONE_CLIENT_CODE")
        password = _env("ANGEL_ONE_PASSWORD")
        totp_secret = _env("ANGEL_ONE_TOTP_SECRET")

        missing = [
            k
            for k, v in {
                "ANGEL_ONE_API_KEY": api_key,
                "ANGEL_ONE_CLIENT_CODE": client_code,
                "ANGEL_ONE_PASSWORD": password,
                "ANGEL_ONE_TOTP_SECRET": totp_secret,
            }.items()
            if not v
        ]
        if missing:
            raise RuntimeError(
                f"Angel One credentials missing: {', '.join(missing)}. "
                "See backend/docs/BROKERS.md for setup."
            )

        async with httpx.AsyncClient(base_url=_BASE_URL, timeout=20.0) as client:
            login_payload = {
                "clientcode": client_code,
                "password": password,
                "totp": _generate_totp(totp_secret),
            }
            login_res = await client.post(
                _LOGIN_PATH, json=login_payload, headers=_common_headers(api_key)
            )
            login_res.raise_for_status()
            login_data: dict[str, Any] = login_res.json()
            if not login_data.get("status"):
                raise RuntimeError(
                    f"Angel One login failed: {login_data.get('message') or login_data}"
                )
            jwt_token = login_data["data"]["jwtToken"]

            holdings_res = await client.get(
                _HOLDING_PATH,
                headers={**_common_headers(api_key), "Authorization": f"Bearer {jwt_token}"},
            )
            holdings_res.raise_for_status()
            payload: dict[str, Any] = holdings_res.json()

        if not payload.get("status"):
            raise RuntimeError(f"Angel One getHolding failed: {payload.get('message')}")

        rows: list[dict[str, Any]] = payload.get("data") or []
        out: list[Holding] = []
        for r in rows:
            qty = float(r.get("quantity") or 0)
            avg = float(r.get("averageprice") or 0)
            ltp = float(r.get("ltp") or 0)
            invested = qty * avg
            current = qty * ltp
            pnl = current - invested
            out.append(
                Holding(
                    source=self.slug,
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
            )
        logger.info("Angel One: fetched %d holdings", len(out))
        return out

"""Angel One SmartAPI — login, headers, row mapper."""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.modules.brokers._otp import generate_totp
from app.modules.brokers.base import AssetClass, Holding

BASE_URL = "https://apiconnect.angelbroking.com"
LOGIN_PATH = "/rest/auth/angelbroking/user/v1/loginByPassword"
HOLDING_PATH = "/rest/secure/angelbroking/portfolio/v1/getHolding"
REQUIRED_ENV = (
    "ANGEL_ONE_API_KEY", "ANGEL_ONE_CLIENT_CODE",
    "ANGEL_ONE_PASSWORD", "ANGEL_ONE_TOTP_SECRET",
)


def env(key: str) -> str:
    return os.getenv(key, "").strip()


def common_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": env("ANGEL_ONE_CLIENT_IP") or "127.0.0.1",
        "X-ClientPublicIP": env("ANGEL_ONE_CLIENT_PUBLIC_IP") or "127.0.0.1",
        "X-MACAddress": env("ANGEL_ONE_MAC") or "00:00:00:00:00:00",
        "X-PrivateKey": api_key,
    }


async def login_and_fetch_holdings() -> list[dict[str, Any]]:
    missing = [k for k in REQUIRED_ENV if not env(k)]
    if missing:
        raise RuntimeError(f"Angel One credentials missing: {', '.join(missing)}")

    api_key = env("ANGEL_ONE_API_KEY")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=20.0) as client:
        res = await client.post(
            LOGIN_PATH,
            json={
                "clientcode": env("ANGEL_ONE_CLIENT_CODE"),
                "password": env("ANGEL_ONE_PASSWORD"),
                "totp": generate_totp(env("ANGEL_ONE_TOTP_SECRET")),
            },
            headers=common_headers(api_key),
        )
        res.raise_for_status()
        data: dict[str, Any] = res.json()
        if not data.get("status"):
            raise RuntimeError(f"Angel One login failed: {data.get('message') or data}")
        jwt_token = data["data"]["jwtToken"]

        h = await client.get(
            HOLDING_PATH,
            headers={**common_headers(api_key), "Authorization": f"Bearer {jwt_token}"},
        )
        h.raise_for_status()
        payload: dict[str, Any] = h.json()
    if not payload.get("status"):
        raise RuntimeError(f"Angel One getHolding failed: {payload.get('message')}")
    return list(payload.get("data") or [])


def map_holding(r: dict[str, Any], slug: str) -> Holding:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("averageprice") or 0)
    ltp = float(r.get("ltp") or 0)
    invested, current = qty * avg, qty * ltp
    pnl = current - invested
    return Holding(
        source=slug, asset_class=AssetClass.EQUITY,
        symbol=str(r.get("tradingsymbol") or "").upper(),
        isin=r.get("isin"),
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=invested, current_value=current, pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
        exchange=r.get("exchange"),
    )

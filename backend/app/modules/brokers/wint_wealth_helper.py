"""Wint Wealth — OTP login flow + holdings fetch + row mapper."""

from __future__ import annotations

import os
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._http import clear_session, load_session, make_client, save_session
from app.modules.brokers.base import AssetClass, Holding

logger = get_logger("brokers.wint_wealth_helper")

WINT_BASE = "https://api.wintwealth.com"
HOLDINGS_PATH = "/portfolio/holdings"
_OTP_PATH = "/auth/login/otp"
_VERIFY_PATH = "/auth/login/verify"


def env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


async def send_otp(slug: str) -> dict[str, Any]:
    user_id = env("WINT_USER_ID")
    if not user_id:
        raise RuntimeError("WINT_USER_ID not set")
    channel = env("WINT_OTP_CHANNEL", "sms")
    async with make_client(base_url=WINT_BASE) as client:
        res = await client.post(_OTP_PATH, json={"identifier": user_id, "channel": channel})
        res.raise_for_status()
        data: dict[str, Any] = res.json()
    ref = data.get("reference_id") or data.get("ref")
    if ref:
        cached = load_session(slug)
        cached["pending_ref"] = ref
        save_session(slug, cached)
    logger.info("Wint Wealth: OTP sent (ref=%s)", ref)
    return {"sent": True, "channel": channel, "reference_id": ref}


async def verify_otp(slug: str, code: str) -> str:
    user_id = env("WINT_USER_ID")
    if not user_id:
        raise RuntimeError("WINT_USER_ID not set")
    ref = load_session(slug).get("pending_ref")
    async with make_client(base_url=WINT_BASE) as client:
        res = await client.post(
            _VERIFY_PATH,
            json={"identifier": user_id, "otp": code, "reference_id": ref},
        )
        res.raise_for_status()
        data: dict[str, Any] = res.json()
    jwt = data.get("token") or data.get("access_token") or data.get("jwt")
    if not jwt:
        raise RuntimeError(f"Wint Wealth verify did not return a token: {data}")
    save_session(slug, {"jwt": jwt})
    logger.info("Wint Wealth: token cached")
    return str(jwt)


async def fetch_holdings_json(jwt: str, slug: str) -> list[dict[str, Any]]:
    headers = {"Authorization": f"Bearer {jwt}"}
    async with make_client(base_url=WINT_BASE, headers=headers) as client:
        res = await client.get(HOLDINGS_PATH)
        if res.status_code == 401:
            clear_session(slug)
            raise RuntimeError(
                "Wint Wealth token expired — re-run /sources/wint-wealth/start-login"
            )
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    return list(payload.get("data") or payload.get("holdings") or [])


def map_holding(r: dict[str, Any], slug: str) -> Holding:
    qty = float(r.get("units") or r.get("quantity") or r.get("face_value") or 0)
    invested = float(r.get("invested_amount") or r.get("investment") or 0)
    current = float(r.get("current_value") or r.get("market_value") or invested)
    avg = invested / qty if qty else 0.0
    ltp = current / qty if qty else 0.0
    pnl = current - invested
    name = r.get("bond_name") or r.get("name") or r.get("issuer") or ""
    return Holding(
        source=slug, asset_class=AssetClass.BOND,
        symbol=str(r.get("isin") or name[:24]),
        name=name or None, isin=r.get("isin"),
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=invested, current_value=current, pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
    )

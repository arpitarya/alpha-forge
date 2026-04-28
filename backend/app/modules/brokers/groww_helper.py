"""Groww — login + token cache + authenticated GET."""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.core.logging import get_logger
from app.modules.brokers._http import load_session, make_client, save_session
from app.modules.brokers._otp import generate_totp

logger = get_logger("brokers.groww_helper")

GROWW_BASE = "https://groww.in"
STOCKS_PATH = "/v1/api/stocks_data/v2/stocks/portfolio"
MF_PATH = "/v1/api/mutual_funds/v1/portfolio"
REQUIRED_ENV = ("GROWW_USER_ID", "GROWW_PASSWORD")

_LOGIN_PATH = "/v1/api/auth/v3/users/login"
_MFA_PATH = "/v1/api/auth/v3/users/login/mfa"


def env(key: str) -> str:
    return os.getenv(key, "").strip()


async def _login() -> str:
    missing = [k for k in REQUIRED_ENV if not env(k)]
    if missing:
        raise RuntimeError(f"Groww credentials missing: {', '.join(missing)}")
    async with make_client(base_url=GROWW_BASE) as client:
        r1 = await client.post(
            _LOGIN_PATH,
            json={"username": env("GROWW_USER_ID"), "password": env("GROWW_PASSWORD")},
        )
        r1.raise_for_status()
        d1: dict[str, Any] = r1.json()
        token = d1.get("access_token") or d1.get("authToken")
        if token:
            return str(token)
        mfa_token = d1.get("mfa_token") or d1.get("mfaToken")
        if not mfa_token:
            raise RuntimeError(f"Groww login response unrecognised: {d1}")
        totp_secret = env("GROWW_TOTP_SECRET")
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


async def acquire_token(force: bool = False) -> str:
    cached = load_session("groww")
    if not force and cached.get("access_token"):
        return str(cached["access_token"])
    token = await _login()
    save_session("groww", {"access_token": token})
    logger.info("Groww: acquired new access token")
    return token


async def get_with_auth(path: str, token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}"}
    async with make_client(base_url=GROWW_BASE, headers=headers) as client:
        res = await client.get(path)
        if res.status_code == 401:
            raise httpx.HTTPStatusError("token expired", request=res.request, response=res)
        res.raise_for_status()
        return res.json()

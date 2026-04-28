"""Zerodha Kite — Playwright login + enctoken cache + holdings fetch."""

from __future__ import annotations

import os
from typing import Any

import httpx

from app.core.logging import get_logger
from app.modules.brokers._http import load_session, make_client, save_session
from app.modules.brokers._otp import generate_totp

logger = get_logger("brokers.zerodha_kite_helper")

KITE_BASE = "https://kite.zerodha.com"
HOLDINGS_PATH = "/oms/portfolio/holdings"
REQUIRED_ENV = ("ZERODHA_USER_ID", "ZERODHA_APP_CODE", "ZERODHA_TOTP_SECRET")

_LOGIN_URL = "https://kite.zerodha.com/"
_LOGIN_TIMEOUT_MS = 30_000
_TOTP_SELECTOR = (
    'input[label="External TOTP"], input[type="number"], '
    'input[type="text"]:not([disabled])'
)
_HEADLESS = os.getenv("ZERODHA_LOGIN_HEADLESS", "true").lower() != "false"


def env(key: str) -> str:
    return os.getenv(key, "").strip()


async def playwright_login(user_id: str, app_code: str, totp_secret: str) -> str:
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise RuntimeError("playwright not installed; run uv sync && playwright install chromium") from e

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=_HEADLESS)
        try:
            context = await browser.new_context()
            page = await context.new_page()
            page.set_default_timeout(_LOGIN_TIMEOUT_MS)
            await page.goto(_LOGIN_URL, wait_until="domcontentloaded")
            await page.wait_for_selector('input[type="text"]')
            await page.fill('input[type="text"]', user_id)
            await page.fill('input[type="password"]', app_code)
            await page.click('button[type="submit"]')
            await page.wait_for_selector(_TOTP_SELECTOR)
            await page.locator(
                'input[label="External TOTP"], input[type="number"], input#userid'
            ).last.fill(generate_totp(totp_secret))
            try:
                await page.click('button[type="submit"]', timeout=2_000)
            except Exception as e:
                logger.debug("Zerodha: TOTP submit click skipped (%s)", e)
            await page.wait_for_url("**/dashboard**")
            cookies = await context.cookies()
            enctoken = next((c["value"] for c in cookies if c["name"] == "enctoken"), None)
            if not enctoken:
                raise RuntimeError("Zerodha login succeeded but no enctoken cookie was set")
            return enctoken
        finally:
            await browser.close()


async def acquire_enctoken(force: bool = False) -> str:
    cached = load_session("zerodha")
    if not force and cached.get("enctoken"):
        return str(cached["enctoken"])

    missing = [k for k in REQUIRED_ENV if not env(k)]
    if missing:
        raise RuntimeError(f"Zerodha credentials missing: {', '.join(missing)}")

    enctoken = await playwright_login(
        env("ZERODHA_USER_ID"), env("ZERODHA_APP_CODE"), env("ZERODHA_TOTP_SECRET")
    )
    save_session("zerodha", {"enctoken": enctoken, "user_id": env("ZERODHA_USER_ID")})
    logger.info("Zerodha: acquired new enctoken via Playwright")
    return enctoken


async def fetch_holdings_json(enctoken: str) -> list[dict[str, Any]]:
    headers = {"Authorization": f"enctoken {enctoken}"}
    async with make_client(base_url=KITE_BASE, headers=headers) as client:
        client.cookies.set("enctoken", enctoken, domain="kite.zerodha.com")
        res = await client.get(HOLDINGS_PATH)
        if res.status_code == 401:
            raise httpx.HTTPStatusError("enctoken expired", request=res.request, response=res)
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    if payload.get("status") != "success":
        raise RuntimeError(f"Zerodha holdings failed: {payload.get('message') or payload}")
    return list(payload.get("data") or [])

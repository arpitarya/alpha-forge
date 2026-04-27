"""Zerodha Kite — equity holdings via Playwright-driven web login.

Kite Connect (the official paid REST API at ₹2000/mo) is ruled out. We drive
the real browser login flow with Playwright:

  1. Launch Chromium, navigate to https://kite.zerodha.com
  2. Fill user_id + app_code, submit
  3. Fill TOTP on the 2FA screen, submit
  4. Wait for the dashboard, extract the `enctoken` cookie
  5. Hand the enctoken to httpx for /oms/portfolio/holdings calls

The `enctoken` is cached on disk so daily syncs don't relaunch a browser.
First run requires `playwright install chromium`.

Credentials (.env.cred):
  ZERODHA_USER_ID
  ZERODHA_APP_CODE        (Kite app code — sent as the `password` field)
  ZERODHA_TOTP_SECRET

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
from app.modules.brokers.csv_sources import ZerodhaCSVSource as _ZerodhaCSV

logger = get_logger("brokers.zerodha_kite")


_KITE_BASE = "https://kite.zerodha.com"
_KITE_LOGIN_URL = "https://kite.zerodha.com/"
_HOLDINGS_PATH = "/oms/portfolio/holdings"

_REQUIRED = ("ZERODHA_USER_ID", "ZERODHA_APP_CODE", "ZERODHA_TOTP_SECRET")

_LOGIN_TIMEOUT_MS = 30_000
_HEADLESS = os.getenv("ZERODHA_LOGIN_HEADLESS", "true").lower() != "false"


def _env(key: str) -> str:
    return os.getenv(key, "").strip()


async def _playwright_login(user_id: str, app_code: str, totp_secret: str) -> str:
    """Drive Kite's web login with Playwright and return the `enctoken` cookie."""
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise RuntimeError(
            "playwright not installed. Run: pdm add playwright && playwright install chromium"
        ) from e

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        try:
            context = await browser.new_context()
            page = await context.new_page()
            page.set_default_timeout(_LOGIN_TIMEOUT_MS)

            await page.goto(_KITE_LOGIN_URL, wait_until="domcontentloaded")

            await page.wait_for_selector('input[type="text"]', timeout=_LOGIN_TIMEOUT_MS)

            await page.fill('input[type="text"]', user_id)
            await page.fill('input[type="password"]', app_code)
            await page.click('button[type="submit"]')

            totp_selector = (
                'input[label="External TOTP"], input[type="number"], '
                'input[type="text"]:not([disabled])'
            )
            await page.wait_for_selector(totp_selector, timeout=_LOGIN_TIMEOUT_MS)
            totp = generate_totp(totp_secret)
            totp_input = page.locator(
                'input[label="External TOTP"], input[type="number"], input#userid'
            ).last
            await totp_input.fill(totp)

            try:
                await page.click('button[type="submit"]', timeout=2_000)
            except Exception as e:
                # Some Kite UI variants auto-submit on TOTP completion; non-fatal.
                logger.debug("Zerodha: TOTP submit click skipped (%s)", e)

            await page.wait_for_url("**/dashboard**", timeout=_LOGIN_TIMEOUT_MS)

            cookies = await context.cookies()
            enctoken = next((c["value"] for c in cookies if c["name"] == "enctoken"), None)
            if not enctoken:
                raise RuntimeError("Zerodha login succeeded but no enctoken cookie was set")
            return enctoken
        finally:
            await browser.close()


async def acquire_enctoken(force: bool = False) -> str:
    """Return a valid enctoken cookie value, logging in via Playwright if needed.

    Cached on disk under `.cache/brokers/zerodha.json`. Other Zerodha sources
    (Coin) call this to share the session.
    """
    cached = load_session("zerodha")
    if not force and cached.get("enctoken"):
        return str(cached["enctoken"])

    missing = [k for k in _REQUIRED if not _env(k)]
    if missing:
        raise RuntimeError(f"Zerodha credentials missing: {', '.join(missing)}")

    user_id = _env("ZERODHA_USER_ID")
    app_code = _env("ZERODHA_APP_CODE")
    totp_secret = _env("ZERODHA_TOTP_SECRET")

    enctoken = await _playwright_login(user_id, app_code, totp_secret)
    save_session("zerodha", {"enctoken": enctoken, "user_id": user_id})
    logger.info("Zerodha: acquired new enctoken via Playwright")
    return enctoken


async def _get_holdings_json(enctoken: str) -> list[dict[str, Any]]:
    headers = {"Authorization": f"enctoken {enctoken}"}
    async with make_client(base_url=_KITE_BASE, headers=headers) as client:
        client.cookies.set("enctoken", enctoken, domain="kite.zerodha.com")
        res = await client.get(_HOLDINGS_PATH)
        if res.status_code == 401:
            raise httpx.HTTPStatusError("enctoken expired", request=res.request, response=res)
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    if payload.get("status") != "success":
        raise RuntimeError(f"Zerodha holdings failed: {payload.get('message') or payload}")
    return list(payload.get("data") or [])


class ZerodhaKiteSource(BrokerSource):
    slug = "zerodha"
    label = "Zerodha (Kite)"
    kind = SourceKind.API
    notes = (
        "Uses the unofficial Kite web-login flow (free). Set "
        "ZERODHA_USER_ID / ZERODHA_APP_CODE / ZERODHA_TOTP_SECRET in .env.cred."
    )

    def __init__(self) -> None:
        super().__init__()
        if all(_env(k) for k in _REQUIRED):
            self._status = SourceStatus.READY

    def parse(self, stream, filename=None):  # type: ignore[override]
        """CSV upload fallback — delegates to ZerodhaCSVSource parser."""
        holdings = _ZerodhaCSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    async def fetch(self) -> list[Holding]:
        try:
            enctoken = await acquire_enctoken()
            rows = await _get_holdings_json(enctoken)
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 401:
                logger.warning("Zerodha: enctoken expired, re-logging in")
                clear_session("zerodha")
                enctoken = await acquire_enctoken(force=True)
                rows = await _get_holdings_json(enctoken)
            else:
                raise

        out: list[Holding] = []
        for r in rows:
            qty = float(r.get("quantity") or 0)
            avg = float(r.get("average_price") or 0)
            ltp = float(r.get("last_price") or 0)
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
        logger.info("Zerodha Kite: fetched %d holdings", len(out))
        return out

"""Connect to an existing Chrome started with --remote-debugging-port=PORT.

Lets you log in manually once in your normal Chrome window (Zerodha, Groww,
Wint Wealth, Dezerv, Zerodha Coin), then have the backend reuse those cookies
without re-doing 2FA. Shared by every broker helper that scrapes the web app.

Start Chrome (one-time) with the debugging port:
    /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\
        --remote-debugging-port=9299 \\
        --user-data-dir="$HOME/.cache/alphaforge-chrome"
"""

from __future__ import annotations

import os
from typing import Any

from app.core.logging import get_logger

logger = get_logger("brokers.cdp")

DEFAULT_CDP_PORT = int(os.getenv("BROKER_CDP_PORT", "9299"))
DEFAULT_CDP_HOST = os.getenv("BROKER_CDP_HOST", "127.0.0.1")


def cdp_url(port: int | None = None) -> str:
    return f"http://{DEFAULT_CDP_HOST}:{port or DEFAULT_CDP_PORT}"


def _verify_loopback(host: str) -> None:
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise RuntimeError(
            f"Refusing to attach to non-loopback CDP host {host!r}. "
            "Chrome's debugging port must be bound to localhost only — "
            "remote attackers can read cookies otherwise."
        )


async def connect_existing_chrome(port: int | None = None) -> tuple[Any, Any]:
    """Return (playwright, browser) attached to the running Chrome via CDP."""
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise RuntimeError(
            "playwright not installed; run uv sync && playwright install chromium"
        ) from e
    _verify_loopback(DEFAULT_CDP_HOST)
    pw = await async_playwright().start()
    url = cdp_url(port)
    try:
        browser = await pw.chromium.connect_over_cdp(url)
    except Exception as e:
        await pw.stop()
        raise RuntimeError(
            f"Could not attach to Chrome at {url}. Start Chrome with "
            f"--remote-debugging-port={port or DEFAULT_CDP_PORT} "
            f"--remote-debugging-address=127.0.0.1 and try again."
        ) from e
    logger.info("CDP: attached to Chrome at %s", url)
    return pw, browser


async def find_or_open_page(browser: Any, target_url: str, match: str) -> Any:
    """Return the first existing page whose URL contains `match`, else open one."""
    for ctx in browser.contexts:
        for page in ctx.pages:
            if match in page.url:
                return page
    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = await ctx.new_page()
    await page.goto(target_url, wait_until="domcontentloaded")
    return page


async def cookie_value(
    context: Any, name: str, domain_substr: str = ""
) -> str | None:
    for c in await context.cookies():
        if c["name"] == name and (not domain_substr or domain_substr in c.get("domain", "")):
            return str(c["value"])
    return None

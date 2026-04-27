"""Shared httpx client factory + a tiny on-disk JSON cache for session tokens.

Brokers that scrape the web app (Zerodha, Groww) keep an `enctoken`/`access_token`
on disk so daily syncs don't trigger a fresh login + 2FA every time.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

DEFAULT_TIMEOUT = httpx.Timeout(20.0, connect=10.0)
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
}


def make_client(
    base_url: str = "",
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
) -> httpx.AsyncClient:
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}
    return httpx.AsyncClient(
        base_url=base_url,
        headers=merged_headers,
        cookies=cookies or {},
        timeout=DEFAULT_TIMEOUT,
        follow_redirects=True,
    )


# ── Token cache ───────────────────────────────────────────────────────────────


def _cache_root() -> Path:
    root = Path(os.getenv("BROKER_CACHE_DIR", ".cache/brokers")).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def load_session(slug: str) -> dict[str, Any]:
    f = _cache_root() / f"{slug}.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def save_session(slug: str, data: dict[str, Any]) -> None:
    f = _cache_root() / f"{slug}.json"
    f.write_text(json.dumps(data, indent=2))


def clear_session(slug: str) -> None:
    f = _cache_root() / f"{slug}.json"
    if f.exists():
        f.unlink()

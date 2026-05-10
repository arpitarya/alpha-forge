"""Shared httpx client factory + a tiny on-disk JSON cache for session tokens.

Brokers that scrape the web app (Zerodha, Groww) keep an `enctoken`/`access_token`
on disk so daily syncs don't trigger a fresh login + 2FA every time.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import httpx
from cryptography.fernet import Fernet, InvalidToken

SESSION_TTL_SECONDS = int(os.getenv("BROKER_SESSION_TTL", "82800"))  # 23h default

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
    os.chmod(root, 0o700)
    return root


def _fernet() -> Fernet:
    key = os.getenv("BROKER_CACHE_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "BROKER_CACHE_KEY not set. Generate with: "
            "python -c 'from cryptography.fernet import Fernet;"
            " print(Fernet.generate_key().decode())'"
        )
    return Fernet(key.encode())


def load_session(slug: str) -> dict[str, Any]:
    f = _cache_root() / f"{slug}.bin"
    if not f.exists():
        return {}
    try:
        decrypted = _fernet().decrypt(f.read_bytes())
        data = json.loads(decrypted)
    except (OSError, json.JSONDecodeError, InvalidToken):
        return {}
    if time.time() - float(data.get("_saved_at", 0)) > SESSION_TTL_SECONDS:
        return {}
    data.pop("_saved_at", None)
    return data


def save_session(slug: str, data: dict[str, Any]) -> None:
    f = _cache_root() / f"{slug}.bin"
    payload = {**data, "_saved_at": time.time()}
    f.write_bytes(_fernet().encrypt(json.dumps(payload).encode()))
    os.chmod(f, 0o600)


def clear_session(slug: str) -> None:
    f = _cache_root() / f"{slug}.bin"
    if f.exists():
        f.unlink()

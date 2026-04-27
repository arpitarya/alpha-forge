"""Wint Wealth — bond holdings via the OTP-bound web/PWA API.

Wint Wealth uses an OTP-only login (no password). Since OTPs reach the
user's phone/email, we expose a two-step flow that the frontend drives:

  POST /api/v1/portfolio/sources/wint-wealth/start-login
       → backend POSTs api.wintwealth.com/auth/login/otp { mobile_or_email }
       → user receives the OTP

  POST /api/v1/portfolio/sources/wint-wealth/otp { code }
       → backend POSTs api.wintwealth.com/auth/login/verify
       → caches the JWT under .cache/brokers/wint-wealth.json (~30 days)

  POST /api/v1/portfolio/sources/wint-wealth/sync
       → uses the cached JWT to GET /portfolio/holdings

Credentials (.env.cred):
  WINT_USER_ID         (registered mobile number or email)
  WINT_OTP_CHANNEL     ("sms" or "email"; defaults to sms)

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import os
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers._http import (
    clear_session,
    load_session,
    make_client,
    save_session,
)
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
)
from app.modules.brokers.csv_sources import WintWealthCSVSource as _WintCSV

logger = get_logger("brokers.wint_wealth")


_WINT_BASE = "https://api.wintwealth.com"
_OTP_PATH = "/auth/login/otp"
_VERIFY_PATH = "/auth/login/verify"
_HOLDINGS_PATH = "/portfolio/holdings"


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


class WintWealthSource(BrokerSource):
    slug = "wint-wealth"
    label = "Wint Wealth"
    kind = SourceKind.API
    notes = (
        "OTP-bound login. Call /sources/wint-wealth/start-login, then "
        "/sources/wint-wealth/otp with the code received."
    )

    def __init__(self) -> None:
        super().__init__()
        cached = load_session(self.slug)
        if cached.get("jwt"):
            self._status = SourceStatus.READY
        elif _env("WINT_USER_ID"):
            # creds present but no token yet — user must run OTP flow
            self._status = SourceStatus.UNCONFIGURED

    # ── OTP flow (called from routes/portfolio.py) ───────────────────────

    async def start_login(self) -> dict[str, Any]:
        user_id = _env("WINT_USER_ID")
        if not user_id:
            raise RuntimeError("WINT_USER_ID not set")
        channel = _env("WINT_OTP_CHANNEL", "sms")
        async with make_client(base_url=_WINT_BASE) as client:
            res = await client.post(
                _OTP_PATH,
                json={"identifier": user_id, "channel": channel},
            )
            res.raise_for_status()
            data: dict[str, Any] = res.json()
        ref = data.get("reference_id") or data.get("ref")
        if ref:
            cached = load_session(self.slug)
            cached["pending_ref"] = ref
            save_session(self.slug, cached)
        logger.info("Wint Wealth: OTP sent (ref=%s)", ref)
        return {"sent": True, "channel": channel, "reference_id": ref}

    async def submit_otp(self, code: str) -> dict[str, Any]:
        user_id = _env("WINT_USER_ID")
        if not user_id:
            raise RuntimeError("WINT_USER_ID not set")
        cached = load_session(self.slug)
        ref = cached.get("pending_ref")
        async with make_client(base_url=_WINT_BASE) as client:
            res = await client.post(
                _VERIFY_PATH,
                json={"identifier": user_id, "otp": code, "reference_id": ref},
            )
            res.raise_for_status()
            data: dict[str, Any] = res.json()
        jwt = data.get("token") or data.get("access_token") or data.get("jwt")
        if not jwt:
            raise RuntimeError(f"Wint Wealth verify did not return a token: {data}")
        save_session(self.slug, {"jwt": jwt})
        self._status = SourceStatus.READY
        logger.info("Wint Wealth: token cached")
        return {"verified": True}

    def parse(self, stream, filename=None):  # type: ignore[override]
        holdings = _WintCSV().parse(stream, filename)
        return [h.model_copy(update={"source": self.slug}) for h in holdings]

    # ── Holdings fetch ───────────────────────────────────────────────────

    async def fetch(self) -> list[Holding]:
        cached = load_session(self.slug)
        jwt = cached.get("jwt")
        if not jwt:
            raise RuntimeError(
                "Wint Wealth not authenticated — POST /sources/wint-wealth/start-login first"
            )

        headers = {"Authorization": f"Bearer {jwt}"}
        async with make_client(base_url=_WINT_BASE, headers=headers) as client:
            res = await client.get(_HOLDINGS_PATH)
            if res.status_code == 401:
                clear_session(self.slug)
                self._status = SourceStatus.UNCONFIGURED
                raise RuntimeError(
                    "Wint Wealth token expired — re-run /sources/wint-wealth/start-login"
                )
            res.raise_for_status()
            payload: dict[str, Any] = res.json()

        rows = payload.get("data") or payload.get("holdings") or []
        out: list[Holding] = []
        for r in rows:
            qty = float(r.get("units") or r.get("quantity") or r.get("face_value") or 0)
            invested = float(r.get("invested_amount") or r.get("investment") or 0)
            current = float(r.get("current_value") or r.get("market_value") or invested)
            avg = invested / qty if qty else 0.0
            ltp = current / qty if qty else 0.0
            pnl = current - invested
            name = r.get("bond_name") or r.get("name") or r.get("issuer") or ""
            out.append(
                Holding(
                    source=self.slug,
                    asset_class=AssetClass.BOND,
                    symbol=str(r.get("isin") or name[:24]),
                    name=name or None,
                    isin=r.get("isin"),
                    quantity=qty,
                    avg_price=avg,
                    last_price=ltp,
                    invested=invested,
                    current_value=current,
                    pnl=pnl,
                    pnl_pct=(pnl / invested * 100) if invested else 0.0,
                )
            )
        logger.info("Wint Wealth: fetched %d holdings", len(out))
        return out

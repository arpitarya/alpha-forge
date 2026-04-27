---
name: Per-Source Broker API Plan
status: Draft
owner: AlphaForge / Portfolio module
last_updated: 2026-04-27
---

# Per-Source Broker APIs — Plan

## Goal

Replace the current CSV-upload-only flow for most sources with **first-class per-source clients** that pull holdings automatically using whichever free path is realistic for that platform:

- **Direct REST API** if the platform exposes a free one (or an unofficial-but-stable one).
- **HTTP session scraping** (login → cookie/token → JSON endpoint) if there is no public API but the web app talks to one.
- **Browser automation** (Playwright headless) to log in, navigate, and download an export CSV when nothing else works.

Each source remains in **its own file** under [backend/app/services/brokers/](.), implements [BrokerSource](base.py), and is plugged into [registry.py](registry.py). The existing [aggregator.py](aggregator.py) and [routes/portfolio.py](../../routes/portfolio.py) endpoints do **not** change shape — they already operate over the abstract `BrokerSource` interface.

## Sources & Strategy

| Source | Free Path | Module | Auth Inputs (.env) |
|---|---|---|---|
| **Zerodha Kite** (equity) | Browser automation → CSV download (Kite Connect API is ₹2000/mo; ruled out) | `zerodha_kite.py` | `ZERODHA_USER_ID`, `ZERODHA_APP_CODE`, `ZERODHA_TOTP_SECRET` |
| **Zerodha Coin** (mutual funds) | Browser automation → Holdings CSV (shared session w/ Kite) | `zerodha_coin.py` | reuses Zerodha creds above |
| **Groww** | Direct API (`groww.in/v1/api/...`) using web access token after login (reverse-engineered, free) — fallback to Playwright | `groww.py` | `GROWW_USER_ID`, `GROWW_PASSWORD`, `GROWW_TOTP_SECRET` |
| **Angel One** | Direct REST — SmartAPI free tier (already implemented, keep) | `angel_one.py` | `ANGEL_ONE_API_KEY`, `ANGEL_ONE_CLIENT_CODE`, `ANGEL_ONE_PASSWORD`, `ANGEL_ONE_TOTP_SECRET` |
| **Wint Wealth** | Direct API used by the web/PWA (`api.wintwealth.com`) discovered via browser devtools — fallback Playwright | `wint_wealth.py` | `WINT_USER_ID`, `WINT_PASSWORD`, `WINT_OTP_MODE` (sms/email; OTP supplied at runtime via `/sources/wint-wealth/otp`) |

CSV upload remains as a **manual fallback** for every source (path `POST /sources/{slug}/upload`), but `kind=API` becomes the primary mode.

## Module Layout

```
backend/app/services/brokers/
├── base.py              ← BrokerSource ABC, Holding, SourceKind, SourceStatus  (existing, unchanged)
├── registry.py          ← single source-of-truth instance map                  (extend with new sources)
├── aggregator.py        ← merges Holdings across sources                       (no change)
│
├── _http.py             ← shared httpx.AsyncClient factory + retry/backoff     (NEW)
├── _automation.py       ← shared Playwright session helper (cookie cache)     (NEW)
├── _otp.py              ← TOTP helper (wraps pyotp, lazy import)              (NEW; lift from angel_one.py)
│
├── zerodha_kite.py      ← Zerodha equity holdings                             (NEW; replaces ZerodhaCSVSource as primary)
├── zerodha_coin.py      ← Zerodha Coin MF holdings                            (NEW; replaces ZerodhaCoinCSVSource)
├── groww.py             ← Groww equity + MF                                   (NEW; replaces GrowwCSVSource)
├── angel_one.py         ← Angel One SmartAPI                                  (existing; keep)
├── wint_wealth.py       ← Wint Wealth bonds                                   (NEW; replaces WintWealthCSVSource)
│
└── csv_sources.py       ← keep ONLY parsers, used by /upload fallback         (refactor: classes become parser fns)
```

The aggregator reads from `SOURCES` in [registry.py](registry.py); we keep its slug strings stable (`zerodha`, `zerodha-coin`, `groww`, `angel-one`, `wint-wealth`) so the frontend doesn't need to change.

## Per-Source Design

### 1. Zerodha Kite — `zerodha_kite.py`

Kite Connect (the official REST API) requires a paid app subscription, so we go through the **web login** route exactly as a browser does:

1. POST `https://kite.zerodha.com/api/login` with `user_id` + `password` → `request_id`.
2. POST `https://kite.zerodha.com/api/twofa` with `user_id`, `request_id`, `twofa_value` (TOTP from `ZERODHA_TOTP_SECRET`) → sets `enctoken` cookie.
3. GET `https://kite.zerodha.com/oms/portfolio/holdings` with that cookie → JSON list of holdings (same payload as Kite Connect's `/portfolio/holdings`).
4. Map to `Holding` (asset_class=EQUITY, exchange from row).

If step 2 ever fails we fall through to **Playwright headless**: spin a Chromium context, fill the login form, wait for `kite.zerodha.com/dashboard`, screenshot the holdings page, and download the CSV via the Console export link. Cached cookie is persisted to `.cache/brokers/zerodha.json` (gitignored) so daily syncs don't re-login.

**Risk:** Zerodha may rotate the unofficial endpoint or add Cloudflare. Mitigation: graceful fallback to Playwright, status surface in `info().error_message`.

### 2. Zerodha Coin — `zerodha_coin.py`

Coin shares Kite's session. Reuse the cookie obtained by `zerodha_kite.py` (via a small `ZerodhaSession` singleton in `_automation.py`):

- GET `https://coin.zerodha.com/api/dashboard/holdings` with `enctoken` cookie → MF holdings JSON.

If unauthorized, trigger Kite login flow first, then retry. Asset class = MUTUAL_FUND.

### 3. Groww — `groww.py`

Groww's web app calls `groww.in/v1/api/stocks_data/v2/...` and `groww.in/v1/api/mutual_funds/v1/...` with a bearer token that's set in localStorage after login. Two-tier strategy:

- **Tier 1 — direct API:** POST `https://groww.in/v1/api/auth/v3/users/login` with `email`/`password`; if MFA required, complete with TOTP. Pull access token. GET `/v1/api/stocks_data/v2/stocks/portfolio` and `/v1/api/mutual_funds/v1/portfolio`.
- **Tier 2 — Playwright fallback:** if the auth endpoint changes, log in via the UI, intercept `Authorization` header from a network request, then resume tier-1 API calls.

Asset class inferred per endpoint (stocks → EQUITY, MFs → MUTUAL_FUND).

### 4. Angel One — `angel_one.py` (keep existing)

Already uses the official SmartAPI. No changes beyond:

- Lift the inline `_generate_totp` into shared [_otp.py](_otp.py).
- Lift `_common_headers` into a class so it can be reused if we add Angel order placement later.

### 5. Wint Wealth — `wint_wealth.py`

No advertised public API. Approach:

1. **Discover endpoint** via browser devtools once (manual, one-time): the PWA calls `https://api.wintwealth.com/portfolio/holdings` with a `Bearer` JWT.
2. **Login flow** is OTP-only (SMS/email). We can't auto-fetch the OTP, so:
   - Step A: `POST /sources/wint-wealth/start-login` triggers `https://api.wintwealth.com/auth/login/otp` with `WINT_USER_ID`.
   - Step B: User receives OTP, calls `POST /sources/wint-wealth/otp` with the code → backend exchanges it for a JWT and caches it for ~30 days.
   - Step C: Subsequent `/sources/wint-wealth/sync` uses the cached JWT.
3. If the API changes, Playwright fallback navigates the PWA, types the OTP supplied via the same `/otp` endpoint, and screen-scrapes the holdings list.

Asset class = BOND (Wint is bonds-only).

## Aggregator API

No new endpoints needed — the existing routes already cover the surface:

- `GET /api/v1/portfolio/sources` — list sources & status (already wired)
- `POST /api/v1/portfolio/sources/{slug}/sync` — pull from upstream (API sources)
- `POST /api/v1/portfolio/sources/{slug}/upload` — manual CSV fallback
- `GET /api/v1/portfolio/holdings` — aggregate across sources (already wired)
- `GET /api/v1/portfolio/treemap` / `/rebalance` — derived views (already wired)

**New endpoints (small additions):**

- `POST /api/v1/portfolio/sources/sync-all` — fan-out sync over every API source, returns per-source success/error map. Used by the frontend "Refresh All" button.
- `POST /api/v1/portfolio/sources/wint-wealth/start-login` and `.../otp` — OTP-bound flow described above. Generic enough to expose as `/sources/{slug}/otp` so future sources can opt in.

## Credential Conventions

All credentials live in `backend/.env.cred` (gitignored), loaded via `pydantic-settings` in [core/config.py](../../core/config.py). Each source reads only what it needs and surfaces missing creds via `info().error_message`. New keys to add to `.env.cred.example`:

```
# Zerodha (Kite + Coin share creds)
ZERODHA_USER_ID=
ZERODHA_APP_CODE=
ZERODHA_TOTP_SECRET=

# Groww
GROWW_USER_ID=
GROWW_PASSWORD=
GROWW_TOTP_SECRET=

# Wint Wealth (OTP-only; no password)
WINT_USER_ID=
WINT_OTP_CHANNEL=sms        # sms | email
```

`ANGEL_ONE_*` are already documented.

## Phasing

| Phase | Scope | Exit criteria |
|---|---|---|
| **P0 — scaffolding** | Add `_http.py`, `_otp.py`, `_automation.py`. Move TOTP out of `angel_one.py`. | Existing tests still green; no behavior change. |
| **P1 — Zerodha Kite (HTTP-only)** | Implement direct login + holdings API. Persist cookie to `.cache/`. | `pdm run pytest tests/brokers/test_zerodha_kite.py`; live `/sources/zerodha/sync` returns ≥ 1 holding for a real account. |
| **P2 — Zerodha Coin** | Share session w/ Kite, hit Coin holdings endpoint. | Same as P1 for `zerodha-coin`. |
| **P3 — Groww (direct API)** | Tier-1 path only. | Same as P1 for `groww`. |
| **P4 — Wint Wealth (OTP flow)** | `/start-login` + `/otp` + cached JWT. | OTP-driven sync works end-to-end on a real account. |
| **P5 — Playwright fallbacks** | Add fallback paths to Zerodha & Groww when HTTP fails. | Simulated failure (force-401) routes through Playwright cleanly. |
| **P6 — `/sources/sync-all` + frontend wire-up** | Fan-out endpoint + a "Refresh All" button on the portfolio page. | Single click syncs every configured source; partial failures surfaced. |

## Testing

- **Unit:** mock `httpx` responses for each source's happy path + 401/5xx; assert `Holding` mapping (qty, avg, ltp, pnl).
- **Contract:** record real responses once via `vcrpy` in `tests/brokers/cassettes/` (with PII scrubbed) so future runs don't need live creds.
- **Smoke (manual, gated):** `just brokers-smoke` runs every `kind=API` source against real creds and prints holding counts. Skipped in CI.

## Non-goals

- Order placement or live quotes via these sources (still goes through `BaseBroker` in [services/broker_base.py](../broker_base.py); brokers vs broker_sources are intentionally separate concerns).
- Storing holdings in Postgres — current in-memory cache is enough until we hit multi-user. Persistence is a separate plan.
- Trying to monetise/distribute these scrapers; this is personal use only and we obey each platform's ToS rate-wise (≤ 1 sync per 5 min default).

## Open questions

- Wint Wealth: confirm the `api.wintwealth.com` host before P4 (do a one-time devtools capture).
- Groww MFA: is TOTP universally available, or are some accounts SMS-only? If SMS-only, route through the same `/otp` flow we built for Wint.
- Cookie/JWT cache location: `.cache/brokers/` works locally; revisit for the eventual server deploy (encrypted at rest, per the root [CLAUDE.md](../../../../CLAUDE.md) guardrail).

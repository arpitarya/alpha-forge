# Broker Sources — Setup & Usage

> Where to download each broker's CSV, where credentials go, and how to exercise the API end-to-end.

The portfolio module aggregates holdings from six sources. Each source is one of two kinds:

- **CSV** — user uploads an export. The broker offers no free API; this is the only legal path.
- **API** — pulled programmatically. Only Angel One falls in this bucket on the free tier.

| Source | Slug | Kind | Where to get the data |
|---|---|---|---|
| Zerodha (equities) | `zerodha` | CSV | [console.zerodha.com](https://console.zerodha.com) → **Holdings** → Download → CSV |
| Zerodha Coin (MF) | `zerodha-coin` | CSV | [coin.zerodha.com](https://coin.zerodha.com) → **Statements** → Holdings → CSV |
| Groww | `groww` | CSV | [groww.in](https://groww.in) → **Reports** → Holdings → Export (stocks **or** MF) |
| Dezerv | `dezerv` | CSV | Dezerv app → **Statements** → Holdings export |
| Wint Wealth | `wint-wealth` | CSV | Wint Wealth app → **Investments** → Export |
| Angel One | `angel-one` | API | [smartapi.angelbroking.com](https://smartapi.angelbroking.com) — register an app, see below |

> Disclaimer: Not SEBI registered investment advice. This module reads holdings only — no orders are placed.

---

## Why so many CSVs?

| Broker | Free public API? | Notes |
|---|---|---|
| Zerodha (Kite Connect) | **No** — ₹2000/mo per app | The Console CSV export is free + official. |
| Zerodha Coin | **No** | Same — only CSV. |
| Groww | **No** | Reverse-engineered endpoints exist; we don't ship them (ToS). |
| Dezerv | **No** public API. |
| Wint Wealth | **No** public API. |
| Angel One SmartAPI | **Yes** — free with an API key + TOTP. |

We chose the honest path: free + official + reproducible. As paid integrations get added (Kite Connect later, etc.), they slot into the same `BrokerSource` ABC without rewriting routes or the frontend.

---

## Angel One — SmartAPI setup

1. Create a SmartAPI app at <https://smartapi.angelbroking.com/>. Take note of the **API key**.
2. In the Angel One mobile app, go to **Profile → 2FA** and enable TOTP. Save the **base32 secret** (this is what `pyotp` consumes).
3. Add to `backend/.env`:

   ```bash
   ANGEL_ONE_API_KEY=<your_smartapi_key>
   ANGEL_ONE_CLIENT_CODE=<your_trading_client_id>   # e.g. ABCD12345
   ANGEL_ONE_PASSWORD=<login_pin_or_mpin>
   ANGEL_ONE_TOTP_SECRET=<base32_secret_from_step_2>
   ```

4. Install `pyotp` (lazy import — only needed for Angel One):

   ```bash
   cd backend && pdm add pyotp
   ```

5. Trigger a sync:

   ```bash
   curl -X POST http://localhost:8000/api/v1/portfolio/sources/angel-one/sync
   ```

If anything is missing, the source returns a `RuntimeError` listing the missing env vars — no silent fallback.

---

## Endpoints

All paths are prefixed with `/api/v1`.

### Read

| Method | Path | Description |
|---|---|---|
| `GET` | `/portfolio/holdings?source=<slug>` | Aggregated holdings + totals + allocation. Omit `source` for all. |
| `GET` | `/portfolio/treemap?source=<slug>` | Pre-computed treemap layout (left/top/width/height in %). |
| `GET` | `/portfolio/rebalance` | Drift vs target allocation + suggestions. |
| `GET` | `/portfolio/sources` | List all sources + status + last sync time. |
| `GET` | `/portfolio/sources/{slug}` | Single source info. |
| `GET` | `/portfolio/summary` | Legacy short shape (kept for backward compat). |

### Write

| Method | Path | Body | Description |
|---|---|---|---|
| `POST` | `/portfolio/sources/{slug}/upload` | multipart `file` | CSV ingest. Errors with 400 on API sources. |
| `POST` | `/portfolio/sources/{slug}/sync`   | — | Pull from upstream. Errors with 400 on CSV sources. |
| `POST` | `/portfolio/sources/{slug}/reset`  | — | Clear cached holdings (lets you re-upload). |

### Unified `Holding` shape

```json
{
  "source": "zerodha",
  "asset_class": "equity",
  "symbol": "RELIANCE",
  "name": null,
  "isin": "INE002A01018",
  "quantity": 120,
  "avg_price": 2410.0,
  "last_price": 2914.05,
  "invested": 289200.0,
  "current_value": 349686.0,
  "pnl": 60486.0,
  "pnl_pct": 20.91,
  "exchange": "NSE",
  "as_of": "2026-04-26T17:31:00+00:00"
}
```

---

## Dev workflows

### 1. Pytest suite (in-process, no server needed)

```bash
cd backend
pdm run pytest tests/test_brokers.py -v
```

Tests cover:
- Each CSV parser against a fixture export (column-shape resilience).
- `HoldingsAggregator` totals / allocation / treemap geometry / rebalance.
- All HTTP routes (`/sources`, `/upload`, `/sync`, `/holdings`, `/treemap`, `/rebalance`, `/reset`) via `TestClient`.

Add new fixtures to `backend/tests/fixtures/broker_csvs/` — the parser tests are organized one class per source so it's clear where to drop a new shape.

### 2. CLI smoke tester

```bash
# List sources
pdm run python scripts/dev_brokers.py sources

# Upload one CSV
pdm run python scripts/dev_brokers.py upload zerodha tests/fixtures/broker_csvs/zerodha_holdings.csv

# Upload all fixtures in one go (handy first-run check)
pdm run python scripts/dev_brokers.py upload-all

# Read aggregates
pdm run python scripts/dev_brokers.py holdings
pdm run python scripts/dev_brokers.py treemap --source zerodha
pdm run python scripts/dev_brokers.py rebalance

# Trigger Angel One pull (requires creds — see above)
pdm run python scripts/dev_brokers.py sync angel-one

# Reset
pdm run python scripts/dev_brokers.py reset zerodha
```

Override the API base via `AF_API`:

```bash
AF_API=http://localhost:8765/api/v1 pdm run python scripts/dev_brokers.py sources
```

### 3. Jupyter playground

```bash
cd backend && pdm run jupyter lab notebooks/portfolio_dev.ipynb
```

Toggle `MODE = "in_process"` ↔ `"http"` to switch between `TestClient` and a live server. Useful for parser debugging (in-process) vs CORS / frontend integration testing (http).

### 4. Frontend

The `/portfolio` page consumes the same endpoints via `useHoldings`, `useTreemap`, `useRebalance`, `useSources` hooks (see `frontend/src/lib/queries.ts`). Upload happens via `useUploadCsv`; the `<SourcesPanel/>` component renders a per-source row with an upload-or-sync button.

---

## Adding a new source

1. Create `backend/app/services/brokers/<your_source>.py` extending `BrokerSource`. Set `slug`, `label`, `kind`, and override **either** `parse(stream, filename)` (CSV) **or** `async fetch()` (API).
2. Register it in `backend/app/services/brokers/registry.py` (one line in `_build_sources()`).
3. Add a fixture CSV at `backend/tests/fixtures/broker_csvs/<source>_<kind>.csv` and a `Test<YourSource>Parser` class in `tests/test_brokers.py`.
4. Add an entry to the matrix at the top of this file.

That's it — the routes, aggregator, treemap layout, frontend `<SourcesPanel/>`, and CLI tester all pick it up automatically.

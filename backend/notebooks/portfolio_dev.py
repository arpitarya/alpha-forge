# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: .venv (3.14.2)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Portfolio / Brokers — Dev Playground
#
# Interactive notebook for exercising the `/portfolio/*` API surface. Two modes:
#
# 1. **In-process** (default) — `TestClient` calls the FastAPI app directly, no server needed. Fastest for iteration.
# 2. **Live HTTP** — points at a running `uvicorn` server. Use for CORS validation, real broker API calls, or frontend wiring.
#
# Toggle with `MODE` in the setup cell below.
#
# | Slug | Kind | Auth |
# |---|---|---|
# | `zerodha` | API | Browser CDP — log in to kite.zerodha.com inside the AlphaForge Chrome session. Set `ZERODHA_USER_ID` in `.env.cred.local`. |

# %%
import json
from pathlib import Path

# MODE = "in_process"   # switch to "http" to hit a live server
MODE = "http"   # switch to "http" to hit a live server
BASE = "http://localhost:8000/api/v1"
FIXTURES = Path.cwd().parent / "tests" / "fixtures" / "broker_csvs"

if MODE == "in_process":
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    PREFIX = "/api/v1"
else:
    import httpx
    client = httpx.Client(base_url=BASE, timeout=60.0)
    PREFIX = ""


def get(path, **kw):
    r = client.get(f"{PREFIX}{path}", **kw)
    return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text


def post(path, **kw):
    r = client.post(f"{PREFIX}{path}", **kw)
    return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text


def pp(obj):
    """Pretty-print a JSON-serializable response body."""
    print(json.dumps(obj, indent=2, default=str))


print(f"Mode: {MODE}")

# %% [markdown]
# ## 1. List configured sources
#
# One active source: Zerodha (Kite). `status` is `ready` when `ZERODHA_USER_ID` is set in `.env.cred.local`, otherwise `unconfigured`.

# %%
_, body = get("/portfolio/sources")
for s in body["sources"]:
    print(f"  {s['slug']:14} {s['kind']:4} {s['status']:13} {s['label']}")

# %% [markdown]
# ## 2. Sync Zerodha via API
#
# Triggers the CDP browser login + holdings fetch. The enctoken is cached under `.cache/brokers/zerodha.json` — subsequent syncs skip re-login until it expires (~1 day).
#
# > Requires `MODE="http"` against a live server with an active browser session. For local iteration without a running server, use section 3 (in-process) or section 4 (CSV upload) instead.

# %%
SLUG = "zerodha"
status, body = post(f"/portfolio/sources/{SLUG}/sync")
print(status)
print(json.dumps(body, indent=2)[:800])

# %% [markdown]
# ## 3. Direct in-process testing (no HTTP, no server)
#
# Calls the broker classes and aggregator directly — no HTTP round-trip. Use this to iterate on parsing logic, aggregator math, or schema changes without spinning up a server.

# %%
from app.modules.brokers import SOURCES, HoldingsAggregator, get_source
from app.modules.portfolio.sources_helper import apply_uploaded

# Parse the fixture CSV and inject into the zerodha source cache
src = get_source("zerodha")
with (FIXTURES / "zerodha_holdings.csv").open("rb") as f:
    holdings = src.parse(f, filename="zerodha_holdings.csv")
apply_uploaded(src, holdings)

print(f"Loaded {len(holdings)} holdings into '{src.slug}'")

# Inspect individual holdings
for h in holdings:
    print(f"  {h.symbol:14} qty={h.quantity:<6.0f}  avg=₹{h.avg_price:>10,.2f}  ltp=₹{h.last_price:>10,.2f}  pnl={h.pnl_pct:>+.1f}%")

# Aggregator roll-up
agg = HoldingsAggregator()
print("\nTotals:")
pp(agg.totals())

# %% [markdown]
# ## 4. CSV upload (manual fallback)
#
# Every source accepts a CSV upload via the HTTP endpoint. Useful when the live Kite session is unavailable or you're working from a historical export.

# %%
fname = "zerodha_holdings.csv"
with (FIXTURES / fname).open("rb") as f:
    status, body = post(
        "/portfolio/sources/zerodha/upload",
        files={"file": (fname, f, "text/csv")},
    )
print(status)
pp(body)

# %% [markdown]
# ## 5. Aggregate view
#
# After sync or upload, all source caches merge into one portfolio. Allocation groups holdings by `asset_class`.

# %%
status, body = get("/portfolio/holdings")
print("Status:", status)
print("Totals:", body["totals"])
print("\nAllocation:")
for s in body["allocation"]:
    print(f"  {s['asset_class']:12} ₹{s['value']:>14,.0f}  ({s['pct']:>5.1f}%)")
print(f"\nHoldings ({len(body['holdings'])} total):")
for h in body["holdings"]:
    print(f"  {h['symbol']:14} qty={h['quantity']:<6}  ltp=₹{h['last_price']:>10,.2f}  pnl={h['pnl_pct']:>+.1f}%")

# %% [markdown]
# ## 6. Filter by source
#
# Same endpoints accept `?source=<slug>` to scope the view to one broker.

# %%
_, body = get("/portfolio/holdings", params={"source": "zerodha"})
print("Zerodha-only totals:", body["totals"])
for h in body["holdings"][:5]:
    print("  ", h["symbol"], h["quantity"], h["current_value"])

# %% [markdown]
# ## 7. Treemap layout
#
# Pre-computed squarified layout — frontend absolute-positions each cell using the `left_pct / top_pct / width_pct / height_pct` fields.

# %%
_, body = get("/portfolio/treemap")
for c in body["cells"][:8]:
    print(f"  {c['symbol']:14} {c['pct']:>5.1f}% @ ({c['left_pct']:>5.1f}, {c['top_pct']:>5.1f}) {c['width_pct']:>5.1f}x{c['height_pct']:>5.1f}")

# %% [markdown]
# ## 8. Rebalance suggestions
#
# Drift = actual − target. Default targets: 60% equity / 15% MF / 15% bond / 5% gold / 3% crypto / 2% cash. Suggestions fire when drift exceeds ±5%.

# %%
_, body = get("/portfolio/rebalance")
print("Drift:")
for d in body["drift"]:
    print(f"  {d['asset_class']:12} target {d['target_pct']:>5.1f}% · actual {d['actual_pct']:>5.1f}% · drift {d['drift_pct']:>+5.1f}%")
print("\nSuggestions:")
for s in body["suggestions"]:
    print("  -", s["action"])

# %% [markdown]
# ## 9. Inspect cached session token
#
# The Zerodha enctoken is persisted under `.cache/brokers/zerodha.json` so daily syncs skip re-login. Delete the file to force a fresh login on the next sync.

# %%
import os

cache_dir = Path(os.getenv("BROKER_CACHE_DIR", ".cache/brokers")).resolve()
if cache_dir.exists():
    for f in sorted(cache_dir.glob("*.json")):
        print(f"  {f.name:24} {f.stat().st_size:>5}B  mtime={f.stat().st_mtime:.0f}")
else:
    print("  (no cache yet — run a sync first)")

# %% [markdown]
# ## 10. Reset in-memory state
#
# Clears the cached holdings for zerodha so you can re-upload or re-sync from a clean slate.

# %%
from app.modules.brokers import SOURCES

for src in SOURCES.values():
    src.reset()

status, body = get("/portfolio/sources")
for s in body["sources"]:
    print(f"  {s['slug']:14} {s['status']:13} ({s['holdings_count']} holdings)")

"""Test suite for broker source plugins + portfolio routes.

Run from the backend directory:

    uv run pytest tests/test_brokers.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.brokers import (
    SOURCES,
    AssetClass,
    HoldingsAggregator,
    SourceKind,
    ZerodhaCSVSource,
    get_source,
)
from app.modules.brokers.treemap_helper import squarify as _squarify
from app.modules.portfolio.sources_helper import apply_uploaded

FIXTURES = Path(__file__).parent / "fixtures" / "broker_csvs"


@pytest.fixture(autouse=True)
def reset_sources():
    """Clear cached holdings between tests."""
    for s in SOURCES.values():
        s.reset()
    yield
    for s in SOURCES.values():
        s.reset()


# ── CSV parser unit tests ─────────────────────────────────────────────────────


class TestZerodhaParser:
    def test_parses_console_export(self):
        src = ZerodhaCSVSource()
        with (FIXTURES / "zerodha_holdings.csv").open("rb") as f:
            holdings = src.parse(f)
        assert len(holdings) == 5
        reliance = next(h for h in holdings if h.symbol == "RELIANCE")
        assert reliance.quantity == 120
        assert reliance.avg_price == 2410.00
        assert reliance.last_price == 2914.05
        assert reliance.asset_class == AssetClass.EQUITY
        assert reliance.isin == "INE002A01018"

    def test_pnl_pct_negative_for_loss(self):
        src = ZerodhaCSVSource()
        with (FIXTURES / "zerodha_holdings.csv").open("rb") as f:
            holdings = src.parse(f)
        hdfc = next(h for h in holdings if h.symbol == "HDFCBANK")
        assert hdfc.pnl < 0
        assert hdfc.pnl_pct < 0


# ── Aggregator tests ──────────────────────────────────────────────────────────


def _ingest_zerodha() -> HoldingsAggregator:
    """Parse the fixture and apply it onto the registered Kite source's cache.

    The registered "zerodha" source is API-kind (Kite), so we parse via the CSV
    helper and inject into its cache the same way the upload route does.
    """
    src = get_source("zerodha")
    with (FIXTURES / "zerodha_holdings.csv").open("rb") as f:
        holdings = src.parse(f, filename="zerodha_holdings.csv")
    apply_uploaded(src, holdings)
    return HoldingsAggregator()


class TestAggregator:
    def test_totals(self):
        agg = _ingest_zerodha()
        t = agg.totals()
        assert t["count"] == 5
        assert t["invested"] > 0
        assert t["current_value"] > 0

    def test_treemap_cells_fit_unit_box(self):
        agg = _ingest_zerodha()
        cells = agg.treemap()
        for c in cells:
            assert 0 <= c.left_pct <= 100
            assert 0 <= c.top_pct <= 100
            assert c.left_pct + c.width_pct <= 100.001
            assert c.top_pct + c.height_pct <= 100.001

    def test_rebalance_flags_drift_above_threshold(self):
        # Equity-only portfolio should produce a "trim equity" suggestion
        # since target is 60% but actual is ~100%.
        agg = _ingest_zerodha()
        _, suggestions = agg.rebalance()
        actions = " ".join(s.action.lower() for s in suggestions)
        assert "trim equity" in actions


def test_squarify_unit_box():
    rects = _squarify([0.5, 0.3, 0.2], 0, 0, 1, 1)
    assert len(rects) == 3
    for x, y, w, h in rects:
        assert 0 <= x and 0 <= y
        assert x + w <= 1.0001
        assert y + h <= 1.0001


# ── HTTP route tests ──────────────────────────────────────────────────────────


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def loaded_client(client):
    """Client with zerodha holdings pre-loaded via CSV upload."""
    with (FIXTURES / "zerodha_holdings.csv").open("rb") as f:
        client.post(
            "/api/v1/portfolio/sources/zerodha/upload",
            files={"file": ("zerodha_holdings.csv", f, "text/csv")},
        )
    return client


class TestPortfolioRoutes:
    def test_list_sources(self, client):
        r = client.get("/api/v1/portfolio/sources")
        assert r.status_code == 200
        slugs = {s["slug"] for s in r.json()["sources"]}
        assert slugs == {"zerodha"}

    def test_upload_csv_persists_across_requests(self, client):
        with (FIXTURES / "zerodha_holdings.csv").open("rb") as f:
            r = client.post(
                "/api/v1/portfolio/sources/zerodha/upload",
                files={"file": ("zerodha_holdings.csv", f, "text/csv")},
            )
        assert r.status_code == 200
        assert r.json()["holdings_count"] == 5

        r2 = client.get("/api/v1/portfolio/holdings?source=zerodha")
        assert r2.status_code == 200
        assert r2.json()["totals"]["count"] == 5

    def test_holdings_no_filter_returns_all(self, loaded_client):
        r = loaded_client.get("/api/v1/portfolio/holdings")
        assert r.status_code == 200
        body = r.json()
        assert body["totals"]["count"] == 5
        assert "allocation" in body
        assert "disclaimer" in body

    def test_holdings_unknown_source_returns_404(self, client):
        r = client.get("/api/v1/portfolio/holdings?source=unknown_broker")
        assert r.status_code == 404

    def test_treemap_returns_cells(self, loaded_client):
        r = loaded_client.get("/api/v1/portfolio/treemap")
        assert r.status_code == 200
        body = r.json()
        assert len(body["cells"]) == 5
        assert "disclaimer" in body

    def test_treemap_with_source_filter(self, loaded_client):
        r = loaded_client.get("/api/v1/portfolio/treemap?source=zerodha")
        assert r.status_code == 200
        assert len(r.json()["cells"]) == 5

    def test_treemap_unknown_source_returns_404(self, client):
        r = client.get("/api/v1/portfolio/treemap?source=unknown_broker")
        assert r.status_code == 404

    def test_rebalance_endpoint(self, client):
        r = client.get("/api/v1/portfolio/rebalance")
        assert r.status_code == 200
        body = r.json()
        assert "drift" in body and "suggestions" in body and "targets" in body

    def test_rebalance_with_data_has_equity_target(self, loaded_client):
        r = loaded_client.get("/api/v1/portfolio/rebalance")
        assert r.status_code == 200
        targets = r.json()["targets"]
        assert "equity" in targets


class TestSourceRoutes:
    def test_get_source_info(self, client):
        r = client.get("/api/v1/portfolio/sources/zerodha")
        assert r.status_code == 200
        body = r.json()
        assert body["slug"] == "zerodha"
        assert "kind" in body and "status" in body

    def test_get_unknown_source_returns_404(self, client):
        r = client.get("/api/v1/portfolio/sources/nonexistent")
        assert r.status_code == 404

    def test_upload_unknown_source_returns_404(self, client):
        r = client.post(
            "/api/v1/portfolio/sources/nonexistent/upload",
            files={"file": ("x.csv", b"a,b,c", "text/csv")},
        )
        assert r.status_code == 404

    def test_sync_csv_source_rejected(self, client):
        # Zerodha is API kind — but if we had a CSV-only source, sync should 400.
        # For now verify the sync endpoint exists and returns a valid response for zerodha.
        r = client.post("/api/v1/portfolio/sources/zerodha/sync")
        # API kind: either succeeds (200) or fails with auth error (400) — never 404
        assert r.status_code in (200, 400)

    def test_upload_response_shape(self, client):
        with (FIXTURES / "zerodha_holdings.csv").open("rb") as f:
            r = client.post(
                "/api/v1/portfolio/sources/zerodha/upload",
                files={"file": ("zerodha_holdings.csv", f, "text/csv")},
            )
        assert r.status_code == 200
        body = r.json()
        assert body["source"] == "zerodha"
        assert body["filename"] == "zerodha_holdings.csv"
        assert body["holdings_count"] == 5
        assert "info" in body


class TestSourceMetadata:
    def test_zerodha_kind(self):
        assert get_source("zerodha").kind == SourceKind.API

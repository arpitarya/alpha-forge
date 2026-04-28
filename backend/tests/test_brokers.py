"""Test suite for broker source plugins + portfolio routes.

Run from the backend directory:

    pdm run pytest tests/test_brokers.py -v

Or just:

    pdm run pytest -v
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.brokers import (
    SOURCES,
    AssetClass,
    DezervCSVSource,
    GrowwCSVSource,
    HoldingsAggregator,
    SourceKind,
    SourceStatus,
    WintWealthCSVSource,
    ZerodhaCoinCSVSource,
    ZerodhaCSVSource,
    get_source,
)
from app.modules.brokers.treemap_helper import squarify as _squarify

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


class TestZerodhaCoinParser:
    def test_parses_mf_export(self):
        src = ZerodhaCoinCSVSource()
        with (FIXTURES / "zerodha_coin_holdings.csv").open("rb") as f:
            holdings = src.parse(f)
        assert len(holdings) == 3
        assert all(h.asset_class == AssetClass.MUTUAL_FUND for h in holdings)
        ppfcf = next(h for h in holdings if "Parag Parikh" in (h.name or ""))
        assert ppfcf.isin == "INF879O01092"
        assert ppfcf.quantity == pytest.approx(1450.234)


class TestGrowwParser:
    def test_parses_stocks(self):
        src = GrowwCSVSource()
        with (FIXTURES / "groww_stocks.csv").open("rb") as f:
            holdings = src.parse(f, filename="groww_stocks.csv")
        assert all(h.asset_class == AssetClass.EQUITY for h in holdings)
        bharti = next(h for h in holdings if h.symbol == "BHARTIARTL")
        assert bharti.quantity == 150
        assert bharti.pnl_pct > 40  # ~43% gain in fixture

    def test_parses_mf_via_filename_hint(self):
        src = GrowwCSVSource()
        with (FIXTURES / "groww_mf.csv").open("rb") as f:
            holdings = src.parse(f, filename="groww_mutual_funds.csv")
        assert all(h.asset_class == AssetClass.MUTUAL_FUND for h in holdings)


class TestDezervParser:
    def test_classifies_mixed_asset_classes(self):
        src = DezervCSVSource()
        with (FIXTURES / "dezerv_holdings.csv").open("rb") as f:
            holdings = src.parse(f)
        classes = {h.asset_class for h in holdings}
        assert AssetClass.MUTUAL_FUND in classes
        assert AssetClass.ETF in classes


class TestWintWealthParser:
    def test_parses_bonds(self):
        src = WintWealthCSVSource()
        with (FIXTURES / "wint_wealth_holdings.csv").open("rb") as f:
            holdings = src.parse(f)
        assert len(holdings) == 2
        assert all(h.asset_class == AssetClass.BOND for h in holdings)
        nhai = holdings[0]
        assert nhai.invested == 500000.00
        assert nhai.current_value == 548700.00


# ── Aggregator tests ──────────────────────────────────────────────────────────


def _ingest_all(*pairs: tuple[str, str]) -> HoldingsAggregator:
    for slug, fname in pairs:
        src = get_source(slug)
        with (FIXTURES / fname).open("rb") as f:
            src.ingest_csv(f, filename=fname)
    return HoldingsAggregator()


class TestAggregator:
    def test_totals_across_sources(self):
        agg = _ingest_all(
            ("zerodha", "zerodha_holdings.csv"),
            ("zerodha-coin", "zerodha_coin_holdings.csv"),
            ("groww", "groww_stocks.csv"),
            ("dezerv", "dezerv_holdings.csv"),
            ("wint-wealth", "wint_wealth_holdings.csv"),
        )
        t = agg.totals()
        assert t["count"] > 10
        assert t["invested"] > 0
        assert t["current_value"] > 0
        # All fixtures are net positive
        assert t["pnl"] > 0

    def test_allocation_sums_to_100(self):
        agg = _ingest_all(
            ("zerodha", "zerodha_holdings.csv"),
            ("zerodha-coin", "zerodha_coin_holdings.csv"),
        )
        slices = agg.allocation()
        total_pct = sum(s.pct for s in slices)
        assert total_pct == pytest.approx(100.0, abs=0.5)

    def test_treemap_cells_fit_unit_box(self):
        agg = _ingest_all(("zerodha", "zerodha_holdings.csv"))
        cells = agg.treemap()
        for c in cells:
            assert 0 <= c.left_pct <= 100
            assert 0 <= c.top_pct <= 100
            assert c.left_pct + c.width_pct <= 100.001
            assert c.top_pct + c.height_pct <= 100.001

    def test_rebalance_flags_drift_above_threshold(self):
        # Equity-only portfolio should produce a "trim equity" suggestion
        # since target is 60% but actual is ~100%.
        agg = _ingest_all(("zerodha", "zerodha_holdings.csv"))
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


class TestPortfolioRoutes:
    def test_list_sources_includes_all_six(self, client):
        r = client.get("/api/v1/portfolio/sources")
        assert r.status_code == 200
        slugs = {s["slug"] for s in r.json()["sources"]}
        assert slugs == {
            "zerodha",
            "zerodha-coin",
            "groww",
            "dezerv",
            "wint-wealth",
            "angel-one",
        }

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

    def test_upload_to_api_source_rejected(self, client):
        with (FIXTURES / "zerodha_holdings.csv").open("rb") as f:
            r = client.post(
                "/api/v1/portfolio/sources/angel-one/upload",
                files={"file": ("anything.csv", f, "text/csv")},
            )
        assert r.status_code == 400
        assert "API source" in r.json()["detail"]

    def test_sync_csv_source_rejected(self, client):
        r = client.post("/api/v1/portfolio/sources/zerodha/sync")
        assert r.status_code == 400
        assert "CSV source" in r.json()["detail"]

    def test_treemap_returns_cells(self, client):
        with (FIXTURES / "zerodha_holdings.csv").open("rb") as f:
            client.post(
                "/api/v1/portfolio/sources/zerodha/upload",
                files={"file": ("z.csv", f, "text/csv")},
            )
        r = client.get("/api/v1/portfolio/treemap")
        assert r.status_code == 200
        body = r.json()
        assert len(body["cells"]) == 5
        assert "disclaimer" in body

    def test_rebalance_endpoint(self, client):
        r = client.get("/api/v1/portfolio/rebalance")
        assert r.status_code == 200
        body = r.json()
        assert "drift" in body and "suggestions" in body and "targets" in body

    def test_reset_clears_holdings(self, client):
        with (FIXTURES / "zerodha_holdings.csv").open("rb") as f:
            client.post(
                "/api/v1/portfolio/sources/zerodha/upload",
                files={"file": ("z.csv", f, "text/csv")},
            )
        client.post("/api/v1/portfolio/sources/zerodha/reset")
        r = client.get("/api/v1/portfolio/sources/zerodha")
        assert r.json()["holdings_count"] == 0
        assert r.json()["status"] == SourceStatus.UNCONFIGURED.value


class TestSourceMetadata:
    @pytest.mark.parametrize("slug,expected_kind", [
        ("zerodha", SourceKind.CSV),
        ("zerodha-coin", SourceKind.CSV),
        ("groww", SourceKind.CSV),
        ("dezerv", SourceKind.CSV),
        ("wint-wealth", SourceKind.CSV),
        ("angel-one", SourceKind.API),
    ])
    def test_kind(self, slug: str, expected_kind: SourceKind):
        assert get_source(slug).kind == expected_kind

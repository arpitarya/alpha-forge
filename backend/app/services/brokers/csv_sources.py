"""CSV-based broker sources.

Each source class declares its expected columns + a small mapping from header
aliases → unified Holding fields. We're tolerant by design: brokers tweak
their CSV layouts often, and we want users to be able to drop in last
month's export without us shipping a release.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import csv
import io
from typing import IO

from app.services.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _to_float(value: object, default: float = 0.0) -> float:
    """Forgiving float parser — handles empty, currency symbols, commas."""
    if value is None:
        return default
    s = str(value).strip().replace(",", "").replace("₹", "").replace("$", "")
    if not s or s.lower() in {"-", "n/a", "na", "—"}:
        return default
    try:
        return float(s)
    except ValueError:
        return default


def _to_int(value: object, default: int = 0) -> int:
    return int(_to_float(value, default))


def _read_csv(stream: IO[bytes]) -> list[dict[str, str]]:
    """Decode + parse a CSV stream into a list of header-keyed dicts.

    Skips fully empty rows and trims whitespace from headers + values.
    """
    raw = stream.read().decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(raw))
    rows: list[dict[str, str]] = []
    for row in reader:
        if not row:
            continue
        cleaned = {(k or "").strip(): (v or "").strip() for k, v in row.items() if k}
        if any(cleaned.values()):
            rows.append(cleaned)
    return rows


def _pick(row: dict[str, str], *aliases: str, default: str = "") -> str:
    """Return the first non-empty value among `aliases` (case-insensitive)."""
    lowered = {k.lower(): v for k, v in row.items()}
    for a in aliases:
        v = lowered.get(a.lower())
        if v:
            return v
    return default


# ── Zerodha (Kite/Console) ────────────────────────────────────────────────────


class ZerodhaCSVSource(BrokerSource):
    """Zerodha equity holdings — exported from console.zerodha.com → Holdings.

    Expected columns (Console CSV, 2024+):
        Symbol, Quantity, Average Price, Previous Closing Price,
        Last Traded Price, Current Value, P&L, ISIN.
    """

    slug = "zerodha"
    label = "Zerodha (Kite Console)"
    kind = SourceKind.CSV
    notes = "Export via console.zerodha.com → Holdings → Download → CSV"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:  # noqa: ARG002
        out: list[Holding] = []
        for row in _read_csv(stream):
            symbol = _pick(row, "Symbol", "Tradingsymbol", "Instrument").upper()
            if not symbol:
                continue
            qty = _to_float(_pick(row, "Quantity", "Qty"))
            avg = _to_float(_pick(row, "Average Price", "Avg. Price", "Avg Price"))
            ltp = _to_float(_pick(row, "Last Traded Price", "LTP", "Current Price"))
            invested = qty * avg
            current_value = _to_float(_pick(row, "Current Value", "Mkt Value"), invested) or qty * ltp
            pnl = _to_float(_pick(row, "P&L", "PnL", "Unrealized P&L"), current_value - invested)
            pnl_pct = (pnl / invested * 100) if invested else 0.0

            out.append(
                Holding(
                    source=self.slug,
                    asset_class=AssetClass.EQUITY,
                    symbol=symbol,
                    isin=_pick(row, "ISIN") or None,
                    quantity=qty,
                    avg_price=avg,
                    last_price=ltp or (current_value / qty if qty else 0.0),
                    invested=invested,
                    current_value=current_value,
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                    exchange=_pick(row, "Exchange") or "NSE",
                )
            )
        return out


# ── Zerodha Coin (mutual funds) ───────────────────────────────────────────────


class ZerodhaCoinCSVSource(BrokerSource):
    """Mutual fund holdings from Coin → Statements → Holdings (CSV)."""

    slug = "zerodha-coin"
    label = "Zerodha Coin"
    kind = SourceKind.CSV
    notes = "Export via coin.zerodha.com → Statements → Holdings → CSV"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:  # noqa: ARG002
        out: list[Holding] = []
        for row in _read_csv(stream):
            scheme = _pick(row, "Scheme Name", "Scheme", "Fund")
            isin = _pick(row, "ISIN")
            if not (scheme or isin):
                continue
            units = _to_float(_pick(row, "Units", "Total Units"))
            avg_nav = _to_float(_pick(row, "Avg. NAV", "Avg NAV", "Average NAV"))
            ltp_nav = _to_float(_pick(row, "Current NAV", "NAV", "Latest NAV"))
            invested = _to_float(_pick(row, "Invested", "Invested Value"), units * avg_nav)
            current_value = _to_float(_pick(row, "Current Value", "Market Value"), units * ltp_nav)
            pnl = _to_float(_pick(row, "P&L", "Returns", "Unrealised P&L"), current_value - invested)
            pnl_pct = (pnl / invested * 100) if invested else 0.0
            out.append(
                Holding(
                    source=self.slug,
                    asset_class=AssetClass.MUTUAL_FUND,
                    symbol=isin or scheme[:24],
                    name=scheme or None,
                    isin=isin or None,
                    quantity=units,
                    avg_price=avg_nav,
                    last_price=ltp_nav,
                    invested=invested,
                    current_value=current_value,
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                )
            )
        return out


# ── Groww ─────────────────────────────────────────────────────────────────────


class GrowwCSVSource(BrokerSource):
    """Groww holdings — Reports → Holdings → Export.

    Groww emits separate Stocks vs Mutual Funds CSVs; we infer asset class
    from the columns present.
    """

    slug = "groww"
    label = "Groww"
    kind = SourceKind.CSV
    notes = "Export via groww.in → Reports → Holdings → CSV (stocks or MF)"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        out: list[Holding] = []
        rows = _read_csv(stream)
        # Infer asset class from filename hint or column names
        is_mf = (
            (filename and "mutual" in filename.lower())
            or any("scheme" in (k or "").lower() for k in (rows[0].keys() if rows else []))
        )
        for row in rows:
            if is_mf:
                scheme = _pick(row, "Scheme Name", "Scheme")
                if not scheme:
                    continue
                units = _to_float(_pick(row, "Units"))
                avg_nav = _to_float(_pick(row, "Average NAV", "Avg NAV"))
                ltp_nav = _to_float(_pick(row, "Current NAV", "NAV"))
                invested = _to_float(_pick(row, "Invested Amount", "Invested"), units * avg_nav)
                current_value = _to_float(
                    _pick(row, "Current Value", "Current Amount"), units * ltp_nav
                )
                pnl = _to_float(_pick(row, "Returns", "P&L"), current_value - invested)
                out.append(
                    Holding(
                        source=self.slug,
                        asset_class=AssetClass.MUTUAL_FUND,
                        symbol=_pick(row, "ISIN") or scheme[:24],
                        name=scheme,
                        isin=_pick(row, "ISIN") or None,
                        quantity=units,
                        avg_price=avg_nav,
                        last_price=ltp_nav,
                        invested=invested,
                        current_value=current_value,
                        pnl=pnl,
                        pnl_pct=(pnl / invested * 100) if invested else 0.0,
                    )
                )
            else:
                symbol = _pick(row, "Stock Name", "Symbol", "Company Name").upper()
                if not symbol:
                    continue
                qty = _to_float(_pick(row, "Quantity", "Qty"))
                avg = _to_float(_pick(row, "Average Buy Price", "Avg. Price", "Avg Price"))
                ltp = _to_float(_pick(row, "Current Price", "LTP"))
                invested = _to_float(_pick(row, "Invested Amount"), qty * avg)
                current_value = _to_float(_pick(row, "Current Value"), qty * ltp)
                pnl = _to_float(_pick(row, "Returns", "P&L"), current_value - invested)
                out.append(
                    Holding(
                        source=self.slug,
                        asset_class=AssetClass.EQUITY,
                        symbol=symbol,
                        name=_pick(row, "Stock Name", "Company Name") or None,
                        isin=_pick(row, "ISIN") or None,
                        quantity=qty,
                        avg_price=avg,
                        last_price=ltp,
                        invested=invested,
                        current_value=current_value,
                        pnl=pnl,
                        pnl_pct=(pnl / invested * 100) if invested else 0.0,
                        exchange=_pick(row, "Exchange") or "NSE",
                    )
                )
        return out


# ── Dezerv ────────────────────────────────────────────────────────────────────


class DezervCSVSource(BrokerSource):
    """Dezerv portfolio export.

    Dezerv exports a flat statement; we only care about rows tagged as
    holdings (skip transactions). Asset class column is reliable.
    """

    slug = "dezerv"
    label = "Dezerv"
    kind = SourceKind.CSV
    notes = "Export via Dezerv app → Statements → Holdings"

    _CLASS_MAP = {
        "equity": AssetClass.EQUITY,
        "mutual fund": AssetClass.MUTUAL_FUND,
        "mf": AssetClass.MUTUAL_FUND,
        "etf": AssetClass.ETF,
        "bond": AssetClass.BOND,
        "fd": AssetClass.BOND,
        "gold": AssetClass.GOLD,
        "cash": AssetClass.CASH,
    }

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:  # noqa: ARG002
        out: list[Holding] = []
        for row in _read_csv(stream):
            name = _pick(row, "Instrument Name", "Scheme Name", "Name")
            if not name:
                continue
            cls_raw = _pick(row, "Asset Class", "Type", "Category").lower()
            asset_class = self._CLASS_MAP.get(cls_raw, AssetClass.OTHER)
            qty = _to_float(_pick(row, "Units", "Quantity"))
            avg = _to_float(_pick(row, "Average Cost", "Avg Price", "Avg NAV"))
            ltp = _to_float(_pick(row, "Current NAV", "Current Price", "LTP"))
            invested = _to_float(_pick(row, "Invested Amount", "Invested"), qty * avg)
            current_value = _to_float(_pick(row, "Current Value", "Market Value"), qty * ltp)
            pnl = _to_float(_pick(row, "Unrealized P&L", "Returns", "Gain/Loss"), current_value - invested)
            out.append(
                Holding(
                    source=self.slug,
                    asset_class=asset_class,
                    symbol=_pick(row, "ISIN") or name[:24],
                    name=name,
                    isin=_pick(row, "ISIN") or None,
                    quantity=qty,
                    avg_price=avg,
                    last_price=ltp,
                    invested=invested,
                    current_value=current_value,
                    pnl=pnl,
                    pnl_pct=(pnl / invested * 100) if invested else 0.0,
                )
            )
        return out


# ── Wint Wealth (bonds) ───────────────────────────────────────────────────────


class WintWealthCSVSource(BrokerSource):
    """Wint Wealth bond holdings export."""

    slug = "wint-wealth"
    label = "Wint Wealth"
    kind = SourceKind.CSV
    notes = "Export via Wint Wealth app → Investments → Export"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:  # noqa: ARG002
        out: list[Holding] = []
        for row in _read_csv(stream):
            name = _pick(row, "Bond Name", "Instrument", "Name", "Issuer")
            if not name:
                continue
            qty = _to_float(_pick(row, "Units", "Face Value Held", "Quantity"))
            invested = _to_float(_pick(row, "Investment Amount", "Invested"))
            current_value = _to_float(_pick(row, "Current Value", "Market Value"), invested)
            avg = invested / qty if qty else 0.0
            ltp = current_value / qty if qty else 0.0
            pnl = current_value - invested
            out.append(
                Holding(
                    source=self.slug,
                    asset_class=AssetClass.BOND,
                    symbol=_pick(row, "ISIN") or name[:24],
                    name=name,
                    isin=_pick(row, "ISIN") or None,
                    quantity=qty,
                    avg_price=avg,
                    last_price=ltp,
                    invested=invested,
                    current_value=current_value,
                    pnl=pnl,
                    pnl_pct=(pnl / invested * 100) if invested else 0.0,
                )
            )
        return out

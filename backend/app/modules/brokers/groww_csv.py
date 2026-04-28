"""Groww holdings CSV source — accepts both stocks and MF exports."""

from __future__ import annotations

from typing import IO

from app.modules.brokers._csv_helper import pick, read_csv, to_float
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind


def _is_mf_export(rows: list[dict[str, str]], filename: str | None) -> bool:
    if filename and "mutual" in filename.lower():
        return True
    return any("scheme" in (k or "").lower() for k in (rows[0].keys() if rows else []))


def _parse_mf(row: dict[str, str], slug: str) -> Holding | None:
    scheme = pick(row, "Scheme Name", "Scheme")
    if not scheme:
        return None
    units = to_float(pick(row, "Units"))
    avg_nav = to_float(pick(row, "Average NAV", "Avg NAV"))
    ltp_nav = to_float(pick(row, "Current NAV", "NAV"))
    invested = to_float(pick(row, "Invested Amount", "Invested"), units * avg_nav)
    current_value = to_float(pick(row, "Current Value", "Current Amount"), units * ltp_nav)
    pnl = to_float(pick(row, "Returns", "P&L"), current_value - invested)
    return Holding(
        source=slug,
        asset_class=AssetClass.MUTUAL_FUND,
        symbol=pick(row, "ISIN") or scheme[:24],
        name=scheme,
        isin=pick(row, "ISIN") or None,
        quantity=units,
        avg_price=avg_nav,
        last_price=ltp_nav,
        invested=invested,
        current_value=current_value,
        pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
    )


def _parse_equity(row: dict[str, str], slug: str) -> Holding | None:
    symbol = pick(row, "Stock Name", "Symbol", "Company Name").upper()
    if not symbol:
        return None
    qty = to_float(pick(row, "Quantity", "Qty"))
    avg = to_float(pick(row, "Average Buy Price", "Avg. Price", "Avg Price"))
    ltp = to_float(pick(row, "Current Price", "LTP"))
    invested = to_float(pick(row, "Invested Amount"), qty * avg)
    current_value = to_float(pick(row, "Current Value"), qty * ltp)
    pnl = to_float(pick(row, "Returns", "P&L"), current_value - invested)
    return Holding(
        source=slug,
        asset_class=AssetClass.EQUITY,
        symbol=symbol,
        name=pick(row, "Stock Name", "Company Name") or None,
        isin=pick(row, "ISIN") or None,
        quantity=qty,
        avg_price=avg,
        last_price=ltp,
        invested=invested,
        current_value=current_value,
        pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
        exchange=pick(row, "Exchange") or "NSE",
    )


class GrowwCSVSource(BrokerSource):
    slug = "groww"
    label = "Groww"
    kind = SourceKind.CSV
    notes = "Export via groww.in → Reports → Holdings → CSV (stocks or MF)"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        rows = read_csv(stream)
        is_mf = _is_mf_export(rows, filename)
        out: list[Holding] = []
        for row in rows:
            h = _parse_mf(row, self.slug) if is_mf else _parse_equity(row, self.slug)
            if h:
                out.append(h)
        return out

"""Dezerv portfolio CSV source — flat statement export."""

from __future__ import annotations

from typing import IO

from app.modules.brokers._csv_helper import pick, read_csv, to_float
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind

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


class DezervCSVSource(BrokerSource):
    slug = "dezerv"
    label = "Dezerv"
    kind = SourceKind.CSV
    notes = "Export via Dezerv app → Statements → Holdings"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:  # noqa: ARG002
        out: list[Holding] = []
        for row in read_csv(stream):
            name = pick(row, "Instrument Name", "Scheme Name", "Name")
            if not name:
                continue
            cls_raw = pick(row, "Asset Class", "Type", "Category").lower()
            asset_class = _CLASS_MAP.get(cls_raw, AssetClass.OTHER)
            qty = to_float(pick(row, "Units", "Quantity"))
            avg = to_float(pick(row, "Average Cost", "Avg Price", "Avg NAV"))
            ltp = to_float(pick(row, "Current NAV", "Current Price", "LTP"))
            invested = to_float(pick(row, "Invested Amount", "Invested"), qty * avg)
            current_value = to_float(pick(row, "Current Value", "Market Value"), qty * ltp)
            pnl = to_float(
                pick(row, "Unrealized P&L", "Returns", "Gain/Loss"),
                current_value - invested,
            )
            out.append(
                Holding(
                    source=self.slug,
                    asset_class=asset_class,
                    symbol=pick(row, "ISIN") or name[:24],
                    name=name,
                    isin=pick(row, "ISIN") or None,
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

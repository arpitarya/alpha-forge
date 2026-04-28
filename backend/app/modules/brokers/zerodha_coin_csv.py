"""Zerodha Coin mutual-fund holdings CSV source."""

from __future__ import annotations

from typing import IO

from app.modules.brokers._csv_helper import pick, read_csv, to_float
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind


class ZerodhaCoinCSVSource(BrokerSource):
    slug = "zerodha-coin"
    label = "Zerodha Coin"
    kind = SourceKind.CSV
    notes = "Export via coin.zerodha.com → Statements → Holdings → CSV"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:  # noqa: ARG002
        out: list[Holding] = []
        for row in read_csv(stream):
            scheme = pick(row, "Scheme Name", "Scheme", "Fund")
            isin = pick(row, "ISIN")
            if not (scheme or isin):
                continue
            units = to_float(pick(row, "Units", "Total Units"))
            avg_nav = to_float(pick(row, "Avg. NAV", "Avg NAV", "Average NAV"))
            ltp_nav = to_float(pick(row, "Current NAV", "NAV", "Latest NAV"))
            invested = to_float(pick(row, "Invested", "Invested Value"), units * avg_nav)
            current_value = to_float(
                pick(row, "Current Value", "Market Value"), units * ltp_nav
            )
            pnl = to_float(
                pick(row, "P&L", "Returns", "Unrealised P&L"), current_value - invested
            )
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
                    pnl_pct=(pnl / invested * 100) if invested else 0.0,
                )
            )
        return out

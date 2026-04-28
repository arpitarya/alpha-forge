"""Wint Wealth bond holdings CSV source."""

from __future__ import annotations

from typing import IO

from app.modules.brokers._csv_helper import pick, read_csv, to_float
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind


class WintWealthCSVSource(BrokerSource):
    slug = "wint-wealth"
    label = "Wint Wealth"
    kind = SourceKind.CSV
    notes = "Export via Wint Wealth app → Investments → Export"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:  # noqa: ARG002
        out: list[Holding] = []
        for row in read_csv(stream):
            name = pick(row, "Bond Name", "Instrument", "Name", "Issuer")
            if not name:
                continue
            qty = to_float(pick(row, "Units", "Face Value Held", "Quantity"))
            invested = to_float(pick(row, "Investment Amount", "Invested"))
            current_value = to_float(pick(row, "Current Value", "Market Value"), invested)
            avg = invested / qty if qty else 0.0
            ltp = current_value / qty if qty else 0.0
            pnl = current_value - invested
            out.append(
                Holding(
                    source=self.slug,
                    asset_class=AssetClass.BOND,
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

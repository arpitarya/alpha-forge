"""Groww API row → Holding mappers."""

from __future__ import annotations

from typing import Any

from app.modules.brokers.base import AssetClass, Holding


def map_stock(r: dict[str, Any]) -> Holding:
    qty = float(r.get("quantity") or r.get("holding_quantity") or 0)
    avg = float(r.get("average_price") or r.get("avg_price") or 0)
    ltp = float(r.get("ltp") or r.get("current_price") or 0)
    invested, current = qty * avg, qty * ltp
    pnl = current - invested
    sym = str(r.get("nse_scrip_code") or r.get("symbol") or r.get("trading_symbol") or "").upper()
    return Holding(
        source="groww", asset_class=AssetClass.EQUITY, symbol=sym,
        name=r.get("company_name") or r.get("name"), isin=r.get("isin"),
        quantity=qty, avg_price=avg, last_price=ltp,
        invested=invested, current_value=current, pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
        exchange=r.get("exchange") or "NSE",
    )


def map_mf(r: dict[str, Any]) -> Holding:
    units = float(r.get("units") or r.get("total_units") or 0)
    avg_nav = float(r.get("average_nav") or r.get("avg_nav") or 0)
    ltp_nav = float(r.get("nav") or r.get("current_nav") or 0)
    invested = float(r.get("invested_amount") or units * avg_nav)
    current = float(r.get("current_value") or units * ltp_nav)
    pnl = current - invested
    scheme = r.get("scheme_name") or r.get("name") or ""
    return Holding(
        source="groww", asset_class=AssetClass.MUTUAL_FUND,
        symbol=str(r.get("isin") or scheme[:24]),
        name=scheme or None, isin=r.get("isin"),
        quantity=units, avg_price=avg_nav, last_price=ltp_nav,
        invested=invested, current_value=current, pnl=pnl,
        pnl_pct=(pnl / invested * 100) if invested else 0.0,
    )

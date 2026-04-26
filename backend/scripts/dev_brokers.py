#!/usr/bin/env python
"""Interactive CLI for the broker / portfolio API surface.

A thin wrapper around httpx that lets you exercise every endpoint without
leaving the terminal — useful while developing a new broker source or
debugging a CSV parser.

Usage (backend running on :8000):

    pdm run python scripts/dev_brokers.py sources
    pdm run python scripts/dev_brokers.py upload zerodha tests/fixtures/broker_csvs/zerodha_holdings.csv
    pdm run python scripts/dev_brokers.py upload-all
    pdm run python scripts/dev_brokers.py sync angel-one
    pdm run python scripts/dev_brokers.py holdings
    pdm run python scripts/dev_brokers.py treemap
    pdm run python scripts/dev_brokers.py rebalance
    pdm run python scripts/dev_brokers.py reset zerodha

Override the base URL via env var:

    AF_API=http://localhost:8765 pdm run python scripts/dev_brokers.py sources
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

DEFAULT_BASE = os.getenv("AF_API", "http://localhost:8000/api/v1")
FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "broker_csvs"

# Map source slug → fixture filename for `upload-all`
FIXTURE_MAP = {
    "zerodha": "zerodha_holdings.csv",
    "zerodha-coin": "zerodha_coin_holdings.csv",
    "groww": "groww_stocks.csv",
    "dezerv": "dezerv_holdings.csv",
    "wint-wealth": "wint_wealth_holdings.csv",
}


def _pretty(obj: object) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


def cmd_sources(client: httpx.Client) -> None:
    r = client.get("/portfolio/sources")
    r.raise_for_status()
    print(_pretty(r.json()))


def cmd_upload(client: httpx.Client, slug: str, csv_path: str) -> None:
    path = Path(csv_path)
    if not path.exists():
        sys.exit(f"file not found: {csv_path}")
    with path.open("rb") as f:
        r = client.post(
            f"/portfolio/sources/{slug}/upload",
            files={"file": (path.name, f, "text/csv")},
        )
    print(f"[{r.status_code}] {r.url}")
    print(_pretty(r.json()))


def cmd_upload_all(client: httpx.Client) -> None:
    for slug, filename in FIXTURE_MAP.items():
        path = FIXTURES / filename
        if not path.exists():
            print(f"  skip {slug} — fixture missing")
            continue
        with path.open("rb") as f:
            r = client.post(
                f"/portfolio/sources/{slug}/upload",
                files={"file": (path.name, f, "text/csv")},
            )
        if r.is_success:
            count = r.json().get("holdings_count", 0)
            print(f"  ✓ {slug:14} {count} holdings")
        else:
            print(f"  ✗ {slug:14} {r.status_code} {r.text[:120]}")


def cmd_sync(client: httpx.Client, slug: str) -> None:
    r = client.post(f"/portfolio/sources/{slug}/sync")
    print(f"[{r.status_code}] {r.url}")
    try:
        print(_pretty(r.json()))
    except Exception:
        print(r.text)


def cmd_holdings(client: httpx.Client, source: str | None) -> None:
    r = client.get("/portfolio/holdings", params={"source": source} if source else None)
    r.raise_for_status()
    print(_pretty(r.json()))


def cmd_treemap(client: httpx.Client, source: str | None) -> None:
    r = client.get("/portfolio/treemap", params={"source": source} if source else None)
    r.raise_for_status()
    print(_pretty(r.json()))


def cmd_rebalance(client: httpx.Client) -> None:
    r = client.get("/portfolio/rebalance")
    r.raise_for_status()
    print(_pretty(r.json()))


def cmd_reset(client: httpx.Client, slug: str) -> None:
    r = client.post(f"/portfolio/sources/{slug}/reset")
    print(f"[{r.status_code}] {r.url}")
    print(_pretty(r.json()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", default=DEFAULT_BASE, help=f"API base URL (default: {DEFAULT_BASE})")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("sources", help="List all configured broker sources + status")

    p_upload = sub.add_parser("upload", help="Upload a CSV to one source")
    p_upload.add_argument("slug")
    p_upload.add_argument("csv_path")

    sub.add_parser("upload-all", help="Upload every fixture CSV (handy smoke test)")

    p_sync = sub.add_parser("sync", help="Trigger an API source pull")
    p_sync.add_argument("slug")

    p_holdings = sub.add_parser("holdings", help="Get aggregated holdings")
    p_holdings.add_argument("--source", default=None)

    p_treemap = sub.add_parser("treemap", help="Get treemap layout")
    p_treemap.add_argument("--source", default=None)

    sub.add_parser("rebalance", help="Get drift + suggestions")

    p_reset = sub.add_parser("reset", help="Clear cached holdings for a source")
    p_reset.add_argument("slug")

    args = parser.parse_args()
    client = httpx.Client(base_url=args.base, timeout=30.0)

    try:
        if args.cmd == "sources":
            cmd_sources(client)
        elif args.cmd == "upload":
            cmd_upload(client, args.slug, args.csv_path)
        elif args.cmd == "upload-all":
            cmd_upload_all(client)
        elif args.cmd == "sync":
            cmd_sync(client, args.slug)
        elif args.cmd == "holdings":
            cmd_holdings(client, args.source)
        elif args.cmd == "treemap":
            cmd_treemap(client, args.source)
        elif args.cmd == "rebalance":
            cmd_rebalance(client)
        elif args.cmd == "reset":
            cmd_reset(client, args.slug)
    finally:
        client.close()


if __name__ == "__main__":
    main()

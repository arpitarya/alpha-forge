"""Screener service — manages screener picks storage and retrieval.

Bridges the standalone screener module with the AlphaForge backend API.
Picks are stored as JSON files on disk (no DB dependency for v1).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from app.core.logging import get_logger

logger = get_logger("services.screener")

# Picks storage directory (inside backend data, separate from screener module)
PICKS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "screener" / "live" / "picks"
PICKS_DIR.mkdir(parents=True, exist_ok=True)


class ScreenerService:
    """Manage screener pick results for the AlphaForge API."""

    def __init__(self) -> None:
        self._picks_dir = PICKS_DIR

    async def save_picks(self, scan_date: str, model_type: str, picks: list[dict]) -> dict:
        """Save screener picks from a scan run."""
        filename = f"{scan_date}_{model_type}_picks.json"
        filepath = self._picks_dir / filename

        payload = {
            "scan_date": scan_date,
            "model_type": model_type,
            "count": len(picks),
            "picks": picks,
        }

        filepath.write_text(json.dumps(payload, indent=2))
        logger.info("Saved %d picks to %s", len(picks), filename)
        return {"status": "ok", "file": filename, "count": len(picks)}

    async def get_picks(self, scan_date: str | None = None) -> dict:
        """Retrieve picks for a given date (or latest available)."""
        if scan_date:
            # Look for exact date match
            matches = list(self._picks_dir.glob(f"{scan_date}_*_picks.json"))
        else:
            # Get latest available
            matches = sorted(self._picks_dir.glob("*_picks.json"))

        if not matches:
            # Fallback: try CSV files from the screener module
            csv_matches = sorted(self._picks_dir.glob("*_weekly_picks.csv"))
            if csv_matches:
                import csv

                latest = csv_matches[-1]
                logger.info("Loading picks from CSV: %s", latest.name)
                picks = []
                with open(latest) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        picks.append(row)
                return {
                    "scan_date": latest.stem.split("_")[0],
                    "model_type": "csv",
                    "count": len(picks),
                    "picks": picks,
                }
            return {"scan_date": scan_date or str(date.today()), "picks": [], "count": 0}

        latest = matches[-1]
        data = json.loads(latest.read_text())
        logger.info("Loaded %d picks from %s", len(data.get("picks", [])), latest.name)
        return data

    async def list_scan_dates(self) -> list[str]:
        """List all available scan dates."""
        dates = set()
        for f in self._picks_dir.glob("*_picks.*"):
            # Extract date from filename like "2026-04-07_lightgbm_picks.json"
            parts = f.stem.split("_")
            if parts and len(parts[0]) == 10:  # YYYY-MM-DD
                dates.add(parts[0])
        return sorted(dates, reverse=True)

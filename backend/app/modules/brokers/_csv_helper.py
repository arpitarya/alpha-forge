"""CSV parsing helpers shared by every CSV broker source."""

from __future__ import annotations

import csv
import io
from typing import IO


def to_float(value: object, default: float = 0.0) -> float:
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


def to_int(value: object, default: int = 0) -> int:
    return int(to_float(value, default))


def read_csv(stream: IO[bytes]) -> list[dict[str, str]]:
    """Decode + parse a CSV stream into a list of header-keyed dicts."""
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


def pick(row: dict[str, str], *aliases: str, default: str = "") -> str:
    """Return the first non-empty value among `aliases` (case-insensitive)."""
    lowered = {k.lower(): v for k, v in row.items()}
    for a in aliases:
        v = lowered.get(a.lower())
        if v:
            return v
    return default

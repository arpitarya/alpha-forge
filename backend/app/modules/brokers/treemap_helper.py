"""Squarified-treemap layout — pure geometry, no domain dependencies."""

from __future__ import annotations


def squarify(
    values: list[float], x: float, y: float, w: float, h: float
) -> list[tuple[float, float, float, float]]:
    """Squarified treemap layout. Returns (left, top, width, height) per value."""
    if not values or w <= 0 or h <= 0:
        return []
    if len(values) == 1:
        return [(x, y, w, h)]
    total = sum(values)
    if total <= 0:
        return [(x, y, 0, 0) for _ in values]

    along_w = w >= h
    short_side = h if along_w else w
    long_side = w if along_w else h

    row: list[float] = []
    remaining = values[:]
    while remaining:
        candidate = row + [remaining[0]]
        if not row or _worst(candidate, short_side, total) >= _worst(row, short_side, total):
            row = candidate
            remaining.pop(0)
        else:
            break

    row_total = sum(row)
    row_long = (row_total / total) * long_side
    rects: list[tuple[float, float, float, float]] = []
    cursor = 0.0
    for v in row:
        size = (v / row_total) * short_side if row_total else 0.0
        if along_w:
            rects.append((x, y + cursor, row_long, size))
        else:
            rects.append((x + cursor, y, size, row_long))
        cursor += size

    if remaining:
        if along_w:
            rects.extend(squarify(remaining, x + row_long, y, w - row_long, h))
        else:
            rects.extend(squarify(remaining, x, y + row_long, w, h - row_long))
    return rects


def _worst(row: list[float], short_side: float, total: float) -> float:
    if not row:
        return float("inf")
    s = sum(row) or 1e-9
    long_side = s / total if total else 0.0
    cells_short = [v / s * short_side for v in row] if s else []
    if not cells_short or short_side <= 0:
        return float("inf")
    max_short = max(cells_short)
    min_short = min(cells_short)
    if min_short <= 0:
        return float("inf")
    return max(long_side / min_short, max_short / long_side)

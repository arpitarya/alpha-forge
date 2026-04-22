"""Bounded file read — always safe to expose to an agent."""

from __future__ import annotations

from pathlib import Path

from alphaforge_repo_context.config import get_settings

MAX_LINES = 500


def read_file_range(path: str, start: int = 1, end: int | None = None) -> dict:
    root = get_settings().repo_root
    target = (root / path).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return {"error": "path outside repo root"}
    if not target.exists() or not target.is_file():
        return {"error": "not a file"}

    try:
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        return {"error": str(e)}

    start = max(1, start)
    cap = end if end is not None else start + MAX_LINES - 1
    cap = min(cap, len(lines), start + MAX_LINES - 1)
    body = "\n".join(lines[start - 1 : cap])
    return {
        "path": str(Path(path)),
        "start_line": start,
        "end_line": cap,
        "total_lines": len(lines),
        "content": body,
    }

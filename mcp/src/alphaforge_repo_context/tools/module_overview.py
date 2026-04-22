"""Module overview: nearest CLAUDE.md / PLAN.md / README.md plus a file listing."""

from __future__ import annotations

from pathlib import Path

from alphaforge_repo_context.config import get_settings

_DOC_NAMES = ("CLAUDE.md", "PLAN.md", "README.md", "implement.txt")


def module_overview(path: str) -> dict:
    root = get_settings().repo_root
    target = (root / path).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return {"error": "path outside repo root"}

    module_dir = target if target.is_dir() else target.parent

    docs: dict[str, str] = {}
    for d in _walk_up(module_dir, root):
        for name in _DOC_NAMES:
            candidate = d / name
            if candidate.exists() and name not in docs:
                try:
                    docs[name] = candidate.read_text(encoding="utf-8", errors="replace")[:8000]
                except OSError:
                    continue

    files: list[str] = []
    if module_dir.is_dir():
        for p in sorted(module_dir.iterdir()):
            if p.name.startswith(".") or p.name in {"__pycache__", "node_modules"}:
                continue
            files.append(p.name + ("/" if p.is_dir() else ""))

    return {
        "module_dir": str(module_dir.relative_to(root)),
        "docs": docs,
        "files": files,
    }


def _walk_up(start: Path, stop: Path):
    cur = start
    while True:
        yield cur
        if cur == stop:
            return
        if cur.parent == cur:
            return
        cur = cur.parent

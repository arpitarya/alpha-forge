"""File watcher: debounced re-index on save."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from watchfiles import Change, awatch

from alphaforge_repo_context.config import get_settings
from alphaforge_repo_context.indexer import _load_gitignore, remove_paths, reindex_paths

logger = logging.getLogger("repo_context.watcher")

DEBOUNCE_MS = 500


def _is_watchable(path: Path, root: Path, spec, deny: set[str], allowed: set[str]) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    parts = set(rel.parts)
    if parts & deny:
        return False
    if path.suffix.lower() not in allowed:
        return False
    if spec.match_file(str(rel)):
        return False
    return True


async def run_watch() -> None:
    s = get_settings()
    root = s.repo_root
    spec = _load_gitignore(root)
    deny = set(s.index_deny_dirs)
    allowed = set(s.index_allowed_suffixes)

    logger.info("watching %s", root)

    async for changes in awatch(root, step=DEBOUNCE_MS):
        to_index: list[Path] = []
        to_remove: list[str] = []
        for change, raw in changes:
            p = Path(raw)
            if not _is_watchable(p, root, spec, deny, allowed):
                continue
            if change == Change.deleted:
                to_remove.append(str(p.relative_to(root)))
            elif p.is_file():
                to_index.append(p)

        if to_remove:
            removed = await remove_paths(to_remove)
            logger.info("removed %d chunks for %d paths", removed, len(to_remove))
        if to_index:
            totals = await reindex_paths(to_index)
            logger.info(
                "reindexed %d files (%d chunks changed)",
                totals["files"],
                totals["changed"],
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(run_watch())

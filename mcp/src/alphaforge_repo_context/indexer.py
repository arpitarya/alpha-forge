"""Repo indexer: walk → chunk → embed → pgvector."""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

import pathspec
from sqlalchemy import delete, select

from alphaforge_repo_context.chunker import Chunk, chunk_file
from alphaforge_repo_context.config import get_settings
from alphaforge_repo_context.db import RepoChunk, get_sessionmaker, init_schema
from alphaforge_repo_context.embeddings import EmbeddingClient

logger = logging.getLogger("repo_context.indexer")


def _load_gitignore(root: Path) -> pathspec.PathSpec:
    patterns: list[str] = []
    gi = root / ".gitignore"
    if gi.exists():
        patterns = gi.read_text(encoding="utf-8", errors="replace").splitlines()
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


def iter_repo_files(root: Path) -> list[Path]:
    s = get_settings()
    spec = _load_gitignore(root)
    deny = set(s.index_deny_dirs)
    allowed = set(s.index_allowed_suffixes)
    out: list[Path] = []

    for path in root.rglob("*"):
        rel = path.relative_to(root)
        parts = set(rel.parts)
        if parts & deny:
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in allowed:
            continue
        if spec.match_file(str(rel)):
            continue
        try:
            if path.stat().st_size > s.max_file_bytes:
                continue
        except OSError:
            continue
        out.append(path)
    return out


async def _upsert_file(
    session_factory,
    embed: EmbeddingClient,
    rel_path: str,
    chunks: list[Chunk],
) -> tuple[int, int]:
    """Returns (new_or_changed, unchanged)."""
    async with session_factory() as session:
        existing = {
            (row.chunk_index, row.content_hash): row
            for row in (
                await session.execute(select(RepoChunk).where(RepoChunk.path == rel_path))
            )
            .scalars()
            .all()
        }
        existing_by_idx = {idx: row for (idx, _h), row in existing.items()}

        changed: list[Chunk] = []
        for c in chunks:
            prior = existing_by_idx.get(c.chunk_index)
            if prior and prior.content_hash == c.content_hash and prior.embedding is not None:
                continue
            changed.append(c)

        # delete stale chunks (file shrank)
        current_indices = {c.chunk_index for c in chunks}
        stale = [row for idx, row in existing_by_idx.items() if idx not in current_indices]
        for row in stale:
            await session.delete(row)

        if not changed:
            await session.commit()
            return 0, len(chunks)

        vectors = await embed.embed_batch([c.content for c in changed])

        for c, vec in zip(changed, vectors, strict=True):
            prior = existing_by_idx.get(c.chunk_index)
            if prior:
                prior.start_line = c.start_line
                prior.end_line = c.end_line
                prior.symbol = c.symbol
                prior.kind = c.kind
                prior.lang = c.lang
                prior.content = c.content
                prior.content_hash = c.content_hash
                prior.embedding = vec
            else:
                session.add(
                    RepoChunk(
                        path=c.path,
                        chunk_index=c.chunk_index,
                        start_line=c.start_line,
                        end_line=c.end_line,
                        symbol=c.symbol,
                        kind=c.kind,
                        lang=c.lang,
                        content=c.content,
                        content_hash=c.content_hash,
                        embedding=vec,
                    )
                )
        await session.commit()
        return len(changed), len(chunks) - len(changed)


async def reindex_paths(paths: list[Path]) -> dict[str, int]:
    s = get_settings()
    await init_schema()
    session_factory = get_sessionmaker()
    embed = EmbeddingClient()

    totals = {"files": 0, "changed": 0, "unchanged": 0, "removed_files": 0}
    try:
        for p in paths:
            rel = str(p.relative_to(s.repo_root))
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                logger.warning("skip %s: %s", rel, e)
                continue
            chunks = chunk_file(rel, text)
            if not chunks:
                continue
            new_or_changed, unchanged = await _upsert_file(
                session_factory, embed, rel, chunks
            )
            totals["files"] += 1
            totals["changed"] += new_or_changed
            totals["unchanged"] += unchanged
            if new_or_changed:
                logger.info("indexed %s (%d changed / %d total chunks)",
                            rel, new_or_changed, len(chunks))
    finally:
        await embed.close()
    return totals


async def remove_paths(rel_paths: list[str]) -> int:
    await init_schema()
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        result = await session.execute(
            delete(RepoChunk).where(RepoChunk.path.in_(rel_paths))
        )
        await session.commit()
        return result.rowcount or 0


async def reindex_all() -> dict[str, int]:
    s = get_settings()
    files = iter_repo_files(s.repo_root)
    logger.info("full reindex: %d files under %s", len(files), s.repo_root)
    return await reindex_paths(files)


def cli_main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    p = argparse.ArgumentParser(prog="alphaforge-repo-context-index")
    p.add_argument("--full", action="store_true", help="Reindex every file")
    p.add_argument("--watch", action="store_true", help="Watch for changes")
    args = p.parse_args()

    if args.watch:
        from alphaforge_repo_context.watcher import run_watch

        asyncio.run(run_watch())
        return

    totals = asyncio.run(reindex_all())
    logger.info(
        "done: %d files, %d chunks changed, %d unchanged",
        totals["files"],
        totals["changed"],
        totals["unchanged"],
    )


if __name__ == "__main__":
    cli_main()

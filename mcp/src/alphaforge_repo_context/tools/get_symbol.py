"""Symbol lookup by name (function/class/interface/type)."""

from __future__ import annotations

from sqlalchemy import select

from alphaforge_repo_context.db import RepoChunk, get_sessionmaker


async def get_symbol(name: str, kind: str | None = None, limit: int = 10) -> list[dict]:
    stmt = select(RepoChunk).where(RepoChunk.symbol == name)
    if kind:
        stmt = stmt.where(RepoChunk.kind == kind)
    stmt = stmt.limit(limit)

    async with get_sessionmaker()() as session:
        rows = (await session.execute(stmt)).scalars().all()

    if rows:
        return [_row_dict(r) for r in rows]

    # fallback: fuzzy name match
    fuzzy = select(RepoChunk).where(RepoChunk.symbol.ilike(f"%{name}%")).limit(limit)
    async with get_sessionmaker()() as session:
        rows = (await session.execute(fuzzy)).scalars().all()
    return [_row_dict(r) for r in rows]


def _row_dict(r: RepoChunk) -> dict:
    return {
        "path": r.path,
        "symbol": r.symbol,
        "kind": r.kind,
        "lang": r.lang,
        "start_line": r.start_line,
        "end_line": r.end_line,
        "content": r.content,
    }

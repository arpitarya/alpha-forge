"""Semantic code search via pgvector cosine distance."""

from __future__ import annotations

from sqlalchemy import select

from alphaforge_repo_context.db import RepoChunk, get_sessionmaker
from alphaforge_repo_context.embeddings import EmbeddingClient


async def search_code(
    query: str,
    k: int = 8,
    lang: str | None = None,
    path_prefix: str | None = None,
) -> list[dict]:
    embed = EmbeddingClient()
    try:
        qvec = await embed.embed(query, task_type="RETRIEVAL_QUERY")
    finally:
        await embed.close()

    stmt = select(
        RepoChunk,
        RepoChunk.embedding.cosine_distance(qvec).label("distance"),
    ).where(RepoChunk.embedding.is_not(None))
    if lang:
        stmt = stmt.where(RepoChunk.lang == lang)
    if path_prefix:
        stmt = stmt.where(RepoChunk.path.like(f"{path_prefix}%"))
    stmt = stmt.order_by("distance").limit(k)

    session_factory = get_sessionmaker()
    async with session_factory() as session:
        rows = (await session.execute(stmt)).all()

    results: list[dict] = []
    for chunk, distance in rows:
        results.append(
            {
                "path": chunk.path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "symbol": chunk.symbol,
                "kind": chunk.kind,
                "lang": chunk.lang,
                "score": round(1.0 - float(distance), 4),
                "preview": chunk.content[:400],
            }
        )
    return results

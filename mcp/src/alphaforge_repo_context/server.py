"""MCP server — exposes repo-context tools over stdio.

Launch via:
    python -m alphaforge_repo_context.server
    # or after `pdm install`:
    alphaforge-repo-context-mcp

Any MCP client (Claude Code, VS Code / Copilot, Cursor, Cline, Zed, Windsurf)
can connect by pointing its config at that command.
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from alphaforge_repo_context.tools.get_symbol import get_symbol as _get_symbol
from alphaforge_repo_context.tools.module_overview import module_overview as _module_overview
from alphaforge_repo_context.tools.read_file_range import read_file_range as _read_file_range
from alphaforge_repo_context.tools.recent_changes import recent_changes as _recent_changes
from alphaforge_repo_context.tools.search_code import search_code as _search_code

logger = logging.getLogger("repo_context.server")

mcp = FastMCP("alphaforge-repo-context")


@mcp.tool()
async def search_code(
    query: str,
    k: int = 8,
    lang: str | None = None,
    path_prefix: str | None = None,
) -> list[dict]:
    """Semantic search over the AlphaForge codebase.

    Returns chunks ranked by cosine similarity. Use `lang` (e.g. "python",
    "typescript", "tsx", "markdown") or `path_prefix` (e.g. "backend/app/")
    to narrow results.
    """
    return await _search_code(query, k=k, lang=lang, path_prefix=path_prefix)


@mcp.tool()
async def get_symbol(name: str, kind: str | None = None, limit: int = 10) -> list[dict]:
    """Look up a function, class, interface, or type by name.

    `kind` may be one of: function, class, interface, type, section, module.
    Falls back to a fuzzy ILIKE match if no exact match is found.
    """
    return await _get_symbol(name, kind=kind, limit=limit)


@mcp.tool()
def module_overview(path: str) -> dict:
    """Summarize a module: nearest CLAUDE.md / PLAN.md / README.md + file listing.

    `path` is relative to the repo root (file or directory).
    """
    return _module_overview(path)


@mcp.tool()
async def recent_changes(limit: int = 20, path: str | None = None) -> list[dict]:
    """Recent git commits — optionally scoped to a path."""
    return await _recent_changes(limit=limit, path=path)


@mcp.tool()
def read_file_range(path: str, start: int = 1, end: int | None = None) -> dict:
    """Read a bounded slice of a repo file. Max 500 lines per call."""
    return _read_file_range(path, start=start, end=end)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    mcp.run()


if __name__ == "__main__":
    main()

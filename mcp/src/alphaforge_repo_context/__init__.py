"""AlphaForge repo-context MCP server.

A tool-agnostic MCP server that gives coding agents semantic + structural
context over the AlphaForge monorepo. Works with any MCP-capable client:
Claude Code, GitHub Copilot (VS Code), Cursor, Cline, Zed, Windsurf.
"""

from alphaforge_repo_context.config import Settings, get_settings

__version__ = "0.1.0"
__all__ = ["Settings", "get_settings", "__version__"]

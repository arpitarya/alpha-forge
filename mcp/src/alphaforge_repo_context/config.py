"""Configuration for the repo-context MCP server.

Reads from environment (and the repo root `.env` / `.env.cred` files when
present) so it shares the Gemini API key + database URL already configured
for the rest of AlphaForge.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_repo_root(start: Path | None = None) -> Path:
    """Walk up from this file to find the repo root (has .git)."""
    here = (start or Path(__file__)).resolve()
    for parent in [here, *here.parents]:
        if (parent / ".git").exists():
            return parent
    return here.parents[3] if len(here.parents) >= 4 else here.parent


REPO_ROOT = _find_repo_root()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(REPO_ROOT / ".env"),
            str(REPO_ROOT / ".env.cred"),
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    repo_root: Path = REPO_ROOT

    database_url: str = "postgresql+asyncpg://alphaforge:alphaforge@localhost:5432/alphaforge"

    gemini_api_key: str = ""
    embedding_model: str = "text-embedding-004"
    embedding_dimensions: int = 768

    chunk_max_lines: int = 80
    chunk_overlap_lines: int = 20
    search_default_k: int = 8

    index_deny_dirs: tuple[str, ...] = (
        ".venv",
        "venv",
        "node_modules",
        ".next",
        "dist",
        "build",
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "htmlcov",
        "logs",
        ".pdm-build",
        ".turbo",
    )

    index_allowed_suffixes: tuple[str, ...] = (
        ".py",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".md",
        ".mdx",
        ".toml",
        ".json",
        ".yaml",
        ".yml",
        ".css",
        ".sql",
        ".sh",
        ".ipynb",
    )

    max_file_bytes: int = 512_000  # skip files larger than 500 KB
    embed_batch_sleep_seconds: float = 1.1  # Gemini free tier pacing


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

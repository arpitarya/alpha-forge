"""Resolve the ordered list of .env files to load.

Mirrors Next.js convention with two extra defaults (`.env.cred*`, `.env.port`).
Later files override earlier ones.

Order (low → high priority):
    .env.port
    .env
    .env.cred
    .env.{env}
    .env.local            (skipped when env == "test")
    .env.cred.local       (skipped when env == "test")
    .env.{env}.local
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_env_files(
    env: str | None = None,
    *,
    root: Path | None = None,
    existing_only: bool = True,
) -> tuple[Path, ...]:
    """Return the ordered tuple of .env file paths for the given environment.

    `env` falls back to APP_ENV, then NODE_ENV, then "development".
    """
    env = (env or os.getenv("APP_ENV") or os.getenv("NODE_ENV") or "development").lower()
    root = root or _repo_root()
    is_test = env == "test"

    candidates: list[str] = [
        ".env.port",
        ".env",
        ".env.cred",
        f".env.{env}",
    ]
    if not is_test:
        candidates += [".env.local", ".env.cred.local"]
    candidates.append(f".env.{env}.local")

    paths = tuple(root / name for name in candidates)
    if existing_only:
        paths = tuple(p for p in paths if p.is_file())
    return paths


def load_env_files(env: str | None = None, *, root: Path | None = None, override: bool = False) -> tuple[Path, ...]:
    """Inject `.env*` files into `os.environ` in priority order (later wins).

    Pydantic-settings only populates `Settings` fields; modules that read via
    `os.getenv` need this. Call once at process start.
    """
    files = get_env_files(env, root=root, existing_only=True)
    for path in files:
        load_dotenv(path, override=override)
        override = True
    return files

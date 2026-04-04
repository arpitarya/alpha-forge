"""Centralized logging configuration for AlphaForge backend.

Thin wrapper around the ``alphaforge-logger`` package that reads
configuration from pydantic settings and passes it through.
"""

from __future__ import annotations

import logging

from alphaforge_logger import get_logger as _get_logger
from alphaforge_logger import setup_logging as _setup_logging

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure and return the application root logger."""
    return _setup_logging(
        level=settings.log_level,
        log_dir=settings.log_dir,
        log_file=settings.log_file,
        max_bytes=settings.log_max_bytes,
        backup_count=settings.log_backup_count,
        quiet_loggers=["uvicorn.access", "httpx"],
    )


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``alphaforge`` namespace."""
    return _get_logger(name)

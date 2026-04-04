"""Centralized logging configuration for AlphaForge Python services.

Usage::

    from alphaforge_logger import setup_logging, get_logger

    # Call once at application startup
    setup_logging(
        level="INFO",
        log_dir="logs",
        log_file="my-service.log",
    )

    # Then anywhere in the codebase
    logger = get_logger("routes.market")
    logger.info("Quote requested for symbol=%s", symbol)
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


_DEFAULT_NAMESPACE = "alphaforge"

# ── Defaults (overridden by kwargs or env vars) ─────────────
_ENV_LOG_LEVEL = "LOG_LEVEL"
_ENV_LOG_DIR = "LOG_DIR"
_ENV_LOG_FILE = "LOG_FILE"
_ENV_LOG_MAX_BYTES = "LOG_MAX_BYTES"
_ENV_LOG_BACKUP_COUNT = "LOG_BACKUP_COUNT"


def setup_logging(
    *,
    namespace: str = _DEFAULT_NAMESPACE,
    level: str | None = None,
    log_dir: str | None = None,
    log_file: str | None = None,
    max_bytes: int | None = None,
    backup_count: int | None = None,
    fmt: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    date_fmt: str = "%Y-%m-%d %H:%M:%S",
    quiet_loggers: list[str] | None = None,
) -> logging.Logger:
    """Configure and return the application root logger.

    Resolution order for every parameter:
    1. Explicit kwarg
    2. Environment variable (``LOG_LEVEL``, ``LOG_DIR``, etc.)
    3. Built-in default

    Parameters
    ----------
    namespace:
        Root logger name. Child loggers are ``namespace.xxx``.
    level:
        Minimum log level (DEBUG / INFO / WARNING / ERROR / CRITICAL).
    log_dir:
        Directory for log files. Created if it doesn't exist.
    log_file:
        Log filename inside *log_dir*.
    max_bytes:
        Max bytes per log file before rotation.
    backup_count:
        Number of rotated backup files to keep.
    fmt / date_fmt:
        Log format strings.
    quiet_loggers:
        Third-party logger names to silence to WARNING.
    """

    resolved_level = (level or os.getenv(_ENV_LOG_LEVEL, "INFO")).upper()
    resolved_dir = log_dir or os.getenv(_ENV_LOG_DIR, "logs")
    resolved_file = log_file or os.getenv(_ENV_LOG_FILE, "alphaforge.log")
    resolved_max = max_bytes or int(os.getenv(_ENV_LOG_MAX_BYTES, "10485760"))
    resolved_backup = backup_count or int(os.getenv(_ENV_LOG_BACKUP_COUNT, "5"))

    log_path = Path(resolved_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    full_path = log_path / resolved_file

    numeric_level = getattr(logging, resolved_level, logging.INFO)
    formatter = logging.Formatter(fmt, datefmt=date_fmt)

    # ── Console handler ──────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)

    # ── File handler (rotating) ──────────────────────────────
    file_handler = RotatingFileHandler(
        filename=str(full_path),
        maxBytes=resolved_max,
        backupCount=resolved_backup,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(numeric_level)

    # ── Root logger ──────────────────────────────────────────
    root_logger = logging.getLogger(namespace)
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Quieten noisy third-party loggers
    for name in quiet_loggers or []:
        logging.getLogger(name).setLevel(logging.WARNING)

    root_logger.info(
        "Logging initialised — level=%s, file=%s",
        resolved_level,
        full_path,
    )
    return root_logger


def get_logger(name: str, *, namespace: str = _DEFAULT_NAMESPACE) -> logging.Logger:
    """Return a child logger under the given *namespace*.

    Example::

        logger = get_logger("routes.market")
        # → logging.getLogger("alphaforge.routes.market")
    """
    return logging.getLogger(f"{namespace}.{name}")

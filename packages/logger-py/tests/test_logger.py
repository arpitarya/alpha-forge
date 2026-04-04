"""Tests for alphaforge_logger."""

from __future__ import annotations

import logging
from pathlib import Path

from alphaforge_logger import get_logger, setup_logging


def test_setup_logging_creates_dir(tmp_path: Path) -> None:
    log_dir = tmp_path / "test_logs"
    root = setup_logging(
        level="DEBUG",
        log_dir=str(log_dir),
        log_file="test.log",
    )
    assert log_dir.exists()
    assert (log_dir / "test.log").exists()
    assert root.level == logging.DEBUG


def test_get_logger_returns_child() -> None:
    logger = get_logger("routes.market")
    assert logger.name == "alphaforge.routes.market"


def test_get_logger_custom_namespace() -> None:
    logger = get_logger("worker", namespace="myapp")
    assert logger.name == "myapp.worker"


def test_log_writes_to_file(tmp_path: Path) -> None:
    log_dir = tmp_path / "file_logs"
    setup_logging(level="INFO", log_dir=str(log_dir), log_file="out.log")
    logger = get_logger("test")
    logger.info("hello from test")

    content = (log_dir / "out.log").read_text()
    assert "hello from test" in content

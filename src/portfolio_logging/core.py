"""Reusable console, rotating-file, and JSON logging configuration."""

import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """Format a logging record as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logger(
    name: str = "portfolio",
    *,
    level: str = "INFO",
    console: bool = True,
    file: str | Path | None = None,
    json_format: bool = False,
    max_bytes: int = 1_000_000,
    backup_count: int = 3,
) -> logging.Logger:
    """Configure a named logger without duplicating handlers on repeated calls."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    if not isinstance(level, str) or level.upper() not in logging._nameToLevel:
        raise ValueError("invalid logging level")
    normalized = level.upper()
    if normalized not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0:
        raise ValueError("max_bytes must be a positive integer")
    if not isinstance(backup_count, int) or isinstance(backup_count, bool) or backup_count < 0:
        raise ValueError("backup_count must be a non-negative integer")
    if not console and file is None:
        raise ValueError("enable console or provide a file")

    logger = logging.getLogger(name)
    formatter = (
        JsonFormatter()
        if json_format
        else logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    handlers: list[logging.Handler] = []
    try:
        if console:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            handlers.append(stream_handler)
        if file is not None:
            destination = Path(file)
            destination.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                destination, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
    except Exception:
        for handler in handlers:
            handler.close()
        raise

    for old_handler in logger.handlers[:]:
        logger.removeHandler(old_handler)
        old_handler.close()
    for handler in handlers:
        logger.addHandler(handler)
    logger.setLevel(normalized)
    logger.propagate = False
    return logger


def get_logger(name: str = "portfolio") -> logging.Logger:
    """Retrieve a logger previously configured with configure_logger."""
    return logging.getLogger(name)

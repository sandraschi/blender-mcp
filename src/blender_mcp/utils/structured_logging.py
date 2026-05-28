"""Structured JSON logging for Loki ingestion."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any


class JsonLogFormatter(logging.Formatter):
    """Emit one JSON object per log line for Promtail/Loki."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "blender-mcp",
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key in ("operation", "tool", "job_id", "duration_ms", "status"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=True)


def configure_json_logging(root: logging.Logger | None = None) -> None:
    """Replace formatters on root handlers with JSON output."""
    target = root or logging.getLogger()
    formatter = JsonLogFormatter()
    for handler in target.handlers:
        handler.setFormatter(formatter)

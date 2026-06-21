"""Prometheus metrics and telemetry helpers for blender-mcp."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

_metrics_initialized = False
_tool_calls_total = None
_tool_duration_seconds = None
_blender_jobs_active = None
_session_connected = None
_app_info = None


def metrics_enabled() -> bool:
    value = os.getenv("BLENDER_MCP_METRICS_ENABLED", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def init_metrics() -> None:
    """Initialize Prometheus metrics (idempotent)."""
    global _metrics_initialized, _tool_calls_total, _tool_duration_seconds
    global _blender_jobs_active, _session_connected, _app_info

    if _metrics_initialized or not metrics_enabled():
        return

    try:
        from prometheus_client import REGISTRY

        if "blender_mcp_tool_calls_total" in getattr(REGISTRY, "_names_to_collectors", {}):
            _metrics_initialized = True
            return
    except ImportError:
        pass

    try:
        from prometheus_client import Counter, Gauge, Histogram, Info
    except ImportError:
        logger.warning("prometheus_client not installed; metrics disabled. Install with: uv sync --extra monitoring")
        return

    try:
        _tool_calls_total = Counter(
            "blender_mcp_tool_calls_total",
            "Total MCP tool invocations",
            ["tool", "status"],
        )
        _tool_duration_seconds = Histogram(
            "blender_mcp_tool_duration_seconds",
            "MCP tool execution duration",
            ["tool"],
            buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
        )
        _blender_jobs_active = Gauge(
            "blender_mcp_jobs_active",
            "Active async blender jobs",
        )
        _session_connected = Gauge(
            "blender_mcp_session_connected",
            "Whether a live Blender bridge session is connected (1=yes)",
        )
        _app_info = Info("blender_mcp", "Blender MCP application info")

        from blender_mcp import __version__

        _app_info.info({"version": __version__, "service": "blender-mcp"})
    except ValueError as exc:
        if "Duplicated timeseries" not in str(exc):
            raise
        logger.debug("Prometheus metrics already registered")

    _metrics_initialized = True
    logger.info("Prometheus metrics initialized")


def record_tool_call(tool_name: str, status: str, duration_seconds: float) -> None:
    if not _metrics_initialized:
        return
    _tool_calls_total.labels(tool=tool_name, status=status).inc()
    _tool_duration_seconds.labels(tool=tool_name).observe(max(duration_seconds, 0.0))


def set_jobs_active(count: int) -> None:
    if _metrics_initialized and _blender_jobs_active is not None:
        _blender_jobs_active.set(count)


def set_session_connected(connected: bool) -> None:
    if _metrics_initialized and _session_connected is not None:
        _session_connected.set(1 if connected else 0)


def render_metrics() -> bytes:
    if not _metrics_initialized:
        return b"# metrics disabled\n"
    from prometheus_client import generate_latest

    return generate_latest()


def metrics_content_type() -> str:
    from prometheus_client import CONTENT_TYPE_LATEST

    return CONTENT_TYPE_LATEST


def start_metrics_server(port: int | None = None) -> None:
    """Start standalone Prometheus scrape endpoint (optional sidecar port)."""
    if not _metrics_initialized:
        init_metrics()
    if not _metrics_initialized:
        return

    scrape_port = port or int(os.getenv("PROMETHEUS_PORT", "9091"))
    try:
        from prometheus_client import start_http_server

        start_http_server(scrape_port)
        logger.info("Prometheus metrics server listening on port %s", scrape_port)
    except OSError as exc:
        logger.error("Failed to start Prometheus metrics server on %s: %s", scrape_port, exc)


class ToolCallTimer:
    """Context manager for timed tool call metrics."""

    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name
        self.status = "success"
        self._start = 0.0

    def __enter__(self) -> ToolCallTimer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if exc_type is not None:
            self.status = "error"
        record_tool_call(self.tool_name, self.status, time.perf_counter() - self._start)


def install_tool_call_wrapper(app: Any) -> None:
    """Wrap FastMCP call_tool to record latency and success/error counts."""
    if not metrics_enabled():
        return
    init_metrics()
    if not _metrics_initialized:
        return

    if getattr(app, "_telemetry_wrapped", False):
        return

    original = app.call_tool

    async def wrapped_call_tool(name: str, arguments: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        timer = ToolCallTimer(name)
        with timer:
            return await original(name, arguments or {}, **kwargs)

    app.call_tool = wrapped_call_tool
    app._telemetry_wrapped = True
    logger.info("Installed MCP tool telemetry wrapper")

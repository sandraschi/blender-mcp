"""Blender MCP Server - FastMCP 2.14.3 implementation with modular architecture.

This module provides the main entry point for the Blender MCP server, which exposes
various Blender operations as FastMCP tools using the decorator pattern.
"""

import argparse
import datetime
import logging
import sys

logger = logging.getLogger(__name__)

# Import the app instance (FastMCP)
from blender_mcp.app import app

# ASGI app for uvicorn (webapp/start.ps1): uvicorn blender_mcp.server:asgi_app
asgi_app = app.http_app()

# Import from our compatibility module
# Import all handlers to ensure tool registration is handled in app.py
from blender_mcp.compat import *


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Blender MCP Server")

    # Server configuration
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server instead of stdio")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser.parse_args()


# Global memory buffer for log viewing
_memory_logs = []
_MAX_MEMORY_LOGS = 1000  # Keep last 1000 log entries


class _MemoryLogHandler(logging.Handler):
    """Handler that stores recent log records for get_recent_logs / blender_view_logs."""

    def emit(self, record: logging.LogRecord) -> None:
        global _memory_logs
        try:
            _memory_logs.append(
                {
                    "timestamp": datetime.datetime.fromtimestamp(record.created),
                    "level": record.levelname,
                    "name": record.name,
                    "function": record.funcName,
                    "line": record.lineno,
                    "message": record.getMessage(),
                    "extra": getattr(record, "extra", {}),
                }
            )
            if len(_memory_logs) > _MAX_MEMORY_LOGS:
                _memory_logs.pop(0)
        except Exception:
            self.handleError(record)


def get_recent_logs(level_filter=None, module_filter=None, limit=50, since_minutes=None):
    """Get recent logs with optional filtering."""
    global _memory_logs
    logs = _memory_logs.copy()

    if since_minutes:
        cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=since_minutes)
        logs = [log for log in logs if log["timestamp"] > cutoff_time]

    if level_filter:
        level_filter = level_filter.upper()
        logs = [log for log in logs if log["level"] == level_filter]

    if module_filter:
        logs = [log for log in logs if module_filter.lower() in log["name"].lower()]

    return logs[-limit:] if limit else logs


def setup_logging(log_level: str = "INFO") -> None:
    """Configure stdlib logging with stderr and in-memory buffer."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for h in root.handlers[:]:
        root.removeHandler(h)

    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s")
    stderr = logging.StreamHandler(sys.stderr)
    stderr.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    stderr.setFormatter(fmt)
    root.addHandler(stderr)

    memory_handler = _MemoryLogHandler()
    memory_handler.setLevel(logging.DEBUG)
    root.addHandler(memory_handler)


def main():
    """Main entry point for the Blender MCP server with unified transport (FastMCP 2.14.4+)."""
    from .transport import run_server

    # Configure logging before starting
    setup_logging("INFO")

    logger.info("[START] Starting Blender MCP Server")
    logger.info(f"Python version: {sys.version}")

    run_server(app, server_name="blender-mcp")


# =============================================================================
# MCP Entry Points - Industry Standard Installation
# =============================================================================


def create_server():
    """Create and return the MCP server instance.

    This function is used by MCP client libraries to automatically
    discover and instantiate the server.

    Returns:
        FastMCP app instance
    """
    return app


def main_stdio():
    """Entry point for stdio mode - used by most MCP clients.

    This is the standard way MCP servers communicate with clients
    through stdin/stdout streams.
    """
    import logging

    logging.basicConfig(level=logging.INFO)

    logger.info("[MCP] Starting Blender MCP server in stdio mode")
    logger.info("[MCP] Ready to accept MCP protocol messages")

    try:
        app.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("[MCP] Server stopped by user")
    except Exception as e:
        logger.error(f"[MCP] Server error: {e}")
        raise


def main_http(host="127.0.0.1", port=10771):
    """Entry point for HTTP mode - for web-based MCP clients.

    Args:
        host: Host to bind to
        port: Port to bind to
    """
    import logging

    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(f"[HTTP] Starting Blender MCP server on {host}:{port}")

    try:
        app.run(transport="http", host=host, port=port)
    except KeyboardInterrupt:
        logger.info("[HTTP] Server stopped by user")
    except Exception as e:
        logger.error(f"[HTTP] Server error: {e}")
        raise


if __name__ == "__main__":
    main()

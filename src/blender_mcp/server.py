"""Blender MCP Server - FastMCP 2.14.3 implementation with modular architecture.

This module provides the main entry point for the Blender MCP server, which exposes
various Blender operations as FastMCP tools using the decorator pattern.
"""

import argparse
import datetime
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

logger = logging.getLogger(__name__)

# Global memory buffer for log viewing
_memory_logs = []
_MAX_MEMORY_LOGS = 1000


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


def setup_logging(log_level: str = "INFO") -> None:
    """Configure stdlib logging with stderr, rotating file, and in-memory buffer."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for h in root.handlers[:]:
        root.removeHandler(h)

    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s")

    stderr = logging.StreamHandler(sys.stderr)
    stderr.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    stderr.setFormatter(fmt)
    root.addHandler(stderr)

    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = RotatingFileHandler(
        log_dir / "blender-mcp.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    memory_handler = _MemoryLogHandler()
    memory_handler.setLevel(logging.DEBUG)
    root.addHandler(memory_handler)

    logger.info("Logging initialized: stderr=%s file=%s", log_level, log_dir / "blender-mcp.log")

    if os.getenv("BLENDER_MCP_LOG_FORMAT", "").strip().lower() == "json":
        from blender_mcp.utils.structured_logging import configure_json_logging

        configure_json_logging(root)
        logger.info("JSON log format enabled for Loki ingestion")


# Initialize file logging before any app imports
setup_logging(os.getenv("BLENDER_MCP_LOG_LEVEL", "INFO"))

# Import the app instance (FastMCP)
from blender_mcp.app import app

# ASGI app for uvicorn (webapp/start.ps1): uvicorn blender_mcp.server:asgi_app
asgi_app = app.http_app()

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route


async def _health(request):
    return JSONResponse({"status": "ok", "service": "blender-mcp"})


asgi_app.router.routes.append(Route("/health", endpoint=_health))
asgi_app.router.routes.append(Route("/api/health", endpoint=_health))
asgi_app.router.routes.append(Route("/api/status", endpoint=_health))
asgi_app.router.routes.append(Route("/api/v1/status", endpoint=_health))


async def _logs_endpoint(request):
    """REST endpoint for logs: GET /api/v1/logs?level=INFO&limit=50&since_minutes=60"""
    level_filter = request.query_params.get("level")
    module_filter = request.query_params.get("module")
    search = request.query_params.get("search")
    since_minutes_str = request.query_params.get("since_minutes")
    limit_str = request.query_params.get("limit", "50")
    try:
        limit = max(1, min(500, int(limit_str)))
    except (ValueError, TypeError):
        limit = 50
    since_minutes = None
    if since_minutes_str:
        try:
            since_minutes = max(0, int(since_minutes_str))
        except (ValueError, TypeError):
            pass
    logs = get_recent_logs(
        level_filter=level_filter,
        module_filter=module_filter,
        limit=limit,
        since_minutes=since_minutes,
    )
    if search:
        search_lower = search.lower()
        logs = [log for log in logs if search_lower in log["message"].lower() or (search_lower in log["name"].lower())]
    result = []
    for log in logs:
        result.append(
            {
                "timestamp": log["timestamp"].isoformat(),
                "level": log["level"],
                "name": log["name"],
                "function": log["function"],
                "line": log["line"],
                "message": log["message"],
            }
        )
    return JSONResponse({"success": True, "logs": result, "count": len(result)})


asgi_app.router.routes.append(Route("/api/v1/logs", endpoint=_logs_endpoint, methods=["GET"]))

_server_start_time = datetime.datetime.now()


async def _diagnostics_endpoint(request):
    """GET /api/v1/diagnostics — system status, tool count, uptime, resources."""
    uptime = (datetime.datetime.now() - _server_start_time).total_seconds()
    tool_list = [t.name for t in await app.list_tools()]
    import psutil

    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.2)
    disk = psutil.disk_usage(".")
    import platform

    bridge_host = os.environ.get("BLENDER_BRIDGE_HOST", os.environ.get("BLENDER_HOST", "127.0.0.1"))
    bridge_port = int(os.environ.get("BLENDER_BRIDGE_PORT", "10850"))
    bridge_alive = False
    try:
        import json as _json
        import socket as _sock
        import struct as _struct

        s = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
        s.settimeout(2)
        s.connect((bridge_host, bridge_port))
        payload = _json.dumps({"type": "ping"}).encode("utf-8")
        s.sendall(_struct.pack("!I", len(payload)) + payload)
        header = s.recv(4)
        if len(header) == 4:
            body_len = _struct.unpack("!I", header)[0]
            body = s.recv(body_len)
            resp = _json.loads(body.decode("utf-8"))
            bridge_alive = resp.get("status") == "success"
        s.close()
    except Exception:
        pass

    return JSONResponse(
        {
            "server": {
                "name": "blender-mcp",
                "version": __import__("blender_mcp").__version__,
                "uptime_seconds": uptime,
                "port": 10849,
                "tool_count": len(tool_list),
                "status": "ok",
            },
            "system": {
                "platform": platform.platform(),
                "python": platform.python_version(),
                "cpu_percent": cpu,
                "memory_percent": mem.percent,
                "memory_used_gb": round(mem.used / (1024**3), 1),
                "memory_total_gb": round(mem.total / (1024**3), 1),
                "disk_percent": disk.percent,
            },
            "blender": {
                "connected": bridge_alive,
                "bridge_addon": bridge_alive,
                "bridge_host": bridge_host,
                "socket_bridge_port": bridge_port,
            },
        }
    )


asgi_app.router.routes.append(Route("/api/v1/diagnostics", endpoint=_diagnostics_endpoint, methods=["GET"]))


async def _skills_list_endpoint(request):
    """GET /api/skills — list registered skills from FastMCP resource providers."""
    skills = []
    try:
        providers = getattr(app, "_resource_providers", [])
        for prov in providers:
            if hasattr(prov, "list_resources"):
                resources = await prov.list_resources()
                for r in resources:
                    uri = str(r.uri) if hasattr(r, "uri") else str(r)
                    if "/SKILL.md" in uri or "skill://" in uri:
                        skills.append({"uri": uri, "name": uri.split("/")[-2] if "/" in uri else uri})
    except Exception:
        pass
    return JSONResponse({"success": True, "skills": skills, "count": len(skills)})


async def _skills_detail_endpoint(request):
    """GET /api/skills/{name} — render skill markdown content."""
    name = request.path_params.get("name", "")
    try:
        providers = getattr(app, "_resource_providers", [])
        for prov in providers:
            if hasattr(prov, "list_resources"):
                resources = await prov.list_resources()
                for r in resources:
                    uri = str(r.uri) if hasattr(r, "uri") else str(r)
                    if f"skill://{name}/SKILL.md" in uri or (f"/{name}/" in uri and "/SKILL.md" in uri):
                        content = await prov.read_resource(uri)
                        return JSONResponse({"success": True, "name": name, "content": str(content)})
    except Exception:
        pass
    return JSONResponse({"success": False, "error": f"Skill '{name}' not found"}, status_code=404)


asgi_app.router.routes.append(Route("/api/skills", endpoint=_skills_list_endpoint, methods=["GET"]))
asgi_app.router.routes.append(Route("/api/skills/{name}", endpoint=_skills_detail_endpoint, methods=["GET"]))

asgi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:10849",
        "http://localhost:10849",
        "http://goliath:10849",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ],
    allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ensure tool registration via app.py


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Blender MCP Server")

    # Server configuration
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["stdio", "http", "dual"],
        default=None,
        help="Transport mode: stdio, http, or dual (http+stdio). Overrides --http and --stdio.",
    )
    parser.add_argument("--http", action="store_true", help="Run as HTTP server instead of stdio")
    parser.add_argument("--stdio", action="store_true", help="Run in stdio mode (default)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser.parse_args()


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

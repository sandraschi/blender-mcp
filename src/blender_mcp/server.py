"""Blender MCP Server - FastMCP 2.12 implementation with modular architecture.

This module provides the main entry point for the Blender MCP server, which exposes
various Blender operations as FastMCP tools using the decorator pattern.
"""

import sys
import os
import argparse
from pathlib import Path
from loguru import logger

# Import from our compatibility module
from blender_mcp.compat import *

# Import the app instance
from blender_mcp.app import app

# Import all handlers to ensure tool registration
# These imports are necessary for the @app.tool decorators to register the tools
from blender_mcp.handlers import (
    addon_handler,
    animation_handler,
    camera_handler,
    compositor_handler,
    export_handler,
    file_io_handler,
    grease_pencil_handler,
    import_handler,
    lighting_handler,
    material_handler,
    mesh_handler,
    modifier_handler,
    particle_handler,
    physics_handler,
    render_handler,
    rendering_handler,
    rigging_handler,
    scene_handler,
    scripting_handler,
    selection_handler,
    shader_handler,
    simulation_handler,
    texture_handler,
    transform_handler,
    uv_handler
)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Blender MCP Server')
    
    # Server configuration
    parser.add_argument('--host', type=str, default='127.0.0.1',
                      help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8000,
                      help='Port to run the server on')
    parser.add_argument('--http', action='store_true',
                      help='Run as HTTP server instead of stdio')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging')
    
    return parser.parse_args()

# Global memory buffer for log viewing
_memory_logs = []
_MAX_MEMORY_LOGS = 1000  # Keep last 1000 log entries

def _memory_log_handler(message):
    """Memory handler that stores recent logs for viewing."""
    global _memory_logs

    # Add new log entry
    _memory_logs.append({
        'timestamp': message.record['time'],
        'level': message.record['level'].name,
        'name': message.record['name'],
        'function': message.record['function'],
        'line': message.record['line'],
        'message': message.record['message'],
        'extra': message.record['extra']
    })

    # Keep only the most recent logs (circular buffer)
    if len(_memory_logs) > _MAX_MEMORY_LOGS:
        _memory_logs.pop(0)

def get_recent_logs(level_filter=None, module_filter=None, limit=50, since_minutes=None):
    """Get recent logs with optional filtering."""
    global _memory_logs
    import datetime

    logs = _memory_logs.copy()

    # Apply time filter
    if since_minutes:
        cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=since_minutes)
        logs = [log for log in logs if log['timestamp'] > cutoff_time]

    # Apply level filter
    if level_filter:
        level_filter = level_filter.upper()
        logs = [log for log in logs if log['level'] == level_filter]

    # Apply module filter
    if module_filter:
        logs = [log for log in logs if module_filter.lower() in log['name'].lower()]

    # Return most recent logs (limited)
    return logs[-limit:] if limit else logs

def setup_logging(log_level: str = "INFO"):
    """Configure structured logging with loguru."""
    logger.remove()  # Remove default handler

    # Configure log format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Add console handler
    logger.add(
        sys.stderr,
        level=log_level,
        format=log_format,
        colorize=True
    )

    # Add memory handler for log viewing (always captures DEBUG and above)
    logger.add(
        _memory_log_handler,
        level="DEBUG",
        format="{time} | {level} | {name}:{function}:{line} - {message}",
        filter=lambda record: True  # Capture all logs for memory buffer
    )

def main():
    """Main entry point for the Blender MCP server."""
    # Parse command line arguments
    args = parse_args()

    # Configure logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(log_level)

    logger.info("[START] Starting Blender MCP Server")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Running in {'HTTP' if args.http else 'stdio'} mode")

    try:
        if args.http:
            logger.info(f"[HTTP] Starting HTTP server on {args.host}:{args.port}")
            # HTTP mode - use the app's built-in HTTP server
            app.run_http(host=args.host, port=args.port)
        else:
            logger.info("[STDIO] Starting stdio server")
            # Stdio mode - use the app's built-in stdio server
            app.run_stdio()
    except Exception as e:
        logger.error(f"[ERROR] Server error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("[SHUTDOWN] Shutting down gracefully...")
        sys.exit(0)

if __name__ == "__main__":
    main()

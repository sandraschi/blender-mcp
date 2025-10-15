"""Blender MCP Server - Fixed version with manual tool registration.

This version avoids circular imports by registering tools manually after
all modules are loaded.
"""

import asyncio
import sys
import os
import argparse
from loguru import logger

# Import FastMCP
from fastmcp import FastMCP

# Import utilities and config
from blender_mcp.compat import *

# Initialize FastMCP application
app = FastMCP(name="blender-mcp", version="1.0.0")


def register_all_tools():
    """Manually register all tools from handlers."""
    logger.info("Registering Blender MCP tools...")

    # Import handlers (this will not trigger @app.tool since we commented them out)
    try:
        from blender_mcp.handlers import scene_handler

        # Register scene tools
        app.tool(scene_handler.create_scene)
        app.tool(scene_handler.list_scenes)
        app.tool(scene_handler.clear_scene)
        logger.info("  Registered scene tools")

    except Exception as e:
        logger.error(f"Failed to register scene tools: {e}")

    try:
        from blender_mcp.handlers import mesh_handler

        # Register mesh tools
        app.tool(mesh_handler.create_chaiselongue)
        app.tool(mesh_handler.create_ornate_mirror)
        logger.info("  Registered mesh tools")

    except Exception as e:
        logger.error(f"Failed to register mesh tools: {e}")

    try:
        from blender_mcp.handlers import material_handler

        # Register material tools
        app.tool(material_handler.create_fabric_material)
        app.tool(material_handler.create_metal_material)
        app.tool(material_handler.create_wood_material)
        logger.info("  Registered material tools")

    except Exception as e:
        logger.error(f"Failed to register material tools: {e}")

    try:
        from blender_mcp.handlers import export_handler

        # Register export tools
        app.tool(export_handler.export_for_unity)
        app.tool(export_handler.export_for_vrchat)
        logger.info("  Registered export tools")

    except Exception as e:
        logger.error(f"Failed to register export tools: {e}")

    try:
        from blender_mcp.handlers import render_handler

        # Register render tools
        app.tool(render_handler.render_turntable)
        app.tool(render_handler.render_preview)
        logger.info("  Registered render tools")

    except Exception as e:
        logger.error(f"Failed to register render tools: {e}")

    logger.info("Tool registration complete")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Blender MCP Server (Fixed)")

    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server instead of stdio")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--blender", type=str, default="blender", help="Path to Blender executable")

    return parser.parse_args()


def setup_logging(log_level: str = "INFO"):
    """Configure structured logging with loguru."""
    logger.remove()  # Remove default handler

    # Simple format without emojis (Windows-safe)
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(sys.stderr, level=log_level, format=log_format, colorize=True)


async def main():
    """Main entry point for the Blender MCP server."""
    args = parse_args()

    # Configure logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(log_level)

    logger.info("[START] Starting Blender MCP Server (Fixed)")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Running in {'HTTP' if args.http else 'stdio'} mode")

    # Set Blender executable
    os.environ["BLENDER_EXECUTABLE"] = args.blender
    logger.info(f"Blender executable: {args.blender}")

    # Register all tools
    try:
        register_all_tools()
    except Exception as e:
        logger.error(f"[ERROR] Failed to register tools: {e}")
        sys.exit(1)

    try:
        if args.http:
            logger.info(f"[HTTP] Starting HTTP server on {args.host}:{args.port}")
            await app.run_http_async(host=args.host, port=args.port)
        else:
            logger.info("[STDIO] Starting stdio server")
            await app.run_stdio_async()
    except Exception as e:
        logger.error(f"[ERROR] Server error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("[SHUTDOWN] Shutting down gracefully...")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

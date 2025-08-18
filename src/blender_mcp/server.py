"""Blender MCP Server - FastMCP 2.10 implementation with modular architecture.

This module provides the main entry point for the Blender MCP server, which exposes
various Blender operations as FastMCP tools using the decorator pattern.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Any, Dict, Optional, List
import argparse
from loguru import logger

# Import the app instance
from .app import app

# Import handlers to register tools via @app.tool decorators
# Only import the working handlers for now
from .handlers import scene_handler, mesh_handler
# Temporarily disabled: material_handler, export_handler, render_handler, shader_handler

# Tools are now automatically registered via @app.tool decorators in handlers
logger.info("✅ Working tools registered via @app.tool decorators")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Blender MCP Server")
    parser.add_argument(
        "--http", 
        action="store_true", 
        help="Enable HTTP server mode (default: stdio mode)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind to in HTTP mode (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to listen on in HTTP mode (default: 8000)"
    )
    parser.add_argument(
        "--blender", 
        default="blender", 
        help="Path to Blender executable (default: 'blender' in PATH)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level"
    )
    return parser.parse_args()

def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured logging with loguru."""
    logger.remove()  # Remove default handler
    
    # Add console handler with structured format
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

async def main() -> None:
    """Main entry point for the Blender MCP server."""
    args = parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Set Blender executable path in the environment
    os.environ["BLENDER_EXECUTABLE"] = args.blender
    
    logger.info(f"🚀 Starting Blender MCP server v1.0.0")
    logger.info(f"📊 Log level: {args.log_level}")
    logger.info(f"🎨 Blender executable: {args.blender}")
    
    if args.http:
        logger.info(f"🌐 Starting HTTP server on {args.host}:{args.port}")
        from fastmcp.server import Server
        server = Server(app, host=args.host, port=args.port)
        await server.serve()
    else:
        logger.info("💬 Starting stdio server")
        await app.serve_stdio()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Shutting down Blender MCP server")
    except Exception as e:
        logger.critical(f"💥 Fatal error: {str(e)}")
        sys.exit(1)

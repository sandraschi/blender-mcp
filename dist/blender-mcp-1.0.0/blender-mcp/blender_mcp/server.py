"""Blender MCP Server - FastMCP 2.10 implementation with modular architecture.

This module provides the main entry point for the Blender MCP server, which exposes
various Blender operations as FastMCP tools using the decorator pattern.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import argparse
from loguru import logger

from fastmcp import FastMCP

# Import tool functions from handlers to register them with FastMCP
from .handlers.scene_handler import create_scene, list_scenes, clear_scene
from .handlers.mesh_handler import create_chaiselongue, create_vanity_table
from .handlers.material_handler import create_fabric_material, create_metal_material, create_wood_material
from .handlers.export_handler import export_for_unity, export_for_vrchat
from .handlers.render_handler import render_turntable

# Create FastMCP instance
app = FastMCP("blender-mcp")

# Register all tools with the FastMCP app
app.tool()(create_scene)
app.tool()(list_scenes)
app.tool()(clear_scene)

# Register mesh tools
app.tool()(create_chaiselongue)
app.tool()(create_vanity_table)

# Register material tools
app.tool()(create_fabric_material)
app.tool()(create_metal_material)
app.tool()(create_wood_material)

# Register export and render tools
app.tool()(export_for_unity)
app.tool()(export_for_vrchat)
app.tool()(render_turntable)


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
    return parser.parse_args()


async def main() -> None:
    """Main entry point for the Blender MCP server.
    
    Supports both stdio and HTTP server modes.
    """
    args = parse_args()
    
    # Set Blender executable path in the environment
    import os
    os.environ["BLENDER_EXECUTABLE"] = args.blender
    
    logger.info(f"Starting Blender MCP server (Blender: {args.blender})")
    
    if args.http:
        from fastmcp.server import Server
        logger.info(f"Starting HTTP server on {args.host}:{args.port}")
        server = Server(app, host=args.host, port=args.port)
        await server.serve()
    else:
        logger.info("Starting stdio server")
        await app.serve_stdio()


if __name__ == "__main__":
    asyncio.run(main())

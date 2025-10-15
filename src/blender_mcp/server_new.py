"""Blender MCP Server - FastMCP 2.10 compliant implementation."""

from loguru import logger

from fastmcp import FastMCP

from ..compat import *

# Import tool functions from handlers
from .handlers.scene_handler import create_scene, list_scenes, clear_scene
from .handlers.mesh_handler import (
    create_chaiselongue,
    create_candle_set,
    create_ornate_mirror,
    create_feather_duster,
)
from .handlers.material_handler import (
    create_fabric_material,
    create_metal_material,
    create_wood_material,
)
from .handlers.export_handler import export_for_unity, export_for_vrchat
from .handlers.render_handler import render_preview, render_turntable

# Initialize FastMCP application
app = FastMCP(
    name="blender-mcp",
    version="1.0.0",
    description="Blender MCP Server for 3D content creation and automation",
)

# Register all tools with the FastMCP app
app.tool()(create_scene)
app.tool()(list_scenes)
app.tool()(clear_scene)
app.tool()(create_chaiselongue)
app.tool()(create_candle_set)
app.tool()(create_ornate_mirror)
app.tool()(create_feather_duster)
app.tool()(create_fabric_material)
app.tool()(create_metal_material)
app.tool()(create_wood_material)
app.tool()(export_for_unity)
app.tool()(export_for_vrchat)
app.tool()(render_preview)
app.tool()(render_turntable)

# Stdio is automatic with FastMCP 2.10
if __name__ == "__main__":
    logger.info("🎨 Starting Blender MCP server (FastMCP 2.10)")
    app.run()  # Handles stdio automatically

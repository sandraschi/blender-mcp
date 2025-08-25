"""Handler modules for Blender MCP operations.

This module provides a collection of handler functions for different aspects of Blender operations,
including scene management, mesh creation, material handling, and more. These handlers are designed
to be used with the Blender MCP server to provide a clean API for Blender automation.
"""

from blender_mcp.compat import *

# Scene handlers
from blender_mcp.handlers.scene_handler import create_scene, list_scenes, clear_scene

# Mesh handlers - only import existing functions
from blender_mcp.handlers.mesh_handler import (
    create_chaiselongue,
    create_ornate_mirror
)

# Material handlers - temporarily disabled until FastMCP compatibility is fixed
# from blender_mcp.handlers.material_handler import (
#     create_fabric_material,
#     create_metal_material,
#     create_wood_material
# )

# Other handlers - check what exists  
# try:
#     from blender_mcp.handlers.shader_handler import (
#         ShaderType,
#         create_shader_node,
#         connect_shader_nodes,
#         create_shader_material
#     )
# except ImportError:
#     pass

# try:
#     from blender_mcp.handlers.export_handler import export_for_unity, export_for_vrchat
# except ImportError:
#     pass

# try:
#     from blender_mcp.handlers.render_handler import render_turntable, render_preview
# except ImportError:
#     pass

__all__ = [
    # Scene operations
    'create_scene',
    'list_scenes', 
    'clear_scene',
    
    # Mesh operations (only existing ones)
    'create_chaiselongue',
    'create_ornate_mirror'
    
    # Material and other operations temporarily disabled
]

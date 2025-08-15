"""Handler modules for Blender MCP operations.

This module provides a collection of handler functions for different aspects of Blender operations,
including scene management, mesh creation, material handling, and more. These handlers are designed
to be used with the Blender MCP server to provide a clean API for Blender automation.
"""

# Scene handlers
from .scene_handler import create_scene, list_scenes, clear_scene

# Mesh handlers
from .mesh_handler import (
    create_chaiselongue,
    create_vanity_table,
    create_candle_set,
    create_ornate_mirror,
    create_feather_duster
)

# Material handlers
from .material_handler import (
    create_fabric_material,
    create_metal_material,
    create_wood_material
)

# Shader handlers
from .shader_handler import (
    ShaderType,
    create_shader_node,
    connect_shader_nodes,
    create_shader_material
)

# Export handlers
from .export_handler import export_for_unity, export_for_vrchat

# Render handlers
from .render_handler import render_turntable, render_preview

__all__ = [
    # Scene operations
    'create_scene',
    'list_scenes',
    'clear_scene',
    
    # Mesh operations
    'create_chaiselongue',
    'create_vanity_table',
    'create_candle_set',
    'create_ornate_mirror',
    'create_feather_duster',
    
    # Material operations
    'create_fabric_material',
    'create_metal_material',
    'create_wood_material',
    
    # Shader operations
    'ShaderType',
    'create_shader_node',
    'connect_shader_nodes',
    'create_shader_material',
    
    # Export operations
    'export_for_unity',
    'export_for_vrchat',
    
    # Render operations
    'render_turntable',
    'render_preview'
]

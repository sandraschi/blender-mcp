"""Core handlers for Blender MCP functionality.

This package contains the core handler implementations for Blender MCP,
including mesh, material, scene, and camera operations.
"""
from ..compat import *

from .mesh_handler import *
from .material_handler import *
from .scene_handler import *
from .camera_handler import *
from .lighting_handler import *
from .animation_handler import *

__all__ = [
    # Mesh operations
    "create_cube",
    "create_sphere",
    "create_cylinder",
    "create_plane",
    "extrude_mesh",
    "subdivide_mesh",
    "boolean_operation",
    # Material operations
    "create_material",
    "assign_material",
    "remove_material",
    "create_shader_node",
    "connect_shader_nodes",
    # Scene operations
    "create_scene",
    "set_active_scene",
    "link_object_to_scene",
    "unlink_object_from_scene",
    "set_active_object",
    # Camera operations
    "create_camera",
    "set_active_camera",
    "set_camera_target",
    "set_camera_lens",
    "set_camera_clip",
    # Lighting operations
    "create_light",
    "set_light_energy",
    "set_light_color",
    "set_light_type",
    "set_light_shadow",
    # Animation operations
    "insert_keyframe",
    "remove_keyframe",
    "bake_animation",
    "create_fcurve",
    "set_animation_range",
]

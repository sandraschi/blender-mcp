"""Core handlers for Blender MCP functionality.

This package contains the core handler implementations for Blender MCP,
including mesh, material, scene, and camera operations.
"""

from ..compat import *
from .animation_handler import *
from .camera_handler import *
from .lighting_handler import *
from .material_handler import *
from .mesh_handler import *
from .scene_handler import *

__all__ = [
    "assign_material",
    "bake_animation",
    "boolean_operation",
    "connect_shader_nodes",
    # Camera operations
    "create_camera",
    # Mesh operations
    "create_cube",
    "create_cylinder",
    "create_fcurve",
    # Lighting operations
    "create_light",
    # Material operations
    "create_material",
    "create_plane",
    # Scene operations
    "create_scene",
    "create_shader_node",
    "create_sphere",
    "extrude_mesh",
    # Animation operations
    "insert_keyframe",
    "link_object_to_scene",
    "remove_keyframe",
    "remove_material",
    "set_active_camera",
    "set_active_object",
    "set_active_scene",
    "set_animation_range",
    "set_camera_clip",
    "set_camera_lens",
    "set_camera_target",
    "set_light_color",
    "set_light_energy",
    "set_light_shadow",
    "set_light_type",
    "subdivide_mesh",
    "unlink_object_from_scene",
]

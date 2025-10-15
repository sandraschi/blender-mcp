"""Handler modules for Blender MCP operations.

This module provides a collection of handler functions for different aspects of Blender operations,
including scene management, mesh creation, material handling, and more. These handlers are designed
to be used with the Blender MCP server to provide a clean API for Blender automation.
"""

from ..compat import *

from blender_mcp.compat import *

# Scene handlers
from blender_mcp.handlers.scene_handler import create_scene, list_scenes, clear_scene

# Mesh handlers
from blender_mcp.handlers.mesh_handler import (
    create_cube,
    create_sphere,
    create_cylinder,
    create_cone,
    create_plane,
    create_torus,
    create_monkey,
    duplicate_object,
    delete_object,
)

# Animation handlers
from blender_mcp.handlers.animation_handler import (
    set_keyframe,
    animate_location,
    animate_rotation,
    animate_scale,
    play_animation,
    set_frame_range,
    clear_animation,
)

# Lighting handlers
from blender_mcp.handlers.lighting_handler import (
    create_sun_light,
    create_point_light,
    create_spot_light,
    create_area_light,
    setup_three_point_lighting,
    setup_hdri_environment,
    adjust_light,
)

# Export handlers
from blender_mcp.handlers.export_handler import export_for_unity, export_for_vrchat

# Import handlers
from blender_mcp.handlers.import_handler import import_file, link_asset

# Texture handlers
from blender_mcp.handlers.texture_handler import (
    create_texture,
    assign_texture_to_material,
    bake_texture,
)

# Camera handlers
from blender_mcp.handlers.camera_handler import create_camera, set_active_camera, set_camera_lens

# Addon handlers
from blender_mcp.handlers.addon_handler import install_addon, uninstall_addon, list_addons

# Modifier handlers
from blender_mcp.handlers.modifier_handler import (
    add_modifier,
    remove_modifier,
    get_modifiers,
    apply_modifier,
)

# Render handlers
from blender_mcp.handlers.render_handler import render_turntable, render_preview

# Transform handlers
from blender_mcp.handlers.transform_handler import set_transform, apply_transform

# Selection handlers
from blender_mcp.handlers.selection_handler import (
    select_objects,
    select_by_type,
    select_by_material,
)

# Rigging handlers
from blender_mcp.handlers.rigging_handler import create_armature, add_bone, create_bone_ik

# Physics handlers
from blender_mcp.handlers.physics_handler import (
    enable_physics,
    bake_physics_simulation,
    add_force_field,
    add_rigid_body_constraint,
    configure_rigid_body_world,
    set_rigid_body_collision_shape,
    configure_cloth_simulation,
)

# Particle handlers
from blender_mcp.handlers.particle_handler import create_particle_system, bake_particles

# UV handlers
from blender_mcp.handlers.uv_handler import unwrap, project_from_view, reset_uvs, get_uv_info

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
    "create_scene",
    "list_scenes",
    "clear_scene",
    # Mesh operations
    "create_cube",
    "create_sphere",
    "create_cylinder",
    "create_cone",
    "create_plane",
    "create_torus",
    "create_monkey",
    "duplicate_object",
    "delete_object",
    # Animation operations
    "set_keyframe",
    "animate_location",
    "animate_rotation",
    "animate_scale",
    "play_animation",
    "set_frame_range",
    "clear_animation",
    # Lighting operations
    "create_sun_light",
    "create_point_light",
    "create_spot_light",
    "create_area_light",
    "setup_three_point_lighting",
    "setup_hdri_environment",
    "adjust_light",
    # Export operations
    "export_for_unity",
    "export_for_vrchat",
    # Import operations
    "import_file",
    "link_asset",
    # Texture operations
    "create_texture",
    "assign_texture_to_material",
    "bake_texture",
    # Camera operations
    "create_camera",
    "set_active_camera",
    "set_camera_lens",
    # Addon operations
    "install_addon",
    "uninstall_addon",
    "list_addons",
    # Modifier operations
    "add_modifier",
    "remove_modifier",
    "get_modifiers",
    "apply_modifier",
    # Render operations
    "render_turntable",
    "render_preview",
    # Transform operations
    "set_transform",
    "apply_transform",
    # Selection operations
    "select_objects",
    "select_by_type",
    "select_by_material",
    # Rigging operations
    "create_armature",
    "add_bone",
    "create_bone_ik",
    # Physics operations
    "enable_physics",
    "bake_physics_simulation",
    "add_force_field",
    "add_rigid_body_constraint",
    "configure_rigid_body_world",
    "set_rigid_body_collision_shape",
    "configure_cloth_simulation",
    # Particle operations
    "create_particle_system",
    "bake_particles",
    # UV operations
    "unwrap",
    "project_from_view",
    "reset_uvs",
    "get_uv_info",
    # Material and other operations temporarily disabled
]

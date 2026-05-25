"""Handler modules for Blender MCP operations.

This module provides a collection of handler functions for different aspects of Blender operations,
including scene management, mesh creation, material handling, and more. These handlers are designed
to be used with the Blender MCP server to provide a clean API for Blender automation.
"""

from blender_mcp.compat import *

# Addon handlers
from blender_mcp.handlers.addon_handler import install_addon, list_addons, uninstall_addon

# Animation handlers
from blender_mcp.handlers.animation_handler import (
    animate_location,
    animate_rotation,
    animate_scale,
    clear_animation,
    play_animation,
    set_frame_range,
    set_keyframe,
)

# Camera handlers
from blender_mcp.handlers.camera_handler import create_camera, set_active_camera, set_camera_lens

# Export handlers
from blender_mcp.handlers.export_handler import export_for_unity, export_for_vrchat

# Import handlers
from blender_mcp.handlers.import_handler import import_file, link_asset

# Lighting handlers
from blender_mcp.handlers.lighting_handler import (
    adjust_light,
    create_area_light,
    create_point_light,
    create_spot_light,
    create_sun_light,
    setup_hdri_environment,
    setup_three_point_lighting,
)

# Material handlers
from blender_mcp.handlers.material_handler import (  # noqa: F401
    create_fabric_material,
    create_metal_material,
    create_wood_material,
)

# Mesh handlers
from blender_mcp.handlers.mesh_handler import (
    create_cone,
    create_cube,
    create_cylinder,
    create_monkey,
    create_plane,
    create_sphere,
    create_torus,
    delete_object,
    duplicate_object,
)

# Modifier handlers
from blender_mcp.handlers.modifier_handler import (
    add_modifier,
    apply_modifier,
    get_modifiers,
    remove_modifier,
)

# Particle handlers
from blender_mcp.handlers.particle_handler import bake_particles, create_particle_system

# Physics handlers
from blender_mcp.handlers.physics_handler import (
    add_force_field,
    add_rigid_body_constraint,
    bake_physics_simulation,
    configure_cloth_simulation,
    configure_rigid_body_world,
    enable_physics,
    set_rigid_body_collision_shape,
)

# Render handlers
from blender_mcp.handlers.render_handler import render_preview, render_turntable

# Rigging handlers
from blender_mcp.handlers.rigging_handler import add_bone, create_armature, create_bone_ik

# Scene handlers
# Scene handlers
from blender_mcp.handlers.scene_handler import (  # noqa: F401
    scene_get_hierarchy,
)

# Selection handlers
from blender_mcp.handlers.selection_handler import (
    select_by_material,
    select_by_type,
    select_objects,
)

# Texture handlers
from blender_mcp.handlers.texture_handler import (
    assign_texture_to_material,
    bake_texture,
    create_texture,
)

# Transform handlers
from blender_mcp.handlers.transform_handler import apply_transform, set_transform

# UV handlers
from blender_mcp.handlers.uv_handler import get_uv_info, project_from_view, reset_uvs, unwrap

# VSE handlers
from blender_mcp.handlers.vse_handler import (
    add_color,
    add_effect,
    add_image_sequence,
    add_movie,
    add_scene,
    add_sound,
    add_text,
    clear_vse,
    cut_strip,
    delete_strip,
    get_timeline_info,
    list_strips,
    lock_strip,
    move_strip,
    mute_strip,
    render_video,
    set_blend,
    set_speed,
    trim_strip,
)
from blender_mcp.handlers.vse_handler import (
    set_transform as set_strip_transform,
)

from ..compat import *

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
    "add_bone",
    "add_color",
    "add_effect",
    "add_force_field",
    "add_image_sequence",
    "add_modifier",
    "add_movie",
    "add_rigid_body_constraint",
    "add_scene",
    "add_sound",
    "add_text",
    "adjust_light",
    "animate_location",
    "animate_rotation",
    "animate_scale",
    "apply_modifier",
    "apply_transform",
    "assign_texture_to_material",
    "bake_particles",
    "bake_physics_simulation",
    "bake_texture",
    "clear_animation",
    "clear_scene",
    "clear_vse",
    "configure_cloth_simulation",
    "configure_rigid_body_world",
    "create_area_light",
    # Rigging operations
    "create_armature",
    "create_bone_ik",
    # Camera operations
    "create_camera",
    "create_cone",
    # Mesh operations
    "create_cube",
    "create_cylinder",
    "create_monkey",
    # Particle operations
    "create_particle_system",
    "create_plane",
    "create_point_light",
    # Scene operations
    "create_scene",
    "create_sphere",
    "create_spot_light",
    # Lighting operations
    "create_sun_light",
    # Texture operations
    "create_texture",
    "create_torus",
    "cut_strip",
    "delete_object",
    "delete_strip",
    "duplicate_object",
    # Physics operations
    "enable_physics",
    # Export operations
    "export_for_unity",
    "export_for_vrchat",
    "get_modifiers",
    "get_timeline_info",
    "get_uv_info",
    # Import operations
    "import_file",
    # Addon operations
    "install_addon",
    "link_asset",
    "list_addons",
    "list_scenes",
    "list_strips",
    "lock_strip",
    "move_strip",
    "mute_strip",
    "play_animation",
    "project_from_view",
    "remove_modifier",
    "render_preview",
    # Render operations
    "render_turntable",
    "render_video",
    "reset_uvs",
    "select_by_material",
    "select_by_type",
    # Selection operations
    "select_objects",
    "set_active_camera",
    "set_blend",
    "set_camera_lens",
    "set_frame_range",
    # Animation operations
    "set_keyframe",
    "set_rigid_body_collision_shape",
    "set_speed",
    "set_strip_transform",
    # Transform operations
    "set_transform",
    "setup_hdri_environment",
    "setup_three_point_lighting",
    "trim_strip",
    "uninstall_addon",
    # UV operations
    "unwrap",
    # Material and other operations temporarily disabled
]

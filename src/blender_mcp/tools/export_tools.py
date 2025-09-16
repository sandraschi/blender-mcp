"""
Export Tools for Blender-MCP.

This module provides tools for exporting Blender scenes to various file formats.
"""
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
from pydantic import BaseModel, Field, validator
from ..compat import JSONType
# Temporarily commented out until handler functions are implemented
# from blender_mcp.handlers.export_handler import (
#     export_fbx,
#     export_obj,
#     export_gltf,
#     export_stl,
#     export_abc
# )
from blender_mcp.tools import register_tool, validate_with
from blender_mcp.utils.error_handling import handle_errors
# from blender_mcp.utils.validation import BaseValidator, ObjectValidator

# Enums for export settings
class AxisForward(str, Enum):
    """Forward axis for export."""
    X = "X"
    Y = "Y"
    Z = "Z"
    NEG_X = "-X"
    NEG_Y = "-Y"
    NEG_Z = "-Z"

class AxisUp(str, Enum):
    """Up axis for export."""
    X = "X"
    Y = "Y"
    Z = "Z"
    NEG_X = "-X"
    NEG_Y = "-Y"
    NEG_Z = "-Z"

class ExportFormat(str, Enum):
    """Supported export formats."""
    FBX = "FBX"
    OBJ = "OBJ"
    GLTF = "GLTF"
    GLB = "GLB"
    STL = "STL"
    ABC = "ABC"

# Parameter Models - Commented out due to BaseValidator import issues
# class BaseExportParams(BaseValidator):
#     """Base parameters for all export operations."""
#     filepath: str = Field(..., description="Output file path")
#     use_selection: bool = Field(False, description="Export selected objects only")
#     use_active_collection: bool = Field(False, description="Export active collection only")
#     global_scale: float = Field(1.0, gt=0.0, description="Scale all data")
#     path_mode: str = Field("AUTO", description="Path mode for external files")
#     axis_forward: AxisForward = Field(AxisForward.NEG_Z, description="Forward axis")
#     axis_up: AxisUp = Field(AxisUp.Y, description="Up axis")

# class ExportFBXParams(BaseExportParams):
    """Parameters for FBX export."""
    use_mesh_modifiers: bool = Field(True, description="Apply modifiers")
    bake_anim: bool = Field(True, description="Export animation")
    bake_anim_use_nla_strips: bool = Field(True, description="Use NLA strips")
    bake_anim_use_all_actions: bool = Field(True, description="Export all actions")
    add_leaf_bones: bool = Field(True, description="Add leaf bones")
    primary_bone_axis: AxisUp = Field(AxisUp.Y, description="Primary bone axis")
    secondary_bone_axis: AxisUp = Field(AxisUp.X, description="Secondary bone axis")
    use_armature_deform_only: bool = Field(False, description="Only export deforming bones")
    bake_anim_step: float = Field(1.0, gt=0.0, description="Sampling rate")
    bake_anim_simplify_factor: float = Field(1.0, description="Animation simplification factor")

class ExportGLTFParams(BaseExportParams):
    """Parameters for glTF/GLB export."""
    export_format: str = Field("GLB", description="Export format (GLB or GLTF)")
    export_texture_dir: str = Field("", description="Directory for textures")
    export_texcoords: bool = Field(True, description="Export UVs")
    export_normals: bool = Field(True, description="Export normals")
    export_materials: str = Field("EXPORT", description="Export materials mode")
    export_cameras: bool = Field(False, description="Export cameras")
    export_lights: bool = Field(False, description="Export lights")
    export_skins: bool = Field(True, description="Export skinning")
    export_morph: bool = Field(True, description="Export shape keys")
    apply_modifiers: bool = Field(False, description="Apply modifiers")
    export_animations: bool = Field(True, description="Export animations")
    export_frame_range: bool = Field(True, description="Export frame range")
    export_frame_step: int = Field(1, ge=1, description="Frame step")
    export_force_sampling: bool = Field(False, description="Force sampling")
    export_nla_strips: bool = Field(True, description="Use NLA strips")

class ExportOBJParams(BaseExportParams):
    """Parameters for OBJ export."""
    use_mesh_modifiers: bool = Field(True, description="Apply modifiers")
    use_edges: bool = Field(True, description="Export edges")
    use_smooth_groups: bool = Field(False, description="Generate smooth groups")
    use_normals: bool = Field(True, description="Export normals")
    use_uvs: bool = Field(True, description="Export UVs")
    use_materials: bool = Field(True, description="Export materials")
    use_triangles: bool = Field(False, description="Triangulate")
    use_vertex_groups: bool = Field(False, description="Export vertex groups")
    keep_vertex_order: bool = Field(False, description="Keep vertex order")

class ExportSTLParams(BaseExportParams):
    """Parameters for STL export."""
    use_selection: bool = Field(False, description="Export selected only")
    use_mesh_modifiers: bool = Field(True, description="Apply modifiers")
    ascii: bool = Field(False, description="Export as ASCII")
    use_scene_unit: bool = Field(False, description="Use scene units")
    batch_mode: str = Field("OFF", description="Batch mode")

class ExportAlembicParams(BaseValidator):
    """Parameters for Alembic export."""
    filepath: str = Field(..., description="Output file path")
    start: int = Field(1, description="Start frame")
    end: int = Field(250, description="End frame")
    selected: bool = Field(False, description="Export selected only")
    visible_objects_only: bool = Field(False, description="Export visible only")
    renderable_only: bool = Field(True, description="Export renderable only")
    flatten: bool = Field(False, description="Flatten hierarchy")
    uvs: bool = Field(True, description="Export UVs")
    packuv: bool = Field(True, description="Pack UV islands")
    normals: bool = Field(True, description="Export normals")
    colors: bool = Field(False, description="Export vertex colors")
    face_sets: bool = Field(False, description="Export face sets")
    subdiv_schema: bool = Field(False, description="Use subdivision schema")
    apply_subdiv: bool = Field(False, description="Apply subdivision")
    curves_as_mesh: bool = Field(False, description="Export curves as mesh")
    export_hair: bool = Field(True, description="Export hair")
    export_particles: bool = Field(True, description="Export particles")
    export_custom_properties: bool = Field(True, description="Export custom properties")
    as_background_job: bool = Field(False, description="Run as background job")
    global_scale: float = Field(1.0, gt=0.0, description="Scale all data")
    triangulate: bool = Field(False, description="Triangulate")
    quad_method: str = Field("SHORTEST_DIAGONAL", description="Quad method")
    ngon_method: str = Field("BEAUTY", description="N-gon method")

# Tool Definitions - Temporarily commented out until handler functions are implemented
# @register_tool(
#     name="export_fbx",
#     description="Export scene or selected objects to FBX format"
# )
# @handle_errors
# @validate_with(ExportFBXParams)
# async def export_fbx_tool(params: Dict[str, Any]) -> JSONType:
#     """Export scene or selected objects to FBX format."""
#     result = await export_fbx(
#         filepath=params["filepath"],
#         use_selection=params["use_selection"],
#         use_active_collection=params["use_active_collection"],
#         global_scale=params["global_scale"],
#         path_mode=params["path_mode"],
#         axis_forward=params["axis_forward"].value,
#         axis_up=params["axis_up"].value,
#         use_mesh_modifiers=params["use_mesh_modifiers"],
#         bake_anim=params["bake_anim"],
#         bake_anim_use_nla_strips=params["bake_anim_use_nla_strips"],
#         bake_anim_use_all_actions=params["bake_anim_use_all_actions"],
#         add_leaf_bones=params["add_leaf_bones"],
#         primary_bone_axis=params["primary_bone_axis"].value,
#         secondary_bone_axis=params["secondary_bone_axis"].value,
#         use_armature_deform_only=params["use_armature_deform_only"],
#         bake_anim_step=params["bake_anim_step"],
#         bake_anim_simplify_factor=params["bake_anim_simplify_factor"]
#     )
#     return {"status": "SUCCESS", "result": result}

# All remaining tool registrations temporarily commented out
# until handler functions are implemented

# @register_tool(
#     name="export_gltf",
#     description="Export scene or selected objects to glTF/GLB format"
# )
# @handle_errors
# @validate_with(ExportGLTFParams)
# async def export_gltf_tool(params: Dict[str, Any]) -> JSONType:
#     """Export scene or selected objects to glTF/GLB format."""
#     result = await export_gltf(
#         filepath=params["filepath"],
#         export_format=params["export_format"],
#         export_texture_dir=params["export_texture_dir"] or None,
#         export_texcoords=params["export_texcoords"],
#         export_normals=params["export_normals"],
#         export_materials=params["export_materials"],
#         export_cameras=params["export_cameras"],
#         export_lights=params["export_lights"],
#         export_skins=params["export_skins"],
#         export_morph=params["export_morph"],
#         apply_modifiers=params["apply_modifiers"],
#         export_animations=params["export_animations"],
#         export_frame_range=params["export_frame_range"],
#         export_frame_step=params["export_frame_step"],
#         export_force_sampling=params["export_force_sampling"],
#         export_nla_strips=params["export_nla_strips"],
#         use_selection=params["use_selection"],
#         use_active_collection=params["use_active_collection"],
#         global_scale=params["global_scale"],
#         path_mode=params["path_mode"],
#         axis_forward=params["axis_forward"].value,
#         axis_up=params["axis_up"].value
#     )
#     return {"status": "SUCCESS", "result": result}

# @register_tool(
#     name="export_obj",
#     description="Export scene or selected objects to OBJ format"
# )
# @handle_errors
# @validate_with(ExportOBJParams)
# async def export_obj_tool(params: Dict[str, Any]) -> JSONType:
#     """Export scene or selected objects to OBJ format."""
#     result = await export_obj(
#         filepath=params["filepath"],
#         use_selection=params["use_selection"],
#         use_active_collection=params["use_active_collection"],
#         global_scale=params["global_scale"],
#         path_mode=params["path_mode"],
#         axis_forward=params["axis_forward"].value,
#         axis_up=params["axis_up"].value,
#         use_mesh_modifiers=params["use_mesh_modifiers"],
#         use_edges=params["use_edges"],
#         use_smooth_groups=params["use_smooth_groups"],
#         use_normals=params["use_normals"],
#         use_uvs=params["use_uvs"],
#         use_materials=params["use_materials"],
#         use_triangles=params["use_triangles"],
#         use_vertex_groups=params["use_vertex_groups"],
#         keep_vertex_order=params["keep_vertex_order"]
#     )
#     return {"status": "SUCCESS", "result": result}

# @register_tool(
#     name="export_stl",
#     description="Export scene or selected objects to STL format"
# )
# @handle_errors
# @validate_with(ExportSTLParams)
# async def export_stl_tool(params: Dict[str, Any]) -> JSONType:
#     """Export scene or selected objects to STL format."""
#     result = await export_stl(
#         filepath=params["filepath"],
#         use_selection=params["use_selection"],
#         use_mesh_modifiers=params["use_mesh_modifiers"],
#         ascii=params["ascii"],
#         use_scene_unit=params["use_scene_unit"],
#         batch_mode=params["batch_mode"],
#         global_scale=params["global_scale"],
#         axis_forward=params["axis_forward"].value,
#         axis_up=params["axis_up"].value
#     )
#     return {"status": "SUCCESS", "result": result}

# @register_tool(
#     name="export_alembic",
#     description="Export scene or selected objects to Alembic format"
# )
# @handle_errors
# @validate_with(ExportAlembicParams)
# async def export_alembic_tool(params: Dict[str, Any]) -> JSONType:
#     """Export scene or selected objects to Alembic format."""
#     result = await export_abc(
#         filepath=params["filepath"],
#         start=params["start"],
#         end=params["end"],
#         selected=params["selected"],
#         visible_objects_only=params["visible_objects_only"],
#         renderable_only=params["renderable_only"],
#         flatten=params["flatten"],
#         uvs=params["uvs"],
#         packuv=params["packuv"],
#         normals=params["normals"],
#         colors=params["colors"],
#         face_sets=params["face_sets"],
#         subdiv_schema=params["subdiv_schema"],
#         apply_subdiv=params["apply_subdiv"],
#         curves_as_mesh=params["curves_as_mesh"],
#         export_hair=params["export_hair"],
#         export_particles=params["export_particles"],
#         export_custom_properties=params["export_custom_properties"],
#         as_background_job=params["as_background_job"],
#         global_scale=params["global_scale"],
#         triangulate=params["triangulate"],
#         quad_method=params["quad_method"],
#         ngon_method=params["ngon_method"]
#     )
#     return {"status": "SUCCESS", "result": result}

def register() -> None:
    """Register all export tools."""
    # Tools are registered via decorators
    pass

# Auto-register tools when module is imported
register()

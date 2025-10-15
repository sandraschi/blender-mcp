"""
Export Tools for Blender-MCP.

This module provides tools for exporting Blender scenes to various file formats.
The actual tool functions are defined in the handlers and registered with @app.tool decorators.
This module provides parameter models and enums for documentation and validation purposes.
"""

from ..compat import *

from enum import Enum
from pydantic import BaseModel, Field

# Note: The actual tool functions are defined in the handlers and registered with @app.tool decorators.
# This module provides parameter models and enums for documentation and validation purposes.
# We don't import from handlers to avoid circular imports.


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


class PathMode(str, Enum):
    """Path mode for export."""

    AUTO = "AUTO"
    COPY = "COPY"
    RELATIVE = "RELATIVE"
    STRIP = "STRIP"
    STRIP_LEADING = "STRIP_LEADING"


class ApplyScaleOptions(str, Enum):
    """Apply scale options for export."""

    NONE = "NONE"
    SCALE = "SCALE"
    SCALE_CUR = "SCALE_CUR"


class ObjectTypes(str, Enum):
    """Object types for export."""

    MESH = "MESH"
    ARMATURE = "ARMATURE"
    CAMERA = "CAMERA"
    LIGHT = "LIGHT"
    OTHER = "OTHER"


class ArmatureNodeType(str, Enum):
    """Armature node type for export."""

    NULL = "NULL"
    ROOT = "ROOT"


class QuadMethod(str, Enum):
    """Quad method for export."""

    SHORTEST_DIAGONAL = "SHORTEST_DIAGONAL"
    LONGEST_DIAGONAL = "LONGEST_DIAGONAL"
    BEAUTY = "BEAUTY"
    FIXED = "FIXED"


class NgonMethod(str, Enum):
    """N-gon method for export."""

    BEAUTY = "BEAUTY"
    CLIP = "CLIP"


class BatchMode(str, Enum):
    """Batch mode for export."""

    OFF = "OFF"
    SCENE = "SCENE"
    GROUP = "GROUP"


# Parameter Models for validation and documentation
class BaseExportParams(BaseModel):
    """Base parameters for all export operations."""

    filepath: str = Field(..., description="Output file path")
    use_selection: bool = Field(False, description="Export selected objects only")
    use_active_collection: bool = Field(False, description="Export active collection only")
    global_scale: float = Field(1.0, gt=0.0, description="Global scale factor")
    path_mode: PathMode = Field(PathMode.AUTO, description="Path mode")
    axis_forward: AxisForward = Field(AxisForward.NEG_Z, description="Forward axis")
    axis_up: AxisUp = Field(AxisUp.Y, description="Up axis")


class ExportFBXParams(BaseExportParams):
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


class ExportAlembicParams(BaseModel):
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


# Tool Definitions
# Note: The actual tool functions are defined in the handlers and registered with @app.tool decorators.
# This module provides parameter models and enums for documentation and validation purposes.

# The following tools are available (registered in handlers):
# - export_for_unity: Export scene optimized for Unity3D with full pipeline support
# - export_for_vrchat: Export scene optimized for VRChat with avatar-specific settings


def register() -> None:
    """Register all export tools."""
    # Tools are already registered via @app.tool decorators in handlers
    pass


# Auto-register tools when module is imported
register()

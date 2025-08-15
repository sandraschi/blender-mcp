"""
Material Tools for Blender-MCP.

This module provides tools for material and shader operations in Blender.
"""
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
from pydantic import BaseModel, Field, validator, conlist
from fastmcp.types import JSONType

from blender_mcp.handlers.material_handler import (
    create_material,
    set_material_property,
    create_shader_node,
    connect_shader_nodes,
    set_uv_map,
    create_texture,
    setup_pbr_material,
    setup_emission_material,
    setup_glass_material,
    setup_volume_material
)
from blender_mcp.tools import register_tool, validate_with
from blender_mcp.utils.error_handling import handle_errors
from blender_mcp.utils.validation import (
    validate_object_exists,
    validate_material_exists,
    BaseValidator,
    ObjectValidator
)

# Enums for material and shader types
class ShaderType(str, Enum):
    """Types of shader nodes."""
    BSDF_PRINCIPLED = "BSDF_PRINCIPLED"
    BSDF_DIFFUSE = "BSDF_DIFFUSE"
    BSDF_GLOSSY = "BSDF_GLOSSY"
    BSDF_GLASS = "BSDF_GLASS"
    BSDF_REFRACTION = "BSDF_REFRACTION"
    BSDF_TOON = "BSDF_TOON"
    BSDF_TRANSLUCENT = "BSDF_TRANSLUCENT"
    BSDF_TRANSPARENT = "BSDF_TRANSPARENT"
    BSDF_VELVET = "BSDF_VELVET"
    EMISSION = "EMISSION"
    SUBSURFACE_SCATTERING = "SUBSURFACE_SCATTERING"
    VOLUME_ABSORPTION = "VOLUME_ABSORPTION"
    VOLUME_SCATTER = "VOLUME_SCATTER"
    MIX_SHADER = "MIX_SHADER"
    ADD_SHADER = "ADD_SHADER"
    AMBIENT_OCCLUSION = "AMBIENT_OCCLUSION"
    NORMAL = "NORMAL"
    TEX_IMAGE = "TEX_IMAGE"
    TEX_NOISE = "TEX_NOISE"
    TEX_VORONOI = "TEX_VORONOI"
    TEX_MUSGRAVE = "TEX_MUSGRAVE"
    TEX_CHECKER = "TEX_CHECKER"
    TEX_BRICK = "TEX_BRICK"
    TEX_GRADIENT = "TEX_GRADIENT"
    TEX_MAGIC = "TEX_MAGIC"
    TEX_WAVE = "TEX_WAVE"
    TEX_ENVIRONMENT = "TEX_ENVIRONMENT"
    BUMP = "BUMP"
    NORMAL_MAP = "NORMAL_MAP"
    DISPLACEMENT = "DISPLACEMENT"
    VECTOR_DISPLACEMENT = "VECTOR_DISPLACEMENT"
    TEX_COORD = "TEX_COORD"
    MAPPING = "MAPPING"
    VALUE = "VALUE"
    RGB = "RGB"
    BRIGHTCONTRAST = "BRIGHTCONTRAST"
    GAMMA = "GAMMA"
    INVERT = "INVERT"
    LIGHT_PATH = "LIGHT_PATH"
    MATH = "MATH"
    VECTOR_MATH = "VECTOR_MATH"

class TextureType(str, Enum):
    """Types of textures."""
    IMAGE = "IMAGE"
    NOISE = "NOISE"
    VORONOI = "VORONOI"
    MUSGRAVE = "MUSGRAVE"
    CHECKER = "CHECKER"
    BRICK = "BRICK"
    GRADIENT = "GRADIENT"
    MAGIC = "MAGIC"
    WAVE = "WAVE"
    ENVIRONMENT = "ENVIRONMENT"

class PBRPreset(str, Enum):
    """PBR material presets."""
    METAL = "METAL"
    ROUGH_METAL = "ROUGH_METAL"
    GLOSSY = "GLOSSY"
    ROUGH = "ROUGH"
    PLASTIC = "PLASTIC"
    CERAMIC = "CERAMIC"
    GLASS = "GLASS"
    EMISSION = "EMISSION"
    SUBSURFACE = "SUBSURFACE"

# Parameter Models
class RGBAColor(BaseModel):
    """RGBA color with values from 0.0 to 1.0."""
    r: float = Field(1.0, ge=0.0, le=1.0)
    g: float = Field(1.0, ge=0.0, le=1.0)
    b: float = Field(1.0, ge=0.0, le=1.0)
    a: float = Field(1.0, ge=0.0, le=1.0)

class CreateMaterialParams(BaseValidator):
    """Parameters for creating a material."""
    name: str = Field("Material", description="Name of the material")
    use_nodes: bool = Field(True, description="Use nodes for the material")
    make_node_tree: bool = Field(True, description="Create a node tree")
    use_shader_nodes: bool = Field(True, description="Use shader nodes")
    use_fake_user: bool = Field(True, description="Set fake user for the material")

class SetMaterialPropertyParams(BaseValidator, ObjectValidator):
    """Parameters for setting a material property."""
    material_name: str = Field(..., description="Name of the material")
    property_name: str = Field(..., description="Name of the property to set")
    property_value: Any = Field(..., description="Value to set")

class CreateShaderNodeParams(BaseValidator, ObjectValidator):
    """Parameters for creating a shader node."""
    material_name: str = Field(..., description="Name of the material")
    node_type: ShaderType = Field(..., description="Type of shader node to create")
    node_name: str = Field("", description="Name of the node")
    location: Tuple[float, float] = Field(
        (0.0, 0.0),
        description="Location of the node in the node editor"
    )
    width: float = Field(140.0, description="Width of the node")
    hide: bool = Field(False, description="Hide the node")
    label: str = Field("", description="Label of the node")

class ConnectShaderNodesParams(BaseValidator, ObjectValidator):
    """Parameters for connecting shader nodes."""
    material_name: str = Field(..., description="Name of the material")
    from_node: str = Field(..., description="Name of the output node")
    from_socket: str = Field(..., description="Name of the output socket")
    to_node: str = Field(..., description="Name of the input node")
    to_socket: str = Field(..., description="Name of the input socket")

class SetUVMapParams(BaseValidator, ObjectValidator):
    """Parameters for setting a UV map."""
    uv_map_name: str = Field("UVMap", description="Name of the UV map")
    active_render: bool = Field(True, description="Set as active for render")
    active_clone: bool = Field(False, description="Set as active for cloning")
    active_mask: bool = Field(False, description="Set as active for masking")
    active: bool = Field(True, description="Set as active")

class CreateTextureParams(BaseValidator):
    """Parameters for creating a texture."""
    name: str = Field("Texture", description="Name of the texture")
    texture_type: TextureType = Field(TextureType.IMAGE, description="Type of texture")
    image_path: str = Field("", description="Path to the image file (for image textures)")
    width: int = Field(1024, description="Width of the texture")
    height: int = Field(1024, description="Height of the texture")
    color1: RGBAColor = Field(RGBAColor(), description="First color (for procedural textures)")
    color2: RGBAColor = Field(RGBAColor(r=0.0, g=0.0, b=0.0), description="Second color (for procedural textures)")
    scale: float = Field(1.0, description="Scale of the texture")
    use_alpha: bool = Field(True, description="Use alpha channel")

class SetupPBRMaterialParams(BaseValidator, ObjectValidator):
    """Parameters for setting up a PBR material."""
    name: str = Field("PBR_Material", description="Name of the material")
    preset: PBRPreset = Field(PBRPreset.ROUGH, description="PBR material preset")
    base_color: RGBAColor = Field(RGBAColor(), description="Base color of the material")
    metallic: float = Field(0.0, ge=0.0, le=1.0, description="Metallic value")
    roughness: float = Field(0.5, ge=0.0, le=1.0, description="Roughness value")
    specular: float = Field(0.5, ge=0.0, le=1.0, description="Specular value")
    ior: float = Field(1.45, ge=1.0, le=4.0, description="Index of refraction")
    transmission: float = Field(0.0, ge=0.0, le=1.0, description="Transmission value")
    emission_strength: float = Field(0.0, ge=0.0, description="Emission strength")
    emission_color: RGBAColor = Field(RGBAColor(), description="Emission color")
    normal_strength: float = Field(1.0, ge=0.0, description="Normal map strength")
    displacement_scale: float = Field(0.1, description="Displacement scale")
    use_clearcoat: bool = Field(False, description="Use clearcoat")
    clearcoat: float = Field(0.0, ge=0.0, le=1.0, description="Clearcoat amount")
    clearcoat_roughness: float = Field(0.03, ge=0.0, le=1.0, description="Clearcoat roughness")

# Tool Definitions
@register_tool(
    name="create_material",
    description="Create a new material"
)
@handle_errors
@validate_with(CreateMaterialParams)
async def create_material_tool(params: Dict[str, Any]) -> JSONType:
    """Create a new material."""
    result = await create_material(
        name=params["name"],
        use_nodes=params["use_nodes"],
        make_node_tree=params["make_node_tree"],
        use_shader_nodes=params["use_shader_nodes"],
        use_fake_user=params["use_fake_user"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="set_material_property",
    description="Set a property on a material"
)
@handle_errors
@validate_with(SetMaterialPropertyParams)
async def set_material_property_tool(params: Dict[str, Any]) -> JSONType:
    """Set a property on a material."""
    result = await set_material_property(
        object_name=params["object_name"],
        material_name=params["material_name"],
        property_name=params["property_name"],
        property_value=params["property_value"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="create_shader_node",
    description="Create a shader node in a material"
)
@handle_errors
@validate_with(CreateShaderNodeParams)
async def create_shader_node_tool(params: Dict[str, Any]) -> JSONType:
    """Create a shader node in a material."""
    result = await create_shader_node(
        object_name=params["object_name"],
        material_name=params["material_name"],
        node_type=params["node_type"].value,
        node_name=params["node_name"] or None,
        location=params["location"],
        width=params["width"],
        hide=params["hide"],
        label=params["label"] or None
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="connect_shader_nodes",
    description="Connect two shader nodes in a material"
)
@handle_errors
@validate_with(ConnectShaderNodesParams)
async def connect_shader_nodes_tool(params: Dict[str, Any]) -> JSONType:
    """Connect two shader nodes in a material."""
    result = await connect_shader_nodes(
        object_name=params["object_name"],
        material_name=params["material_name"],
        from_node=params["from_node"],
        from_socket=params["from_socket"],
        to_node=params["to_node"],
        to_socket=params["to_socket"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="setup_pbr_material",
    description="Set up a PBR material with the specified properties"
)
@handle_errors
@validate_with(SetupPBRMaterialParams)
async def setup_pbr_material_tool(params: Dict[str, Any]) -> JSONType:
    """Set up a PBR material with the specified properties."""
    result = await setup_pbr_material(
        object_name=params["object_name"],
        name=params["name"],
        preset=params["preset"].value,
        base_color=params["base_color"].dict(),
        metallic=params["metallic"],
        roughness=params["roughness"],
        specular=params["specular"],
        ior=params["ior"],
        transmission=params["transmission"],
        emission_strength=params["emission_strength"],
        emission_color=params["emission_color"].dict(),
        normal_strength=params["normal_strength"],
        displacement_scale=params["displacement_scale"],
        use_clearcoat=params["use_clearcoat"],
        clearcoat=params["clearcoat"],
        clearcoat_roughness=params["clearcoat_roughness"]
    )
    return {"status": "SUCCESS", "result": result}

def register() -> None:
    """Register all material tools."""
    # Tools are registered via decorators
    pass

# Auto-register tools when module is imported
register()

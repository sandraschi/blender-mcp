"""
Material Tools for Blender-MCP.

This module provides tools for advanced material controls and settings.
The actual tool functions are defined in the handlers and registered with @app.tool decorators.
This module provides parameter models and enums for documentation and validation purposes.
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

# Note: The actual tool functions are defined in the handlers and registered with @app.tool decorators.
# This module provides parameter models and enums for documentation and validation purposes.
# We don't import from handlers to avoid circular imports.


# Enums for material types
class MaterialType(str, Enum):
    """Supported material types."""

    FABRIC = "fabric"
    METAL = "metal"
    WOOD = "wood"
    GLASS = "glass"
    CERAMIC = "ceramic"
    LEATHER = "leather"
    STONE = "stone"
    EMISSIVE = "emissive"


class MaterialPreset(str, Enum):
    """Available presets for each material type."""

    # Fabric presets
    VELVET = "velvet"
    SILK = "silk"
    COTTON = "cotton"
    LINEN = "linen"
    BROCADE = "brocade"
    SATIN = "satin"
    WOOL = "wool"

    # Metal presets
    GOLD = "gold"
    SILVER = "silver"
    BRASS = "brass"
    COPPER = "copper"
    IRON = "iron"
    ALUMINUM = "aluminum"

    # Wood presets
    OAK = "oak"
    PINE = "pine"
    MAHOGANY = "mahogany"
    WALNUT = "walnut"
    CHERRY = "cherry"
    BEECH = "beech"

    # Glass presets
    CLEAR = "clear"
    TINTED = "tinted"
    FROSTED = "frosted"
    STAINED = "stained"

    # Ceramic presets
    PORCELAIN = "porcelain"
    CERAMIC = "ceramic"
    TERRA_COTTA = "terra_cotta"

    # Leather presets
    BROWN_LEATHER = "brown_leather"
    BLACK_LEATHER = "black_leather"
    RED_LEATHER = "red_leather"

    # Stone presets
    MARBLE = "marble"
    GRANITE = "granite"
    LIMESTONE = "limestone"
    SANDSTONE = "sandstone"


class Vector3D(BaseModel):
    """3D vector with x, y, z components."""

    x: float = Field(..., description="X component")
    y: float = Field(..., description="Y component")
    z: float = Field(..., description="Z component")


# Tool parameter schemas
class CreateFabricMaterialParams(BaseModel):
    """Parameters for creating fabric materials."""

    name: str = Field(..., description="Name for the new material")
    fabric_type: MaterialPreset = Field(default=MaterialPreset.VELVET, description="Type of fabric")
    base_color: List[float] = Field(
        default=[0.8, 0.75, 0.7], description="Base color as RGB (0-1)", min_items=3, max_items=3
    )
    roughness: float = Field(default=0.8, ge=0.0, le=1.0, description="Roughness value")
    sub_surface: float = Field(default=0.2, ge=0.0, le=1.0, description="Subsurface scattering")
    normal_strength: float = Field(default=0.5, ge=0.0, le=1.0, description="Normal map strength")
    velvet_softness: float = Field(default=0.5, ge=0.0, le=1.0, description="Velvet softness")
    silk_sheen: float = Field(default=0.8, ge=0.0, le=1.0, description="Silk sheen")
    weave_scale: float = Field(default=1.0, ge=0.1, le=10.0, description="Weave scale")


class CreateMetalMaterialParams(BaseModel):
    """Parameters for creating metal materials."""

    name: str = Field(..., description="Name for the new material")
    metal_type: MaterialPreset = Field(default=MaterialPreset.GOLD, description="Type of metal")
    base_color: List[float] = Field(
        default=[1.0, 0.8, 0.0], description="Base color as RGB (0-1)", min_items=3, max_items=3
    )
    roughness: float = Field(default=0.2, ge=0.0, le=1.0, description="Roughness value")
    metallic: float = Field(default=1.0, ge=0.0, le=1.0, description="Metallic value")
    anisotropy: float = Field(default=0.0, ge=0.0, le=1.0, description="Anisotropy")


class CreateWoodMaterialParams(BaseModel):
    """Parameters for creating wood materials."""

    name: str = Field(..., description="Name for the new material")
    wood_type: MaterialPreset = Field(default=MaterialPreset.OAK, description="Type of wood")
    base_color: List[float] = Field(
        default=[0.6, 0.4, 0.2], description="Base color as RGB (0-1)", min_items=3, max_items=3
    )
    roughness: float = Field(default=0.7, ge=0.0, le=1.0, description="Roughness value")
    grain_scale: float = Field(default=1.0, ge=0.1, le=5.0, description="Wood grain scale")


class CreateGlassMaterialParams(BaseModel):
    """Parameters for creating glass materials."""

    name: str = Field(..., description="Name for the new material")
    glass_type: MaterialPreset = Field(default=MaterialPreset.CLEAR, description="Type of glass")
    base_color: List[float] = Field(
        default=[0.9, 0.95, 1.0], description="Base color as RGB (0-1)", min_items=3, max_items=3
    )
    transmission: float = Field(default=1.0, ge=0.0, le=1.0, description="Transmission amount")
    roughness: float = Field(default=0.0, ge=0.0, le=1.0, description="Roughness")
    ior: float = Field(default=1.45, ge=1.0, le=2.5, description="Index of refraction")


class AssignMaterialParams(BaseModel):
    """Parameters for assigning materials to objects."""

    object_name: str = Field(..., description="Name of the object")
    material_name: str = Field(..., description="Name of the material to assign")
    material_slot: Optional[int] = Field(default=None, description="Material slot index (optional)")


class RemoveMaterialParams(BaseModel):
    """Parameters for removing materials."""

    material_name: str = Field(..., description="Name of the material to remove")


class ListMaterialsParams(BaseModel):
    """Parameters for listing materials (no parameters needed)."""

    pass


# Tool registration happens in handlers with @app.tool decorators
# This file provides the parameter schemas and documentation

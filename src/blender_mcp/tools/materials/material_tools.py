"""
Material creation and management tools for Blender MCP.

Provides comprehensive tools for creating various types of materials including
fabrics, metals, woods, glass, ceramics, leather, stone, and more.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# Import app lazily to avoid circular imports
def get_app():
    from blender_mcp.app import app

    return app


# Parameter schemas for material creation
class CreateFabricMaterialParams(BaseModel):
    """Parameters for creating fabric materials."""

    name: str = Field("ElegantFabric", description="Name for the new material")
    fabric_type: str = Field(
        "velvet", description="Type of fabric (velvet, silk, cotton, linen, brocade, satin, wool)"
    )
    base_color: List[float] = Field(
        [0.8, 0.75, 0.7], description="Base color as RGB (0-1)", min_length=3, max_length=3
    )
    roughness: float = Field(0.8, ge=0.0, le=1.0, description="Roughness value")
    sub_surface: float = Field(0.2, ge=0.0, le=1.0, description="Subsurface scattering")
    normal_strength: float = Field(0.5, ge=0.0, le=1.0, description="Normal map strength")
    velvet_softness: float = Field(0.5, ge=0.0, le=1.0, description="Velvet softness")
    silk_sheen: float = Field(0.8, ge=0.0, le=1.0, description="Silk sheen")
    weave_scale: float = Field(1.0, ge=0.1, le=10.0, description="Weave scale")


class CreateMetalMaterialParams(BaseModel):
    """Parameters for creating metal materials."""

    name: str = Field("MetalMaterial", description="Name for the new material")
    metal_type: str = Field(
        "gold", description="Type of metal (gold, silver, brass, copper, iron, aluminum)"
    )
    base_color: List[float] = Field(
        [1.0, 0.8, 0.0], description="Base color as RGB (0-1)", min_length=3, max_length=3
    )
    roughness: float = Field(0.2, ge=0.0, le=1.0, description="Roughness value")
    metallic: float = Field(1.0, ge=0.0, le=1.0, description="Metallic value")
    anisotropy: float = Field(0.0, ge=0.0, le=1.0, description="Anisotropy")


class CreateWoodMaterialParams(BaseModel):
    """Parameters for creating wood materials."""

    name: str = Field("WoodMaterial", description="Name for the new material")
    wood_type: str = Field(
        "oak", description="Type of wood (oak, pine, mahogany, walnut, cherry, beech)"
    )
    base_color: List[float] = Field(
        [0.6, 0.4, 0.2], description="Base color as RGB (0-1)", min_length=3, max_length=3
    )
    roughness: float = Field(0.7, ge=0.0, le=1.0, description="Roughness value")
    grain_scale: float = Field(1.0, ge=0.1, le=5.0, description="Wood grain scale")


class CreateGlassMaterialParams(BaseModel):
    """Parameters for creating glass materials."""

    name: str = Field("GlassMaterial", description="Name for the new material")
    glass_type: str = Field("clear", description="Type of glass (clear, tinted, frosted, stained)")
    base_color: List[float] = Field(
        [0.9, 0.95, 1.0], description="Base color as RGB (0-1)", min_length=3, max_length=3
    )
    transmission: float = Field(1.0, ge=0.0, le=1.0, description="Transmission amount")
    roughness: float = Field(0.0, ge=0.0, le=1.0, description="Roughness")
    ior: float = Field(1.45, ge=1.0, le=2.5, description="Index of refraction")


class CreateCeramicMaterialParams(BaseModel):
    """Parameters for creating ceramic materials."""

    name: str = Field("CeramicMaterial", description="Name for the new material")
    ceramic_type: str = Field(
        "porcelain", description="Type of ceramic (porcelain, ceramic, terra_cotta)"
    )
    base_color: List[float] = Field(
        [0.95, 0.95, 0.95], description="Base color as RGB (0-1)", min_length=3, max_length=3
    )
    roughness: float = Field(0.1, ge=0.0, le=1.0, description="Roughness value")
    glossiness: float = Field(0.9, ge=0.0, le=1.0, description="Surface glossiness")


class AssignMaterialParams(BaseModel):
    """Parameters for assigning materials to objects."""

    object_name: str = Field(..., description="Name of the object to assign material to")
    material_name: str = Field(..., description="Name of the material to assign")


class CreateMaterialFromPresetParams(BaseModel):
    """Parameters for creating materials from presets."""

    preset_name: str = Field(..., description="Name of the material preset to use")
    material_name: Optional[str] = Field(
        None, description="Optional custom name for the new material"
    )


# Tool registration functions
def _register_material_tools():
    """Register all material creation and management tools with FastMCP."""
    app = get_app()

    @app.tool
    async def create_fabric_material(
        name: str = "ElegantFabric",
        fabric_type: str = "velvet",
        base_color: List[float] = [0.8, 0.75, 0.7],
        roughness: float = 0.8,
        sub_surface: float = 0.2,
        normal_strength: float = 0.5,
        velvet_softness: float = 0.5,
        silk_sheen: float = 0.8,
        weave_scale: float = 1.0,
    ) -> str:
        """
        Create a comprehensive fabric material with PBR properties.

        Generates realistic fabric materials with appropriate textures,
        normal maps, and PBR properties for different fabric types.

        Args:
            name: Name for the new material
            fabric_type: Type of fabric (velvet, silk, cotton, linen, brocade, satin, wool)
            base_color: Base color as RGB values (0-1)
            roughness: Surface roughness (0-1)
            sub_surface: Subsurface scattering amount (0-1)
            normal_strength: Normal map intensity (0-1)
            velvet_softness: Softness for velvet materials (0-1)
            silk_sheen: Sheen intensity for silk materials (0-1)
            weave_scale: Scale of weave pattern (0.1-10.0)

        Returns:
            Confirmation message about material creation
        """
        from blender_mcp.handlers.material_handler import create_fabric_material

        return await create_fabric_material(
            name=name,
            fabric_type=fabric_type,
            base_color=tuple(base_color),
            roughness=roughness,
            sub_surface=sub_surface,
            normal_strength=normal_strength,
            velvet_softness=velvet_softness,
            silk_sheen=silk_sheen,
            weave_scale=weave_scale,
        )

    @app.tool
    async def create_metal_material(
        name: str = "MetalMaterial",
        metal_type: str = "gold",
        base_color: List[float] = [1.0, 0.8, 0.0],
        roughness: float = 0.2,
        metallic: float = 1.0,
        anisotropy: float = 0.0,
    ) -> str:
        """
        Create a realistic metal material with PBR properties.

        Generates metal materials with appropriate reflectivity,
        roughness, and color properties for different metal types.

        Args:
            name: Name for the new material
            metal_type: Type of metal (gold, silver, brass, copper, iron, aluminum)
            base_color: Base color as RGB values (0-1)
            roughness: Surface roughness (0-1)
            metallic: Metallic property (0-1)
            anisotropy: Surface anisotropy for brushed effects (0-1)

        Returns:
            Confirmation message about material creation
        """
        from blender_mcp.handlers.material_handler import create_metal_material

        return await create_metal_material(
            name=name,
            metal_type=metal_type,
            base_color=tuple(base_color),
            roughness=roughness,
            metallic=metallic,
            anisotropy=anisotropy,
        )

    @app.tool
    async def create_wood_material(
        name: str = "WoodMaterial",
        wood_type: str = "oak",
        base_color: List[float] = [0.6, 0.4, 0.2],
        roughness: float = 0.7,
        grain_scale: float = 1.0,
    ) -> str:
        """
        Create a realistic wood material with grain textures.

        Generates wood materials with procedural grain patterns,
        appropriate colors, and surface properties.

        Args:
            name: Name for the new material
            wood_type: Type of wood (oak, pine, mahogany, walnut, cherry, beech)
            base_color: Base color as RGB values (0-1)
            roughness: Surface roughness (0-1)
            grain_scale: Scale of wood grain pattern (0.1-5.0)

        Returns:
            Confirmation message about material creation
        """
        from blender_mcp.handlers.material_handler import create_wood_material

        return await create_wood_material(
            name=name,
            wood_type=wood_type,
            base_color=tuple(base_color),
            roughness=roughness,
            grain_scale=grain_scale,
        )

    @app.tool
    async def create_glass_material(
        name: str = "GlassMaterial",
        glass_type: str = "clear",
        base_color: List[float] = [0.9, 0.95, 1.0],
        transmission: float = 1.0,
        roughness: float = 0.0,
        ior: float = 1.45,
    ) -> str:
        """
        Create a realistic glass material with transparency.

        Generates glass materials with proper refraction, reflection,
        and transparency properties.

        Args:
            name: Name for the new material
            glass_type: Type of glass (clear, tinted, frosted, stained)
            base_color: Base color as RGB values (0-1)
            transmission: Light transmission amount (0-1)
            roughness: Surface roughness (0-1)
            ior: Index of refraction (1.0-2.5)

        Returns:
            Confirmation message about material creation
        """
        from blender_mcp.handlers.material_handler import create_glass_material

        return await create_glass_material(
            name=name,
            glass_type=glass_type,
            base_color=tuple(base_color),
            transmission=transmission,
            roughness=roughness,
            ior=ior,
        )

    @app.tool
    async def create_ceramic_material(
        name: str = "CeramicMaterial",
        ceramic_type: str = "porcelain",
        base_color: List[float] = [0.95, 0.95, 0.95],
        roughness: float = 0.1,
        glossiness: float = 0.9,
    ) -> str:
        """
        Create a ceramic material with glossy surface properties.

        Generates ceramic materials with appropriate glossiness,
        roughness, and reflective properties.

        Args:
            name: Name for the new material
            ceramic_type: Type of ceramic (porcelain, ceramic, terra_cotta)
            base_color: Base color as RGB values (0-1)
            roughness: Surface roughness (0-1)
            glossiness: Surface glossiness (0-1)

        Returns:
            Confirmation message about material creation
        """
        from blender_mcp.handlers.material_handler import create_ceramic_material

        return await create_ceramic_material(
            name=name,
            ceramic_type=ceramic_type,
            base_color=tuple(base_color),
            roughness=roughness,
            glossiness=glossiness,
        )

    @app.tool
    async def assign_material_to_object(object_name: str, material_name: str) -> str:
        """
        Assign a material to an object in the scene.

        Links an existing material to an object, replacing any existing
        material assignment on the specified material slot.

        Args:
            object_name: Name of the object to assign material to
            material_name: Name of the material to assign

        Returns:
            Confirmation message about material assignment
        """
        from blender_mcp.handlers.material_handler import assign_material_async

        return await assign_material_async(object_name, material_name)

    @app.tool
    async def create_material_from_preset(
        preset_name: str, material_name: Optional[str] = None
    ) -> str:
        """
        Create a material from a predefined preset.

        Uses predefined material configurations to quickly create
        common materials with optimized settings.

        Args:
            preset_name: Name of the material preset to use
            material_name: Optional custom name for the new material

        Returns:
            Confirmation message about material creation from preset
        """
        from blender_mcp.handlers.material_handler import create_material_from_preset

        return await create_material_from_preset(preset_name, material_name)


# Register tools when this module is imported
_register_material_tools()

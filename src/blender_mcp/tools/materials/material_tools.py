"""
Material creation portmanteau tool for Blender MCP.

Provides a single comprehensive tool for creating and managing PBR materials.
"""

from typing import List, Literal

from blender_mcp.compat import *


def get_app():
    from blender_mcp.app import app
    return app


def _register_material_tools():
    """Register the blender_materials portmanteau tool."""
    app = get_app()

    @app.tool
    async def blender_materials(
        operation: Literal[
            "create_fabric", "create_metal", "create_wood", "create_glass",
            "create_ceramic", "assign_to_object", "create_from_preset"
        ] = "create_fabric",
        name: str = "Material",
        # Fabric params
        fabric_type: str = "velvet",
        velvet_softness: float = 0.5,
        silk_sheen: float = 0.8,
        weave_scale: float = 1.0,
        sub_surface: float = 0.2,
        normal_strength: float = 0.5,
        # Metal params
        metal_type: str = "gold",
        metallic: float = 1.0,
        anisotropy: float = 0.0,
        # Wood params
        wood_type: str = "oak",
        grain_scale: float = 1.0,
        # Glass params
        glass_type: str = "clear",
        transmission: float = 1.0,
        ior: float = 1.45,
        # Ceramic params
        ceramic_type: str = "porcelain",
        glossiness: float = 0.9,
        # Common params
        base_color: List[float] = [0.8, 0.8, 0.8],
        roughness: float = 0.5,
        # Assignment params
        object_name: str = "",
        material_name: str = "",
        # Preset params
        preset_name: str = "",
    ) -> str:
        """
        Create and manage PBR materials in Blender.

        Supports multiple operations through the operation parameter:
        - create_fabric: Create fabric material (velvet, silk, cotton, linen, etc.)
        - create_metal: Create metal material (gold, silver, brass, copper, etc.)
        - create_wood: Create wood material (oak, pine, mahogany, walnut, etc.)
        - create_glass: Create glass material (clear, tinted, frosted, stained)
        - create_ceramic: Create ceramic material (porcelain, ceramic, terra_cotta)
        - assign_to_object: Assign existing material to object
        - create_from_preset: Create material from predefined preset

        Args:
            operation: Material operation type
            name: Name for the new material
            fabric_type: Type of fabric (velvet, silk, cotton, linen, brocade, satin, wool)
            velvet_softness: Softness for velvet materials (0-1)
            silk_sheen: Sheen intensity for silk materials (0-1)
            weave_scale: Scale of weave pattern (0.1-10.0)
            sub_surface: Subsurface scattering amount (0-1)
            normal_strength: Normal map intensity (0-1)
            metal_type: Type of metal (gold, silver, brass, copper, iron, aluminum)
            metallic: Metallic property (0-1)
            anisotropy: Surface anisotropy for brushed effects (0-1)
            wood_type: Type of wood (oak, pine, mahogany, walnut, cherry, beech)
            grain_scale: Scale of wood grain pattern (0.1-5.0)
            glass_type: Type of glass (clear, tinted, frosted, stained)
            transmission: Light transmission amount (0-1)
            ior: Index of refraction (1.0-2.5)
            ceramic_type: Type of ceramic (porcelain, ceramic, terra_cotta)
            glossiness: Surface glossiness (0-1)
            base_color: Base color as RGB values (0-1)
            roughness: Surface roughness (0-1)
            object_name: Name of object for assignment
            material_name: Name of material for assignment
            preset_name: Name of material preset to use

        Returns:
            Confirmation message about material operation
        """
        from blender_mcp.handlers.material_handler import (
            assign_material_async,
            create_ceramic_material,
            create_fabric_material,
            create_glass_material,
            create_material_from_preset,
            create_metal_material,
            create_wood_material,
        )

        try:
            color_tuple = tuple(base_color) if len(base_color) == 3 else (0.8, 0.8, 0.8)

            if operation == "create_fabric":
                return await create_fabric_material(
                    name=name,
                    fabric_type=fabric_type,
                    base_color=color_tuple,
                    roughness=roughness,
                    sub_surface=sub_surface,
                    normal_strength=normal_strength,
                    velvet_softness=velvet_softness,
                    silk_sheen=silk_sheen,
                    weave_scale=weave_scale,
                )
            elif operation == "create_metal":
                return await create_metal_material(
                    name=name,
                    metal_type=metal_type,
                    base_color=color_tuple,
                    roughness=roughness,
                    metallic=metallic,
                    anisotropy=anisotropy,
                )
            elif operation == "create_wood":
                return await create_wood_material(
                    name=name,
                    wood_type=wood_type,
                    base_color=color_tuple,
                    roughness=roughness,
                    grain_scale=grain_scale,
                )
            elif operation == "create_glass":
                return await create_glass_material(
                    name=name,
                    glass_type=glass_type,
                    base_color=color_tuple,
                    transmission=transmission,
                    roughness=roughness,
                    ior=ior,
                )
            elif operation == "create_ceramic":
                return await create_ceramic_material(
                    name=name,
                    ceramic_type=ceramic_type,
                    base_color=color_tuple,
                    roughness=roughness,
                    glossiness=glossiness,
                )
            elif operation == "assign_to_object":
                if not object_name or not material_name:
                    return "Error: object_name and material_name required for assign_to_object"
                return await assign_material_async(object_name, material_name)
            elif operation == "create_from_preset":
                if not preset_name:
                    return "Error: preset_name required for create_from_preset"
                return await create_material_from_preset(preset_name, name if name != "Material" else None)
            else:
                return f"Unknown operation: {operation}"
        except Exception as e:
            return f"Error in blender_materials({operation}): {str(e)}"


# Register tools when module is imported
_register_material_tools()

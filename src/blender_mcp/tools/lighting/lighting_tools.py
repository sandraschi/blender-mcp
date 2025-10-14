"""
Lighting creation and management tools for Blender MCP.

Provides tools for creating various types of lights and managing lighting setups.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Union
from blender_mcp.app import get_app


def _register_lighting_tools():
    """Register all lighting-related tools."""
    app = get_app()

    @app.tool
    async def blender_lighting(
        operation: str = "create_sun",
        light_name: str = "Light",
        light_type: str = "SUN",
        location: Tuple[float, float, float] = (5, 5, 5),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        energy: float = 1.0,
        color: Tuple[float, float, float] = (1, 1, 1),
        shadow_soft_size: float = 0.1,
        size: float = 1.0,
        spot_size: float = 45.0,
        spot_blend: float = 0.15
    ) -> str:
        """
        Create and manage lighting in Blender scenes.

        Supports multiple operations through the operation parameter:
        - create_sun: Create directional sun light
        - create_point: Create omnidirectional point light
        - create_spot: Create focused spot light
        - create_area: Create area light for soft shadows
        - setup_three_point: Create basic three-point lighting setup
        - setup_hdri: Set up HDRI environment lighting
        - adjust_light: Modify existing light properties

        Args:
            operation: Operation type
            light_name: Name for the new light
            light_type: Type of light (SUN, POINT, SPOT, AREA)
            location: Light position coordinates
            rotation: Light rotation angles (degrees)
            energy: Light intensity/energy
            color: Light color (RGB 0-1)
            shadow_soft_size: Shadow softness for sun lights
            size: Size for area lights
            spot_size: Beam angle for spot lights (degrees)
            spot_blend: Softness of spot light edge

        Returns:
            Operation result message
        """
        from blender_mcp.handlers.lighting_handler import (
            create_sun_light, create_point_light, create_spot_light, create_area_light,
            setup_three_point_lighting, setup_hdri_environment, adjust_light
        )

        try:
            if operation == "create_sun":
                return await create_sun_light(
                    name=light_name, location=location, rotation=rotation,
                    energy=energy, color=color, shadow_soft_size=shadow_soft_size
                )

            elif operation == "create_point":
                return await create_point_light(
                    name=light_name, location=location, energy=energy, color=color
                )

            elif operation == "create_spot":
                return await create_spot_light(
                    name=light_name, location=location, rotation=rotation,
                    energy=energy, color=color, spot_size=spot_size, spot_blend=spot_blend
                )

            elif operation == "create_area":
                return await create_area_light(
                    name=light_name, location=location, rotation=rotation,
                    energy=energy, color=color, size=size
                )

            elif operation == "setup_three_point":
                return await setup_three_point_lighting()

            elif operation == "setup_hdri":
                return await setup_hdri_environment()

            elif operation == "adjust_light":
                return await adjust_light(
                    name=light_name, location=location, rotation=rotation,
                    energy=energy, color=color
                )

            else:
                return f"Unknown operation: {operation}"

        except Exception as e:
            return f"Error in lighting operation '{operation}': {str(e)}"


_register_lighting_tools()

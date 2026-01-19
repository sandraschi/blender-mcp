"""
Lighting creation and management tools for Blender MCP.

Provides tools for creating various types of lights and managing lighting setups.
"""

from typing import Tuple

from blender_mcp.app import get_app
from blender_mcp.compat import *


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
        spot_blend: float = 0.15,
    ) -> str:
        """
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates 7 related lighting operations into single interface. Prevents tool explosion while maintaining
        full lighting workflow from basic lights to professional HDRI setups. Follows FastMCP 2.14.3 best practices.

        Professional lighting system for Blender supporting all light types, HDRI environments, and lighting rigs.

        **Light Creation (4 operations):**
        - **create_sun**: Generate directional sunlight with shadow control for outdoor scenes
        - **create_point**: Create omnidirectional point light for general illumination
        - **create_spot**: Generate focused spotlight with beam angle and softness control
        - **create_area**: Create rectangular area light for soft, realistic shadows

        **Lighting Setups (2 operations):**
        - **setup_three_point**: Create professional three-point lighting rig (key, fill, rim lights)
        - **setup_hdri**: Configure HDRI environment lighting with world background

        **Light Management (1 operation):**
        - **adjust_light**: Modify properties of existing lights (energy, color, position, etc.)

        Args:
            operation (str, required): The lighting operation to perform. Must be one of: "create_sun",
                "create_point", "create_spot", "create_area", "setup_three_point", "setup_hdri", "adjust_light".
                - Light creation: "create_*" operations (use: light_name, location, rotation, energy, color + type-specific params)
                - Lighting setups: "setup_*" operations (use: minimal parameters, auto-position lights)
                - Light adjustment: "adjust_light" (use: light_name + properties to modify)
            light_name (str): Name for the new light object. Default: "Light". Must be unique in scene.
                Required for: all "create_*" and "adjust_light" operations.
            light_type (str): Type of light for creation operations. One of: "SUN", "POINT", "SPOT", "AREA".
                Default: "SUN". Auto-detected from operation when possible.
            location (Tuple[float, float, float]): 3D position coordinates (x, y, z) in world space.
                Default: (5, 5, 5). Used for: all "create_*" operations.
            rotation (Tuple[float, float, float]): Rotation angles in degrees (x, y, z) around each axis.
                Default: (0, 0, 0). Primarily affects: "create_spot" for beam direction.
            energy (float): Light intensity/energy multiplier. Default: 1.0. Range: 0.0 to 100.0.
                Higher values = brighter light. Used for: all light creation and adjustment.
            color (Tuple[float, float, float]): Light color as RGB values. Default: (1, 1, 1) (white).
                Range: 0.0 to 1.0 per channel. Used for: all light creation and adjustment.
            shadow_soft_size (float): Shadow softness for sun lights. Default: 0.1. Range: 0.0 to 10.0.
                Higher values = softer shadows. Only used for: "create_sun".
            size (float): Physical size of area lights. Default: 1.0. Range: 0.01 to 100.0.
                Larger sizes = softer, more realistic shadows. Only used for: "create_area".
            spot_size (float): Beam angle in degrees for spot lights. Default: 45.0. Range: 1.0 to 180.0.
                Smaller angles = more focused beam. Only used for: "create_spot".
            spot_blend (float): Edge softness for spot lights. Default: 0.15. Range: 0.0 to 1.0.
                Higher values = softer beam edges. Only used for: "create_spot".

        Returns:
            str: Lighting operation result message with success/failure status and light details.
                Format: "SUCCESS: {operation} - {light_name} created at {location}" or
                "ERROR: {operation} failed - {error_details}"

        Raises:
            ValueError: If operation parameters are invalid or light names conflict
            RuntimeError: If Blender lighting system fails or scene state is invalid

        Examples:
            Basic sunlight: blender_lighting("create_sun", light_name="SunLight", energy=2.0, shadow_soft_size=0.5)
            Studio setup: blender_lighting("setup_three_point", energy=1.5)
            Colored spot: blender_lighting("create_spot", light_name="Accent", color=(1, 0.5, 0), spot_size=30.0)
            HDRI environment: blender_lighting("setup_hdri")
            Light adjustment: blender_lighting("adjust_light", light_name="SunLight", energy=3.0, color=(1, 0.9, 0.8))

        Note:
            Three-point lighting automatically positions key (45°), fill (-45°), and rim (135°) lights.
            HDRI setup requires an HDRI image file to be loaded separately.
            Use blender_camera tools to adjust camera exposure for different lighting conditions.
        """
        from loguru import logger

        from blender_mcp.handlers.lighting_handler import (
            adjust_light,
            create_area_light,
            create_point_light,
            create_spot_light,
            create_sun_light,
            setup_hdri_environment,
            setup_three_point_lighting,
        )

        logger.info(
            f"blender_lighting called with operation='{operation}', light_name='{light_name}', location={location}"
        )

        try:
            # Convert tuple parameters to proper formats
            location_tuple = (
                tuple(float(x) for x in location)
                if hasattr(location, "__iter__") and not isinstance(location, str)
                else location
            )
            rotation_tuple = (
                tuple(float(x) for x in rotation)
                if hasattr(rotation, "__iter__") and not isinstance(rotation, str)
                else rotation
            )
            color_tuple = (
                tuple(float(x) for x in color)
                if hasattr(color, "__iter__") and not isinstance(color, str)
                else color
            )

            # Validate 3-element vectors
            if len(location_tuple) != 3:
                return f"Error: location must be a 3-element array/tuple, got {len(location_tuple)} elements"
            if len(rotation_tuple) != 3:
                return f"Error: rotation must be a 3-element array/tuple, got {len(rotation_tuple)} elements"
            if len(color_tuple) != 3:
                return (
                    f"Error: color must be a 3-element array/tuple, got {len(color_tuple)} elements"
                )

            # Validate color values are in 0-1 range
            if not all(0 <= c <= 1 for c in color_tuple):
                return f"Error: color values must be between 0 and 1, got {color_tuple}"

            if operation == "create_sun":
                return await create_sun_light(
                    name=light_name,
                    location=location_tuple,
                    rotation=rotation_tuple,
                    energy=energy,
                    color=color_tuple,
                    shadow_soft_size=shadow_soft_size,
                )

            elif operation == "create_point":
                return await create_point_light(
                    name=light_name, location=location_tuple, energy=energy, color=color_tuple
                )

            elif operation == "create_spot":
                return await create_spot_light(
                    name=light_name,
                    location=location_tuple,
                    rotation=rotation_tuple,
                    energy=energy,
                    color=color_tuple,
                    spot_size=spot_size,
                    spot_blend=spot_blend,
                )

            elif operation == "create_area":
                return await create_area_light(
                    name=light_name,
                    location=location_tuple,
                    rotation=rotation_tuple,
                    energy=energy,
                    color=color_tuple,
                    size=size,
                )

            elif operation == "setup_three_point":
                return await setup_three_point_lighting()

            elif operation == "setup_hdri":
                return await setup_hdri_environment()

            elif operation == "adjust_light":
                return await adjust_light(
                    name=light_name,
                    location=location,
                    rotation=rotation,
                    energy=energy,
                    color=color,
                )

            else:
                return f"Unknown operation: {operation}"

        except Exception as e:
            logger.error(f"ERROR: Error in lighting operation '{operation}': {str(e)}")
            return f"Error in lighting operation '{operation}': {str(e)}"


_register_lighting_tools()

"""
Camera control and management tools for Blender MCP.

Provides tools for creating and controlling cameras in Blender scenes.
"""

from blender_mcp.compat import *

from typing import Optional, Tuple
from blender_mcp.app import get_app


def _register_camera_tools():
    """Register all camera-related tools."""
    app = get_app()

    @app.tool
    async def blender_camera(
        operation: str = "create_camera",
        camera_name: str = "Camera",
        location: Tuple[float, float, float] = (0, 10, 0),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        target_location: Optional[Tuple[float, float, float]] = None,
        lens: float = 50.0,
        sensor_width: float = 36.0,
        fov: Optional[float] = None,
        clip_start: float = 0.1,
        clip_end: float = 1000.0,
    ) -> str:
        """
        Create and control cameras in Blender scenes.

        Supports multiple operations through the operation parameter:
        - create_camera: Create a new camera
        - set_active_camera: Set the active camera
        - set_camera_lens: Adjust camera lens and sensor settings

        Args:
            operation: Camera operation type
            camera_name: Name for the camera
            location: Camera position coordinates
            rotation: Camera rotation angles in degrees
            target_location: Target position for look_at operations
            lens: Camera lens focal length in mm
            sensor_width: Camera sensor width in mm
            fov: Field of view in degrees
            clip_start: Near clipping distance
            clip_end: Far clipping distance

        Returns:
            Success message with camera details
        """
        from blender_mcp.handlers.camera_handler import (
            create_camera,
            set_active_camera,
            set_camera_lens,
        )

        from loguru import logger

        logger.info(
            f"📷 blender_camera called with operation='{operation}', camera_name='{camera_name}', location={location}"
        )

        try:
            # Convert parameters to proper formats
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
            target_tuple = (
                tuple(float(x) for x in target_location)
                if target_location
                and hasattr(target_location, "__iter__")
                and not isinstance(target_location, str)
                else target_location
            )

            # Validate 3-element vectors
            if len(location_tuple) != 3:
                return f"Error: location must be a 3-element array/tuple, got {len(location_tuple)} elements"
            if len(rotation_tuple) != 3:
                return f"Error: rotation must be a 3-element array/tuple, got {len(rotation_tuple)} elements"
            if target_tuple and len(target_tuple) != 3:
                return f"Error: target_location must be a 3-element array/tuple, got {len(target_tuple)} elements"

            if operation == "create_camera":
                return await create_camera(
                    name=camera_name,
                    location=location_tuple,
                    rotation=rotation_tuple,
                    lens=lens,
                    sensor_width=sensor_width,
                )

            elif operation == "set_active_camera":
                return await set_active_camera(camera_name=camera_name)

            elif operation == "set_camera_lens":
                return await set_camera_lens(
                    camera_name=camera_name,
                    lens=lens,
                    sensor_width=sensor_width,
                    fov=fov,
                    clip_start=clip_start,
                    clip_end=clip_end,
                )

            else:
                return f"Unknown camera operation: {operation}. Available: create_camera, set_active_camera, set_camera_lens"

        except Exception as e:
            logger.error(f"❌ Error in camera operation '{operation}': {str(e)}")
            return f"Error in camera operation '{operation}': {str(e)}"


_register_camera_tools()

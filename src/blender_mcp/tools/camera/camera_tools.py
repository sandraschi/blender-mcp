"""
Camera control and management tools for Blender MCP.

Provides tools for creating and controlling cameras in Blender scenes.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Union
from blender_mcp.app import get_app


def get_app():
    from blender_mcp.app import app
    return app


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
    clip_end: float = 1000.0
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
            create_camera, set_active_camera, set_camera_lens
        )

        try:
            if operation == "create_camera":
                return await create_camera(
                    name=camera_name,
                    location=location,
                    rotation=rotation,
                    lens=lens,
                    sensor_width=sensor_width
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
                    clip_end=clip_end
                )

            else:
                return f"Unknown camera operation: {operation}. Available: create_camera, set_active_camera, set_camera_lens"

        except Exception as e:
            return f"Error in camera operation '{operation}': {str(e)}"


_register_camera_tools()

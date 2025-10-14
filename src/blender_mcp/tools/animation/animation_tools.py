"""
Animation and motion tools for Blender MCP.

Provides tools for creating keyframes, basic animations, and object motion.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Union
from blender_mcp.app import get_app


def _register_animation_tools():
    """Register all animation-related tools."""
    app = get_app()

    @app.tool
    async def blender_animation(
        operation: str = "set_keyframe",
        object_name: str = "",
        frame: int = 1,
        location: Optional[Tuple[float, float, float]] = None,
        rotation: Optional[Tuple[float, float, float]] = None,
        scale: Optional[Tuple[float, float, float]] = None,
        property_name: str = "location",
        property_value: Union[float, Tuple[float, float, float]] = 0.0,
        interpolation: str = "BEZIER",
        start_frame: int = 1,
        end_frame: int = 60,
        start_location: Tuple[float, float, float] = (0, 0, 0),
        end_location: Tuple[float, float, float] = (5, 0, 0),
        start_rotation: Tuple[float, float, float] = (0, 0, 0),
        end_rotation: Tuple[float, float, float] = (360, 0, 0),
        start_scale: Tuple[float, float, float] = (1, 1, 1),
        end_scale: Tuple[float, float, float] = (2, 2, 2)
    ) -> str:
        """
        Create animations and keyframes for objects in Blender.

        Supports multiple operations through the operation parameter:
        - set_keyframe: Set keyframe for location/rotation/scale
        - animate_location: Animate object movement over frames
        - animate_rotation: Animate object rotation over frames
        - animate_scale: Animate object scaling over frames
        - play_animation: Play animation in viewport
        - set_frame_range: Set animation frame range
        - clear_animation: Clear all keyframes from object

        Args:
            operation: Operation type
            object_name: Name of object to animate
            frame: Frame number for keyframe
            location: Location coordinates for keyframe
            rotation: Rotation angles (degrees) for keyframe
            scale: Scale factors for keyframe
            property_name: Property to animate (location, rotation_euler, scale)
            property_value: Value to set for property
            interpolation: Interpolation type (CONSTANT, LINEAR, BEZIER)
            start_frame: Start frame for animation ranges
            end_frame: End frame for animation ranges
            start_value: Starting value for property animation
            end_value: Ending value for property animation

        Returns:
            Operation result message
        """
        from blender_mcp.handlers.animation_handler import (
            set_keyframe, animate_location, animate_rotation, animate_scale,
            play_animation, set_frame_range, clear_animation
        )

        try:
            if operation == "set_keyframe":
                return await set_keyframe(
                    object_name=object_name, frame=frame,
                    location=location, rotation=rotation, scale=scale
                )

            elif operation == "animate_location":
                return await animate_location(
                    object_name=object_name,
                    start_frame=start_frame, end_frame=end_frame,
                    start_location=start_location, end_location=end_location
                )

            elif operation == "animate_rotation":
                return await animate_rotation(
                    object_name=object_name,
                    start_frame=start_frame, end_frame=end_frame,
                    start_rotation=start_rotation, end_rotation=end_rotation
                )

            elif operation == "animate_scale":
                return await animate_scale(
                    object_name=object_name,
                    start_frame=start_frame, end_frame=end_frame,
                    start_scale=start_scale, end_scale=end_scale
                )

            elif operation == "play_animation":
                return await play_animation()

            elif operation == "set_frame_range":
                return await set_frame_range(start_frame=start_frame, end_frame=end_frame)

            elif operation == "clear_animation":
                return await clear_animation(object_name=object_name)

            else:
                return f"Unknown operation: {operation}"

        except Exception as e:
            return f"Error in animation operation '{operation}': {str(e)}"


_register_animation_tools()

"""
Animation and motion tools for Blender MCP.

Provides tools for creating keyframes, basic animations, and object motion.
"""

from typing import Optional, Tuple, Union
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
        end_scale: Tuple[float, float, float] = (2, 2, 2),
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
            set_keyframe,
            animate_location,
            animate_rotation,
            animate_scale,
            play_animation,
            set_frame_range,
            clear_animation,
        )

        from loguru import logger

        logger.info(
            f"🎬 blender_animation called with operation='{operation}', object_name='{object_name}'"
        )

        try:
            # Convert tuple parameters to proper formats
            location_tuple = (
                tuple(float(x) for x in location)
                if location and hasattr(location, "__iter__") and not isinstance(location, str)
                else location
            )
            rotation_tuple = (
                tuple(float(x) for x in rotation)
                if rotation and hasattr(rotation, "__iter__") and not isinstance(rotation, str)
                else rotation
            )
            scale_tuple = (
                tuple(float(x) for x in scale)
                if scale and hasattr(scale, "__iter__") and not isinstance(scale, str)
                else scale
            )
            start_location_tuple = (
                tuple(float(x) for x in start_location)
                if hasattr(start_location, "__iter__") and not isinstance(start_location, str)
                else start_location
            )
            end_location_tuple = (
                tuple(float(x) for x in end_location)
                if hasattr(end_location, "__iter__") and not isinstance(end_location, str)
                else end_location
            )
            start_rotation_tuple = (
                tuple(float(x) for x in start_rotation)
                if hasattr(start_rotation, "__iter__") and not isinstance(start_rotation, str)
                else start_rotation
            )
            end_rotation_tuple = (
                tuple(float(x) for x in end_rotation)
                if hasattr(end_rotation, "__iter__") and not isinstance(end_rotation, str)
                else end_rotation
            )
            start_scale_tuple = (
                tuple(float(x) for x in start_scale)
                if hasattr(start_scale, "__iter__") and not isinstance(start_scale, str)
                else start_scale
            )
            end_scale_tuple = (
                tuple(float(x) for x in end_scale)
                if hasattr(end_scale, "__iter__") and not isinstance(end_scale, str)
                else end_scale
            )

            # Validate 3-element vectors where applicable
            if location_tuple and len(location_tuple) != 3:
                return f"Error: location must be a 3-element array/tuple, got {len(location_tuple)} elements"
            if rotation_tuple and len(rotation_tuple) != 3:
                return f"Error: rotation must be a 3-element array/tuple, got {len(rotation_tuple)} elements"
            if scale_tuple and len(scale_tuple) != 3:
                return (
                    f"Error: scale must be a 3-element array/tuple, got {len(scale_tuple)} elements"
                )
            if len(start_location_tuple) != 3 or len(end_location_tuple) != 3:
                return "Error: start_location and end_location must be 3-element arrays/tuples"
            if len(start_rotation_tuple) != 3 or len(end_rotation_tuple) != 3:
                return "Error: start_rotation and end_rotation must be 3-element arrays/tuples"
            if len(start_scale_tuple) != 3 or len(end_scale_tuple) != 3:
                return "Error: start_scale and end_scale must be 3-element arrays/tuples"

            if operation == "set_keyframe":
                return await set_keyframe(
                    object_name=object_name,
                    frame=frame,
                    location=location_tuple,
                    rotation=rotation_tuple,
                    scale=scale_tuple,
                )

            elif operation == "animate_location":
                return await animate_location(
                    object_name=object_name,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    start_location=start_location_tuple,
                    end_location=end_location_tuple,
                )

            elif operation == "animate_rotation":
                return await animate_rotation(
                    object_name=object_name,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    start_rotation=start_rotation_tuple,
                    end_rotation=end_rotation_tuple,
                )

            elif operation == "animate_scale":
                return await animate_scale(
                    object_name=object_name,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    start_scale=start_scale_tuple,
                    end_scale=end_scale_tuple,
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
            logger.error(f"❌ Error in animation operation '{operation}': {str(e)}")
            return f"Error in animation operation '{operation}': {str(e)}"


_register_animation_tools()

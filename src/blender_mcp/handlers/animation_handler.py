"""
Animation and motion handler for Blender MCP.

Provides functions for creating keyframes and basic animations.
"""

from typing import Tuple, Optional
from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()


@blender_operation("set_keyframe")
async def set_keyframe(
    object_name: str,
    frame: int = 1,
    location: Optional[Tuple[float, float, float]] = None,
    rotation: Optional[Tuple[float, float, float]] = None,
    scale: Optional[Tuple[float, float, float]] = None,
) -> str:
    """
    Set keyframe for object properties.

    Args:
        object_name: Name of object to animate
        frame: Frame number
        location: Location coordinates (optional)
        rotation: Rotation angles in degrees (optional)
        scale: Scale factors (optional)

    Returns:
        Success message
    """
    location_str = f"obj.location = {location}" if location else ""
    rotation_str = (
        f"obj.rotation_euler = ({rotation[0]} * 3.14159/180, {rotation[1]} * 3.14159/180, {rotation[2]} * 3.14159/180)"
        if rotation
        else ""
    )
    scale_str = f"obj.scale = {scale}" if scale else ""

    script = f"""
import bpy

# Find object
obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{{object_name}}' not found")

# Set properties
{location_str}
{rotation_str}
{scale_str}

# Set keyframe
bpy.context.scene.frame_set({frame})
obj.keyframe_insert(data_path="location")
if {rotation is not None}:
    obj.keyframe_insert(data_path="rotation_euler")
if {scale is not None}:
    obj.keyframe_insert(data_path="scale")

logger.info(f"🎬 Set keyframe for {object_name} at frame {frame}")
"""
    result = await _executor.execute_script(script)
    return f"Set keyframe for '{object_name}' at frame {frame}"


@blender_operation("animate_location")
async def animate_location(
    object_name: str,
    start_frame: int = 1,
    end_frame: int = 60,
    start_location: Tuple[float, float, float] = (0, 0, 0),
    end_location: Tuple[float, float, float] = (5, 0, 0),
) -> str:
    """
    Animate object location over time.

    Args:
        object_name: Name of object to animate
        start_frame: Starting frame
        end_frame: Ending frame
        start_location: Starting location
        end_location: Ending location

    Returns:
        Success message
    """
    script = f"""
import bpy

# Find object
obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{{object_name}}' not found")

# Set start keyframe
bpy.context.scene.frame_set({start_frame})
obj.location = {start_location}
obj.keyframe_insert(data_path="location")

# Set end keyframe
bpy.context.scene.frame_set({end_frame})
obj.location = {end_location}
obj.keyframe_insert(data_path="location")

logger.info(f"🎬 Animated {object_name} location from {start_location} to {end_location}")
"""
    result = await _executor.execute_script(script)
    return f"Animated '{object_name}' location from {start_location} to {end_location} over frames {start_frame}-{end_frame}"


@blender_operation("animate_rotation")
async def animate_rotation(
    object_name: str,
    start_frame: int = 1,
    end_frame: int = 60,
    start_rotation: Tuple[float, float, float] = (0, 0, 0),
    end_rotation: Tuple[float, float, float] = (360, 0, 0),
) -> str:
    """
    Animate object rotation over time.

    Args:
        object_name: Name of object to animate
        start_frame: Starting frame
        end_frame: Ending frame
        start_rotation: Starting rotation angles in degrees
        end_rotation: Ending rotation angles in degrees

    Returns:
        Success message
    """
    script = f"""
import bpy

# Find object
obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{{object_name}}' not found")

# Convert degrees to radians
start_rad = ({start_rotation[0]} * 3.14159/180, {start_rotation[1]} * 3.14159/180, {start_rotation[2]} * 3.14159/180)
end_rad = ({end_rotation[0]} * 3.14159/180, {end_rotation[1]} * 3.14159/180, {end_rotation[2]} * 3.14159/180)

# Set start keyframe
bpy.context.scene.frame_set({start_frame})
obj.rotation_euler = start_rad
obj.keyframe_insert(data_path="rotation_euler")

# Set end keyframe
bpy.context.scene.frame_set({end_frame})
obj.rotation_euler = end_rad
obj.keyframe_insert(data_path="rotation_euler")

logger.info(f"🎬 Animated {object_name} rotation from {start_rotation}° to {end_rotation}°")
"""
    result = await _executor.execute_script(script)
    return f"Animated '{object_name}' rotation from {start_rotation}° to {end_rotation}° over frames {start_frame}-{end_frame}"


@blender_operation("animate_scale")
async def animate_scale(
    object_name: str,
    start_frame: int = 1,
    end_frame: int = 60,
    start_scale: Tuple[float, float, float] = (1, 1, 1),
    end_scale: Tuple[float, float, float] = (2, 2, 2),
) -> str:
    """
    Animate object scale over time.

    Args:
        object_name: Name of object to animate
        start_frame: Starting frame
        end_frame: Ending frame
        start_scale: Starting scale
        end_scale: Ending scale

    Returns:
        Success message
    """
    script = f"""
import bpy

# Find object
obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{{object_name}}' not found")

# Set start keyframe
bpy.context.scene.frame_set({start_frame})
obj.scale = {start_scale}
obj.keyframe_insert(data_path="scale")

# Set end keyframe
bpy.context.scene.frame_set({end_frame})
obj.scale = {end_scale}
obj.keyframe_insert(data_path="scale")

logger.info(f"🎬 Animated {object_name} scale from {start_scale} to {end_scale}")
"""
    result = await _executor.execute_script(script)
    return f"Animated '{object_name}' scale from {start_scale} to {end_scale} over frames {start_frame}-{end_frame}"


@blender_operation("play_animation")
async def play_animation() -> str:
    """
    Start animation playback in viewport.

    Returns:
        Success message
    """
    script = """
import bpy

# Start animation playback
bpy.ops.screen.animation_play()

logger.info("🎬 Started animation playback")
"""
    result = await _executor.execute_script(script)
    return "Started animation playback"


@blender_operation("set_frame_range")
async def set_frame_range(start_frame: int = 1, end_frame: int = 250) -> str:
    """
    Set animation frame range.

    Args:
        start_frame: Start frame
        end_frame: End frame

    Returns:
        Success message
    """
    script = f"""
import bpy

# Set frame range
bpy.context.scene.frame_start = {start_frame}
bpy.context.scene.frame_end = {end_frame}

logger.info(f"🎬 Set frame range to {start_frame}-{end_frame}")
"""
    result = await _executor.execute_script(script)
    return f"Set frame range to {start_frame}-{end_frame}"


@blender_operation("clear_animation")
async def clear_animation(object_name: str) -> str:
    """
    Clear all animation data from object.

    Args:
        object_name: Name of object to clear animation from

    Returns:
        Success message
    """
    script = f"""
import bpy

# Find object
obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{{object_name}}' not found")

# Clear animation data
obj.animation_data_clear()

logger.info(f"🎬 Cleared animation data from {object_name}")
"""
    result = await _executor.execute_script(script)
    return f"Cleared all animation data from '{object_name}'"

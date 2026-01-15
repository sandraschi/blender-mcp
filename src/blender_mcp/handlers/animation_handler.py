"""
Animation and motion handler for Blender MCP.

Provides functions for creating keyframes and basic animations.
"""

from typing import Optional, Tuple

from ..compat import *
from ..decorators import blender_operation
from ..utils.blender_executor import get_blender_executor

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
    await _executor.execute_script(script)
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
    await _executor.execute_script(script)
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
    await _executor.execute_script(script)
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
    await _executor.execute_script(script)
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
    await _executor.execute_script(script)
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
    await _executor.execute_script(script)
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
    await _executor.execute_script(script)
    return f"Cleared all animation data from '{object_name}'"


# =============================================================================
# SHAPE KEYS (Essential for VRM facial expressions)
# =============================================================================

@blender_operation("list_shape_keys")
async def list_shape_keys(object_name: str) -> str:
    """List all shape keys on a mesh object (VRM expressions, morphs)."""
    script = f"""
import bpy

obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{object_name}' not found")
if not obj.data.shape_keys:
    result = {{"object": "{object_name}", "shape_keys": [], "message": "No shape keys found"}}
else:
    keys = []
    for key in obj.data.shape_keys.key_blocks:
        keys.append({{
            "name": key.name,
            "value": key.value,
            "min": key.slider_min,
            "max": key.slider_max
        }})
    result = {{"object": "{object_name}", "shape_keys": keys, "count": len(keys)}}

print(str(result))
"""
    output = await _executor.execute_script(script)
    return output


@blender_operation("set_shape_key")
async def set_shape_key(object_name: str, shape_key_name: str, value: float = 1.0) -> str:
    """Set shape key value (0.0 to 1.0 typically)."""
    script = f"""
import bpy

obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{object_name}' not found")
if not obj.data.shape_keys:
    raise ValueError(f"Object '{object_name}' has no shape keys")

key = obj.data.shape_keys.key_blocks.get("{shape_key_name}")
if not key:
    available = [k.name for k in obj.data.shape_keys.key_blocks]
    raise ValueError(f"Shape key '{shape_key_name}' not found. Available: {{available}}")

key.value = {value}
print(f"Set shape key '{shape_key_name}' to {value}")
"""
    await _executor.execute_script(script)
    return f"Set shape key '{shape_key_name}' on '{object_name}' to {value}"


@blender_operation("keyframe_shape_key")
async def keyframe_shape_key(object_name: str, shape_key_name: str, frame: int = 1, value: float = None) -> str:
    """Insert keyframe for shape key at specified frame."""
    value_str = f"key.value = {value}" if value is not None else ""
    script = f"""
import bpy

obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{object_name}' not found")
if not obj.data.shape_keys:
    raise ValueError(f"Object '{object_name}' has no shape keys")

key = obj.data.shape_keys.key_blocks.get("{shape_key_name}")
if not key:
    raise ValueError(f"Shape key '{shape_key_name}' not found")

bpy.context.scene.frame_set({frame})
{value_str}
key.keyframe_insert(data_path="value", frame={frame})
print(f"Keyframed shape key '{shape_key_name}' at frame {frame} with value {{key.value}}")
"""
    await _executor.execute_script(script)
    return f"Keyframed shape key '{shape_key_name}' on '{object_name}' at frame {frame}"


@blender_operation("create_shape_key")
async def create_shape_key(object_name: str, shape_key_name: str, from_mix: bool = False) -> str:
    """Create a new shape key on mesh object."""
    script = f"""
import bpy

obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{object_name}' not found")
if obj.type != 'MESH':
    raise ValueError(f"Object '{object_name}' is not a mesh")

# Select and make active
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Create basis if needed
if not obj.data.shape_keys:
    bpy.ops.object.shape_key_add(from_mix=False)
    obj.data.shape_keys.key_blocks[0].name = "Basis"

# Create new shape key
bpy.ops.object.shape_key_add(from_mix={str(from_mix)})
new_key = obj.data.shape_keys.key_blocks[-1]
new_key.name = "{shape_key_name}"

print(f"Created shape key '{shape_key_name}' on '{object_name}'")
"""
    await _executor.execute_script(script)
    return f"Created shape key '{shape_key_name}' on '{object_name}'"


# =============================================================================
# ACTION MANAGEMENT (Animation clips)
# =============================================================================

@blender_operation("list_actions")
async def list_actions() -> str:
    """List all actions in the blend file."""
    script = """
import bpy

actions = []
for action in bpy.data.actions:
    actions.append({
        "name": action.name,
        "frame_range": list(action.frame_range),
        "users": action.users
    })

result = {"actions": actions, "count": len(actions)}
print(str(result))
"""
    output = await _executor.execute_script(script)
    return output


@blender_operation("create_action")
async def create_action(action_name: str, object_name: str = None) -> str:
    """Create a new action and optionally assign to object."""
    assign_str = ""
    if object_name:
        assign_str = f"""
obj = bpy.data.objects.get("{object_name}")
if obj:
    if not obj.animation_data:
        obj.animation_data_create()
    obj.animation_data.action = action
"""
    script = f"""
import bpy

action = bpy.data.actions.new(name="{action_name}")
{assign_str}
print(f"Created action '{action_name}'")
"""
    await _executor.execute_script(script)
    msg = f"Created action '{action_name}'"
    if object_name:
        msg += f" and assigned to '{object_name}'"
    return msg


@blender_operation("set_active_action")
async def set_active_action(object_name: str, action_name: str) -> str:
    """Set active action for an object."""
    script = f"""
import bpy

obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{object_name}' not found")

action = bpy.data.actions.get("{action_name}")
if not action:
    available = [a.name for a in bpy.data.actions]
    raise ValueError(f"Action '{action_name}' not found. Available: {{available}}")

if not obj.animation_data:
    obj.animation_data_create()
obj.animation_data.action = action

print(f"Set action '{action_name}' as active for '{object_name}'")
"""
    await _executor.execute_script(script)
    return f"Set action '{action_name}' as active for '{object_name}'"


@blender_operation("push_action_to_nla")
async def push_action_to_nla(object_name: str, track_name: str = None) -> str:
    """Push current action to NLA track (non-destructive animation layering)."""
    track_str = f'"{track_name}"' if track_name else "None"
    script = f"""
import bpy

obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{object_name}' not found")
if not obj.animation_data or not obj.animation_data.action:
    raise ValueError(f"Object '{object_name}' has no active action")

action = obj.animation_data.action
track_name = {track_str} or action.name

# Create NLA track
track = obj.animation_data.nla_tracks.new()
track.name = track_name

# Create strip from action
strip = track.strips.new(action.name, int(action.frame_range[0]), action)

# Clear active action (it's now in NLA)
obj.animation_data.action = None

print(f"Pushed action to NLA track '{track_name}'")
"""
    await _executor.execute_script(script)
    return f"Pushed action to NLA track for '{object_name}'"


# =============================================================================
# INTERPOLATION (Easing, smoothing)
# =============================================================================

@blender_operation("set_interpolation")
async def set_interpolation(
    object_name: str,
    interpolation: str = "BEZIER",
    data_path: str = None
) -> str:
    """Set keyframe interpolation type (CONSTANT, LINEAR, BEZIER, BOUNCE, ELASTIC, etc.)."""
    data_path_filter = f'and fc.data_path == "{data_path}"' if data_path else ""
    script = f"""
import bpy

obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{object_name}' not found")
if not obj.animation_data or not obj.animation_data.action:
    raise ValueError(f"Object '{object_name}' has no animation data")

count = 0
for fc in obj.animation_data.action.fcurves:
    if True {data_path_filter}:
        for kp in fc.keyframe_points:
            kp.interpolation = '{interpolation}'
            count += 1

print(f"Set {{count}} keyframes to {interpolation} interpolation")
"""
    await _executor.execute_script(script)
    return f"Set interpolation to '{interpolation}' for '{object_name}'"


@blender_operation("set_easing")
async def set_easing(object_name: str, easing: str = "AUTO") -> str:
    """Set keyframe easing type (AUTO, EASE_IN, EASE_OUT, EASE_IN_OUT)."""
    script = f"""
import bpy

obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{object_name}' not found")
if not obj.animation_data or not obj.animation_data.action:
    raise ValueError(f"Object '{object_name}' has no animation data")

count = 0
for fc in obj.animation_data.action.fcurves:
    for kp in fc.keyframe_points:
        kp.easing = '{easing}'
        count += 1

print(f"Set {{count}} keyframes to {easing} easing")
"""
    await _executor.execute_script(script)
    return f"Set easing to '{easing}' for '{object_name}'"


# =============================================================================
# CONSTRAINTS (Copy rotation, track-to, etc.)
# =============================================================================

@blender_operation("add_constraint")
async def add_constraint(
    object_name: str,
    constraint_type: str,
    target_name: str = None,
    **kwargs
) -> str:
    """Add constraint to object (COPY_ROTATION, TRACK_TO, DAMPED_TRACK, COPY_LOCATION, etc.)."""
    target_str = ""
    if target_name:
        target_str = f"""
target = bpy.data.objects.get("{target_name}")
if target:
    constraint.target = target
"""
    script = f"""
import bpy

obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{object_name}' not found")

constraint = obj.constraints.new(type='{constraint_type}')
{target_str}

print(f"Added {constraint_type} constraint to '{object_name}'")
"""
    await _executor.execute_script(script)
    return f"Added '{constraint_type}' constraint to '{object_name}'"


@blender_operation("add_bone_constraint")
async def add_bone_constraint(
    armature_name: str,
    bone_name: str,
    constraint_type: str,
    target_armature: str = None,
    target_bone: str = None,
    influence: float = 1.0
) -> str:
    """Add constraint to pose bone (for VRM/character rigs)."""
    target_str = ""
    if target_armature:
        target_str = f"""
target_arm = bpy.data.objects.get("{target_armature}")
if target_arm:
    constraint.target = target_arm
    if "{target_bone}":
        constraint.subtarget = "{target_bone}"
"""
    script = f"""
import bpy

armature = bpy.data.objects.get("{armature_name}")
if not armature or armature.type != 'ARMATURE':
    raise ValueError(f"Armature '{armature_name}' not found")

# Enter pose mode
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

pbone = armature.pose.bones.get("{bone_name}")
if not pbone:
    raise ValueError(f"Bone '{bone_name}' not found")

constraint = pbone.constraints.new(type='{constraint_type}')
constraint.influence = {influence}
{target_str}

bpy.ops.object.mode_set(mode='OBJECT')
print(f"Added {constraint_type} constraint to bone '{bone_name}'")
"""
    await _executor.execute_script(script)
    return f"Added '{constraint_type}' constraint to bone '{bone_name}' on '{armature_name}'"


# =============================================================================
# BAKE ANIMATION (Export-ready)
# =============================================================================

@blender_operation("bake_action")
async def bake_action(
    object_name: str,
    frame_start: int = 1,
    frame_end: int = 250,
    only_selected: bool = False,
    visual_keying: bool = True,
    clear_constraints: bool = False,
    bake_types: str = "POSE"  # POSE, OBJECT, or both
) -> str:
    """Bake constraints/physics to keyframes (essential for export)."""
    script = f"""
import bpy

obj = bpy.data.objects.get("{object_name}")
if not obj:
    raise ValueError(f"Object '{object_name}' not found")

# Select object
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Enter pose mode if armature
if obj.type == 'ARMATURE':
    bpy.ops.object.mode_set(mode='POSE')
    if not {only_selected}:
        bpy.ops.pose.select_all(action='SELECT')

# Bake action
bpy.ops.nla.bake(
    frame_start={frame_start},
    frame_end={frame_end},
    only_selected={only_selected},
    visual_keying={visual_keying},
    clear_constraints={clear_constraints},
    bake_types={{'{bake_types}'}}
)

bpy.ops.object.mode_set(mode='OBJECT')
print(f"Baked animation for '{object_name}' frames {frame_start}-{frame_end}")
"""
    await _executor.execute_script(script)
    return f"Baked animation for '{object_name}' from frame {frame_start} to {frame_end}"


@blender_operation("bake_all_actions")
async def bake_all_actions(armature_name: str, frame_start: int = 1, frame_end: int = 250) -> str:
    """Bake all NLA strips to a single action (for VRM export)."""
    script = f"""
import bpy

armature = bpy.data.objects.get("{armature_name}")
if not armature or armature.type != 'ARMATURE':
    raise ValueError(f"Armature '{armature_name}' not found")

bpy.ops.object.select_all(action='DESELECT')
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='SELECT')

# Bake with all NLA influence
bpy.ops.nla.bake(
    frame_start={frame_start},
    frame_end={frame_end},
    only_selected=False,
    visual_keying=True,
    clear_constraints=False,
    bake_types={{'POSE'}}
)

bpy.ops.object.mode_set(mode='OBJECT')
print(f"Baked all NLA to single action for '{armature_name}'")
"""
    await _executor.execute_script(script)
    return f"Baked all NLA strips to single action for '{armature_name}'"

"""
Animation and motion tools for Blender MCP.

Comprehensive animation support including keyframes, shape keys (VRM expressions),
action management, constraints, and animation baking for export.
"""

from blender_mcp.compat import *

from typing import Optional, Tuple, Union, Literal
from blender_mcp.app import get_app


def _register_animation_tools():
    """Register all animation-related tools."""
    app = get_app()

    @app.tool
    async def blender_animation(
        operation: Literal[
            # Basic keyframes
            "set_keyframe", "animate_location", "animate_rotation", "animate_scale",
            "play_animation", "set_frame_range", "clear_animation",
            # Shape keys (VRM facial expressions)
            "list_shape_keys", "set_shape_key", "keyframe_shape_key", "create_shape_key",
            # Action management
            "list_actions", "create_action", "set_active_action", "push_to_nla",
            # Interpolation
            "set_interpolation", "set_easing",
            # Constraints
            "add_constraint", "add_bone_constraint",
            # Baking
            "bake_action", "bake_all_actions"
        ] = "set_keyframe",
        # Object/target
        object_name: str = "",
        armature_name: str = "",
        bone_name: str = "",
        # Frame parameters
        frame: int = 1,
        start_frame: int = 1,
        end_frame: int = 60,
        # Transform parameters
        location: Optional[Tuple[float, float, float]] = None,
        rotation: Optional[Tuple[float, float, float]] = None,
        scale: Optional[Tuple[float, float, float]] = None,
        start_location: Tuple[float, float, float] = (0, 0, 0),
        end_location: Tuple[float, float, float] = (5, 0, 0),
        start_rotation: Tuple[float, float, float] = (0, 0, 0),
        end_rotation: Tuple[float, float, float] = (360, 0, 0),
        start_scale: Tuple[float, float, float] = (1, 1, 1),
        end_scale: Tuple[float, float, float] = (2, 2, 2),
        # Shape key parameters
        shape_key_name: str = "",
        value: float = 1.0,
        from_mix: bool = False,
        # Action parameters
        action_name: str = "",
        track_name: str = "",
        # Interpolation parameters
        interpolation: str = "BEZIER",
        easing: str = "AUTO",
        data_path: str = "",
        # Constraint parameters
        constraint_type: str = "COPY_ROTATION",
        target_name: str = "",
        target_armature: str = "",
        target_bone: str = "",
        influence: float = 1.0,
        # Bake parameters
        visual_keying: bool = True,
        clear_constraints: bool = False,
        bake_types: str = "POSE",
    ) -> str:
        """
        Comprehensive animation tool for Blender.

        BASIC ANIMATION:
        - set_keyframe: Insert keyframe for location/rotation/scale
        - animate_location: Animate movement between frames
        - animate_rotation: Animate rotation between frames
        - animate_scale: Animate scale between frames
        - play_animation: Start viewport playback
        - set_frame_range: Set timeline start/end frames
        - clear_animation: Remove all keyframes from object

        SHAPE KEYS (VRM facial expressions):
        - list_shape_keys: List all shape keys/morphs on mesh
        - set_shape_key: Set shape key value (0.0-1.0)
        - keyframe_shape_key: Insert keyframe for shape key
        - create_shape_key: Create new shape key

        ACTION MANAGEMENT:
        - list_actions: List all actions in file
        - create_action: Create new action clip
        - set_active_action: Assign action to object
        - push_to_nla: Push action to NLA track for layering

        INTERPOLATION:
        - set_interpolation: Set keyframe type (LINEAR, BEZIER, BOUNCE, etc.)
        - set_easing: Set easing (AUTO, EASE_IN, EASE_OUT, EASE_IN_OUT)

        CONSTRAINTS:
        - add_constraint: Add constraint to object
        - add_bone_constraint: Add constraint to pose bone

        BAKING (for export):
        - bake_action: Bake constraints to keyframes
        - bake_all_actions: Bake NLA to single action

        Args:
            operation: Animation operation type
            object_name: Target object name
            armature_name: Target armature (for bone operations)
            bone_name: Target bone name
            frame: Frame number for keyframe
            start_frame/end_frame: Frame range
            location/rotation/scale: Transform values
            shape_key_name: Name of shape key
            value: Shape key value (0.0-1.0)
            action_name: Name for action
            interpolation: CONSTANT, LINEAR, BEZIER, BOUNCE, ELASTIC
            easing: AUTO, EASE_IN, EASE_OUT, EASE_IN_OUT
            constraint_type: COPY_ROTATION, TRACK_TO, DAMPED_TRACK, etc.
            target_name: Constraint target object
            visual_keying: Include visual transforms in bake
            clear_constraints: Remove constraints after bake

        Returns:
            Operation result message
        """
        from blender_mcp.handlers.animation_handler import (
            # Basic
            set_keyframe, animate_location, animate_rotation, animate_scale,
            play_animation, set_frame_range, clear_animation,
            # Shape keys
            list_shape_keys, set_shape_key, keyframe_shape_key, create_shape_key,
            # Actions
            list_actions, create_action, set_active_action, push_action_to_nla,
            # Interpolation
            set_interpolation as _set_interpolation, set_easing as _set_easing,
            # Constraints
            add_constraint, add_bone_constraint,
            # Baking
            bake_action, bake_all_actions,
        )

        from loguru import logger
        logger.info(f"🎬 blender_animation: {operation}")

        try:
            # Helper to convert tuples
            def to_tuple(val):
                if val and hasattr(val, "__iter__") and not isinstance(val, str):
                    return tuple(float(x) for x in val)
                return val

            # BASIC ANIMATION
            if operation == "set_keyframe":
                return await set_keyframe(
                    object_name=object_name, frame=frame,
                    location=to_tuple(location), rotation=to_tuple(rotation), scale=to_tuple(scale)
                )
            elif operation == "animate_location":
                return await animate_location(
                    object_name=object_name, start_frame=start_frame, end_frame=end_frame,
                    start_location=to_tuple(start_location), end_location=to_tuple(end_location)
                )
            elif operation == "animate_rotation":
                return await animate_rotation(
                    object_name=object_name, start_frame=start_frame, end_frame=end_frame,
                    start_rotation=to_tuple(start_rotation), end_rotation=to_tuple(end_rotation)
                )
            elif operation == "animate_scale":
                return await animate_scale(
                    object_name=object_name, start_frame=start_frame, end_frame=end_frame,
                    start_scale=to_tuple(start_scale), end_scale=to_tuple(end_scale)
                )
            elif operation == "play_animation":
                return await play_animation()
            elif operation == "set_frame_range":
                return await set_frame_range(start_frame=start_frame, end_frame=end_frame)
            elif operation == "clear_animation":
                return await clear_animation(object_name=object_name)

            # SHAPE KEYS
            elif operation == "list_shape_keys":
                return await list_shape_keys(object_name=object_name)
            elif operation == "set_shape_key":
                return await set_shape_key(object_name=object_name, shape_key_name=shape_key_name, value=value)
            elif operation == "keyframe_shape_key":
                return await keyframe_shape_key(
                    object_name=object_name, shape_key_name=shape_key_name,
                    frame=frame, value=value if value != 1.0 else None
                )
            elif operation == "create_shape_key":
                return await create_shape_key(object_name=object_name, shape_key_name=shape_key_name, from_mix=from_mix)

            # ACTION MANAGEMENT
            elif operation == "list_actions":
                return await list_actions()
            elif operation == "create_action":
                return await create_action(action_name=action_name, object_name=object_name if object_name else None)
            elif operation == "set_active_action":
                return await set_active_action(object_name=object_name, action_name=action_name)
            elif operation == "push_to_nla":
                return await push_action_to_nla(object_name=object_name, track_name=track_name if track_name else None)

            # INTERPOLATION
            elif operation == "set_interpolation":
                return await _set_interpolation(
                    object_name=object_name, interpolation=interpolation,
                    data_path=data_path if data_path else None
                )
            elif operation == "set_easing":
                return await _set_easing(object_name=object_name, easing=easing)

            # CONSTRAINTS
            elif operation == "add_constraint":
                return await add_constraint(
                    object_name=object_name, constraint_type=constraint_type,
                    target_name=target_name if target_name else None
                )
            elif operation == "add_bone_constraint":
                return await add_bone_constraint(
                    armature_name=armature_name, bone_name=bone_name,
                    constraint_type=constraint_type,
                    target_armature=target_armature if target_armature else None,
                    target_bone=target_bone if target_bone else None,
                    influence=influence
                )

            # BAKING
            elif operation == "bake_action":
                return await bake_action(
                    object_name=object_name, frame_start=start_frame, frame_end=end_frame,
                    visual_keying=visual_keying, clear_constraints=clear_constraints,
                    bake_types=bake_types
                )
            elif operation == "bake_all_actions":
                return await bake_all_actions(
                    armature_name=armature_name, frame_start=start_frame, frame_end=end_frame
                )

            else:
                return f"Unknown operation: {operation}"

        except Exception as e:
            logger.error(f"❌ Animation error ({operation}): {str(e)}")
            return f"Error in {operation}: {str(e)}"


_register_animation_tools()

"""
Animation and motion tools for Blender MCP.

Comprehensive animation support including keyframes, shape keys (VRM expressions),
action management, constraints, and animation baking for export.
"""

from typing import Literal, Optional, Tuple

from blender_mcp.app import get_app
from blender_mcp.compat import *


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
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates 17 related animation operations into single interface. Prevents tool explosion while maintaining
        full animation workflow functionality from basic keyframes to advanced character rigging. Follows FastMCP 2.14.3 best practices.

        Comprehensive animation system for Blender supporting keyframes, shape keys, actions, constraints, and baking.

        **Animation Categories:**

        **Basic Animation (7 operations):**
        - **set_keyframe**: Insert keyframes for location/rotation/scale at specific frames
        - **animate_location**: Create movement animation between start/end frames
        - **animate_rotation**: Create rotation animation with customizable curves
        - **animate_scale**: Create scale animation with interpolation control
        - **play_animation**: Start/stop viewport playback for preview
        - **set_frame_range**: Define timeline start/end frames for scene
        - **clear_animation**: Remove all keyframes from object (destructive)

        **Shape Keys (VRM facial expressions) (4 operations):**
        - **list_shape_keys**: Display all morph targets on mesh object
        - **set_shape_key**: Set blend value (0.0-1.0) for shape key
        - **keyframe_shape_key**: Insert keyframe for shape key animation
        - **create_shape_key**: Create new shape key from current mesh state

        **Action Management (4 operations):**
        - **list_actions**: Show all animation actions in blend file
        - **create_action**: Generate new action clip for object animation
        - **set_active_action**: Assign action to object for playback
        - **push_to_nla**: Push action to NLA track for layering/compositing

        **Interpolation & Timing (2 operations):**
        - **set_interpolation**: Set keyframe interpolation type (LINEAR, BEZIER, BOUNCE, ELASTIC, CONSTANT)
        - **set_easing**: Configure easing curves (AUTO, EASE_IN, EASE_OUT, EASE_IN_OUT)

        **Constraints (2 operations):**
        - **add_constraint**: Add transform constraints to objects
        - **add_bone_constraint**: Add pose constraints to armature bones

        **Baking for Export (2 operations):**
        - **bake_action**: Convert constraints to keyframes for export compatibility
        - **bake_all_actions**: Consolidate NLA strips into single action

        Args:
            operation (Literal, required): The animation operation to perform. Must be one of: "set_keyframe",
                "animate_location", "animate_rotation", "animate_scale", "play_animation", "set_frame_range",
                "clear_animation", "list_shape_keys", "set_shape_key", "keyframe_shape_key", "create_shape_key",
                "list_actions", "create_action", "set_active_action", "push_to_nla", "set_interpolation",
                "set_easing", "add_constraint", "add_bone_constraint", "bake_action", "bake_all_actions".
                - Basic operations: "set_keyframe", "animate_*", "play_animation", "set_frame_range", "clear_animation"
                - Shape key operations: "list_shape_keys", "set_shape_key", "keyframe_shape_key", "create_shape_key"
                - Action operations: "list_actions", "create_action", "set_active_action", "push_to_nla"
                - Interpolation: "set_interpolation", "set_easing"
                - Constraints: "add_constraint", "add_bone_constraint"
                - Baking: "bake_action", "bake_all_actions"
            object_name (str): Target object name for animation operations. Required for most operations.
            armature_name (str): Target armature name for bone-specific operations.
                Required for: "add_bone_constraint", bone targeting in constraints.
            bone_name (str): Target bone name within armature for pose operations.
                Required for: "add_bone_constraint", bone targeting in constraints.
            frame (int): Frame number for keyframe insertion. Default: 1. Range: 1 to 10000.
            start_frame (int): Starting frame for animation ranges. Default: 1. Must be < end_frame.
            end_frame (int): Ending frame for animation ranges. Default: 60. Must be > start_frame.
            location (Tuple[float, float, float] | None): Target location coordinates (x, y, z) for keyframes.
                Required for: "set_keyframe" (location), "animate_location".
            rotation (Tuple[float, float, float] | None): Target rotation values (degrees) for keyframes.
                Required for: "set_keyframe" (rotation), "animate_rotation".
            scale (Tuple[float, float, float] | None): Target scale factors (x, y, z) for keyframes.
                Required for: "set_keyframe" (scale), "animate_scale".
            start_location (Tuple[float, float, float]): Starting location for animation. Default: (0, 0, 0).
            end_location (Tuple[float, float, float]): Ending location for animation. Default: (5, 0, 0).
            start_rotation (Tuple[float, float, float]): Starting rotation for animation. Default: (0, 0, 0).
            end_rotation (Tuple[float, float, float]): Ending rotation for animation. Default: (360, 0, 0).
            start_scale (Tuple[float, float, float]): Starting scale for animation. Default: (1, 1, 1).
            end_scale (Tuple[float, float, float]): Ending scale for animation. Default: (2, 2, 2).
            shape_key_name (str): Name of shape key for morph operations.
                Required for: "set_shape_key", "keyframe_shape_key", "create_shape_key".
            value (float): Shape key blend value. Range: 0.0 to 1.0. Default: 1.0.
                Required for: "set_shape_key", "keyframe_shape_key".
            from_mix (bool): Whether to create shape key from current mix. Default: False.
            action_name (str): Name for new or existing action.
                Required for: "create_action", "set_active_action", "push_to_nla".
            track_name (str): NLA track name for action placement. Default: auto-generated.
            interpolation (str): Keyframe interpolation type. One of: "CONSTANT", "LINEAR", "BEZIER", "SINE",
                "QUAD", "CUBIC", "QUART", "QUINT", "EXPO", "CIRC", "BACK", "BOUNCE", "ELASTIC". Default: "BEZIER".
            easing (str): Keyframe easing mode. One of: "AUTO", "EASE_IN", "EASE_OUT", "EASE_IN_OUT". Default: "AUTO".
            data_path (str): FCurve data path for interpolation operations. Default: auto-detected.
            constraint_type (str): Type of constraint to add. One of: "COPY_ROTATION", "COPY_LOCATION",
                "COPY_SCALE", "TRACK_TO", "DAMPED_TRACK", "LOCKED_TRACK", "STRETCH_TO", "CLAMP_TO",
                "TRANSFORM", "CHILD_OF". Default: "COPY_ROTATION".
            target_name (str): Name of target object for constraint. Required for all constraint operations.
            target_armature (str): Name of target armature for bone constraints.
            target_bone (str): Name of target bone for bone constraints.
            influence (float): Constraint influence factor. Range: 0.0 to 1.0. Default: 1.0.
            visual_keying (bool): Include visual transforms in baking. Default: True.
            clear_constraints (bool): Remove constraints after baking. Default: False.
            bake_types (str): Types of data to bake. One of: "POSE", "OBJECT", "ALL". Default: "POSE".

        Returns:
            str: Operation result message with success/failure status and details.
                Format: "SUCCESS: {operation} - {details}" or "ERROR: {operation} failed - {error_details}"

        Raises:
            ValueError: If operation parameters are invalid or target objects don't exist
            RuntimeError: If Blender animation system fails or scene state is invalid

        Examples:
            Basic keyframe: blender_animation("set_keyframe", object_name="Cube", frame=10, location=(5, 0, 0))
            Shape key animation: blender_animation("keyframe_shape_key", object_name="Face", shape_key_name="Smile", frame=20, value=1.0)
            Action creation: blender_animation("create_action", object_name="Character", action_name="WalkCycle")
            Constraint setup: blender_animation("add_constraint", object_name="Camera", constraint_type="TRACK_TO", target_name="Empty")

        Note:
            Shape keys require mesh objects. Actions work with any animatable object.
            Baking operations are essential for game engine export compatibility.
            Use blender_rigging tools first for character setup before animation.
        """
        from loguru import logger

        from blender_mcp.handlers.animation_handler import (
            add_bone_constraint,
            # Constraints
            add_constraint,
            animate_location,
            animate_rotation,
            animate_scale,
            # Baking
            bake_action,
            bake_all_actions,
            clear_animation,
            create_action,
            create_shape_key,
            keyframe_shape_key,
            # Actions
            list_actions,
            # Shape keys
            list_shape_keys,
            play_animation,
            push_action_to_nla,
            set_active_action,
            set_frame_range,
            # Basic
            set_keyframe,
            set_shape_key,
        )
        from blender_mcp.handlers.animation_handler import (
            set_easing as _set_easing,
        )
        from blender_mcp.handlers.animation_handler import (
            # Interpolation
            set_interpolation as _set_interpolation,
        )
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

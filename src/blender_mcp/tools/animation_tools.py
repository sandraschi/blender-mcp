"""
Animation Tools for Blender-MCP.

This module provides tools for animation and rigging operations in Blender.
"""
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from ..compat import JSONType
from blender_mcp.handlers.animation_handler import (
    insert_keyframe,
    bake_animation,
    create_armature,
    add_bone,
    create_constraint,
    create_action,
    apply_animation
)
from blender_mcp.tools import register_tool, validate_with
from blender_mcp.utils.error_handling import handle_errors
from blender_mcp.utils.validation import (
    validate_object_exists,
    validate_vertex_group,
    BaseValidator,
    ObjectValidator
)

# Enums for animation types
class KeyframeType(str, Enum):
    LOCATION = "LOCATION"
    ROTATION = "ROTATION"
    SCALE = "SCALE"
    LOC_ROT = "LOC_ROT"
    LOC_SCALE = "LOC_SCALE"
    ROT_SCALE = "ROT_SCALE"
    LOC_ROT_SCALE = "LOC_ROT_SCALE"
    DELTA_LOCATION = "DELTA_LOCATION"
    DELTA_ROTATION = "DELTA_ROTATION"
    DELTA_SCALE = "DELTA_SCALE"
    SHAPE_KEY = "SHAPE_KEY"

class InterpolationType(str, Enum):
    CONSTANT = "CONSTANT"
    LINEAR = "LINEAR"
    BEZIER = "BEZIER"
    SINE = "SINE"
    QUAD = "QUAD"
    CUBIC = "CUBIC"
    QUART = "QUART"
    QUINT = "QUINT"
    EXPO = "EXPO"
    CIRC = "CIRC"
    BACK = "BACK"
    BOUNCE = "BOUNCE"
    ELASTIC = "ELASTIC"

class ConstraintType(str, Enum):
    CAMERA_SOLVER = "CAMERA_SOLVER"
    FOLLOW_TRACK = "FOLLOW_TRACK"
    OBJECT_SOLVER = "OBJECT_SOLVER"
    COPY_LOCATION = "COPY_LOCATION"
    COPY_ROTATION = "COPY_ROTATION"
    COPY_SCALE = "COPY_SCALE"
    COPY_TRANSFORMS = "COPY_TRANSFORMS"
    LIMIT_DISTANCE = "LIMIT_DISTANCE"
    LIMIT_LOCATION = "LIMIT_LOCATION"
    LIMIT_ROTATION = "LIMIT_ROTATION"
    LIMIT_SCALE = "LIMIT_SCALE"
    MAINTENANCE = "MAINTENANCE"
    ACTION = "ACTION"
    ARMATURE = "ARMATURE"
    CHILD_OF = "CHILD_OF"
    FLOOR = "FLOOR"
    FOLLOW_PATH = "FOLLOW_PATH"
    PIVOT = "PIVOT"
    SHRINKWRAP = "SHRINKWRAP"
    DAMPED_TRACK = "DAMPED_TRACK"
    IK = "IK"
    LOCKED_TRACK = "LOCKED_TRACK"
    SPLINE_IK = "SPLINE_IK"
    STRETCH_TO = "STRETCH_TO"
    TRACK_TO = "TRACK_TO"
    CLAMP_TO = "CLAMP_TO"
    TRANSFORM = "TRANSFORM"
    TRANSFORM_CACHE = "TRANSFORM_CACHE"

# Parameter Models
class KeyframeParams(BaseValidator, ObjectValidator):
    """Parameters for inserting a keyframe."""
    frame: int = Field(..., ge=0, description="Frame number to insert keyframe")
    keyframe_type: KeyframeType = Field(..., description="Type of keyframe to insert")
    interpolation: InterpolationType = Field(
        InterpolationType.BEZIER,
        description="Interpolation type for the keyframe"
    )
    data_path: str = Field(
        "",
        description="Custom data path (for advanced use, leave empty for automatic)"
    )
    value: Any = Field(
        None,
        description="Value to set (only needed for custom data paths)"
    )

class BakeAnimationParams(BaseValidator, ObjectValidator):
    """Parameters for baking animation."""
    frame_start: int = Field(1, ge=0, description="Start frame")
    frame_end: int = Field(250, ge=1, description="End frame")
    step: int = Field(1, ge=1, le=10, description="Frame step")
    only_selected: bool = Field(True, description="Only bake selected objects")
    visual_keying: bool = Field(False, description="Use visual keying")
    clear_constraints: bool = Field(False, description="Clear constraints after baking")
    clear_parents: bool = Field(False, description="Clear parents after baking")
    bake_types: List[KeyframeType] = Field(
        [KeyframeType.LOC_ROT_SCALE],
        description="Types of keyframes to bake"
    )

class CreateArmatureParams(BaseValidator):
    """Parameters for creating an armature."""
    name: str = Field("Armature", description="Name of the armature object")
    location: List[float] = Field(
        [0.0, 0.0, 0.0],
        min_items=3,
        max_items=3,
        description="Location of the armature"
    )
    enter_edit_mode: bool = Field(True, description="Enter edit mode after creation")
    align: str = Field("WORLD", description="Alignment")

class AddBoneParams(BaseValidator, ObjectValidator):
    """Parameters for adding a bone to an armature."""
    name: str = Field(..., description="Name of the bone")
    head: List[float] = Field(
        [0.0, 0.0, 0.0],
        min_items=3,
        max_items=3,
        description="Head position of the bone"
    )
    tail: List[float] = Field(
        [0.0, 1.0, 0.0],
        min_items=3,
        max_items=3,
        description="Tail position of the bone"
    )
    parent: str = Field("", description="Name of the parent bone (optional)")
    connected: bool = Field(False, description="Connect to parent bone")
    roll: float = Field(0.0, description="Bone roll in radians")

class CreateConstraintParams(BaseValidator, ObjectValidator):
    """Parameters for creating a constraint."""
    constraint_type: ConstraintType = Field(..., description="Type of constraint")
    target: str = Field("", description="Name of the target object")
    subtarget: str = Field("", description="Name of the subtarget (e.g., bone name)")
    influence: float = Field(1.0, ge=0.0, le=1.0, description="Influence of the constraint")
    use_x: bool = Field(True, description="Use X axis")
    use_y: bool = Field(True, description="Use Y axis")
    use_z: bool = Field(True, description="Use Z axis")
    invert_x: bool = Field(False, description="Invert X axis")
    invert_y: bool = Field(False, description="Invert Y axis")
    invert_z: bool = Field(False, description="Invert Z axis")
    mix_mode: str = Field("REPLACE", description="Mix mode for the constraint")
    space: str = Field("WORLD", description="Space for the constraint")
    owner_space: str = Field("WORLD", description="Owner space for the constraint")

class CreateActionParams(BaseValidator, ObjectValidator):
    """Parameters for creating an action."""
    name: str = Field("Action", description="Name of the action")
    frame_start: int = Field(1, ge=0, description="Start frame")
    frame_end: int = Field(250, ge=1, description="End frame")
    use_fake_user: bool = Field(True, description="Set fake user for the action")
    clear_empty: bool = Field(True, description="Clear empty curves")

class ApplyAnimationParams(BaseValidator, ObjectValidator):
    """Parameters for applying animation."""
    frame_start: int = Field(1, ge=0, description="Start frame")
    frame_end: int = Field(250, ge=1, description="End frame")
    bake: bool = Field(True, description="Bake animation before applying")
    visual_keying: bool = Field(False, description="Use visual keying")
    clear_constraints: bool = Field(True, description="Clear constraints after applying")
    clear_parents: bool = Field(False, description="Clear parents after applying")
    bake_types: List[KeyframeType] = Field(
        [KeyframeType.LOC_ROT_SCALE],
        description="Types of keyframes to apply"
    )

# Tool Definitions
@register_tool(
    name="insert_keyframe",
    description="Insert a keyframe for an object's property"
)
@handle_errors
@validate_with(KeyframeParams)
async def insert_keyframe_tool(params: Dict[str, Any]) -> JSONType:
    """Insert a keyframe for an object's property."""
    result = await insert_keyframe(
        object_name=params["object_name"],
        frame=params["frame"],
        keyframe_type=params["keyframe_type"].value,
        interpolation=params["interpolation"].value,
        data_path=params["data_path"] or None,
        value=params["value"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="bake_animation",
    description="Bake animation for an object"
)
@handle_errors
@validate_with(BakeAnimationParams)
async def bake_animation_tool(params: Dict[str, Any]) -> JSONType:
    """Bake animation for an object."""
    result = await bake_animation(
        object_name=params["object_name"],
        frame_start=params["frame_start"],
        frame_end=params["frame_end"],
        step=params["step"],
        only_selected=params["only_selected"],
        visual_keying=params["visual_keying"],
        clear_constraints=params["clear_constraints"],
        clear_parents=params["clear_parents"],
        bake_types=[t.value for t in params["bake_types"]]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="create_armature",
    description="Create a new armature object"
)
@handle_errors
@validate_with(CreateArmatureParams)
async def create_armature_tool(params: Dict[str, Any]) -> JSONType:
    """Create a new armature object."""
    result = await create_armature(
        name=params["name"],
        location=params["location"],
        enter_edit_mode=params["enter_edit_mode"],
        align=params["align"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="add_bone",
    description="Add a bone to an armature"
)
@handle_errors
@validate_with(AddBoneParams)
async def add_bone_tool(params: Dict[str, Any]) -> JSONType:
    """Add a bone to an armature."""
    result = await add_bone(
        object_name=params["object_name"],
        name=params["name"],
        head=params["head"],
        tail=params["tail"],
        parent=params["parent"] or None,
        connected=params["connected"],
        roll=params["roll"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="create_constraint",
    description="Create a constraint on an object"
)
@handle_errors
@validate_with(CreateConstraintParams)
async def create_constraint_tool(params: Dict[str, Any]) -> JSONType:
    """Create a constraint on an object."""
    result = await create_constraint(
        object_name=params["object_name"],
        constraint_type=params["constraint_type"].value,
        target=params["target"] or None,
        subtarget=params["subtarget"] or None,
        influence=params["influence"],
        use_x=params["use_x"],
        use_y=params["use_y"],
        use_z=params["use_z"],
        invert_x=params["invert_x"],
        invert_y=params["invert_y"],
        invert_z=params["invert_z"],
        mix_mode=params["mix_mode"],
        space=params["space"],
        owner_space=params["owner_space"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="create_action",
    description="Create a new action for an object"
)
@handle_errors
@validate_with(CreateActionParams)
async def create_action_tool(params: Dict[str, Any]) -> JSONType:
    """Create a new action for an object."""
    result = await create_action(
        object_name=params["object_name"],
        name=params["name"],
        frame_start=params["frame_start"],
        frame_end=params["frame_end"],
        use_fake_user=params["use_fake_user"],
        clear_empty=params["clear_empty"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="apply_animation",
    description="Apply animation to an object"
)
@handle_errors
@validate_with(ApplyAnimationParams)
async def apply_animation_tool(params: Dict[str, Any]) -> JSONType:
    """Apply animation to an object."""
    result = await apply_animation(
        object_name=params["object_name"],
        frame_start=params["frame_start"],
        frame_end=params["frame_end"],
        bake=params["bake"],
        visual_keying=params["visual_keying"],
        clear_constraints=params["clear_constraints"],
        clear_parents=params["clear_parents"],
        bake_types=[t.value for t in params["bake_types"]]
    )
    return {"status": "SUCCESS", "result": result}

def register() -> None:
    """Register all animation tools."""
    # Tools are registered via decorators
    pass

# Auto-register tools when module is imported
register()

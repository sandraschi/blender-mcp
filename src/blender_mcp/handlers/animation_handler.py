from ..compat import *

"""Animation operations handler for Blender MCP.

This module provides animation and keyframe functions that can be registered as FastMCP tools.
"""

from typing import Optional, Tuple, Dict, Any, Union, List, Literal
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation
from ..app import app

# Initialize the executor with default Blender executable
_executor = get_blender_executor()

class KeyframeType(str, Enum):
    """Supported keyframe types."""
    LOCATION = "LOCATION"
    ROTATION = "ROTATION"
    SCALE = "SCALE"
    LOC_ROT = "LOCATION,ROTATION"
    LOC_SCALE = "LOCATION,SCALE"
    ROT_SCALE = "ROTATION,SCALE"
    LOC_ROT_SCALE = "LOCATION,ROTATION,SCALE"

@blender_operation("insert_keyframe", log_args=True)
async def insert_keyframe(
    object_name: str,
    frame: int = 1,
    keyframe_type: Union[KeyframeType, str] = KeyframeType.LOC_ROT_SCALE,
    **kwargs: Any
) -> Dict[str, Any]:
    """Insert a keyframe for the specified object.
    
    Args:
        object_name: Name of the object to keyframe
        frame: Frame number to insert keyframe
        keyframe_type: Type of keyframe to insert (location, rotation, scale, or combination)
        **kwargs: Additional parameters
            - data_path: Custom data path for the keyframe
            - index: Index for the keyframe data path
            - options: Set of keyframe options (e.g., {'INSERTKEY_NEEDED'})
            
    Returns:
        Dict containing operation status and keyframe details
    """
    data_path = kwargs.get('data_path', '')
    index = kwargs.get('index', -1)  # -1 means all indices
    options = kwargs.get('options', set())
    
    script = f"""

def insert_keyframe():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    # Set the current frame
    bpy.context.scene.frame_set({frame})
    
    # Insert keyframe based on type
    if '{keyframe_type}' in ['LOCATION', 'LOC_ROT', 'LOC_ROT_SCALE', 'LOC_SCALE']:
        obj.keyframe_insert(data_path='location', frame={frame}, index={index})
    
    if '{keyframe_type}' in ['ROTATION', 'LOC_ROT', 'LOC_ROT_SCALE', 'ROT_SCALE']:
        obj.keyframe_insert(data_path='rotation_euler', frame={frame}, index={index})
    
    if '{keyframe_type}' in ['SCALE', 'LOC_SCALE', 'ROT_SCALE', 'LOC_ROT_SCALE']:
        obj.keyframe_insert(data_path='scale', frame={frame}, index={index})
    
    # Handle custom data path if provided
    if '{data_path}':
        obj.keyframe_insert(data_path='{data_path}', frame={frame}, index={index})
    
    return {{
        'status': 'SUCCESS',
        'object': obj.name,
        'frame': {frame},
        'keyframe_type': '{keyframe_type}'
    }}

try:
    result = insert_keyframe()
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(str(result))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to insert keyframe: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("set_animation_range", log_args=True)
async def set_animation_range(
    start_frame: int = 1,
    end_frame: int = 250,
    **kwargs: Any
) -> Dict[str, Any]:
    """Set the animation frame range for the scene.
    
    Args:
        start_frame: First frame of the animation
        end_frame: Last frame of the animation
        **kwargs: Additional parameters
            - frame_current: Current frame to set (optional)
            
    Returns:
        Dict containing operation status and frame range
    """
    current_frame = kwargs.get('frame_current', start_frame)
    
    script = f"""

scene = bpy.context.scene
scene.frame_start = {start_frame}
scene.frame_end = {end_frame}
scene.frame_current = {current_frame}

print(str({{
    'status': 'SUCCESS',
    'start_frame': {start_frame},
    'end_frame': {end_frame},
    'current_frame': {current_frame}
}}))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to set animation range: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("bake_animation", log_args=True)
async def bake_animation(
    object_name: str,
    frame_start: int = 1,
    frame_end: int = 250,
    step: int = 1,
    **kwargs: Any
) -> Dict[str, Any]:
    """Bake animation for the specified object.
    
    Args:
        object_name: Name of the object to bake
        frame_start: First frame to bake
        frame_end: Last frame to bake
        step: Frame step for baking
        **kwargs: Additional parameters
            - only_selected: Only bake selected objects (bool, default: False)
            - visual_keying: Use visual keying (bool, default: True)
            - clear_constraints: Clear constraints after baking (bool, default: False)
            
    Returns:
        Dict containing operation status and bake details
    """
    only_selected = kwargs.get('only_selected', False)
    visual_keying = kwargs.get('visual_keying', True)
    clear_constraints = kwargs.get('clear_constraints', False)
    
    script = f"""

def bake_animation():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    # Select the object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Bake the animation
    bpy.ops.nla.bake(
        frame_start={frame_start},
        frame_end={frame_end},
        step={step},
        only_selected={str(only_selected).lower()},
        visual_keying={str(visual_keying).lower()},
        clear_constraints={str(clear_constraints).lower()},
        bake_types={'OBJECT'}
    )
    
    return {{
        'status': 'SUCCESS',
        'object': obj.name,
        'frame_range': ({frame_start}, {frame_end}),
        'step': {step}
    }}

try:
    result = bake_animation()
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(str(result))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to bake animation: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@app.tool
@blender_operation("create_armature")
async def create_armature(
    name: str = "Armature",
    location: tuple = (0, 0, 0),
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a new armature object.
    
    Args:
        name: Name for the armature object
        location: Position of the armature (x, y, z)
        **kwargs: Additional parameters
            - enter_edit_mode: Whether to enter edit mode after creation (default: True)
            
    Returns:
        Dict containing operation status and armature details
    """
    enter_edit_mode = kwargs.get('enter_edit_mode', True)
    
    script = f"""
import bpy

def create_armature():
    # Create new armature data
    armature_data = bpy.data.armatures.new('{name}_data')
    
    # Create new object with the armature data
    armature = bpy.data.objects.new('{name}', armature_data)
    
    # Link to the current collection
    bpy.context.collection.objects.link(armature)
    
    # Set location
    armature.location = {list(location)}
    
    # Make it the active object
    bpy.context.view_layer.objects.active = armature
    
    # Enter edit mode if requested
    if {str(enter_edit_mode).lower()}:
        bpy.ops.object.mode_set(mode='EDIT')
    
    return {{
        'status': 'SUCCESS',
        'armature': armature.name,
        'location': {list(location)}
    }}

try:
    result = create_armature()
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(str(result))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create armature: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@app.tool
@blender_operation("add_bone")
async def add_bone(
    armature_name: str,
    bone_name: str,
    head: tuple = (0, 0, 0),
    tail: tuple = (0, 1, 0),
    **kwargs: Any
) -> Dict[str, Any]:
    """Add a bone to an armature.
    
    Args:
        armature_name: Name of the armature to add the bone to
        bone_name: Name for the new bone
        head: Head position of the bone (x, y, z)
        tail: Tail position of the bone (x, y, z)
        **kwargs: Additional parameters
            - parent: Name of the parent bone (optional)
            - connected: Whether to connect to parent bone (default: False)
            
    Returns:
        Dict containing operation status and bone details
    """
    parent = kwargs.get('parent', '')
    connected = kwargs.get('connected', False)
    
    script = f"""
import bpy

def add_bone():
    # Get the armature
    armature = bpy.data.objects.get('{armature_name}')
    if not armature or armature.type != 'ARMATURE':
        return {{'status': 'ERROR', 'error': 'Armature not found or invalid type'}}
    
    # Make sure we're in edit mode
    bpy.context.view_layer.objects.active = armature
    if armature.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    # Get edit bones
    edit_bones = armature.data.edit_bones
    
    # Create new bone
    bone = edit_bones.new('{bone_name}')
    bone.head = {list(head)}
    bone.tail = {list(tail)}
    
    # Set parent if specified
    if '{parent}':
        parent_bone = edit_bones.get('{parent}')
        if parent_bone:
            bone.parent = parent_bone
            bone.use_connect = {str(connected).lower()}
    
    return {{
        'status': 'SUCCESS',
        'bone': bone.name,
        'armature': armature.name,
        'head': {list(head)},
        'tail': {list(tail)},
        'parent': '{parent}' if '{parent}' else None
    }}

try:
    result = add_bone()
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(str(result))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to add bone: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@app.tool
@blender_operation("create_constraint")
async def create_constraint(
    object_name: str,
    constraint_type: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a constraint on an object.
    
    Args:
        object_name: Name of the object to add the constraint to
        constraint_type: Type of constraint to add (e.g., 'COPY_LOCATION', 'CHILD_OF')
        **kwargs: Additional parameters for the constraint
            - target: Name of the target object (for constraints that need a target)
            - subtarget: Name of the subtarget (e.g., bone name for armature constraints)
            - influence: Influence of the constraint (0.0 to 1.0)
            - space: Space for the constraint ('WORLD_SPACE' or 'LOCAL_SPACE')
            - owner_space: Owner space for the constraint
            - other constraint-specific parameters
            
    Returns:
        Dict containing operation status and constraint details
    """
    # Common constraint parameters
    target = kwargs.get('target', '')
    subtarget = kwargs.get('subtarget', '')
    influence = kwargs.get('influence', 1.0)
    space = kwargs.get('space', 'WORLD_SPACE')
    owner_space = kwargs.get('owner_space', 'WORLD')
    
    # Filter out None values from kwargs
    constraint_params = {k: v for k, v in kwargs.items() if v is not None}
    
    script = """
import bpy
import json

def create_constraint():
    # Get the object
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    # Create the constraint
    constraint = obj.constraints.new(type='{constraint_type}')
    
    # Set common parameters
    if '{target}':
        target_obj = bpy.data.objects.get('{target}')
        if target_obj:
            constraint.target = target_obj
    
    if hasattr(constraint, 'subtarget') and '{subtarget}':
        constraint.subtarget = '{subtarget}'
    
    if hasattr(constraint, 'influence'):
        constraint.influence = {influence}
    
    if hasattr(constraint, 'owner_space'):
        constraint.owner_space = '{owner_space}'
    
    if hasattr(constraint, 'target_space'):
        constraint.target_space = '{space}'
    
    # Set additional constraint parameters
    constraint_params = {constraint_params}
    for param, value in constraint_params.items():
        if hasattr(constraint, param):
            try:
                setattr(constraint, param, value)
            except Exception as e:
                print(f"Warning: Could not set parameter {{param}}: {{str(e)}}")
    
    return {{
        'status': 'SUCCESS',
        'object': obj.name,
        'constraint': constraint.name,
        'type': '{constraint_type}'
    }}

try:
    result = create_constraint()
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(json.dumps(result))
""".format(
        object_name=object_name,
        constraint_type=constraint_type,
        target=target,
        subtarget=subtarget,
        influence=influence,
        space=space,
        owner_space=owner_space,
        constraint_params=constraint_params
    )
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create constraint: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@app.tool
@blender_operation("create_action")
async def create_action(
    object_name: str,
    action_name: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create or assign an action to an object.
    
    Args:
        object_name: Name of the object to assign the action to
        action_name: Name for the new action
        **kwargs: Additional parameters
            - replace_existing: Whether to replace existing action with same name (default: False)
            - fake_user: Whether to set fake user on the action to prevent deletion (default: True)
            
    Returns:
        Dict containing operation status and action details
    """
    replace_existing = kwargs.get('replace_existing', False)
    fake_user = kwargs.get('fake_user', True)
    
    script = f"""
import bpy
import json

def create_action():
    # Get the object
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    # Check if action with this name already exists
    action = bpy.data.actions.get('{action_name}')
    
    if action:
        if {str(replace_existing).lower()}:
            # Remove existing action if it's not used elsewhere
            if action.users == 0:
                bpy.data.actions.remove(action)
                action = None
        else:
            return {{
                'status': 'ERROR',
                'error': f"Action '{{action_name}}' already exists"
            }}
    
    # Create new action if needed
    if not action:
        action = bpy.data.actions.new('{action_name}')
    
    # Assign the action to the object
    if obj.animation_data is None:
        obj.animation_data_create()
    
    obj.animation_data.action = action
    
    # Set fake user to prevent deletion
    if {str(fake_user).lower()}:
        action.use_fake_user = True
    
    return {{
        'status': 'SUCCESS',
        'object': obj.name,
        'action': action.name,
        'action_path': action.name,
        'fake_user': action.use_fake_user
    }}

try:
    result = create_action()
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(json.dumps(result))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create action: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@app.tool
@blender_operation("apply_animation")
async def apply_animation(
    object_name: str,
    frame: int,
    location: Optional[Tuple[float, float, float]] = None,
    rotation: Optional[Tuple[float, float, float]] = None,
    scale: Optional[Tuple[float, float, float]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Apply animation to an object at a specific frame.
    
    Args:
        object_name: Name of the object to animate
        frame: Frame number to set the keyframe
        location: New location (x, y, z) - optional
        rotation: New rotation in radians (x, y, z) - optional
        scale: New scale (x, y, z) - optional
        **kwargs: Additional parameters
            - keyframe_type: Type of keyframe ('KEYFRAME', 'BREAKDOWN', etc.)
            - interpolation: Interpolation type ('CONSTANT', 'LINEAR', 'BEZIER', etc.)
            
    Returns:
        Dict containing operation status and animation details
    """
    keyframe_type = kwargs.get('keyframe_type', 'KEYFRAME')
    interpolation = kwargs.get('interpolation', 'LINEAR')
    
    script = """
import bpy
import json

def apply_animation():
    # Get the object
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    # Set the current frame
    bpy.context.scene.frame_set({frame})
    
    # Update object properties
    if {location} is not None:
        obj.location = {list(location) if location else None}
    
    if {rotation} is not None:
        if hasattr(obj, 'rotation_euler'):
            obj.rotation_euler = {list(rotation) if rotation else None}
    
    if {scale} is not None:
        obj.scale = {list(scale) if scale else None}
    
    # Insert keyframes
    if {location} is not None:
        obj.keyframe_insert(data_path='location', frame={frame})
    
    if {rotation} is not None and hasattr(obj, 'rotation_euler'):
        obj.keyframe_insert(data_path='rotation_euler', frame={frame})
    
    if {scale} is not None:
        obj.keyframe_insert(data_path='scale', frame={frame})
    
    # Update keyframe interpolation if needed
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                if keyframe.co[0] == {frame}:
                    keyframe.interpolation = '{interpolation}'
                    keyframe.type = '{keyframe_type}'
    
    return {{
        'status': 'SUCCESS',
        'object': obj.name,
        'frame': {frame},
        'location': {list(location) if location else None},
        'rotation': {list(rotation) if rotation else None},
        'scale': {list(scale) if scale else None},
        'keyframe_type': '{keyframe_type}',
        'interpolation': '{interpolation}'
    }}

try:
    result = apply_animation()
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(json.dumps(result))
""".format(
        object_name=object_name,
        frame=frame,
        location=location,
        rotation=rotation,
        scale=scale,
        keyframe_type=keyframe_type,
        interpolation=interpolation
    )
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to apply animation: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

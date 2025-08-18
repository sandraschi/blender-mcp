"""Animation operations handler for Blender MCP.

This module provides animation and keyframe functions that can be registered as FastMCP tools.
"""

from typing import Optional, Tuple, Dict, Any, Union, List, Literal
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

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

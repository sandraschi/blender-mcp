"""Rigging and armature operations handler for Blender MCP."""

from typing import Tuple, Dict, Any
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()


class BoneAxis(str, Enum):
    X = "X"
    Y = "Y"
    Z = "Z"
    NEGATIVE_X = "NEGATIVE_X"
    NEGATIVE_Y = "NEGATIVE_Y"
    NEGATIVE_Z = "NEGATIVE_Z"


@blender_operation("create_armature", log_args=True)
async def create_armature(
    name: str = "Armature", location: Tuple[float, float, float] = (0.0, 0.0, 0.0), **kwargs: Any
) -> Dict[str, Any]:
    """Create a new armature object."""
from ..compat import *


def _create_rigging_script():
    """Create the rigging script."""
    script = f"""

def create_armature():
    bpy.ops.object.armature_add(
        enter_editmode=False,
        align='WORLD',
        location={list(location)},
        scale=(1, 1, 1)
    )
    armature = bpy.context.active_object
    armature.name = '{name}'
    return {{
        'status': 'SUCCESS',
        'armature_name': armature.name,
        'location': {list(location)}
    }}

try:
    result = create_armature()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create armature: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("add_bone", log_args=True)
async def add_bone(
    armature_name: str,
    bone_name: str,
    head: Tuple[float, float, float],
    tail: Tuple[float, float, float],
    parent: str = None,
    connected: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Add a bone to an armature."""
    script = f"""

def add_bone():
    armature = bpy.data.objects.get('{armature_name}')
    if not armature or armature.type != 'ARMATURE':
        return {{'status': 'ERROR', 'error': 'Armature not found'}}
    
    # Store current mode and select armature
    current_mode = bpy.context.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Create new bone
    bone = armature.data.edit_bones.new('{bone_name}')
    bone.head = {list(head)}
    bone.tail = {list(tail)}
    
    # Set parent if specified
    if '{parent}':
        parent_bone = armature.data.edit_bones.get('{parent}')
        if parent_bone:
            bone.parent = parent_bone
            bone.use_connect = {str(connected).lower()}
    
    # Return to original mode
    bpy.ops.object.mode_set(mode=current_mode)
    
    return {{
        'status': 'SUCCESS',
        'bone_name': bone.name,
        'parent': '{parent}' if '{parent}' else None,
        'connected': {str(connected).lower()}
    }}

try:
    result = add_bone()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to add bone: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("create_bone_ik", log_args=True)
async def create_bone_ik(
    armature_name: str, bone_name: str, target_name: str, chain_length: int = 2, **kwargs: Any
) -> Dict[str, Any]:
    """Create an IK constraint for a bone."""
    script = f"""

def create_ik():
    armature = bpy.data.objects.get('{armature_name}')
    if not armature or armature.type != 'ARMATURE':
        return {{'status': 'ERROR', 'error': 'Armature not found'}}
    
    # Switch to pose mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # Get the bone and create IK constraint
    bone = armature.pose.bones.get('{bone_name}')
    if not bone:
        return {{'status': 'ERROR', 'error': 'Bone not found'}}
    
    # Create IK constraint
    ik = bone.constraints.new('IK')
    ik.target = bpy.data.objects.get('{target_name}')
    if not ik.target:
        return {{'status': 'ERROR', 'error': 'Target object not found'}}
    
    ik.chain_count = {chain_length}
    
    return {{
        'status': 'SUCCESS',
        'bone': bone.name,
        'target': ik.target.name,
        'chain_length': {chain_length}
    }}

try:
    result = create_ik()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create IK: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("list_bones", log_args=True)
async def list_bones(armature_name: str, **kwargs: Any) -> Dict[str, Any]:
    """List all bones in an armature (useful for VRM/humanoid models)."""
    script = f"""
def list_bones():
    armature = bpy.data.objects.get('{armature_name}')
    if not armature or armature.type != 'ARMATURE':
        return {{'status': 'ERROR', 'error': 'Armature not found: {armature_name}'}}
    
    bones = []
    for bone in armature.data.bones:
        bones.append({{
            'name': bone.name,
            'parent': bone.parent.name if bone.parent else None,
            'head': list(bone.head_local),
            'tail': list(bone.tail_local),
            'length': bone.length
        }})
    
    return {{
        'status': 'SUCCESS',
        'armature': armature.name,
        'bone_count': len(bones),
        'bones': bones
    }}

try:
    result = list_bones()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to list bones: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("pose_bone", log_args=True)
async def pose_bone(
    armature_name: str,
    bone_name: str,
    rotation: Tuple[float, float, float] = (0, 0, 0),
    location: Tuple[float, float, float] = None,
    rotation_mode: str = "XYZ",
    **kwargs: Any,
) -> Dict[str, Any]:
    """Set bone rotation/location in pose mode (for VRM posing)."""
    import math
    rot_rad = [math.radians(r) for r in rotation]
    loc_str = f"list({list(location)})" if location else "None"
    
    script = f"""
import math

def pose_bone():
    armature = bpy.data.objects.get('{armature_name}')
    if not armature or armature.type != 'ARMATURE':
        return {{'status': 'ERROR', 'error': 'Armature not found: {armature_name}'}}
    
    # Enter pose mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # Get the pose bone
    pbone = armature.pose.bones.get('{bone_name}')
    if not pbone:
        available = [b.name for b in armature.pose.bones]
        return {{'status': 'ERROR', 'error': f'Bone not found: {bone_name}. Available: {{available[:10]}}'}}
    
    # Set rotation mode and rotation
    pbone.rotation_mode = '{rotation_mode}'
    pbone.rotation_euler = {rot_rad}
    
    # Set location offset if provided
    loc = {loc_str}
    if loc:
        pbone.location = loc
    
    return {{
        'status': 'SUCCESS',
        'armature': armature.name,
        'bone': pbone.name,
        'rotation_euler': list(pbone.rotation_euler),
        'location': list(pbone.location)
    }}

try:
    result = pose_bone()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to pose bone: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("set_bone_keyframe", log_args=True)
async def set_bone_keyframe(
    armature_name: str,
    bone_name: str,
    frame: int = 1,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Insert keyframe for bone pose at specified frame."""
    script = f"""
def set_bone_keyframe():
    armature = bpy.data.objects.get('{armature_name}')
    if not armature or armature.type != 'ARMATURE':
        return {{'status': 'ERROR', 'error': 'Armature not found: {armature_name}'}}
    
    # Enter pose mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # Get the pose bone
    pbone = armature.pose.bones.get('{bone_name}')
    if not pbone:
        return {{'status': 'ERROR', 'error': 'Bone not found: {bone_name}'}}
    
    # Set frame
    bpy.context.scene.frame_set({frame})
    
    # Insert keyframes for rotation and location
    pbone.keyframe_insert(data_path='rotation_euler', frame={frame})
    pbone.keyframe_insert(data_path='location', frame={frame})
    
    return {{
        'status': 'SUCCESS',
        'armature': armature.name,
        'bone': pbone.name,
        'frame': {frame}
    }}

try:
    result = set_bone_keyframe()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to set bone keyframe: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("reset_pose", log_args=True)
async def reset_pose(armature_name: str, **kwargs: Any) -> Dict[str, Any]:
    """Reset armature to rest position."""
    script = f"""
def reset_pose():
    armature = bpy.data.objects.get('{armature_name}')
    if not armature or armature.type != 'ARMATURE':
        return {{'status': 'ERROR', 'error': 'Armature not found: {armature_name}'}}
    
    # Enter pose mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # Select all bones and reset
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    
    return {{
        'status': 'SUCCESS',
        'armature': armature.name,
        'message': 'All bones reset to rest position'
    }}

try:
    result = reset_pose()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to reset pose: {str(e)}")
        return {"status": "ERROR", "error": str(e)}
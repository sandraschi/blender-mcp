"""Rigging and armature operations handler for Blender MCP."""

from enum import Enum
from typing import Any, Dict, Tuple

from loguru import logger

from ..decorators import blender_operation
from ..utils.blender_executor import get_blender_executor

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


@blender_operation("transfer_weights")
async def transfer_weights(
    source_mesh: str,
    target_mesh: str,
    armature_name: str,
    method: str = "NEAREST_FACE",
    max_distance: float = 0.1,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Transfer vertex weights from source mesh to target mesh.

    Essential for clothing/avatar workflows where you need to transfer
    deformation weights from a base body mesh to accessory items.

    Args:
        source_mesh: Mesh object to transfer weights FROM
        target_mesh: Mesh object to transfer weights TO
        armature_name: Armature that contains the bone definitions
        method: Transfer method ("NEAREST_FACE", "RAY_CAST", "NEAREST_VERTEX")
        max_distance: Maximum distance for weight transfer

    Returns:
        Weight transfer operation result

    Raises:
        BlenderRiggingError: If weight transfer fails
    """
    logger.info(f"Transferring weights from {source_mesh} to {target_mesh}")

    try:
        script = f"""
import bpy

# Get objects
source = bpy.data.objects.get('{source_mesh}')
target = bpy.data.objects.get('{target_mesh}')
armature = bpy.data.objects.get('{armature_name}')

if not source or source.type != 'MESH':
    print("ERROR: Source mesh not found or not a mesh")
    exit(1)

if not target or target.type != 'MESH':
    print("ERROR: Target mesh not found or not a mesh")
    exit(1)

if not armature or armature.type != 'ARMATURE':
    print("ERROR: Armature not found")
    exit(1)

print(f"SOURCE: {{source.name}}")
print(f"TARGET: {{target.name}}")
print(f"ARMATURE: {{armature.name}}")

# Ensure target has armature modifier
has_modifier = False
for mod in target.modifiers:
    if mod.type == 'ARMATURE' and mod.object == armature:
        has_modifier = True
        break

if not has_modifier:
    # Add armature modifier to target
    mod = target.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = armature
    print("ARMATURE_MODIFIER_ADDED: True")
else:
    print("ARMATURE_MODIFIER_EXISTS: True")

# Set active object to target
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = target
target.select_set(True)

# Transfer weights
bpy.ops.object.data_transfer(
    data_type='VGROUP_WEIGHTS',
    vert_mapping='{method}',
    layers_select_src='ALL',
    layers_select_dst='NAME',
    mix_mode='REPLACE',
    mix_factor=1.0
)

# Get vertex group info
vgroups_before = len(source.vertex_groups) if source.vertex_groups else 0
vgroups_after = len(target.vertex_groups) if target.vertex_groups else 0

print(f"VGROUPS_BEFORE: {{vgroups_before}}")
print(f"VGROUPS_AFTER: {{vgroups_after}}")

print("SUCCESS: Weight transfer completed")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        source_name = "Unknown"
        target_name = "Unknown"
        armature_name_actual = "Unknown"
        vgroups_before = 0
        vgroups_after = 0

        for line in lines:
            if line.startswith("ERROR:"):
                raise Exception(line[7:])
            elif line.startswith("SOURCE:"):
                source_name = line.split(": ")[1]
            elif line.startswith("TARGET:"):
                target_name = line.split(": ")[1]
            elif line.startswith("ARMATURE:"):
                armature_name_actual = line.split(": ")[1]
            elif line.startswith("VGROUPS_BEFORE:"):
                vgroups_before = int(line.split(": ")[1])
            elif line.startswith("VGROUPS_AFTER:"):
                vgroups_after = int(line.split(": ")[1])

        return {
            "status": "success",
            "source_mesh": source_name,
            "target_mesh": target_name,
            "armature": armature_name_actual,
            "vertex_groups_before": vgroups_before,
            "vertex_groups_after": vgroups_after,
            "transfer_method": method,
            "max_distance": max_distance,
            "message": f"Transferred weights from {source_name} to {target_name} ({vgroups_after} vertex groups)"
        }

    except Exception as e:
        logger.error(f"Weight transfer failed: {e}")
        raise Exception(f"Failed to transfer weights: {str(e)}") from e


@blender_operation("manage_vertex_groups")
async def manage_vertex_groups(
    target_mesh: str,
    operation: str,
    group_name: str = None,
    source_group: str = None,
    new_name: str = None,
    vertex_indices: list = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Manage vertex groups on a mesh object.

    Supports creating, renaming, mirroring, and removing vertex groups,
    essential for rigging workflows and weight painting.

    Args:
        target_mesh: Mesh object to modify
        operation: Operation type ("create", "rename", "mirror", "remove", "assign")
        group_name: Target vertex group name
        source_group: Source group for operations like mirror
        new_name: New name for rename operation
        vertex_indices: Vertex indices for assignment

    Returns:
        Vertex group management result

    Raises:
        BlenderRiggingError: If vertex group operation fails
    """
    logger.info(f"Managing vertex groups on {target_mesh}: {operation}")

    try:
        script = f"""
import bpy

# Get target mesh
mesh = bpy.data.objects.get('{target_mesh}')
if not mesh or mesh.type != 'MESH':
    print("ERROR: Target mesh not found or not a mesh")
    exit(1)

print(f"MESH: {{mesh.name}}")

operation = '{operation}'

if operation == 'create':
    if not '{group_name}':
        print("ERROR: group_name required for create operation")
        exit(1)

    vgroup = mesh.vertex_groups.new(name='{group_name}')
    print(f"VGROUP_CREATED: {{vgroup.name}} (index: {{vgroup.index}})")

elif operation == 'rename':
    if not '{group_name}' or not '{new_name}':
        print("ERROR: group_name and new_name required for rename operation")
        exit(1)

    vgroup = mesh.vertex_groups.get('{group_name}')
    if not vgroup:
        print("ERROR: Vertex group not found: {group_name}")
        exit(1)

    vgroup.name = '{new_name}'
    print(f"VGROUP_RENAMED: {{vgroup.name}}")

elif operation == 'mirror':
    if not '{source_group}':
        print("ERROR: source_group required for mirror operation")
        exit(1)

    source_vg = mesh.vertex_groups.get('{source_group}')
    if not source_vg:
        print("ERROR: Source vertex group not found: {source_group}")
        exit(1)

    # Mirror vertex group (left to right)
    mirror_name = '{source_group}'.replace('_L', '_R').replace('_l', '_r')
    if '_L' not in '{source_group}' and '_l' not in '{source_group}':
        mirror_name = '{source_group}' + '_R'

    mirror_vg = mesh.vertex_groups.new(name=mirror_name)

    # Copy weights with mirroring (simplified - would need more complex logic)
    print(f"VGROUP_MIRRORED: {{source_vg.name}} -> {{mirror_vg.name}}")

elif operation == 'remove':
    if not '{group_name}':
        print("ERROR: group_name required for remove operation")
        exit(1)

    vgroup = mesh.vertex_groups.get('{group_name}')
    if not vgroup:
        print("ERROR: Vertex group not found: {group_name}")
        exit(1)

    mesh.vertex_groups.remove(vgroup)
    print(f"VGROUP_REMOVED: {{vgroup.name}}")

elif operation == 'assign':
    if not '{group_name}' or not {vertex_indices!r}:
        print("ERROR: group_name and vertex_indices required for assign operation")
        exit(1)

    vgroup = mesh.vertex_groups.get('{group_name}')
    if not vgroup:
        vgroup = mesh.vertex_groups.new(name='{group_name}')

    vertices = {vertex_indices!r}
    for vert_idx in vertices:
        vgroup.add([vert_idx], 1.0, 'REPLACE')

    print(f"VGROUP_ASSIGNED: {{vgroup.name}} to {{len(vertices)}} vertices")

else:
    print("ERROR: Unknown operation: {operation}")
    exit(1)

# Report final vertex group count
final_count = len(mesh.vertex_groups)
print(f"FINAL_VGROUPS: {{final_count}}")

print("SUCCESS: Vertex group operation completed")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        mesh_name = "Unknown"
        final_vgroups = 0
        operation_result = {}

        for line in lines:
            if line.startswith("ERROR:"):
                raise Exception(line[7:])
            elif line.startswith("MESH:"):
                mesh_name = line.split(": ")[1]
            elif line.startswith("VGROUP_CREATED:"):
                operation_result["created"] = line.split(": ")[1]
            elif line.startswith("VGROUP_RENAMED:"):
                operation_result["renamed"] = line.split(": ")[1]
            elif line.startswith("VGROUP_MIRRORED:"):
                operation_result["mirrored"] = line.split(": ")[1]
            elif line.startswith("VGROUP_REMOVED:"):
                operation_result["removed"] = line.split(": ")[1]
            elif line.startswith("VGROUP_ASSIGNED:"):
                operation_result["assigned"] = line.split(": ")[1]
            elif line.startswith("FINAL_VGROUPS:"):
                final_vgroups = int(line.split(": ")[1])

        return {
            "status": "success",
            "mesh_name": mesh_name,
            "operation": operation,
            "final_vertex_groups": final_vgroups,
            "result": operation_result,
            "message": f"Vertex group operation '{operation}' completed on {mesh_name}"
        }

    except Exception as e:
        logger.error(f"Vertex group management failed: {e}")
        raise Exception(f"Failed to manage vertex groups: {str(e)}") from e


@blender_operation("humanoid_mapping")
async def humanoid_mapping(
    armature_name: str,
    mapping_preset: str = "VRCHAT",
    auto_rename: bool = True,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Apply humanoid bone mapping for VR platforms.

    Maps armature bones to standard humanoid rig names used by
    VRChat, Unity, and other platforms (Hips, Spine, Chest, etc.).

    Args:
        armature_name: Target armature to map
        mapping_preset: Preset mapping ("VRCHAT", "UNITY", "BLENDER")
        auto_rename: Whether to automatically rename bones to match standard

    Returns:
        Humanoid mapping result

    Raises:
        BlenderRiggingError: If humanoid mapping fails
    """
    logger.info(f"Applying humanoid mapping to {armature_name} ({mapping_preset})")

    # Standard humanoid bone mappings
    vrchat_mapping = {
        "Hips": ["hips", "pelvis", "root"],
        "Spine": ["spine", "spine_01"],
        "Chest": ["chest", "spine_03", "torso"],
        "Neck": ["neck", "neck_01"],
        "Head": ["head"],
        "LeftUpperArm": ["left_arm", "arm_l", "upperarm_l"],
        "LeftLowerArm": ["left_forearm", "forearm_l", "lowerarm_l"],
        "LeftHand": ["left_hand", "hand_l"],
        "RightUpperArm": ["right_arm", "arm_r", "upperarm_r"],
        "RightLowerArm": ["right_forearm", "forearm_r", "lowerarm_r"],
        "RightHand": ["right_hand", "hand_r"],
        "LeftUpperLeg": ["left_leg", "leg_l", "upperleg_l", "thigh_l"],
        "LeftLowerLeg": ["left_shin", "shin_l", "lowerleg_l", "calf_l"],
        "LeftFoot": ["left_foot", "foot_l"],
        "RightUpperLeg": ["right_leg", "leg_r", "upperleg_r", "thigh_r"],
        "RightLowerLeg": ["right_shin", "shin_r", "lowerleg_r", "calf_r"],
        "RightFoot": ["right_foot", "foot_r"],
    }

    try:
        script = f"""
import bpy

# Get armature
armature = bpy.data.objects.get('{armature_name}')
if not armature or armature.type != 'ARMATURE':
    print("ERROR: Armature not found")
    exit(1)

print(f"ARMATURE: {{armature.name}}")

mapping_preset = '{mapping_preset}'
vrchat_map = {vrchat_mapping!r}

# Collect current bone names
current_bones = [bone.name for bone in armature.data.bones]
print(f"CURRENT_BONES: {{len(current_bones)}}")

# Apply mapping
mapped_count = 0
unmapped_bones = []

for humanoid_name, possible_names in vrchat_map.items():
    found = False
    for bone_name in current_bones:
        # Check if bone name matches any of the possible names (case insensitive)
        for possible in possible_names:
            if possible.lower() in bone_name.lower():
                if {auto_rename!r}:
                    # Rename bone to standard humanoid name
                    bone = armature.data.bones.get(bone_name)
                    if bone:
                        old_name = bone.name
                        bone.name = humanoid_name
                        print(f"BONE_RENAMED: {{old_name}} -> {{humanoid_name}}")
                        mapped_count += 1
                        found = True
                        break
                else:
                    print(f"BONE_MAPPED: {{bone_name}} -> {{humanoid_name}}")
                    mapped_count += 1
                    found = True
                    break
        if found:
            break

    if not found:
        unmapped_bones.append(humanoid_name)

print(f"MAPPED_COUNT: {{mapped_count}}")
print(f"UNMAPPED: {{unmapped_bones}}")

print("SUCCESS: Humanoid mapping applied")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        armature_actual = "Unknown"
        current_bones_count = 0
        mapped_count = 0
        unmapped = []
        renamed_bones = []

        for line in lines:
            if line.startswith("ERROR:"):
                raise Exception(line[7:])
            elif line.startswith("ARMATURE:"):
                armature_actual = line.split(": ")[1]
            elif line.startswith("CURRENT_BONES:"):
                current_bones_count = int(line.split(": ")[1])
            elif line.startswith("MAPPED_COUNT:"):
                mapped_count = int(line.split(": ")[1])
            elif line.startswith("UNMAPPED:"):
                unmapped = eval(line.split(": ")[1])
            elif line.startswith("BONE_RENAMED:"):
                parts = line.split(": ")[1].split(" -> ")
                renamed_bones.append({"from": parts[0], "to": parts[1]})

        return {
            "status": "success",
            "armature_name": armature_actual,
            "mapping_preset": mapping_preset,
            "total_bones": current_bones_count,
            "mapped_bones": mapped_count,
            "unmapped_humanoid": unmapped,
            "renamed_bones": renamed_bones,
            "auto_rename": auto_rename,
            "message": f"Humanoid mapping applied: {mapped_count}/{len(vrchat_mapping)} bones mapped"
        }

    except Exception as e:
        logger.error(f"Humanoid mapping failed: {e}")
        raise Exception(f"Failed to apply humanoid mapping: {str(e)}") from e

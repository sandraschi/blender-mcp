"""VRM Metadata handler for Blender MCP.

Provides tools for managing VRM-specific metadata including first person offset,
blink/viseme mappings, spring bone parameters, and other VRM avatar data.
"""

from typing import Any, Dict, Optional

from loguru import logger

from ..decorators import blender_operation
from ..exceptions import BlenderVRMError
from ..utils.blender_executor import get_blender_executor

# Initialize the executor with default Blender executable
_executor = get_blender_executor()


@blender_operation("set_first_person_offset")
async def set_first_person_offset(
    offset_x: float = 0.0,
    offset_y: float = 0.0,
    offset_z: float = 0.0,
    target_armature: Optional[str] = None
) -> Dict[str, Any]:
    """
    Set the first person camera offset for VRM avatars.

    This defines where the camera should be positioned when the avatar
    is viewed in first person mode, typically slightly forward of the eyes.

    Args:
        offset_x: X offset from head bone (typically 0.0)
        offset_y: Y offset from head bone (typically 0.0)
        offset_z: Z offset from head bone (typically 0.1-0.2)
        target_armature: Specific armature to modify (defaults to active)

    Returns:
        Confirmation of first person offset setting

    Raises:
        BlenderVRMError: If armature not found or operation fails
    """
    logger.info(f"Setting first person offset: ({offset_x}, {offset_y}, {offset_z})")

    try:
        script = f"""
import bpy

# Get target armature
armature_name = {repr(target_armature)}
if armature_name:
    armature = bpy.data.objects.get(armature_name)
else:
    # Find first armature in scene
    armature = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break

if not armature:
    print("ERROR: No armature found")
    exit(1)

print(f"ARMATURE: {{armature.name}}")

# VRM first person offset is typically stored as custom property
# or in VRM-specific addon data. For now, we'll store it as metadata.
offset_key = "vrm_first_person_offset"
offset_value = [{offset_x}, {offset_y}, {offset_z}]

# Store on armature object
armature[offset_key] = offset_value

print(f"OFFSET_SET: {{offset_value}}")
print("SUCCESS: First person offset configured")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        armature_name = "Unknown"

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderVRMError(line[7:])
            elif line.startswith("ARMATURE:"):
                armature_name = line.split(": ")[1]

        return {
            "status": "success",
            "armature_name": armature_name,
            "first_person_offset": [offset_x, offset_y, offset_z],
            "message": f"First person offset set to ({offset_x}, {offset_y}, {offset_z}) on {armature_name}"
        }

    except Exception as e:
        logger.error(f"First person offset setting failed: {e}")
        raise BlenderVRMError(f"Failed to set first person offset: {str(e)}") from e


@blender_operation("setup_blink_viseme_mappings")
async def setup_blink_viseme_mappings(
    viseme_mappings: Optional[Dict[str, str]] = None,
    blink_shape_key: str = "blink",
    target_mesh: Optional[str] = None
) -> Dict[str, Any]:
    """
    Configure VRM blink and viseme shape key mappings.

    Sets up the standard VRM viseme mappings (A, I, U, E, O) and blink
    functionality that VRChat and other platforms use for facial animation.

    Args:
        viseme_mappings: Custom viseme to shape key mappings (optional)
        blink_shape_key: Shape key name for blink animation
        target_mesh: Target mesh object (defaults to active)

    Returns:
        Viseme mapping configuration result

    Raises:
        BlenderVRMError: If mesh not found or shape keys missing
    """
    logger.info("Setting up VRM blink and viseme mappings")

    # Default VRM viseme mappings
    default_mappings = {
        "aa": "A",    # A sound
        "ih": "I",    # I sound
        "ou": "U",    # U sound
        "ee": "E",    # E sound
        "oh": "O"     # O sound
    }

    if viseme_mappings:
        default_mappings.update(viseme_mappings)

    try:
        script = f"""
import bpy

# Get target mesh
mesh_name = {repr(target_mesh)}
if mesh_name:
    mesh = bpy.data.objects.get(mesh_name)
else:
    mesh = bpy.context.active_object

if not mesh or mesh.type != 'MESH':
    print("ERROR: No valid mesh object selected")
    exit(1)

print(f"MESH: {{mesh.name}}")

# Check for shape keys
if not mesh.data.shape_keys:
    print("WARNING: No shape keys found on mesh")
    shape_count = 0
else:
    shape_count = len(mesh.data.shape_keys.key_blocks)
    print(f"SHAPE_KEYS: {{shape_count}}")

# Check for required viseme shape keys
viseme_keys = {list(default_mappings.values())}
blink_key = {repr(blink_shape_key)}

found_visemes = []
missing_visemes = []

for viseme in viseme_keys:
    if mesh.data.shape_keys and viseme in mesh.data.shape_keys.key_blocks:
        found_visemes.append(viseme)
    else:
        missing_visemes.append(viseme)

# Check blink key
blink_found = False
if mesh.data.shape_keys and blink_key in mesh.data.shape_keys.key_blocks:
    blink_found = True

print(f"FOUND_VISEMES: {{found_visemes}}")
print(f"MISSING_VISEMES: {{missing_visemes}}")
print(f"BLINK_FOUND: {{blink_found}}")

# Store VRM mappings as custom properties
if mesh.data.shape_keys:
    vrm_mappings = {{
        "viseme_mappings": {default_mappings!r},
        "blink_shape_key": {repr(blink_shape_key)}
    }}
    mesh.data.shape_keys["vrm_metadata"] = str(vrm_mappings)

print("SUCCESS: VRM facial mappings configured")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        mesh_name = "Unknown"
        shape_keys_count = 0
        found_visemes = []
        missing_visemes = []
        blink_found = False

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderVRMError(line[7:])
            elif line.startswith("MESH:"):
                mesh_name = line.split(": ")[1]
            elif line.startswith("SHAPE_KEYS:"):
                shape_keys_count = int(line.split(": ")[1])
            elif line.startswith("FOUND_VISEMES:"):
                found_visemes = eval(line.split(": ")[1])
            elif line.startswith("MISSING_VISEMES:"):
                missing_visemes = eval(line.split(": ")[1])
            elif line.startswith("BLINK_FOUND:"):
                blink_found = line.split(": ")[1].lower() == "true"

        result = {
            "status": "success",
            "mesh_name": mesh_name,
            "shape_keys_count": shape_keys_count,
            "viseme_mappings": default_mappings,
            "blink_shape_key": blink_shape_key,
            "found_visemes": found_visemes,
            "missing_visemes": missing_visemes,
            "blink_available": blink_found
        }

        if missing_visemes:
            result["warnings"] = [f"Missing viseme shape keys: {missing_visemes}"]
        if not blink_found:
            result["warnings"] = result.get("warnings", []) + [f"Blink shape key '{blink_shape_key}' not found"]

        return result

    except Exception as e:
        logger.error(f"VRM facial mapping setup failed: {e}")
        raise BlenderVRMError(f"Failed to setup VRM facial mappings: {str(e)}") from e


@blender_operation("configure_spring_bones")
async def configure_spring_bones(
    spring_bone_settings: Optional[Dict[str, Any]] = None,
    target_armature: Optional[str] = None
) -> Dict[str, Any]:
    """
    Configure VRM spring bone parameters for dynamic hair/cloth physics.

    Sets up spring bone parameters that control how hair, tails, ears, etc.
    move and react to movement in VR environments.

    Args:
        spring_bone_settings: Spring bone configuration parameters
        target_armature: Target armature for spring bones

    Returns:
        Spring bone configuration result

    Raises:
        BlenderVRMError: If configuration fails
    """
    logger.info("Configuring VRM spring bones")

    # Default spring bone settings
    default_settings = {
        "stiffness": 0.5,
        "gravity_power": 0.0,
        "gravity_dir": [0, -1, 0],
        "drag_force": 0.5,
        "hit_radius": 0.02,
        "enable_collision": True
    }

    if spring_bone_settings:
        default_settings.update(spring_bone_settings)

    try:
        script = f"""
import bpy

# Get target armature
armature_name = {repr(target_armature)}
if armature_name:
    armature = bpy.data.objects.get(armature_name)
else:
    # Find first armature
    armature = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break

if not armature:
    print("ERROR: No armature found")
    exit(1)

print(f"ARMATURE: {{armature.name}}")

# Store spring bone settings as custom property
settings = {default_settings!r}
armature["vrm_spring_bones"] = str(settings)

print(f"SPRING_SETTINGS: {{settings}}")
print("SUCCESS: Spring bone settings configured")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        armature_name = "Unknown"
        spring_settings = default_settings

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderVRMError(line[7:])
            elif line.startswith("ARMATURE:"):
                armature_name = line.split(": ")[1]

        return {
            "status": "success",
            "armature_name": armature_name,
            "spring_bone_settings": spring_settings,
            "message": f"Spring bone settings configured on {armature_name}"
        }

    except Exception as e:
        logger.error(f"Spring bone configuration failed: {e}")
        raise BlenderVRMError(f"Failed to configure spring bones: {str(e)}") from e


@blender_operation("set_vrm_look_at")
async def set_vrm_look_at(
    look_at_settings: Optional[Dict[str, Any]] = None,
    target_armature: Optional[str] = None
) -> Dict[str, Any]:
    """
    Configure VRM look-at functionality for eye tracking.

    Sets up the look-at parameters that control how the avatar's eyes
    follow the viewer's gaze in VR environments.

    Args:
        look_at_settings: Look-at configuration parameters
        target_armature: Target armature for look-at setup

    Returns:
        Look-at configuration result

    Raises:
        BlenderVRMError: If configuration fails
    """
    logger.info("Configuring VRM look-at functionality")

    # Default look-at settings
    default_settings = {
        "type": "bone",
        "horizontal_inner": {"curve": [0, 0, 0, 1]},
        "horizontal_outer": {"curve": [0, 1, 1, 1]},
        "vertical_down": {"curve": [0, 0, 0, 1]},
        "vertical_up": {"curve": [0, 1, 1, 1]}
    }

    if look_at_settings:
        default_settings.update(look_at_settings)

    try:
        script = f"""
import bpy

# Get target armature
armature_name = {repr(target_armature)}
if armature_name:
    armature = bpy.data.objects.get(armature_name)
else:
    # Find first armature
    armature = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break

if not armature:
    print("ERROR: No armature found")
    exit(1)

print(f"ARMATURE: {{armature.name}}")

# Store look-at settings
settings = {default_settings!r}
armature["vrm_look_at"] = str(settings)

print("SUCCESS: VRM look-at configured")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        armature_name = "Unknown"

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderVRMError(line[7:])
            elif line.startswith("ARMATURE:"):
                armature_name = line.split(": ")[1]

        return {
            "status": "success",
            "armature_name": armature_name,
            "look_at_settings": default_settings,
            "message": f"VRM look-at configured on {armature_name}"
        }

    except Exception as e:
        logger.error(f"VRM look-at configuration failed: {e}")
        raise BlenderVRMError(f"Failed to configure VRM look-at: {str(e)}") from e


@blender_operation("export_vrm_metadata")
async def export_vrm_metadata(
    output_path: str = "//vrm_metadata.json",
    target_armature: Optional[str] = None,
    include_spring_bones: bool = True,
    include_look_at: bool = True
) -> Dict[str, Any]:
    """
    Export VRM metadata for use with VRM exporters.

    Compiles all VRM-specific settings into a JSON file that can be
    used by VRM export tools or imported into other applications.

    Args:
        output_path: Path to save the metadata JSON file
        target_armature: Target armature to export metadata from
        include_spring_bones: Whether to include spring bone settings
        include_look_at: Whether to include look-at settings

    Returns:
        Export result with file path and metadata summary

    Raises:
        BlenderVRMError: If export fails
    """
    logger.info(f"Exporting VRM metadata to {output_path}")

    try:
        script = f"""
import bpy
import json

# Get target armature
armature_name = {repr(target_armature)}
if armature_name:
    armature = bpy.data.objects.get(armature_name)
else:
    # Find first armature
    armature = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
            break

if not armature:
    print("ERROR: No armature found")
    exit(1)

print(f"ARMATURE: {{armature.name}}")

# Collect VRM metadata
metadata = {{
    "armature_name": armature.name,
    "vrm_version": "1.0",
    "exported_from": "Blender MCP"
}}

# First person offset
if "vrm_first_person_offset" in armature:
    metadata["first_person_offset"] = armature["vrm_first_person_offset"]

# Spring bones
if {include_spring_bones!r} and "vrm_spring_bones" in armature:
    try:
        metadata["spring_bones"] = eval(armature["vrm_spring_bones"])
    except:
        metadata["spring_bones"] = armature["vrm_spring_bones"]

# Look at
if {include_look_at!r} and "vrm_look_at" in armature:
    try:
        metadata["look_at"] = eval(armature["vrm_look_at"])
    except:
        metadata["look_at"] = armature["vrm_look_at"]

# Save metadata
output_file = {repr(output_path)}
with open(bpy.path.abspath(output_file), 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"METADATA_SAVED: {{output_file}}")
print("SUCCESS: VRM metadata exported")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        armature_name = "Unknown"
        metadata_file = output_path

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderVRMError(line[7:])
            elif line.startswith("ARMATURE:"):
                armature_name = line.split(": ")[1]
            elif line.startswith("METADATA_SAVED:"):
                metadata_file = line.split(": ")[1]

        return {
            "status": "success",
            "armature_name": armature_name,
            "metadata_file": metadata_file,
            "message": f"VRM metadata exported to {metadata_file}"
        }

    except Exception as e:
        logger.error(f"VRM metadata export failed: {e}")
        raise BlenderVRMError(f"Failed to export VRM metadata: {str(e)}") from e

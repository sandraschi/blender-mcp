"""Validation handler for avatar and model pre-flight checks.

This module provides comprehensive validation functions for VR platforms like
VRChat, Resonite, and general 3D model requirements.
"""

from enum import Enum
from typing import Any, Dict, Optional

from loguru import logger

from ..decorators import blender_operation
from ..exceptions import BlenderValidationError
from ..utils.blender_executor import get_blender_executor

# Initialize the executor with default Blender executable
_executor = get_blender_executor()


class ValidationPlatform(str, Enum):
    """Supported validation platforms."""

    VRCHAT = "vrchat"
    RESONITE = "resonite"
    UNITY = "unity"
    GENERIC = "generic"


@blender_operation("validate_avatar")
def validate_avatar(
    target_platform: str = "vrchat",
    check_materials: bool = True,
    check_rigging: bool = True,
    check_transforms: bool = True,
    check_textures: bool = True
) -> Dict[str, Any]:
    """
    Comprehensive avatar validation for VR platforms.

    Performs pre-flight checks on polycount, materials, rigging, transforms,
    and other requirements for successful deployment.

    Args:
        target_platform: Target platform ("vrchat", "resonite", "unity", "generic")
        check_materials: Whether to validate materials and draw calls
        check_rigging: Whether to validate bone structure and rigging
        check_transforms: Whether to check for unapplied transforms
        check_textures: Whether to validate texture requirements

    Returns:
        Validation report with status, issues, and statistics

    Raises:
        BlenderValidationError: If validation cannot be performed
    """
    logger.info(f"Validating avatar for {target_platform} platform")

    try:
        # Get the validation function based on platform
        if target_platform.lower() == "vrchat":
            return _validate_vrchat_avatar(check_materials, check_rigging, check_transforms, check_textures)
        elif target_platform.lower() == "resonite":
            return _validate_resonite_avatar(check_materials, check_rigging, check_transforms, check_textures)
        elif target_platform.lower() == "unity":
            return _validate_unity_avatar(check_materials, check_rigging, check_transforms, check_textures)
        else:
            return _validate_generic_model(check_materials, check_rigging, check_transforms, check_textures)

    except Exception as e:
        logger.error(f"Avatar validation failed: {e}")
        raise BlenderValidationError(f"Failed to validate avatar: {str(e)}") from e


def _validate_vrchat_avatar(check_materials: bool, check_rigging: bool, check_transforms: bool, check_textures: bool) -> Dict[str, Any]:
    """VRChat-specific avatar validation."""
    report = {
        "status": "PASS",
        "platform": "VRChat",
        "issues": [],
        "stats": {},
        "recommendations": []
    }

    # Polycount validation (VRChat limits)
    polycount_result = _validate_polycount(70000, 20000)  # PC: 70k, Quest: 20k
    report["stats"].update(polycount_result["stats"])

    if polycount_result["status"] != "PASS":
        report["status"] = polycount_result["status"]
        report["issues"].extend(polycount_result["issues"])

    # Material validation
    if check_materials:
        materials_result = _validate_materials(8)  # VRChat prefers < 8 materials
        report["stats"].update(materials_result["stats"])

        if materials_result["status"] != "PASS":
            report["status"] = materials_result["status"]
            report["issues"].extend(materials_result["issues"])

    # Rigging validation
    if check_rigging:
        rigging_result = _validate_rigging(256)  # VRChat bone limit
        report["stats"].update(rigging_result["stats"])

        if rigging_result["status"] != "PASS":
            report["status"] = rigging_result["status"]
            report["issues"].extend(rigging_result["issues"])

    # Transform validation
    if check_transforms:
        transform_result = _validate_transforms()
        if transform_result["status"] != "PASS":
            report["status"] = "CRITICAL"
            report["issues"].extend(transform_result["issues"])

    # Texture validation
    if check_textures:
        texture_result = _validate_textures()
        report["stats"].update(texture_result["stats"])

        if texture_result["status"] != "PASS":
            report["status"] = texture_result["status"]
            report["issues"].extend(texture_result["issues"])

    # VRChat-specific recommendations
    if len(report["issues"]) == 0:
        report["recommendations"].append("Avatar passes all VRChat requirements!")
    else:
        report["recommendations"].append("Consider using blender_atlasing to reduce draw calls")
        report["recommendations"].append("Use blender_modifiers.decimate to reduce polycount if needed")

    return report


def _validate_resonite_avatar(check_materials: bool, check_rigging: bool, check_transforms: bool, check_textures: bool) -> Dict[str, Any]:
    """Resonite-specific avatar validation."""
    report = {
        "status": "PASS",
        "platform": "Resonite",
        "issues": [],
        "stats": {},
        "recommendations": []
    }

    # Resonite is more lenient but still has practical limits
    polycount_result = _validate_polycount(100000, 50000)
    report["stats"].update(polycount_result["stats"])

    if polycount_result["status"] != "PASS":
        report["status"] = polycount_result["status"]
        report["issues"].extend(polycount_result["issues"])

    # Resonite supports more materials but performance matters
    if check_materials:
        materials_result = _validate_materials(16)
        report["stats"].update(materials_result["stats"])

        if materials_result["status"] != "PASS":
            report["status"] = materials_result["status"]
            report["issues"].extend(materials_result["issues"])

    # Rigging (Resonite uses similar humanoid standards)
    if check_rigging:
        rigging_result = _validate_rigging(256)
        report["stats"].update(rigging_result["stats"])

        if rigging_result["status"] != "PASS":
            report["status"] = rigging_result["status"]
            report["issues"].extend(rigging_result["issues"])

    # Transform validation (critical for Resonite)
    if check_transforms:
        transform_result = _validate_transforms()
        if transform_result["status"] != "PASS":
            report["status"] = "CRITICAL"
            report["issues"].extend(transform_result["issues"])

    # Texture validation
    if check_textures:
        texture_result = _validate_textures()
        report["stats"].update(texture_result["stats"])

        if texture_result["status"] != "PASS":
            report["status"] = texture_result["status"]
            report["issues"].extend(texture_result["issues"])

    return report


def _validate_unity_avatar(check_materials: bool, check_rigging: bool, check_transforms: bool, check_textures: bool) -> Dict[str, Any]:
    """Unity-specific avatar validation."""
    report = {
        "status": "PASS",
        "platform": "Unity",
        "issues": [],
        "stats": {},
        "recommendations": []
    }

    # Unity has higher limits but mobile considerations
    polycount_result = _validate_polycount(30000, 15000)  # Mobile vs PC
    report["stats"].update(polycount_result["stats"])

    if polycount_result["status"] != "PASS":
        report["status"] = polycount_result["status"]
        report["issues"].extend(polycount_result["issues"])

    # Materials
    if check_materials:
        materials_result = _validate_materials(4)  # Mobile optimization
        report["stats"].update(materials_result["stats"])

        if materials_result["status"] != "PASS":
            report["status"] = materials_result["status"]
            report["issues"].extend(materials_result["issues"])

    # Rigging
    if check_rigging:
        rigging_result = _validate_rigging(256)
        report["stats"].update(rigging_result["stats"])

        if rigging_result["status"] != "PASS":
            report["status"] = rigging_result["status"]
            report["issues"].extend(rigging_result["issues"])

    # Transforms
    if check_transforms:
        transform_result = _validate_transforms()
        if transform_result["status"] != "PASS":
            report["status"] = "CRITICAL"
            report["issues"].extend(transform_result["issues"])

    return report


def _validate_generic_model(check_materials: bool, check_rigging: bool, check_transforms: bool, check_textures: bool) -> Dict[str, Any]:
    """Generic 3D model validation."""
    report = {
        "status": "PASS",
        "platform": "Generic",
        "issues": [],
        "stats": {},
        "recommendations": []
    }

    # Basic polycount check
    polycount_result = _validate_polycount(50000, 25000)
    report["stats"].update(polycount_result["stats"])

    if polycount_result["status"] != "PASS":
        report["status"] = polycount_result["status"]
        report["issues"].extend(polycount_result["issues"])

    # Materials
    if check_materials:
        materials_result = _validate_materials(8)
        report["stats"].update(materials_result["stats"])

        if materials_result["status"] != "PASS":
            report["status"] = materials_result["status"]
            report["issues"].extend(materials_result["issues"])

    # Transforms
    if check_transforms:
        transform_result = _validate_transforms()
        if transform_result["status"] != "PASS":
            report["status"] = "CRITICAL"
            report["issues"].extend(transform_result["issues"])

    return report


def _validate_polycount(pc_limit: int, mobile_limit: Optional[int] = None) -> Dict[str, Any]:
    """Validate polycount against platform limits."""
    result = {"status": "PASS", "issues": [], "stats": {}}

    try:
        script = f"""
import bpy

# Get active object
obj = bpy.context.active_object
if not obj or obj.type != 'MESH':
    print("ERROR: No active mesh object selected")
    exit(1)

# Calculate triangle count
depsgraph = bpy.context.evaluated_depsgraph_get()
mesh_eval = obj.evaluated_get(depsgraph).to_mesh()
tri_count = len(mesh_eval.polygons)

print(f"TRIANGLES: {{tri_count}}")

# Check limits
if tri_count > {pc_limit}:
    print(f"WARNING: High polycount: {{tri_count:,}} triangles (PC limit: {pc_limit:,})")

if {mobile_limit} is not None and tri_count > {mobile_limit}:
    print(f"FAIL: Excessive polycount: {{tri_count:,}} triangles (Mobile limit: {mobile_limit:,})")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        for line in lines:
            if line.startswith("ERROR:"):
                result["status"] = "ERROR"
                result["issues"].append(line[7:])
            elif line.startswith("TRIANGLES:"):
                result["stats"]["triangles"] = int(line.split(": ")[1])
            elif line.startswith("WARNING:"):
                result["status"] = "WARNING"
                result["issues"].append(line[9:])
            elif line.startswith("FAIL:"):
                result["status"] = "FAIL"
                result["issues"].append(line[6:])

    except Exception as e:
        result["status"] = "ERROR"
        result["issues"].append(f"Polycount validation failed: {str(e)}")

    return result


def _validate_materials(max_materials: int) -> Dict[str, Any]:
    """Validate material count and complexity."""
    result = {"status": "PASS", "issues": [], "stats": {}}

    try:
        script = f"""
import bpy

obj = bpy.context.active_object
if not obj or obj.type != 'MESH':
    print("ERROR: No active mesh object selected")
    exit(1)

mat_count = len(obj.material_slots)
print(f"MATERIALS: {{mat_count}}")

if mat_count > {max_materials}:
    print(f"WARNING: High draw calls: {{mat_count}} materials (recommended: ≤{max_materials})")

# Check for missing materials
empty_slots = sum(1 for slot in obj.material_slots if not slot.material)
if empty_slots > 0:
    print(f"WARNING: Missing materials: {{empty_slots}} empty material slots")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        for line in lines:
            if line.startswith("ERROR:"):
                result["status"] = "ERROR"
                result["issues"].append(line[7:])
            elif line.startswith("MATERIALS:"):
                result["stats"]["materials"] = int(line.split(": ")[1])
            elif line.startswith("WARNING:"):
                result["status"] = "WARNING"
                result["issues"].append(line[9:])

    except Exception as e:
        result["status"] = "ERROR"
        result["issues"].append(f"Material validation failed: {str(e)}")

    return result


def _validate_rigging(max_bones: int) -> Dict[str, Any]:
    """Validate rigging and bone structure."""
    result = {"status": "PASS", "issues": [], "stats": {}}

    try:
        script = f"""
import bpy

obj = bpy.context.active_object
if not obj:
    print("ERROR: No active object selected")
    exit(1)

# Find armature
armature = obj.find_armature()
if not armature:
    print("INFO: No armature found - model may not be rigged")
else:
    bone_count = len(armature.data.bones)
    print(f"BONES: {{bone_count}}")

    if bone_count > {max_bones}:
        print(f"FAIL: Too many bones: {{bone_count}} (limit: {max_bones})")

    # Check for common humanoid bones (basic validation)
    required_bones = ["Hips", "Spine", "Chest", "Head", "LeftUpperArm", "RightUpperArm"]
    bone_names = [bone.name for bone in armature.data.bones]

    missing_bones = []
    for req_bone in required_bones:
        if not any(req_bone in bone_name for bone_name in bone_names):
            missing_bones.append(req_bone)

    if missing_bones:
        print(f"WARNING: Missing standard bones: {{', '.join(missing_bones)}}")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        for line in lines:
            if line.startswith("ERROR:"):
                result["status"] = "ERROR"
                result["issues"].append(line[7:])
            elif line.startswith("BONES:"):
                result["stats"]["bones"] = int(line.split(": ")[1])
            elif line.startswith("FAIL:"):
                result["status"] = "FAIL"
                result["issues"].append(line[6:])
            elif line.startswith("WARNING:"):
                result["status"] = "WARNING"
                result["issues"].append(line[9:])
            elif line.startswith("INFO:"):
                result["issues"].append(line[6:])

    except Exception as e:
        result["status"] = "ERROR"
        result["issues"].append(f"Rigging validation failed: {str(e)}")

    return result


def _validate_transforms() -> Dict[str, Any]:
    """Validate that transforms are applied correctly."""
    result = {"status": "PASS", "issues": []}

    try:
        script = """
import bpy

obj = bpy.context.active_object
if not obj:
    print("ERROR: No active object selected")
    exit(1)

# Check for unapplied scale
scale_issues = []
for i, s in enumerate(obj.scale):
    if abs(s - 1.0) > 0.001:
        scale_issues.append(f"axis {['X', 'Y', 'Z'][i]}: {s:.3f}")

if scale_issues:
    print("CRITICAL: Unapplied scale detected - this will break animations and physics")
    for issue in scale_issues:
        print(f"  Scale {issue}")

# Check for unapplied rotation (non-zero rotation in object mode)
rotation_issues = []
for i, r in enumerate(obj.rotation_euler):
    if abs(r) > 0.001:
        rotation_issues.append(f"axis {['X', 'Y', 'Z'][i]}: {r:.3f}")

if rotation_issues:
    print("WARNING: Unapplied rotation detected - consider applying rotation")
    for issue in rotation_issues:
        print(f"  Rotation {issue}")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        for line in lines:
            if line.startswith("ERROR:"):
                result["status"] = "ERROR"
                result["issues"].append(line[7:])
            elif line.startswith("CRITICAL:"):
                result["status"] = "CRITICAL"
                result["issues"].append(line[10:])
            elif line.startswith("WARNING:"):
                result["status"] = "WARNING"
                result["issues"].append(line[9:])
            elif line.startswith("  Scale ") or line.startswith("  Rotation "):
                result["issues"][-1] += f" ({line.strip()})"

    except Exception as e:
        result["status"] = "ERROR"
        result["issues"].append(f"Transform validation failed: {str(e)}")

    return result


def _validate_textures() -> Dict[str, Any]:
    """Validate texture requirements."""
    result = {"status": "PASS", "issues": [], "stats": {}}

    try:
        script = """
import bpy

obj = bpy.context.active_object
if not obj or obj.type != 'MESH':
    print("ERROR: No active mesh object selected")
    exit(1)

total_textures = 0
missing_textures = 0

for mat_slot in obj.material_slots:
    if not mat_slot.material:
        continue

    mat = mat_slot.material
    if not mat.use_nodes:
        continue

    # Count image textures
    for node in mat.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            total_textures += 1
            if not node.image:
                missing_textures += 1

print(f"TEXTURES_TOTAL: {total_textures}")
print(f"TEXTURES_MISSING: {missing_textures}")

if missing_textures > 0:
    print(f"WARNING: Missing texture references: {missing_textures} image nodes without images")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        for line in lines:
            if line.startswith("ERROR:"):
                result["status"] = "ERROR"
                result["issues"].append(line[7:])
            elif line.startswith("TEXTURES_TOTAL:"):
                result["stats"]["total_textures"] = int(line.split(": ")[1])
            elif line.startswith("TEXTURES_MISSING:"):
                result["stats"]["missing_textures"] = int(line.split(": ")[1])
            elif line.startswith("WARNING:"):
                result["status"] = "WARNING"
                result["issues"].append(line[9:])

    except Exception as e:
        result["status"] = "ERROR"
        result["issues"].append(f"Texture validation failed: {str(e)}")

    return result

"""Export presets handler for Blender MCP.

Provides platform-specific export configurations for VR platforms including
VRChat, Resonite, and Unity with appropriate scale, format, and settings.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from ..decorators import blender_operation
from ..exceptions import BlenderExportError
from ..utils.blender_executor import get_blender_executor

# Initialize the executor with default Blender executable
_executor = get_blender_executor()


# Platform-specific export presets
PLATFORM_PRESETS = {
    "VRCHAT": {
        "scale": 1.0,
        "format": "FBX",
        "apply_transforms": True,
        "include_animation": True,
        "bone_naming": "HUMANOID",
        "max_bones": 256,
        "description": "Unity-compatible export for VRChat avatars"
    },
    "RESONITE": {
        "scale": 1.0,
        "format": "GLTF",
        "apply_transforms": False,
        "include_animation": True,
        "bone_naming": "STANDARD",
        "max_bones": 512,
        "description": "Resonite-compatible export with GLTF format"
    },
    "UNITY": {
        "scale": 1.0,
        "format": "FBX",
        "apply_transforms": True,
        "include_animation": True,
        "bone_naming": "HUMANOID",
        "max_bones": 256,
        "description": "Generic Unity export preset"
    },
    "BLENDER": {
        "scale": 1.0,
        "format": "BLEND",
        "apply_transforms": False,
        "include_animation": True,
        "bone_naming": "BLENDER",
        "max_bones": None,
        "description": "Native Blender format export"
    },
    "LEGACY_VRCHAT": {
        "scale": 0.01,
        "format": "FBX",
        "apply_transforms": True,
        "include_animation": True,
        "bone_naming": "HUMANOID",
        "max_bones": 256,
        "description": "Legacy VRChat export with 0.01 scale"
    }
}


@blender_operation("export_with_preset")
async def export_with_preset(
    target_objects: List[str],
    platform: str = "VRCHAT",
    output_path: str = "//export",
    include_materials: bool = True,
    include_textures: bool = True,
    apply_modifiers: bool = True,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Export objects using platform-specific presets.

    Applies the correct scale, format, and settings for the target VR platform,
    ensuring compatibility and optimal performance.

    Args:
        target_objects: List of object names to export
        platform: Target platform preset ("VRCHAT", "RESONITE", "UNITY", etc.)
        output_path: Export output path (without extension)
        include_materials: Whether to include materials in export
        include_textures: Whether to include textures in export
        apply_modifiers: Whether to apply modifiers before export

    Returns:
        Export operation result with file paths and validation info

    Raises:
        BlenderExportError: If export fails or platform is unsupported
    """
    logger.info(f"Exporting with {platform} preset to {output_path}")

    if platform not in PLATFORM_PRESETS:
        supported = list(PLATFORM_PRESETS.keys())
        raise BlenderExportError(f"Unsupported platform '{platform}'. Supported: {supported}")

    preset = PLATFORM_PRESETS[platform]

    try:
        script = f"""
import bpy
import os

# Get preset settings
preset = {preset!r}
platform = '{platform}'
target_objects = {target_objects!r}
output_path = '{output_path}'
include_materials = {include_materials!r}
include_textures = {include_textures!r}
apply_modifiers = {apply_modifiers!r}

print(f"PLATFORM: {{platform}}")
print(f"SCALE: {{preset['scale']}}")
print(f"FORMAT: {{preset['format']}}")

# Select target objects
export_objects = []
for obj_name in target_objects:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        export_objects.append(obj)
        print(f"SELECTED: {{obj_name}}")
    else:
        print(f"WARNING: Object not found: {{obj_name}}")

if not export_objects:
    print("ERROR: No valid objects to export")
    exit(1)

# Set export scale
original_scale = bpy.context.scene.unit_settings.scale_length
bpy.context.scene.unit_settings.scale_length = preset['scale']

# Apply transforms if required
if preset['apply_transforms']:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in export_objects:
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    print("TRANSFORMS_APPLIED: True")

# Apply modifiers if required
if apply_modifiers:
    for obj in export_objects:
        if obj.type == 'MESH':
            for mod in obj.modifiers:
                if mod.type in ['SUBSURF', 'MIRROR', 'SOLIDIFY']:  # Common modifiers to apply
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                    print(f"MODIFIER_APPLIED: {{mod.name}} on {{obj.name}}")

# Export based on format
export_success = False
final_path = ""

if preset['format'] == 'FBX':
    final_path = output_path + '.fbx'
    bpy.ops.export_scene.fbx(
        filepath=bpy.path.abspath(final_path),
        use_selection=True,
        apply_unit_scale=True,
        bake_space_transform=True,
        use_mesh_modifiers=not apply_modifiers,
        mesh_smooth_type='FACE',
        use_tspace=True,
        add_leaf_bones=False
    )
    export_success = True

elif preset['format'] == 'GLTF':
    final_path = output_path + '.gltf'
    bpy.ops.export_scene.gltf(
        filepath=bpy.path.abspath(final_path),
        use_selection=True,
        export_format='GLTF_SEPARATE',
        export_cameras=False,
        export_lights=False,
        export_apply=True,
        export_yup=True
    )
    export_success = True

elif preset['format'] == 'BLEND':
    final_path = output_path + '.blend'
    # For Blender format, just save selected objects to new file
    bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(final_path))
    export_success = True

# Restore original scale
bpy.context.scene.unit_settings.scale_length = original_scale

if export_success:
    print(f"EXPORT_SUCCESS: {{final_path}}")
    print(f"OBJECTS_EXPORTED: {{len(export_objects)}}")
else:
    print("ERROR: Export failed")
    exit(1)

print("EXPORT_COMPLETE: True")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        final_path = ""
        objects_exported = 0
        warnings = []

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderExportError(line[7:])
            elif line.startswith("EXPORT_SUCCESS:"):
                final_path = line.split(": ")[1]
            elif line.startswith("OBJECTS_EXPORTED:"):
                objects_exported = int(line.split(": ")[1])
            elif line.startswith("WARNING:"):
                warnings.append(line[7:])

        return {
            "status": "success",
            "platform": platform,
            "format": preset["format"],
            "scale": preset["scale"],
            "output_path": final_path,
            "objects_exported": objects_exported,
            "warnings": warnings,
            "message": f"Successfully exported {objects_exported} objects for {platform} platform"
        }

    except Exception as e:
        logger.error(f"Platform export failed: {e}")
        raise BlenderExportError(f"Failed to export with {platform} preset: {str(e)}") from e


@blender_operation("validate_export_preset")
async def validate_export_preset(
    target_objects: List[str],
    platform: str = "VRCHAT",
    check_bones: bool = True,
    check_materials: bool = True,
    check_scale: bool = True
) -> Dict[str, Any]:
    """
    Validate objects against platform export requirements.

    Checks bone count, material limits, scale compatibility, and other
    platform-specific requirements before export.

    Args:
        target_objects: List of object names to validate
        platform: Target platform to validate against
        check_bones: Whether to validate bone count and naming
        check_materials: Whether to validate material compatibility
        check_scale: Whether to validate scale settings

    Returns:
        Validation report with issues and recommendations

    Raises:
        BlenderExportError: If validation fails critically
    """
    logger.info(f"Validating export preset for {platform}")

    if platform not in PLATFORM_PRESETS:
        supported = list(PLATFORM_PRESETS.keys())
        raise BlenderExportError(f"Unsupported platform '{platform}'. Supported: {supported}")

    preset = PLATFORM_PRESETS[platform]

    try:
        script = f"""
import bpy

platform = '{platform}'
preset = {preset!r}
target_objects = {target_objects!r}
check_bones = {check_bones!r}
check_materials = {check_materials!r}
check_scale = {check_scale!r}

print(f"VALIDATING_PLATFORM: {{platform}}")

validation_results = {{
    'status': 'PASS',
    'issues': [],
    'warnings': [],
    'recommendations': []
}}

# Check target objects exist
valid_objects = []
armatures = []

for obj_name in target_objects:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        valid_objects.append(obj)
        if obj.type == 'ARMATURE':
            armatures.append(obj)
        print(f"VALID_OBJECT: {{obj_name}}")
    else:
        validation_results['issues'].append(f"Object not found: {{obj_name}}")

if not valid_objects:
    validation_results['status'] = 'ERROR'
    validation_results['issues'].append("No valid objects to export")
    print("VALIDATION_FAILED: No valid objects")
    exit(1)

# Check bone count and naming
if check_bones and armatures:
    for armature in armatures:
        bone_count = len(armature.data.bones)
        max_bones = preset.get('max_bones')

        if max_bones and bone_count > max_bones:
            validation_results['status'] = 'FAIL'
            validation_results['issues'].append(
                f"Too many bones in {{armature.name}}: {{bone_count}} (max: {{max_bones}})"
            )
        elif bone_count > max_bones * 0.8:  # Warning at 80%
            validation_results['warnings'].append(
                f"High bone count in {{armature.name}}: {{bone_count}} (max: {{max_bones}})"
            )

        print(f"BONE_COUNT: {{armature.name}} = {{bone_count}}")

# Check materials
if check_materials:
    total_materials = 0
    for obj in valid_objects:
        if obj.type == 'MESH':
            total_materials += len(obj.data.materials)

    if total_materials > 8:  # Common mobile limit
        validation_results['warnings'].append(
            f"High material count: {{total_materials}} (recommended max: 8 for mobile VR)"
        )

    print(f"MATERIAL_COUNT: {{total_materials}}")

# Check scale
if check_scale:
    current_scale = bpy.context.scene.unit_settings.scale_length
    target_scale = preset['scale']

    if abs(current_scale - target_scale) > 0.01:
        validation_results['recommendations'].append(
            f"Scene scale ({{current_scale}}) differs from {{platform}} standard ({{target_scale}})"
        )

    print(f"SCALE_CHECK: current={{current_scale}}, target={{target_scale}}")

# Overall status
issues_count = len(validation_results['issues'])
warnings_count = len(validation_results['warnings'])

if issues_count > 0:
    validation_results['status'] = 'FAIL'
elif warnings_count > 0:
    validation_results['status'] = 'WARNING'

print(f"VALIDATION_STATUS: {{validation_results['status']}}")
print(f"ISSUES: {{issues_count}}")
print(f"WARNINGS: {{warnings_count}}")

# Output validation results
import json
print("VALIDATION_RESULTS:" + json.dumps(validation_results))
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        validation_results = {}
        status = "UNKNOWN"

        for line in lines:
            if line.startswith("VALIDATION_FAILED:"):
                raise BlenderExportError(line[20:])
            elif line.startswith("VALIDATION_STATUS:"):
                status = line.split(": ")[1]
            elif line.startswith("VALIDATION_RESULTS:"):
                import json
                validation_results = json.loads(line[19:])

        return {
            "status": status,
            "platform": platform,
            "validation_results": validation_results,
            "message": f"Validation complete for {platform} export"
        }

    except Exception as e:
        logger.error(f"Export validation failed: {e}")
        raise BlenderExportError(f"Failed to validate export preset: {str(e)}") from e


@blender_operation("get_platform_presets")
async def get_platform_presets() -> Dict[str, Any]:
    """
    Get information about available platform export presets.

    Returns details about supported platforms, their requirements,
    and recommended use cases.

    Returns:
        Platform presets information

    Raises:
        BlenderExportError: If preset retrieval fails
    """
    logger.info("Retrieving platform export presets")

    try:
        return {
            "status": "success",
            "presets": PLATFORM_PRESETS,
            "platforms": list(PLATFORM_PRESETS.keys()),
            "message": f"Retrieved {len(PLATFORM_PRESETS)} platform presets"
        }

    except Exception as e:
        logger.error(f"Platform presets retrieval failed: {e}")
        raise BlenderExportError(f"Failed to get platform presets: {str(e)}") from e


@blender_operation("create_custom_preset")
async def create_custom_preset(
    preset_name: str,
    base_platform: str = "VRCHAT",
    custom_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a custom export preset based on an existing platform.

    Allows fine-tuning of export settings while starting from
    proven platform configurations.

    Args:
        preset_name: Name for the custom preset
        base_platform: Platform to base the custom preset on
        custom_settings: Custom settings to override defaults

    Returns:
        Custom preset creation result

    Raises:
        BlenderExportError: If custom preset creation fails
    """
    logger.info(f"Creating custom preset '{preset_name}' based on {base_platform}")

    if base_platform not in PLATFORM_PRESETS:
        supported = list(PLATFORM_PRESETS.keys())
        raise BlenderExportError(f"Unsupported base platform '{base_platform}'. Supported: {supported}")

    # Start with base preset
    custom_preset = PLATFORM_PRESETS[base_platform].copy()
    custom_preset["description"] = f"Custom preset based on {base_platform}"

    # Apply custom settings
    if custom_settings:
        custom_preset.update(custom_settings)

    try:
        # In a real implementation, this would save the preset to a config file
        # For now, we just return the configuration
        return {
            "status": "success",
            "preset_name": preset_name,
            "base_platform": base_platform,
            "custom_preset": custom_preset,
            "message": f"Custom preset '{preset_name}' created successfully"
        }

    except Exception as e:
        logger.error(f"Custom preset creation failed: {e}")
        raise BlenderExportError(f"Failed to create custom preset: {str(e)}") from e

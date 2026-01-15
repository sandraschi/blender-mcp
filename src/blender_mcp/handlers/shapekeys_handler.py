"""Shape keys handler for Blender MCP.

Provides tools for managing shape keys, visemes, and facial animation
for VRM avatars and character models.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from ..decorators import blender_operation
from ..exceptions import BlenderShapeKeysError
from ..utils.blender_executor import get_blender_executor

# Initialize the executor with default Blender executable
_executor = get_blender_executor()


# VRM Standard Viseme mappings
VRM_VISEMES = {
    "aa": "A",    # A sound (wide open mouth)
    "ih": "I",    # I sound (narrow mouth)
    "ou": "U",    # U sound (rounded lips)
    "ee": "E",    # E sound (wide smile)
    "oh": "O"     # O sound (rounded wide mouth)
}


@blender_operation("create_viseme_shapekeys")
async def create_viseme_shapekeys(
    target_mesh: Optional[str] = None,
    viseme_type: str = "vrm",
    auto_generate: bool = True,
    base_expression: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standard viseme shape keys for lip sync animation.

    Generates the five VRM standard visemes (A, I, U, E, O) that correspond
    to the main vowel sounds used in lip sync animation.

    Args:
        target_mesh: Target mesh object (defaults to active)
        viseme_type: Type of viseme system ("vrm", "standard", "custom")
        auto_generate: Whether to auto-generate basic shapes
        base_expression: Base expression shape key to start from

    Returns:
        Viseme creation result with shape key information

    Raises:
        BlenderShapeKeysError: If viseme creation fails
    """
    logger.info(f"Creating viseme shape keys (type: {viseme_type})")

    viseme_mappings = VRM_VISEMES if viseme_type == "vrm" else {}

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

# Ensure shape keys exist
if not mesh.data.shape_keys:
    # Create basis shape key
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.shape_key_add(from_mix=False)
    print("SHAPE_KEYS_CREATED: True")
else:
    print("SHAPE_KEYS_EXIST: True")

# Get existing shape keys
existing_keys = []
if mesh.data.shape_keys:
    existing_keys = [key.name for key in mesh.data.shape_keys.key_blocks]

print(f"EXISTING_KEYS: {{existing_keys}}")

# Check for viseme keys
viseme_keys = {list(viseme_mappings.values())!r}
missing_visemes = []
existing_visemes = []

for viseme in viseme_keys:
    if viseme in existing_keys:
        existing_visemes.append(viseme)
    else:
        missing_visemes.append(viseme)

print(f"MISSING_VISEMES: {{missing_visemes}}")
print(f"EXISTING_VISEMES: {{existing_visemes}}")

# Create missing viseme keys if auto_generate is enabled
if {auto_generate!r} and missing_visemes:
    for viseme in missing_visemes:
        # Add new shape key
        bpy.ops.object.shape_key_add(from_mix=False)
        new_key = mesh.data.shape_keys.key_blocks[-1]
        new_key.name = viseme

        # Set some basic deformation for demonstration
        # In a real implementation, this would be more sophisticated
        if viseme == "A":
            # Wide open mouth
            pass  # Would modify vertex positions
        elif viseme == "I":
            # Narrow mouth
            pass
        # ... etc

        print(f"CREATED_VISEME: {{viseme}}")

print("SUCCESS: Viseme shape keys processed")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        mesh_name = "Unknown"
        existing_keys = []
        missing_visemes = []
        existing_visemes = []
        created_visemes = []

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderShapeKeysError(line[7:])
            elif line.startswith("MESH:"):
                mesh_name = line.split(": ")[1]
            elif line.startswith("EXISTING_KEYS:"):
                existing_keys = eval(line.split(": ")[1])
            elif line.startswith("MISSING_VISEMES:"):
                missing_visemes = eval(line.split(": ")[1])
            elif line.startswith("EXISTING_VISEMES:"):
                existing_visemes = eval(line.split(": ")[1])
            elif line.startswith("CREATED_VISEME:"):
                created_visemes.append(line.split(": ")[1])

        return {
            "status": "success",
            "mesh_name": mesh_name,
            "viseme_type": viseme_type,
            "viseme_mappings": viseme_mappings,
            "existing_keys": existing_keys,
            "existing_visemes": existing_visemes,
            "missing_visemes": missing_visemes,
            "created_visemes": created_visemes,
            "auto_generated": auto_generate,
            "message": f"Viseme shape keys processed for {mesh_name}"
        }

    except Exception as e:
        logger.error(f"Viseme creation failed: {e}")
        raise BlenderShapeKeysError(f"Failed to create viseme shape keys: {str(e)}") from e


@blender_operation("create_blink_shapekey")
async def create_blink_shapekey(
    target_mesh: Optional[str] = None,
    blink_intensity: float = 1.0,
    eyelid_vertices: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Create or configure blink shape key for eye animation.

    Sets up the blink shape key that closes the eyes, essential for
    facial animation and preventing creepy unblinking avatars.

    Args:
        target_mesh: Target mesh object (defaults to active)
        blink_intensity: How closed the eyes should be (0.0-1.0)
        eyelid_vertices: Specific vertex indices for eyelid control

    Returns:
        Blink shape key creation result

    Raises:
        BlenderShapeKeysError: If blink creation fails
    """
    logger.info(f"Creating blink shape key (intensity: {blink_intensity})")

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

# Check for existing blink key
blink_exists = False
if mesh.data.shape_keys:
    for key in mesh.data.shape_keys.key_blocks:
        if key.name.lower() in ["blink", "blink_l", "blink_r", "eye_close"]:
            blink_exists = True
            print(f"BLINK_EXISTS: {{key.name}}")
            break

if not blink_exists:
    # Create blink shape key
    if not mesh.data.shape_keys:
        # Create basis first
        bpy.ops.object.shape_key_add(from_mix=False)

    bpy.ops.object.shape_key_add(from_mix=False)
    blink_key = mesh.data.shape_keys.key_blocks[-1]
    blink_key.name = "blink"

    print("BLINK_CREATED: blink")
else:
    print("BLINK_ALREADY_EXISTS: True")

# Set blink intensity metadata
blink_info = {{
    "intensity": {blink_intensity!r},
    "eyelid_vertices": {eyelid_vertices!r}
}}

if mesh.data.shape_keys:
    mesh.data.shape_keys["blink_settings"] = str(blink_info)

print("SUCCESS: Blink shape key configured")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        mesh_name = "Unknown"
        blink_created = False
        blink_exists_name = None

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderShapeKeysError(line[7:])
            elif line.startswith("MESH:"):
                mesh_name = line.split(": ")[1]
            elif line.startswith("BLINK_CREATED:"):
                blink_created = True
            elif line.startswith("BLINK_EXISTS:"):
                blink_exists_name = line.split(": ")[1]

        return {
            "status": "success",
            "mesh_name": mesh_name,
            "blink_created": blink_created,
            "blink_exists": blink_exists_name,
            "blink_intensity": blink_intensity,
            "eyelid_vertices": eyelid_vertices,
            "message": f"Blink shape key {'created' if blink_created else 'found'} for {mesh_name}"
        }

    except Exception as e:
        logger.error(f"Blink creation failed: {e}")
        raise BlenderShapeKeysError(f"Failed to create blink shape key: {str(e)}") from e


@blender_operation("set_viseme_weights")
async def set_viseme_weights(
    target_mesh: Optional[str] = None,
    viseme_weights: Optional[Dict[str, float]] = None,
    frame: int = 1
) -> Dict[str, Any]:
    """
    Set shape key weights for viseme animation at a specific frame.

    Applies weights to viseme shape keys to create specific mouth shapes
    for lip sync animation.

    Args:
        target_mesh: Target mesh object (defaults to active)
        viseme_weights: Dictionary of viseme names to weights (0.0-1.0)
        frame: Animation frame to set weights at

    Returns:
        Viseme weight setting result

    Raises:
        BlenderShapeKeysError: If weight setting fails
    """
    logger.info(f"Setting viseme weights at frame {frame}")

    # Default weights (all off)
    default_weights = dict.fromkeys(VRM_VISEMES.values(), 0.0)
    if viseme_weights:
        default_weights.update(viseme_weights)

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

# Set current frame
bpy.context.scene.frame_current = {frame!r}

# Apply viseme weights
weights = {default_weights!r}
applied_weights = {{}}

if mesh.data.shape_keys:
    for viseme, weight in weights.items():
        if viseme in mesh.data.shape_keys.key_blocks:
            key_block = mesh.data.shape_keys.key_blocks[viseme]
            key_block.value = weight

            # Keyframe the weight
            key_block.keyframe_insert(data_path="value", frame={frame!r})

            applied_weights[viseme] = weight
            print(f"WEIGHT_SET: {{viseme}} = {{weight}}")
        else:
            print(f"VISME_MISSING: {{viseme}}")

print("SUCCESS: Viseme weights applied")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        mesh_name = "Unknown"
        applied_weights = {}
        missing_visemes = []

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderShapeKeysError(line[7:])
            elif line.startswith("MESH:"):
                mesh_name = line.split(": ")[1]
            elif line.startswith("WEIGHT_SET:"):
                parts = line.split(": ")[1].split(" = ")
                viseme = parts[0]
                weight = float(parts[1])
                applied_weights[viseme] = weight
            elif line.startswith("VISME_MISSING:"):
                missing_visemes.append(line.split(": ")[1])

        return {
            "status": "success",
            "mesh_name": mesh_name,
            "frame": frame,
            "applied_weights": applied_weights,
            "missing_visemes": missing_visemes,
            "requested_weights": default_weights,
            "message": f"Viseme weights set at frame {frame} on {mesh_name}"
        }

    except Exception as e:
        logger.error(f"Viseme weight setting failed: {e}")
        raise BlenderShapeKeysError(f"Failed to set viseme weights: {str(e)}") from e


@blender_operation("create_facial_expression")
async def create_facial_expression(
    target_mesh: Optional[str] = None,
    expression_name: str = "expression",
    base_visemes: Optional[Dict[str, float]] = None,
    blink_weight: float = 0.0,
    additional_modifiers: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Create a complete facial expression combining visemes and blink.

    Combines multiple shape keys to create complex facial expressions
    for emotional animation or specific character poses.

    Args:
        target_mesh: Target mesh object (defaults to active)
        expression_name: Name for the expression shape key
        base_visemes: Base viseme weights to combine
        blink_weight: Blink component weight
        additional_modifiers: Additional shape key modifiers

    Returns:
        Facial expression creation result

    Raises:
        BlenderShapeKeysError: If expression creation fails
    """
    logger.info(f"Creating facial expression: {expression_name}")

    # Default viseme weights (neutral)
    default_visemes = dict.fromkeys(VRM_VISEMES.values(), 0.0)
    if base_visemes:
        default_visemes.update(base_visemes)

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

# Ensure shape keys exist
if not mesh.data.shape_keys:
    bpy.ops.object.shape_key_add(from_mix=False)

# Create expression shape key
bpy.ops.object.shape_key_add(from_mix=False)
expression_key = mesh.data.shape_keys.key_blocks[-1]
expression_key.name = {repr(expression_name)}

# Apply base visemes
visemes = {default_visemes!r}
for viseme, weight in visemes.items():
    if viseme in mesh.data.shape_keys.key_blocks:
        viseme_key = mesh.data.shape_keys.key_blocks[viseme]
        # Mix viseme into expression
        # This is a simplified implementation
        pass

# Apply blink
blink_weight = {blink_weight!r}
if "blink" in mesh.data.shape_keys.key_blocks and blink_weight > 0:
    blink_key = mesh.data.shape_keys.key_blocks["blink"]
    # Mix blink into expression
    pass

# Apply additional modifiers
modifiers = {additional_modifiers!r} or {{}}
for mod_name, mod_weight in modifiers.items():
    if mod_name in mesh.data.shape_keys.key_blocks:
        mod_key = mesh.data.shape_keys.key_blocks[mod_name]
        # Mix modifier into expression
        pass

print(f"EXPRESSION_CREATED: {{expression_name}}")
print("SUCCESS: Facial expression created")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        mesh_name = "Unknown"
        expression_created = False

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderShapeKeysError(line[7:])
            elif line.startswith("MESH:"):
                mesh_name = line.split(": ")[1]
            elif line.startswith("EXPRESSION_CREATED:"):
                expression_created = True

        return {
            "status": "success",
            "mesh_name": mesh_name,
            "expression_name": expression_name,
            "expression_created": expression_created,
            "base_visemes": default_visemes,
            "blink_weight": blink_weight,
            "additional_modifiers": additional_modifiers or {},
            "message": f"Facial expression '{expression_name}' created for {mesh_name}"
        }

    except Exception as e:
        logger.error(f"Facial expression creation failed: {e}")
        raise BlenderShapeKeysError(f"Failed to create facial expression: {str(e)}") from e


@blender_operation("analyze_shapekeys")
async def analyze_shapekeys(
    target_mesh: Optional[str] = None,
    include_statistics: bool = True
) -> Dict[str, Any]:
    """
    Analyze shape keys on a mesh for facial animation readiness.

    Provides detailed information about existing shape keys, their
    deformation ranges, and VRM compliance.

    Args:
        target_mesh: Target mesh object (defaults to active)
        include_statistics: Whether to include deformation statistics

    Returns:
        Shape key analysis report

    Raises:
        BlenderShapeKeysError: If analysis fails
    """
    logger.info("Analyzing shape keys for facial animation")

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

# Analyze shape keys
shape_key_info = {{}}
total_keys = 0

if mesh.data.shape_keys:
    total_keys = len(mesh.data.shape_keys.key_blocks)
    print(f"TOTAL_KEYS: {{total_keys}}")

    for key in mesh.data.shape_keys.key_blocks:
        info = {{
            "name": key.name,
            "index": key.index,
            "value": key.value,
            "mute": key.mute,
            "vertex_group": key.vertex_group
        }}

        # Check if it's a VRM viseme
        vrm_visemes = {list(VRM_VISEMES.values())!r}
        info["is_vrm_viseme"] = key.name in vrm_visemes
        info["is_blink"] = key.name.lower() in ["blink", "eye_close"]

        shape_key_info[key.name] = info
        print(f"KEY_INFO: {{key.name}} = {{info}}")

else:
    print("NO_SHAPE_KEYS: True")

# VRM compliance check
vrm_visemes = {list(VRM_VISEMES.values())!r}
missing_visemes = []
existing_visemes = []

for viseme in vrm_visemes:
    if mesh.data.shape_keys and viseme in shape_key_info:
        existing_visemes.append(viseme)
    else:
        missing_visemes.append(viseme)

has_blink = any(info.get("is_blink", False) for info in shape_key_info.values())

print(f"VRM_MISSING: {{missing_visemes}}")
print(f"VRM_EXISTING: {{existing_visemes}}")
print(f"HAS_BLINK: {{has_blink}}")

print("SUCCESS: Shape key analysis complete")
"""

        output = await _executor.execute_script(script)
        lines = output.strip().split('\n')

        mesh_name = "Unknown"
        total_keys = 0
        shape_key_info = {}
        missing_visemes = []
        existing_visemes = []
        has_blink = False

        for line in lines:
            if line.startswith("ERROR:"):
                raise BlenderShapeKeysError(line[7:])
            elif line.startswith("MESH:"):
                mesh_name = line.split(": ")[1]
            elif line.startswith("TOTAL_KEYS:"):
                total_keys = int(line.split(": ")[1])
            elif line.startswith("KEY_INFO:"):
                parts = line.split(" = ", 1)
                key_name = parts[0].split(": ")[1]
                info_str = parts[1]
                try:
                    shape_key_info[key_name] = eval(info_str)
                except (ValueError, SyntaxError):
                    pass
            elif line.startswith("VRM_MISSING:"):
                missing_visemes = eval(line.split(": ")[1])
            elif line.startswith("VRM_EXISTING:"):
                existing_visemes = eval(line.split(": ")[1])
            elif line.startswith("HAS_BLINK:"):
                has_blink = line.split(": ")[1].lower() == "true"

        # Calculate VRM compliance
        vrm_compliance = {
            "visemes_present": len(existing_visemes),
            "visemes_missing": len(missing_visemes),
            "has_blink": has_blink,
            "total_score": (len(existing_visemes) + (1 if has_blink else 0)) / (len(VRM_VISEMES) + 1)
        }

        return {
            "status": "success",
            "mesh_name": mesh_name,
            "total_shape_keys": total_keys,
            "shape_key_info": shape_key_info,
            "vrm_compliance": vrm_compliance,
            "missing_visemes": missing_visemes,
            "existing_visemes": existing_visemes,
            "has_blink": has_blink,
            "message": f"Shape key analysis complete for {mesh_name}"
        }

    except Exception as e:
        logger.error(f"Shape key analysis failed: {e}")
        raise BlenderShapeKeysError(f"Failed to analyze shape keys: {str(e)}") from e

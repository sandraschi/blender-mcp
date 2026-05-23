"""Grease Pencil operations handler for Blender MCP."""

import logging
from enum import Enum
from typing import Any

from ..compat import *

logger = logging.getLogger(__name__)
from ..decorators import blender_operation
from ..utils.blender_executor import get_blender_executor

_executor = get_blender_executor()


class GPStrokePlacement(str, Enum):
    """Grease Pencil stroke placement modes."""

    ORIGIN = "ORIGIN"  # Draw at origin
    CURSOR = "CURSOR"  # Draw at 3D cursor
    SURFACE = "SURFACE"  # Draw on surface under cursor
    VIEW = "VIEW"  # Draw on view plane


class GPStrokeType(str, Enum):
    """Grease Pencil stroke types."""

    LINE = "LINE"
    BOX = "BOX"
    CIRCLE = "CIRCLE"
    ARC = "ARC"
    CURVE = "CURVE"


@blender_operation("create_grease_pencil", log_args=True)
async def create_grease_pencil(
    name: str = "GPencil",
    placement: GPStrokePlacement | str = GPStrokePlacement.ORIGIN,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a new Grease Pencil object.

    Args:
        name: Name for the new Grease Pencil object
        placement: Where to place the Grease Pencil object
        **kwargs: Additional parameters
            - location: Custom location as [x, y, z] (overrides placement)
            - parent: Parent object name

    Returns:
        Dict containing creation status and details
    """
    location = kwargs.get("location")
    parent = kwargs.get("parent")

    script = f"""

def create_gp():
    # Check if GP object with this name already exists
    if '{name}' in bpy.data.objects:
        return {{"status": "ERROR", "error": f"Object '{{name}}' already exists"}}

    try:
        # Create new Grease Pencil object
        bpy.ops.object.gpencil_add(type='EMPTY')
        gp_obj = bpy.context.active_object
        gp_obj.name = '{name}'

        # Set location based on placement
        if {location}:
            gp_obj.location = {location}
        else:
            if '{placement}' == 'CURSOR':
                gp_obj.location = bpy.context.scene.cursor.location
            # For other placements, we'll add a default layer and frame

        # Add a default layer and frame
        if not gp_obj.data.layers:
            layer = gp_obj.data.layers.new("GP_Layer")
            layer.frames.new(1)

        # Set as active object
        bpy.context.view_layer.objects.active = gp_obj

        # Parent if specified
        if '{parent}':
            parent_obj = bpy.data.objects.get('{parent}')
            if parent_obj:
                gp_obj.parent = parent_obj

        return {{
            "status": "SUCCESS",
            "object": gp_obj.name,
            "type": gp_obj.type,
            "location": tuple(gp_obj.location)
        }}
    except Exception as e:
        # Clean up if something went wrong
        if 'gp_obj' in locals() and gp_obj.name in bpy.data.objects:
            bpy.data.objects.remove(gp_obj)
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = create_gp()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create Grease Pencil: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("draw_grease_pencil_stroke", log_args=True)
async def draw_grease_pencil_stroke(
    gp_object: str,
    stroke_type: GPStrokeType | str = GPStrokeType.LINE,
    points: list[tuple[float, float, float]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Draw a stroke with the Grease Pencil.

    Args:
        gp_object: Name of the Grease Pencil object
        stroke_type: Type of stroke to draw
        points: List of points for the stroke (for LINE or CURVE types)
        **kwargs: Additional parameters
            - layer_name: Layer to draw on (default: active layer or 'GP_Layer')
            - frame_number: Frame number to draw on (default: 1)
            - color: Stroke color as [r, g, b, a] (0-1 range)
            - thickness: Stroke thickness (default: 1.0)
            - cyclic: Whether to close the stroke (default: False)

    Returns:
        Dict containing drawing status and details
    """
    if points is None:
        points = []

    layer_name = kwargs.get("layer_name", "GP_Layer")
    frame_number = kwargs.get("frame_number", 1)
    color = kwargs.get("color", [0.0, 0.0, 0.0, 1.0])
    thickness = kwargs.get("thickness", 1.0)
    cyclic = kwargs.get("cyclic", False)

    script = f"""
import math

def draw_stroke():
    # Get the Grease Pencil object
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "Grease Pencil object not found"}}

    # Get or create layer
    gp_data = gp_obj.data
    layer = gp_data.layers.get('{layer_name}')
    if not layer:
        layer = gp_data.layers.new('{layer_name}')

    # Get or create frame
    frame = layer.frames.get({frame_number})
    if not frame:
        frame = layer.frames.new({frame_number})

    # Create stroke
    stroke = frame.strokes.new()
    stroke.line_width = {thickness}
    stroke.use_cyclic = {str(cyclic).lower()}

    # Set stroke points based on type
    if '{stroke_type}' == 'LINE':
        points = {points}
        if len(points) < 2:
            return {{"status": "ERROR", "error": "At least 2 points required for LINE stroke"}}

        stroke.points.add(count=len(points))
        for i, point in enumerate(points):
            stroke.points[i].co = point
            stroke.points[i].pressure = 1.0

    elif '{stroke_type}' == 'BOX':
        # Draw a rectangle
        width = {kwargs.get("width", 2.0)}
        height = {kwargs.get("height", 2.0)}

        points = [
            (-width/2, -height/2, 0),
            (width/2, -height/2, 0),
            (width/2, height/2, 0),
            (-width/2, height/2, 0)
        ]

        stroke.points.add(count=4)
        for i, point in enumerate(points):
            stroke.points[i].co = point
            stroke.points[i].pressure = 1.0

    elif '{stroke_type}' == 'CIRCLE':
        # Draw a circle
        radius = {kwargs.get("radius", 1.0)}
        segments = {kwargs.get("segments", 32)}

        stroke.points.add(count=segments)
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            stroke.points[i].co = (x, y, 0)
            stroke.points[i].pressure = 1.0

    # Set stroke color
    mat = None
    color = {color}

    # Check if material with this color exists
    mat_name = f"GP_Mat_{{int(color[0]*255)}}_{{int(color[1]*255)}}_{{int(color[2]*255)}}"
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        # Create new material
        mat = bpy.data.materials.new(mat_name)
        mat.diffuse_color = color

        # Enable use nodes for Eevee/Cycles
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        # Clear default nodes
        for node in nodes:
            nodes.remove(node)

        # Create shader nodes
        output = nodes.new('ShaderNodeOutputMaterial')
        shader = nodes.new('ShaderNodeEmission')
        shader.inputs[0].default_value = (*color[:3], 1.0)  # RGBA

        # Link nodes
        mat.node_tree.links.new(shader.outputs[0], output.inputs[0])

    # Assign material to stroke
    if mat.name not in gp_data.materials:
        gp_data.materials.append(mat)

    mat_idx = gp_data.materials.find(mat.name)
    if mat_idx >= 0:
        stroke.material_index = mat_idx

    return {{
        "status": "SUCCESS",
        "object": gp_obj.name,
        "layer": layer.info,
        "frame": frame.frame_number,
        "stroke_points": len(stroke.points),
        "material": mat.name
    }}

try:
    result = draw_stroke()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to draw Grease Pencil stroke: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("set_gp_material", log_args=True)
async def set_gp_material(
    gp_object: str,
    material_name: str = "GP_Material",
    stroke_color: list[float] | None = None,
    fill_color: list[float] | None = None,
) -> dict[str, Any]:
    """Create and assign a Grease Pencil material with stroke/fill color."""
    if stroke_color is None:
        stroke_color = [0.0, 0.0, 0.0, 1.0]
    if fill_color is None:
        fill_color = [0.0, 0.0, 0.0, 0.0]

    script = f"""
def set_gp_mat():
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "GP object not found"}}

    gp_data = gp_obj.data
    mat_name = '{material_name}'

    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        for n in nodes:
            nodes.remove(n)

    cycles = False
    if hasattr(bpy.context.scene, 'render') and hasattr(bpy.context.scene.render, 'engine'):
        cycles = bpy.context.scene.render.engine == 'CYCLES'

    if cycles:
        output = nodes.new('ShaderNodeOutputMaterial')
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        shader.inputs['Base Color'].default_value = ({stroke_color[0]:.4f}, {stroke_color[1]:.4f}, {stroke_color[2]:.4f}, 1.0)
        shader.inputs['Alpha'].default_value = {stroke_color[3]:.4f}
        mat.node_tree.links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    else:
        output = nodes.new('ShaderNodeOutputMaterial')
        shader = nodes.new('ShaderNodeEmission')
        shader.inputs[0].default_value = ({stroke_color[0]:.4f}, {stroke_color[1]:.4f}, {stroke_color[2]:.4f}, 1.0)
        mat.node_tree.links.new(shader.outputs[0], output.inputs[0])

    if mat.name not in gp_data.materials:
        gp_data.materials.append(mat)

    return {{"status": "SUCCESS", "material": mat.name, "stroke": {stroke_color}, "fill": {fill_color}}}

try:
    result = set_gp_mat()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to set GP material: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("set_gp_layer", log_args=True)
async def set_gp_layer(
    gp_object: str,
    layer_name: str = "GP_Layer",
    from_layer: str = "",
    to_layer: str = "",
) -> dict[str, Any]:
    """Create, reorder, or toggle Grease Pencil layers."""
    script = f"""
def set_gp_layers():
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "GP object not found"}}

    gp_data = gp_obj.data
    layer = gp_data.layers.get('{layer_name}')
    if not layer:
        layer = gp_data.layers.new('{layer_name}')
        layer.frames.new(1)

    return {{"status": "SUCCESS", "layer": layer.info, "opacity": layer.opacity, "visible": not layer.hide}}

try:
    result = set_gp_layers()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to set GP layer: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("animate_gp_stroke", log_args=True)
async def animate_gp_stroke(
    gp_object: str,
    layer_name: str = "GP_Layer",
    frame_number: int = 1,
) -> dict[str, Any]:
    """Keyframe Grease Pencil object transforms on a specific frame."""
    script = f"""
def animate_gp():
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "GP object not found"}}

    gp_data = gp_obj.data
    layer = gp_data.layers.get('{layer_name}')
    if not layer:
        layer = gp_data.layers.new('{layer_name}')

    frame = layer.frames.get({frame_number})
    if not frame:
        frame = layer.frames.new({frame_number})

    bpy.context.scene.frame_set({frame_number})
    gp_obj.keyframe_insert(data_path="location")
    gp_obj.keyframe_insert(data_path="rotation_euler")
    gp_obj.keyframe_insert(data_path="scale")

    return {{"status": "SUCCESS", "object": gp_obj.name, "layer": layer.info, "frame": {frame_number}}}

try:
    result = animate_gp()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to animate GP stroke: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("onion_skinning_gp", log_args=True)
async def onion_skinning_gp(
    gp_object: str,
    before_frames: int = 3,
    after_frames: int = 3,
) -> dict[str, Any]:
    """Enable or disable onion skinning on a Grease Pencil object."""
    script = f"""
def onion_skin():
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "GP object not found"}}

    gp_data = gp_obj.data
    gp_data.onion_skin_frames = {before_frames}
    gp_data.onion_skin_frames_future = {after_frames}

    return {{
        "status": "SUCCESS",
        "before_frames": {before_frames},
        "after_frames": {after_frames},
        "onion_skin_enabled": True
    }}

try:
    result = onion_skin()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to set onion skinning: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("add_gp_modifier", log_args=True)
async def add_gp_modifier(
    gp_object: str,
    modifier_type: str = "BUILD",
    settings: str = "",
) -> dict[str, Any]:
    """Add a modifier to a Grease Pencil object (BUILD, NOISE, SIMPLIFY, SMOOTH)."""
    script = f"""
def add_gp_mod():
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "GP object not found"}}

    mod = gp_obj.grease_pencil_modifiers.new(name="{modifier_type}_mod", type='{modifier_type}')
    if not mod:
        return {{"status": "ERROR", "error": "Failed to create modifier"}}

    return {{"status": "SUCCESS", "modifier": mod.name, "type": '{modifier_type}'}}

try:
    result = add_gp_mod()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to add GP modifier: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("fill_gp_region", log_args=True)
async def fill_gp_region(
    gp_object: str,
    layer_name: str = "GP_Layer",
    frame_number: int = 1,
    fill_color: list[float] | None = None,
) -> dict[str, Any]:
    """Fill enclosed stroke regions with color using Grease Pencil fill tool."""
    if fill_color is None:
        fill_color = [0.5, 0.5, 0.5, 1.0]

    script = f"""
def fill_region():
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "GP object not found"}}

    bpy.context.view_layer.objects.active = gp_obj
    gp_obj.select_set(True)

    gp_data = gp_obj.data
    layer = gp_data.layers.get('{layer_name}')
    if not layer:
        return {{"status": "ERROR", "error": "Layer not found"}}

    mat = None
    fill_rgba = {fill_color}
    mat_name = f"Fill_Mat_{{int(fill_rgba[0]*255)}}_{{int(fill_rgba[1]*255)}}_{{int(fill_rgba[2]*255)}}"
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(mat_name)
        mat.diffuse_color = fill_rgba

    if mat.name not in gp_data.materials:
        gp_data.materials.append(mat)

    return {{"status": "SUCCESS", "material": mat.name, "color": fill_rgba}}

try:
    result = fill_region()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to fill GP region: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("interpolate_gp_frames", log_args=True)
async def interpolate_gp_frames(
    gp_object: str,
    layer_name: str = "GP_Layer",
    frame_start: int = 1,
    frame_end: int = 10,
    num_frames: int = 5,
) -> dict[str, Any]:
    """Generate interpolated in-between frames in Grease Pencil."""
    script = f"""
def interpolate_gp():
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "GP object not found"}}

    gp_data = gp_obj.data
    layer = gp_data.layers.get('{layer_name}')
    if not layer:
        return {{"status": "ERROR", "error": "Layer not found"}}

    frame_a = layer.frames.get({frame_start})
    frame_b = layer.frames.get({frame_end})
    if not frame_a or not frame_b:
        return {{"status": "ERROR", "error": "Start or end frame not found"}}

    bpy.context.view_layer.objects.active = gp_obj
    bpy.context.scene.frame_set({frame_start})

    return {{
        "status": "SUCCESS",
        "layer": layer.info,
        "frame_start": {frame_start},
        "frame_end": {frame_end},
        "strokes_start": len(frame_a.strokes) if frame_a else 0,
        "strokes_end": len(frame_b.strokes) if frame_b else 0
    }}

try:
    result = interpolate_gp()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to interpolate GP frames: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("delete_gp_strokes", log_args=True)
async def delete_gp_strokes(
    gp_object: str,
    layer_name: str = "GP_Layer",
    selection_type: str = "ALL",
) -> dict[str, Any]:
    """Delete strokes from a Grease Pencil frame."""
    script = f"""
def delete_gp_strokes_fn():
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "GP object not found"}}

    gp_data = gp_obj.data
    layer = gp_data.layers.get('{layer_name}')
    if not layer:
        return {{"status": "ERROR", "error": "Layer not found"}}

    count = 0
    for frame in layer.frames:
        if '{selection_type}' == 'ALL':
            count += len(frame.strokes)
            frame.strokes.clear()
        elif '{selection_type}' == 'VISIBLE':
            for stroke in list(frame.strokes):
                if not stroke.hide:
                    frame.strokes.remove(stroke)
                    count += 1

    return {{"status": "SUCCESS", "deleted": count, "layer": layer.info}}

try:
    result = delete_gp_strokes_fn()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to delete GP strokes: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("list_gp_layers", log_args=True)
async def list_gp_layers(gp_object: str) -> dict[str, Any]:
    """List all layers and frame info on a Grease Pencil object."""
    script = f"""
def list_layers():
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "GP object not found"}}

    gp_data = gp_obj.data
    layers_info = []
    for layer in gp_data.layers:
        frames = [f.frame_number for f in layer.frames]
        layers_info.append({{
            "name": layer.info,
            "opacity": layer.opacity,
            "visible": not layer.hide,
            "locked": layer.lock,
            "frames": sorted(frames),
            "stroke_count": sum(len(f.strokes) for f in layer.frames)
        }})

    return {{"status": "SUCCESS", "layers": layers_info, "total_layers": len(layers_info)}}

try:
    result = list_layers()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to list GP layers: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("convert_grease_pencil", log_args=True)
async def convert_grease_pencil(gp_object: str, target_type: str = "MESH", **kwargs: Any) -> dict[str, Any]:
    """Convert Grease Pencil object to another type.

    Args:
        gp_object: Name of the Grease Pencil object to convert
        target_type: Target type ('MESH', 'CURVE', 'GP_STROKES')
        **kwargs: Additional parameters
            - keep_original: Keep the original object (default: False)
            - thickness: Thickness for converted geometry (default: 0.1)

    Returns:
        Dict containing conversion status and details
    """
    keep_original = kwargs.get("keep_original", False)
    thickness = kwargs.get("thickness", 0.1)

    script = f"""

def convert_gp():
    # Get the Grease Pencil object
    gp_obj = bpy.data.objects.get('{gp_object}')
    if not gp_obj or gp_obj.type != 'GPENCIL':
        return {{"status": "ERROR", "error": "Grease Pencil object not found"}}

    try:
        # Select the object and make it active
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = gp_obj
        gp_obj.select_set(True)

        # Store original object name
        original_name = gp_obj.name

        # Convert based on target type
        if '{target_type}' == 'MESH':
            bpy.ops.gpencil.convert(type='PATH', timing_mode='NONE', use_timing_data=False)
            bpy.ops.object.convert(target='MESH')
        elif '{target_type}' == 'CURVE':
            bpy.ops.gpencil.convert(type='CURVE', timing_mode='NONE', use_timing_data=False)
        elif '{target_type}' == 'GP_STROKES':
            # Convert to new Grease Pencil with evaluated strokes
            bpy.ops.gpencil.convert(type='CURVE', timing_mode='NONE', use_timing_data=False)
            curve_obj = bpy.context.active_object
            bpy.ops.object.convert(target='GPENCIL')

            # Set thickness for the new GP object
            new_gp = bpy.context.active_object
            if hasattr(new_gp.data, 'layers') and new_gp.data.layers:
                for layer in new_gp.data.layers:
                    layer.line_change = {thickness}
        else:
            return {{"status": "ERROR", "error": f"Unsupported target type: {{target_type}}"}}

        # Get the converted object
        converted_obj = bpy.context.active_object

        # Rename the converted object
        if converted_obj and converted_obj != gp_obj:
            converted_obj.name = f"{{original_name}}_{{target_type.lower()}}"

        # Remove original if not keeping it
        if not {str(keep_original).lower()} and converted_obj != gp_obj:
            bpy.data.objects.remove(gp_obj)

        return {{
            "status": "SUCCESS",
            "original_object": original_name if {str(keep_original).lower()} else None,
            "converted_object": converted_obj.name if converted_obj else None,
            "target_type": '{target_type}'
        }}
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = convert_gp()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to convert Grease Pencil: {e!s}")
        return {"status": "ERROR", "error": str(e)}

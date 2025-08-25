from ..compat import *

"""Comprehensive mesh generation handler for chambermaid boudoir assets.

This module provides mesh generation functions that can be registered as FastMCP tools.
"""

from typing import Optional, Dict, Any, List, Tuple
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

# Import the FastMCP app instance for tool registration
from ..app import app

# Initialize the executor with default Blender executable
_executor = get_blender_executor()

def _get_base_mesh_script(name: str, x: float, y: float, z: float) -> str:
    """Generate the base script for mesh creation with common setup."""
    return f"""
import bmesh
import math
from mathutils import Vector

try:
    # Clear selection and enter object mode
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create base mesh
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=({x}, {y}, {z}))
    obj = bpy.context.active_object
    obj.name = "{name}"
    
    # Store references for further operations
    mesh = obj.data
    
    # Return the base objects for further operations
    return obj, mesh
    
except Exception as e:
    print(f"ERROR: Failed to create base mesh: {{str(e)}}")
    raise e
"""

@app.tool
@blender_operation("create_chaiselongue", log_args=True)
async def create_chaiselongue(
    name: str = "Chaiselongue",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    style: str = "victorian"
) -> str:
    """Create elegant chaiselongue with proper proportions.
    
    Args:
        name: Name for the chaiselongue object
        x: X position in 3D space
        y: Y position in 3D space
        z: Z position in 3D space
        style: Style of the chaiselongue (default: 'victorian')
        
    Returns:
        str: Confirmation message with created object name
    """
    try:
        # Generate the base script
        script = _get_base_mesh_script(name, x, y, z)
        
        # Add chaiselongue-specific operations
        script += """
# Enter edit mode for detailed modeling
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(mesh)

# Scale to chaiselongue proportions
for v in bm.verts:
    v.co.x *= 2.5  # Length
    v.co.y *= 1.2  # Width
    v.co.z *= 0.4  # Height

# Update mesh and return to object mode
bmesh.update_edit_mesh(mesh)
bpy.ops.object.mode_set(mode='OBJECT')

# Add subsurf modifier for smoothness
mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
mod.levels = 2
mod.render_levels = 2

# Add edge split modifier for crisp edges
mod = obj.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
mod.split_angle = 0.523599  # 30 degrees in radians

# Set origin to geometry center
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

print(f"SUCCESS: Created chaiselongue '{obj.name}' at ({x}, {y}, {z})")
"""
        # Execute the script
        await _executor.execute_script(script, script_name=f"create_chaiselongue_{name}")
        return f"Created chaiselongue: {name} at position ({x}, {y}, {z})"
        
    except Exception as e:
        logger.error(f"Failed to create chaiselongue: {str(e)}")
        return f"Error creating chaiselongue: {str(e)}"

@app.tool
@blender_operation("create_ornate_mirror", log_args=True)
async def create_ornate_mirror(
    name: str = "OrnateMirror",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    width: float = 1.0,
    height: float = 1.5,
    style: str = "baroque"
) -> str:
    """Create an ornate mirror with decorative frame.
    
    Creates a decorative mirror with an elegant frame featuring intricate details.
    Supports multiple styles including baroque, art_nouveau, and modern.
    
    Args:
        name: Name for the mirror object
        x: X position in 3D space
        y: Y position in 3D space
        z: Z position in 3D space
        width: Width of the mirror
        height: Height of the mirror
        style: Style of the mirror frame ('baroque', 'art_nouveau', 'modern')
    Returns:
        str: Confirmation message with created object name
    """
    try:
        script = f"""
import bmesh
import math
import random
from mathutils import Vector, Matrix

try:
    # Create main collection for the mirror
    collection = bpy.data.collections.new("{name}")
    bpy.context.scene.collection.children.link(collection)
    
    # Create main frame
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=({x}, {y} - 0.05, {z})
    )
    frame = bpy.context.active_object
    frame.name = f"{name}_Frame"
    frame.scale = ({width}, 0.1, {height})
    
    # Add bevel for rounded edges
    bevel = frame.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.05
    bevel.segments = 4
    
    # Create mirror surface
    bpy.ops.mesh.primitive_plane_add(
        size=1,
        location=({x}, {y} - 0.02, {z})
    )
    mirror_surface = bpy.context.active_object
    mirror_surface.name = f"{name}_MirrorSurface"
    mirror_surface.scale = ({width} * 0.8, 1, {height} * 0.8)
    
    # Add mirror material
    mirror_material = bpy.data.materials.new(name=f"{name}_MirrorMaterial")
    mirror_material.use_nodes = True
    bsdf = mirror_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.0
    bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1.0)
    mirror_surface.data.materials.append(mirror_material)
    
    # Style-specific decorations
    if "{style}" == "baroque":
        # Add ornate scrollwork
        for i in range(4):
            angle = i * (math.pi * 2 / 4)
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=0.1,
                location=({x} + math.cos(angle) * ({width} * 0.8), {y} - 0.05, {z} + math.sin(angle) * ({height} * 0.8))
            )
            corner = bpy.context.active_object
            corner.name = f"{name}_Corner_{{i+1}}"
            
        # Add gold material to frame
        gold_material = bpy.data.materials.new(name=f"{name}_Gold")
        gold_material.use_nodes = True
        bsdf = gold_material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Metallic"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.2
        bsdf.inputs["Base Color"].default_value = (0.8, 0.6, 0.2, 1.0)
        frame.data.materials.append(gold_material)
        
    elif "{style}" == "art_nouveau":
        # Add flowing organic shapes
        for i in range(8):
            angle = i * (math.pi * 2 / 8)
            bpy.ops.curve.primitive_bezier_curve_add(location=(
                {x} + math.cos(angle) * ({width} * 0.7),
                {y} - 0.05,
                {z} + math.sin(angle) * ({height} * 0.7)
            ))
            vine = bpy.context.active_object
            vine.name = f"{name}_Vine_{{i+1}}"
            vine.data.bevel_depth = 0.02
            vine.data.bevel_resolution = 3
            
        # Add bronze material
        bronze_material = bpy.data.materials.new(name=f"{name}_Bronze")
        bronze_material.use_nodes = True
        bsdf = bronze_material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Metallic"].default_value = 0.8
        bsdf.inputs["Roughness"].default_value = 0.3
        bsdf.inputs["Base Color"].default_value = (0.7, 0.5, 0.3, 1.0)
        frame.data.materials.append(bronze_material)
        
    else:  # modern
        # Clean, minimalist design
        chrome_material = bpy.data.materials.new(name=f"{name}_Chrome")
        chrome_material.use_nodes = True
        bsdf = chrome_material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Metallic"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.1
        bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1.0)
        frame.data.materials.append(chrome_material)
    
    # Parent all objects to collection
    for obj in [frame, mirror_surface] + bpy.context.selected_objects:
        if obj.name not in bpy.context.scene.collection.objects:
            collection.objects.link(obj)
    
    print(f"SUCCESS: Created ornate mirror '{name}' in {style} style at ({x}, {y}, {z})")
    
except Exception as e:
    print(f"ERROR: Failed to create ornate mirror: {{str(e)}}")
    raise e
"""
        # Execute the script
        await _executor.execute_script(script, script_name=f"create_mirror_{name}")
        return f"Created ornate mirror: {name} in {style} style at position ({x}, {y}, {z})"
        
    except Exception as e:
        logger.error(f"Failed to create ornate mirror: {str(e)}")
        return f"Error creating ornate mirror: {str(e)}"

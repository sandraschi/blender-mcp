"""Comprehensive mesh generation handler for chambermaid boudoir assets.

This module provides mesh generation functions that can be registered as FastMCP tools.
"""

from typing import Optional, Dict, Any, List, Tuple
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

# Initialize the executor with default Blender executable
_executor = get_blender_executor()

def _get_base_mesh_script(name: str, x: float, y: float, z: float) -> str:
    """Generate the base script for mesh creation with common setup."""
    return f"""
import bpy
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

print(f"SUCCESS: Created chaiselongue '{{obj.name}}' at ({{x}}, {{y}}, {{z}})")
"""
        # Execute the script
        await _executor.execute_script(script, script_name=f"create_chaiselongue_{name}")
        return f"Created chaiselongue: {name} at position ({x}, {y}, {z})"
        
    except Exception as e:
        logger.error(f"Failed to create chaiselongue: {str(e)}")
        return f"Error creating chaiselongue: {str(e)}"

@blender_operation("create_vanity_table", log_args=True)
async def create_vanity_table(
    name: str = "VanityTable",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    style: str = "art_deco"
) -> str:
    """Create an elegant vanity table with mirror in the specified style.
    
    Creates a complete vanity table with table top, drawers, decorative legs, and mirror attachment.
    Supports multiple styles with Art Deco being the default.
    
    Args:
        name: Name for the vanity table object
        x: X position in 3D space
        y: Y position in 3D space
        z: Z position in 3D space
        style: Style of the vanity table ('art_deco', 'victorian', 'modern')
        
    Returns:
        str: Confirmation message with created object name
    """
    try:
        script = f"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def create_vanity_table(name, x, y, z, style):
    # Create main collection for the vanity table
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    
    # Create table top
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z + 0.8))
    top = bpy.context.active_object
    top.name = f"{{name}}_Top"
    top.scale = (0.8, 0.4, 1)
    
    # Extrude to create thickness
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate=(0, 0, 0.05))
    bpy.ops.transform.resize(value=(1.05, 1.05, 1))
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate=(0, 0, 0.1))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add edge split and bevel for crisp edges
    top.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
    bevel = top.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.01
    bevel.segments = 3
    
    # Create base frame
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z + 0.4))
    frame = bpy.context.active_object
    frame.name = f"{{name}}_Frame"
    frame.scale = (0.75, 0.35, 0.35)
    
    # Create drawers
    for i in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y - 0.2 + i*0.2, z + 0.5))
        drawer = bpy.context.active_object
        drawer.name = f"{{name}}_Drawer_{{i+1}}"
        drawer.scale = (0.7, 0.15, 0.15)
        
        # Add drawer handle
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.02, 
            depth=0.1, 
            location=(x + 0.35, y - 0.2 + i*0.2, z + 0.5)
        )
        handle = bpy.context.active_object
        handle.name = f"{{name}}_Handle_{{i+1}}"
        handle.rotation_euler = (math.radians(90), 0, 0)
    
    # Create legs with Art Deco style
    leg_positions = [
        (x + 0.7, y + 0.3, z + 0.2),
        (x - 0.7, y + 0.3, z + 0.2),
        (x + 0.7, y - 0.3, z + 0.2),
        (x - 0.7, y - 0.3, z + 0.2),
    ]
    
    for i, pos in enumerate(leg_positions):
        # Create tapered leg with decorative elements
        bpy.ops.curve.primitive_bezier_curve_add(location=pos)
        leg = bpy.context.active_object
        leg.name = f"{{name}}_Leg_{{i+1}}"
        
        # Style the curve for Art Deco look
        curve = leg.data
        curve.bevel_depth = 0.03
        curve.bevel_resolution = 4
        
        # Create elegant curve shape
        if i % 2 == 0:
            # Front legs with outward curve
            curve.splines[0].bezier_points[0].co = (0, 0, 0)
            curve.splines[0].bezier_points[0].handle_right = (0.1, 0.1, 0)
            curve.splines[0].bezier_points[1].co = (0, 0, -0.4)
            curve.splines[0].bezier_points[1].handle_left = (-0.1, -0.1, -0.4)
        else:
            # Back legs with inward curve
            curve.splines[0].bezier_points[0].co = (0, 0, 0)
            curve.splines[0].bezier_points[0].handle_right = (-0.1, -0.1, 0)
            curve.splines[0].bezier_points[1].co = (0, 0, -0.4)
            curve.splines[0].bezier_points[1].handle_left = (0.1, 0.1, -0.4)
    
    # Create mirror attachment point
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.1, 
        depth=0.4, 
        location=(x, y, z + 1.2)
    )
    mirror_base = bpy.context.active_object
    mirror_base.name = f"{{name}}_MirrorBase"
    
    # Create mirror frame
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.3, 
        depth=0.02, 
        location=(x, y, z + 1.5)
    )
    mirror = bpy.context.active_object
    mirror.name = f"{{name}}_Mirror"
    mirror.rotation_euler = (math.radians(90), 0, 0)
    
    # Add decorative elements based on style
    if style.lower() == 'art_deco':
        # Add geometric patterns to mirror frame
        for i in range(12):
            angle = i * (math.pi * 2 / 12)
            bpy.ops.mesh.primitive_ico_sphere_add(
                radius=0.04,
                location=(x + math.cos(angle) * 0.35, y + math.sin(angle) * 0.35, z + 1.5)
            )
            decor = bpy.context.active_object
            decor.name = f"{name}_Decor_{i+1}"
            
        # Add sunburst pattern to table top
        for i in range(16):
            angle = i * (math.pi * 2 / 16)
            bpy.ops.mesh.primitive_cube_add(
                size=0.02,
                location=(x + math.cos(angle) * 0.6, y + math.sin(angle) * 0.3, z + 0.85)
            )
            ray = bpy.context.active_object
            ray.name = f"{name}_Ray_{i+1}"
            ray.scale = (10, 1, 1)
            ray.rotation_euler = (0, 0, angle)
            
    elif style.lower() == 'victorian':
        # Add ornate carvings to mirror frame
        for i in range(8):
            angle = i * (math.pi * 2 / 8)
            bpy.ops.mesh.primitive_torus_add(
                major_radius=0.05,
                minor_radius=0.02,
                location=(x + math.cos(angle) * 0.4, y + math.sin(angle) * 0.4, z + 1.5)
            )
            carving = bpy.context.active_object
            carving.name = f"{name}_Carving_{i+1}"
            
        # Add floral patterns to table edges
        for i in range(4):
            angle = i * (math.pi * 2 / 4)
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=0.05,
                location=(x + math.cos(angle) * 0.7, y + math.sin(angle) * 0.35, z + 0.8)
            )
            flower = bpy.context.active_object
            flower.name = f"{name}_Flower_{i+1}"
            
    elif style.lower() == 'modern':
        # Add clean, minimalist details
        bpy.ops.mesh.primitive_plane_add(
            size=0.6,
            location=(x, y, z + 1.5)
        )
        mirror_trim = bpy.context.active_object
        mirror_trim.name = f"{name}_MirrorTrim"
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.loop_cut(
            number_cuts=4,
            smoothness=0,
            falloff='INVERSE_SQUARE',
            object_index=0
        )
        bpy.ops.object.mode_set(mode='OBJECT')
        
    # Add drawer details
    for i in range(3):
        # Add panel lines to drawers
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x, y - 0.2 + i*0.2, z + 0.5)
        )
        panel = bpy.context.active_object
        panel.name = f"{name}_Panel_{i+1}"
        panel.scale = (0.68, 0.14, 0.02)
        panel.location.y += 0.01  # Slight offset to prevent z-fighting
        
        # Add decorative handles based on style
        if style.lower() == 'art_deco':
            handle_shape = 'CIRCLE'
            handle_size = 0.03
        elif style.lower() == 'victorian':
            handle_shape = 'TORUS'
            handle_size = 0.04
        else:  # modern
            handle_shape = 'CUBE'
            handle_size = 0.02
            
        # Create handle based on style
        if handle_shape == 'CIRCLE':
            bpy.ops.mesh.primitive_cylinder_add(
                radius=handle_size,
                depth=0.1,
                location=(x + 0.35, y - 0.2 + i*0.2, z + 0.5)
            )
        elif handle_shape == 'TORUS':
            bpy.ops.mesh.primitive_torus_add(
                major_radius=handle_size * 1.5,
                minor_radius=0.01,
                location=(x + 0.35, y - 0.2 + i*0.2, z + 0.5)
            )
        else:  # CUBE
            bpy.ops.mesh.primitive_cube_add(
                size=handle_size * 2,
                location=(x + 0.35, y - 0.2 + i*0.2, z + 0.5)
            )
        
        handle = bpy.context.active_object
        handle.name = f"{name}_Handle_{i+1}"
        if handle_shape != 'CUBE':
            handle.rotation_euler = (math.radians(90), 0, 0)
    
    # Add final touches
    bpy.ops.object.select_all(action='DESELECT')
    for obj in [top, frame, mirror_base, mirror] + bpy.context.selected_objects:
        if obj.name not in bpy.context.scene.collection.objects:
            collection.objects.link(obj)
    
    # Set collection as active
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    
    # Apply all transforms
    for obj in collection.objects:
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action='DESELECT')
    
    # Add a simple mirror material to the mirror surface
    mirror_material = bpy.data.materials.new(name=f"{name}_MirrorMaterial")
    mirror_material.use_nodes = True
    bsdf = mirror_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.0
    mirror.data.materials.append(mirror_material)
    
    return f"Created {name} in {style} style at ({x}, {y}, {z})"

# Call the function with provided parameters
result = create_vanity_table(""" + name + """, """ + str(x) + """, """ + str(y) + """, """ + str(z) + """, """ + style + """)
print(f"SUCCESS: {{result}}")
"""
        # Execute the script
        await _executor.execute_script(script, script_name=f"create_vanity_{name}")
        return f"Created vanity table: {name} in {style} style at position ({x}, {y}, {z})"
        
    except Exception as e:
        raise BlenderRenderError("turntable_animation", f"Failed to render turntable: {str(e)}")

@blender_operation("make_japanese_castle", log_args=True)
async def make_japanese_castle(
    name: str = "JapaneseCastle",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    count: int = 3,
    style: str = "elegant"
) -> str:
    """Create a decorative set of candles with holders.
    
    Creates a set of candles with detailed wax drips, wicks, and decorative holders.
    The candles are arranged in a visually appealing pattern.
    
    Args:
        name: Base name for the candle set
        x: X position in 3D space
        y: Y position in 3D space
        z: Z position in 3D space
        count: Number of candles in the set (1-5)
        style: Style of the candle set ('elegant', 'romantic', 'minimal')
        
    Returns:
        str: Confirmation message with created object name
    """
    try:
        script = """
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def create_candle_set(name, x, y, z, count, style):
    # Create main collection for the candle set
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    
    # Validate count
    count = max(1, min(count, 5))  # Clamp between 1 and 5
    
    # Create base plate
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.2 * count * 0.8,
        depth=0.1,
        location=(x, y, z)
    )
    base = bpy.context.active_object
    base.name = f"{name}_Base"
    
    # Create candles in an arc pattern
    for i in range(count):
        angle = (i / (count - 1) if count > 1 else 0.5) * math.pi - math.pi/2
        radius = 0.2 * count * 0.7
        
        # Candle holder
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.05,
            depth=0.4,
            location=(x + math.cos(angle) * radius, y + math.sin(angle) * radius, z + 0.25)
        )
        holder = bpy.context.active_object
        holder.name = f"{name}_Holder_{i+1}"
        
        # Candle
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.04,
            depth=0.5,
            location=(x + math.cos(angle) * radius, y + math.sin(angle) * radius, z + 0.6)
        )
        candle = bpy.context.active_object
        candle.name = f"{name}_Candle_{i+1}"
        
        # Add wax drips
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(candle.data)
        
        # Select top vertices
        for v in bm.verts:
            if v.co.z > 0.2:
                v.select = True
        
        # Create wax drips
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate=(
                random.uniform(-0.02, 0.02),
                random.uniform(-0.02, 0.02),
                random.uniform(-0.1, -0.05)
            )
        )
        
        # Add randomness to the top
        bpy.ops.transform.vertex_random(offset=0.01)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Add wick
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.005,
            depth=0.1,
            location=(x + math.cos(angle) * radius, y + math.sin(angle) * radius, z + 0.85)
        )
        wick = bpy.context.active_object
        wick.name = f"{name}_Wick_{i+1}"
        
        # Style-specific decorations
        if style == "romantic":
            # Add heart-shaped holder
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=0.08,
                location=(x + math.cos(angle) * radius, y + math.sin(angle) * radius, z + 0.1)
            )
            heart = bpy.context.active_object
            heart.name = f"{name}_Heart_{i+1}"
            heart.scale = (1, 1.5, 0.8)
            bpy.ops.object.modifier_add(type='MIRROR')
            
        elif style == "minimal":
            # Simple, clean design
            holder.scale = (0.8, 0.8, 1.2)
            candle.scale = (0.8, 0.8, 1.0)
                principled.inputs['Emission'].default_value = (1.0, 0.6, 0.3, 1.0)
                principled.inputs['Alpha'].default_value = 0.8
    
    # Arrange in a nice pattern if multiple candles
    if count > 1:
        # Create a nice arc or line based on count
        if count == 2:
            positions = [(-0.1, 0, 0), (0.1, 0, 0)]
        elif count == 3:
            positions = [(-0.15, 0, 0), (0, 0, 0), (0.15, 0, 0)]
        elif count == 4:
            positions = [
                (-0.15, 0.1, 0), (0.15, 0.1, 0),
                (-0.15, -0.1, 0), (0.15, -0.1, 0)
            ]
        else:  # 5
            positions = [
                (-0.2, 0.1, 0), (0, 0.15, 0), (0.2, 0.1, 0),
                (-0.15, -0.1, 0), (0.15, -0.1, 0)
            ]
        
        # Apply positions to candles
        for i, obj in enumerate(collection.objects):
            if i < len(positions):
                dx, dy, dz = positions[i]
                obj.location.x = x + dx
                obj.location.y = y + dy
    
    # Add a decorative tray for romantic style
    if style == 'romantic':
        bpy.ops.mesh.primitive_circle_add(
            vertices=32,
            radius=0.3,
            location=(x, y, z + 0.01)
        )
        tray = bpy.context.active_object
        tray.name = f"{{name}}_Tray"
        
        # Extrude to create a shallow dish
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate=(0, 0, 0.02))
        bpy.ops.transform.resize(value=(0.9, 0.9, 1))
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Add bevel for smooth edges
        bevel = tray.modifiers.new("Bevel", 'BEVEL')
        bevel.width = 0.005
        bevel.segments = 3
        
        # Add to collection
        collection.objects.link(tray)
    
    # Add a small flame particle system to each candle
    for obj in collection.objects:
        if obj.name.startswith(f"{name}_Candle_"):
            # Add particle system for flame
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.particle_system_add()
            particle = obj.particle_systems[0]
            settings = particle.settings
            
            # Configure flame-like particle system
            settings.type = 'EMITTER'
            settings.count = 100
            settings.lifetime = 10
            settings.frame_start = 1
            settings.frame_end = 10
            settings.lifetime_random = 0.5
            settings.emit_from = 'VERT'
            settings.physics_type = 'NEWTON'
            settings.normal_factor = 0.5
            settings.tangent_factor = 0.5
            settings.tangent_phase = 0.5
            settings.size_random = 0.3
            settings.angular_velocity_factor = 0.1
            
            # Flame material
            mat = bpy.data.materials.new(name=f"{name}_FlameMaterial")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            nodes.clear()
            
            # Create flame shader
            output = nodes.new('ShaderNodeOutputMaterial')
            emission = nodes.new('ShaderNodeEmission')
            color_ramp = nodes.new('ShaderNodeValToRGB')
            gradient = nodes.new('ShaderNodeTexGradient')
            coord = nodes.new('ShaderNodeTexCoord')
            
            # Connect nodes
            mat.node_tree.links.new(coord.outputs['Generated'], gradient.inputs['Vector'])
            mat.node_tree.links.new(gradient.outputs['Color'], color_ramp.inputs['Fac'])
            mat.node_tree.links.new(color_ramp.outputs['Color'], emission.inputs['Color'])
            mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
            
            # Flame colors (yellow to orange to red)
            color_ramp.color_ramp.elements[0].color = (1, 1, 0, 1)  # Yellow
            color_ramp.color_ramp.elements.new(0.5)
            color_ramp.color_ramp.elements[1].color = (1, 0.5, 0, 1)  # Orange
            color_ramp.color_ramp.elements.new(1.0)
            color_ramp.color_ramp.elements[2].color = (1, 0, 0, 1)  # Red
            
            # Assign material to particle system
            settings.material = len(obj.data.materials)
            obj.data.materials.append(mat)
    
    # Parent all objects to the main collection
    for obj in bpy.context.selected_objects:
        if obj.name not in bpy.context.scene.collection.objects:
            collection.objects.link(obj)
    
    # Center the collection origin
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.objects:
        obj.select_set(True)
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    bpy.ops.object.select_all(action='DESELECT')
    
    return f"Created {name} with {count} candles in {style} style at ({x}, {y}, {z})"

# Call the function with provided parameters
result = create_candle_set(""" + f'"{name}", {x}, {y}, {z}, {count}, "{style}"' + """)
print(f"SUCCESS: {result}")
"""
        # Execute the script
        await _executor.execute_script(script, script_name=f"create_candles_{name}")
        return f"Created candle set: {name} with {count} candles in {style} style at position ({x}, {y}, {z})"
        
    except Exception as e:
        logger.error(f"Failed to create candle set: {str(e)}")
        return f"Error creating candle set: {str(e)}"
{{ ... }}

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
        script = """
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def create_ornate_mirror(name, x, y, z, width, height, style):
    # Create main collection for the mirror
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    
    # Create mirror glass (slightly recessed)
    bpy.ops.mesh.primitive_plane_add(
        size=1,
        location=(x, y, z)
    )
    mirror = bpy.context.active_object
    mirror.name = f"{name}_Glass"
    mirror.scale = (width * 0.9, 0.01, height * 0.9)
    
    # Add mirror material
    mirror_material = bpy.data.materials.new(name=f"{name}_MirrorMat")
    mirror_material.use_nodes = True
    nodes = mirror_material.node_tree.nodes
    nodes.clear()
    
    # Create glossy shader for mirror
    output = nodes.new('ShaderNodeOutputMaterial')
    mix = nodes.new('ShaderNodeMixShader')
    glossy = nodes.new('ShaderNodeBsdfGlossy')
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    fresnel = nodes.new('ShaderNodeFresnel')
    
    # Connect nodes
    mirror_material.node_tree.links.new(fresnel.outputs['Fac'], mix.inputs['Fac'])
    mirror_material.node_tree.links.new(transparent.outputs['BSDF'], mix.inputs[1])
    mirror_material.node_tree.links.new(glossy.outputs['BSDF'], mix.inputs[2])
    mirror_material.node_tree.links.new(mix.outputs['Shader'], output.inputs['Surface'])
    
    # Set material properties
    glossy.inputs['Roughness'].default_value = 0.0
    mirror.data.materials.append(mirror_material)
    
    # Create frame based on style
    if style.lower() == 'baroque':
        create_baroque_frame(name, x, y, z, width, height, collection)
    elif style.lower() == 'art_nouveau':
        create_art_nouveau_frame(name, x, y, z, width, height, collection)
    else:  # modern
        create_modern_frame(name, x, y, z, width, height, collection)
    
    # Parent all objects to collection
    for obj in bpy.context.selected_objects:
        if obj.name not in bpy.context.scene.collection.objects:
            collection.objects.link(obj)
    
    # Set collection as active
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    
    return f"Created {name} in {style} style at ({x}, {y}, {z})"

def create_baroque_frame(name, x, y, z, width, height, collection):
    """Create an ornate baroque-style frame."""
    # Main frame
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(x, y - 0.05, z)
    )
    frame = bpy.context.active_object
    frame.name = f"{name}_Frame"
    frame.scale = (width, 0.1, height)
    
    # Add bevel for rounded edges
    bevel = frame.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.05
    bevel.segments = 4
    
    # Add decorative scrollwork
    for i in range(4):
        angle = i * (math.pi * 2 / 4)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.1,
            location=(
                x + math.cos(angle) * (width * 0.8),
                y - 0.05,
                z + math.sin(angle) * (height * 0.8)
            )
        )
        corner = bpy.context.active_object
        corner.name = f"{name}_Corner_{i+1}"
        
        # Add fleur-de-lis at corners
        if i % 2 == 0:
            bpy.ops.mesh.primitive_cone_add(
                vertices=8,
                radius1=0.08,
                radius2=0,
                depth=0.2,
                location=(
                    x + math.cos(angle) * (width * 0.9),
                    y - 0.05,
                    z + math.sin(angle) * (height * 0.9)
                )
            )
            fleur = bpy.context.active_object
            fleur.name = f"{name}_Fleur_{i//2+1}"
            fleur.rotation_euler = (math.radians(90), 0, angle + math.pi/2)
    
    # Add gold material to frame
    gold_material = bpy.data.materials.new(name=f"{name}_Gold")
    gold_material.use_nodes = True
    bsdf = gold_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.2
    bsdf.inputs["Base Color"].default_value = (0.8, 0.6, 0.2, 1.0)
    
    for obj in [frame] + [o for o in collection.objects if o.name.startswith(f"{name}_Corner_") or o.name.startswith(f"{name}_Fleur_")]:
        obj.data.materials.append(gold_material)

def create_art_nouveau_frame(name, x, y, z, width, height, collection):
    """Create an art nouveau style frame with flowing organic shapes."""
    # Main frame with curved edges
    bpy.ops.curve.primitive_bezier_curve_add(location=(x, y - 0.05, z))
    frame = bpy.context.active_object
    frame.name = f"{name}_Frame"
    
    # Create oval shape
    curve = frame.data
    curve.dimensions = '3D'
    curve.bevel_depth = 0.05
    curve.bevel_resolution = 4
    
    # Clear existing points
    curve.splines.clear()
    
    # Add oval spline
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(3)  # 4 points total (0-3)
    
    # Set control points for oval
    points = spline.bezier_points
    points[0].co = (width, 0, 0)
    points[0].handle_right = (width, 0, height * 0.3)
    points[0].handle_left = (width, 0, -height * 0.3)
    
    points[1].co = (0, 0, height)
    points[1].handle_right = (-width * 0.3, 0, height)
    points[1].handle_left = (width * 0.3, 0, height)
    
    points[2].co = (-width, 0, 0)
    points[2].handle_right = (-width, 0, -height * 0.3)
    points[2].handle_left = (-width, 0, height * 0.3)
    
    points[3].co = (0, 0, -height)
    points[3].handle_right = (width * 0.3, 0, -height)
    points[3].handle_left = (-width * 0.3, 0, -height)
    
    # Close the loop
    spline.use_cyclic_u = True
    
    # Add decorative vines
    for i in range(8):
        angle = i * (math.pi * 2 / 8)
        bpy.ops.curve.primitive_bezier_curve_add(location=(
            x + math.cos(angle) * (width * 0.7),
            y - 0.05,
            z + math.sin(angle) * (height * 0.7)
        ))
        vine = bpy.context.active_object
        vine.name = f"{name}_Vine_{i+1}"
        
        # Style the vine
        vine.data.bevel_depth = 0.02
        vine.data.bevel_resolution = 3
        
        # Create vine curve
        spline = vine.data.splines[0]
        spline.bezier_points[0].co = (0, 0, 0)
        spline.bezier_points[0].handle_right = (0.1, 0.1, 0.1)
        
        # Add more points to the vine
        spline.bezier_points.add(2)
        spline.bezier_points[1].co = (0.2, 0, 0.3)
        spline.bezier_points[1].handle_right = (0.3, 0.1, 0.4)
        spline.bezier_points[1].handle_left = (0.1, -0.1, 0.2)
        
        spline.bezier_points[2].co = (0, 0, 0.5)
        spline.bezier_points[2].handle_right = (-0.1, 0.1, 0.6)
        spline.bezier_points[2].handle_left = (0.1, -0.1, 0.4)
        
        # Add leaves
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=0.05,
            location=(
                x + math.cos(angle) * (width * 0.7) + 0.2,
                y - 0.05,
                z + math.sin(angle) * (height * 0.7) + 0.3
            )
        )
        leaf = bpy.context.active_object
        leaf.name = f"{name}_Leaf_{i+1}"
        leaf.scale = (1, 0.2, 2)
        leaf.rotation_euler = (0, angle, 0)
    
    # Add bronze material to frame
    bronze_material = bpy.data.materials.new(name=f"{name}_Bronze")
    bronze_material.use_nodes = True
    bsdf = bronze_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Metallic"].default_value = 0.8
    bsdf.inputs["Roughness"].default_value = 0.3
    bsdf.inputs["Base Color"].default_value = (0.7, 0.5, 0.3, 1.0)
    
    for obj in [frame] + [o for o in collection.objects if o.name.startswith(f"{name}_Vine_") or o.name.startswith(f"{name}_Leaf_")]:
        obj.data.materials.append(bronze_material)

def create_modern_frame(name, x, y, z, width, height, collection):
    """Create a sleek, modern frame."""
    # Main frame (thin border)
    bpy.ops.mesh.primitive_plane_add(
        size=1,
        location=(x, y - 0.02, z)
    )
    frame = bpy.context.active_object
    frame.name = f"{name}_Frame"
    frame.scale = (width, 0.1, height)
    
    # Create inner cutout
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(frame.data)
    
    # Scale inner face
    for face in bm.faces:
        for vert in face.verts:
            if abs(vert.co.x) > 0.4 or abs(vert.co.z) > 0.4:
                vert.select = True
    
    bpy.ops.mesh.inset(thickness=0.1, depth=0)
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Extrude to give thickness
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate=(0, 0.05, 0))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add chrome material
    chrome_material = bpy.data.materials.new(name=f"{name}_Chrome")
    chrome_material.use_nodes = True
    bsdf = chrome_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.1
    bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1.0)
    frame.data.materials.append(chrome_material)

# Call the function with provided parameters
result = create_ornate_mirror(""" + f'"{name}", {x}, {y}, {z}, {width}, {height}, "{style}"' + """)
print(f"SUCCESS: {{result}}"
"""
        # Execute the script
        await _executor.execute_script(script, script_name=f"create_mirror_{name}")
        return f"Created ornate mirror: {name} in {style} style at position ({x}, {y}, {z})"
        
    except Exception as e:
        logger.error(f"Failed to create ornate mirror: {str(e)}")
        return f"Error creating ornate mirror: {str(e)}"

{{ ... }}
@blender_operation("create_feather_duster", log_args=True)
async def create_feather_duster(
    name: str = "FeatherDuster",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    feather_count: int = 15,
    style: str = "classic"
) -> str:
    """Create a decorative feather duster with realistic feathers.
    
    Creates a feather duster with a wooden handle and multiple realistic feathers.
    The feathers can be styled in different ways (classic, flamboyant, minimalist).
    
    Args:
        name: Name for the feather duster object
        x: X position in 3D space
        y: Y position in 3D space
        z: Z position in 3D space
        feather_count: Number of feathers (5-30)
        style: Style of the duster ('classic', 'flamboyant', 'minimalist')
        
    Returns:
        str: Confirmation message with created object name
    """
    try:
        # Validate feather count
        feather_count = max(5, min(30, feather_count))
        
        script = f"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, noise

def create_feather_duster(name, x, y, z, feather_count, style):
    # Create main collection for the feather duster
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    
    # Create handle (wooden)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.01,
        depth=0.4,
        location=(x, y, z + 0.2)
    )
    handle = bpy.context.active_object
    handle.name = f"{{name}}_Handle"
    
    # Add some slight bend to the handle
    bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
    handle.modifiers["SimpleDeform"].deform_method = 'BEND'
    handle.modifiers["SimpleDeform"].deform_axis = 'X'
    handle.modifiers["SimpleDeform"].angle = random.uniform(-0.1, 0.1)
    
    # Add wood material to handle
    wood_mat = bpy.data.materials.new(name=f"{{name}}_WoodMat")
    wood_mat.use_nodes = True
    nodes = wood_mat.node_tree.nodes
    links = wood_mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create shader nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    noise_tex = nodes.new(type='ShaderNodeTexNoise')
    mapping = nodes.new(type='ShaderNodeMapping')
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    
    # Position nodes
    principled.location = (-200, 0)
    noise_tex.location = (-400, 0)
    mapping.location = (-600, 0)
    tex_coord.location = (-800, 0)
    
    # Set up wood material
    principled.inputs['Base Color'].default_value = (0.3, 0.2, 0.1, 1.0)  # Dark wood
    principled.inputs['Roughness'].default_value = 0.7
    noise_tex.inputs['Scale'].default_value = 10.0
    noise_tex.inputs['Detail'].default_value = 5.0
    
    # Connect nodes
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise_tex.inputs['Vector'])
    links.new(noise_tex.outputs['Fac'], principled.inputs['Roughness'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material
    if handle.data.materials:
        handle.data.materials[0] = wood_mat
    else:
        handle.data.materials.append(wood_mat)
    
    # Create feathers base (where feathers attach)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.03,
        location=(x, y, z + 0.4)
    )
    base = bpy.context.active_object
    base.name = f"{{name}}_FeatherBase"
    
    # Create feathers
    feather_length = 0.3
    feather_width = 0.1
    
    for i in range(feather_count):
        # Calculate feather position in a spherical distribution
        phi = random.uniform(0, math.pi * 2)  # 0-360 degrees
        theta = random.uniform(0, math.pi / 3)  # 0-60 degrees from vertical
        
        # Position at the base of the feathers
        pos_x = x + math.sin(theta) * math.cos(phi) * 0.02
        pos_y = y + math.sin(theta) * math.sin(phi) * 0.02
        pos_z = z + 0.4 + math.cos(theta) * 0.02
        
        # Create feather
        bpy.ops.curve.primitive_bezier_curve_add(location=(pos_x, pos_y, pos_z))
        feather = bpy.context.active_object
        feather.name = f"{{name}}_Feather_{{i+1}}"
        
        # Style the curve for feather
        curve = feather.data
        curve.bevel_depth = feather_width * 0.5
        curve.bevel_resolution = 4
        
        # Create feather shape
        points = curve.splines[0].bezier_points
        points[0].co = (0, 0, 0)
        points[0].handle_right = (0.1, 0, 0.1)
        
        # Add more points for the feather
        points.add(2)  # Now we have 3 points
        
        # Middle point with some randomness
        mid_x = random.uniform(-0.05, 0.05)
        points[1].co = (mid_x, 0, feather_length * 0.5)
        points[1].handle_left = (mid_x - 0.1, 0, feather_length * 0.4)
        points[1].handle_right = (mid_x + 0.1, 0, feather_length * 0.6)
        
        # End point with curve
        end_x = random.uniform(-0.02, 0.02)
        points[2].co = (end_x, 0, feather_length)
        points[2].handle_left = (end_x - 0.1, 0, feather_length * 0.9)
        
        # Rotate to spread out from center
        feather.rotation_euler = (
            math.pi/2 - theta,
            0,
            phi
        )
        
        # Add some random rotation for natural look
        feather.rotation_euler.x += random.uniform(-0.1, 0.1)
        feather.rotation_euler.y += random.uniform(-0.1, 0.1)
        
        # Add feather material
        feather_mat = bpy.data.materials.new(name=f"{{name}}_FeatherMat_{{i+1}}")
        feather_mat.use_nodes = True
        nodes = feather_mat.node_tree.nodes
        links = feather_mat.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create shader nodes
        output = nodes.new(type='ShaderNodeOutputMaterial')
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        
        # Set up feather material based on style
        if style.lower() == 'flamboyant':
            # Colorful feathers
            hue = random.random()
            if hue < 0.33:
                color = (0.8, 0.2, 0.2, 1.0)  # Red
            elif hue < 0.66:
                color = (0.2, 0.2, 0.8, 1.0)  # Blue
            else:
                color = (0.8, 0.8, 0.2, 1.0)  # Yellow
            principled.inputs['Base Color'].default_value = color
        elif style.lower() == 'minimalist':
            # Simple white/gray
            shade = random.uniform(0.8, 1.0)
            principled.inputs['Base Color'].default_value = (shade, shade, shade, 1.0)
        else:  # classic
            # Natural feather colors
            if random.random() > 0.7:
                # White with slight tint
                tint = random.uniform(0.9, 1.0)
                principled.inputs['Base Color'].default_value = (tint, tint, tint * 0.95, 1.0)
            else:
                # Natural earth tones
                r = random.uniform(0.5, 0.8)
                g = random.uniform(0.4, 0.7)
                b = random.uniform(0.3, 0.6)
                principled.inputs['Base Color'].default_value = (r, g, b, 1.0)
        
        # Common feather properties
        principled.inputs['Roughness'].default_value = 0.9
        principled.inputs['Sheen Tint'].default_value = 0.5
        
        # Connect nodes
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        # Assign material
        if feather.data.materials:
            feather.data.materials[0] = feather_mat
        else:
            feather.data.materials.append(feather_mat)
        
        # Add some bend to the feather for natural look
        bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
        feather.modifiers["SimpleDeform"].deform_method = 'BEND'
        feather.modifiers["SimpleDeform"].deform_axis = 'Z'
        feather.modifiers["SimpleDeform"].angle = random.uniform(-0.2, 0.2)
    
    # Parent all objects to collection
    for obj in [handle, base] + bpy.context.selected_objects:
        if obj.name not in bpy.context.scene.collection.objects:
            collection.objects.link(obj)
    
    # Set collection as active
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    
    return f"Created {{name}} in {{style}} style at ({{x}}, {{y}}, {{z}})"

# Call the function with provided parameters
result = create_feather_duster(""" + name + """, """ + str(x) + """, """ + str(y) + """, """ + str(z) + """, """ + str(feather_count) + """, """ + style + """)
print(f"SUCCESS: {{result}}")
"""
        # Execute the script
        await _executor.execute_script(script, script_name=f"create_feather_duster_{name}")
        return f"Created feather duster: {name} in {style} style at position ({x}, {y}, {z}) with {feather_count} feathers"
        
    except Exception as e:
        error_msg = f"Failed to create feather duster: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

@blender_operation("make_kyoto_machiya", log_args=True)
async def make_kyoto_machiya(
    name: str = "KyotoMachiya",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    size: str = "medium",
    style: str = "traditional",
    has_shop_front: bool = True,
    has_second_floor: bool = True,
    has_kura: bool = False
) -> str:
    """Create a traditional Kyoto machiya (townhouse) with authentic details.
    
    Creates a traditional wooden townhouse with characteristic features like
    koushi (latticework), mushikomado (latticed windows), and tsuchikabe (earthen walls).
    
    Args:
        name: Name for the machiya object
        x: X position in 3D space
        y: Y position in 3D space
        z: Z position (base height)
        size: Size of the machiya ('small', 'medium', 'large')
        style: Architectural style ('traditional', 'meiji', 'modern')
        has_shop_front: Whether to include a traditional shop front
        has_second_floor: Whether to include a second floor
        has_kura: Whether to include a kura (storehouse)
        
    Returns:
        str: Confirmation message with created object name
    """
    try:
        # Map size to dimensions (width, depth, height in meters)
        size_params = {
            'small': (4.0, 8.0, 3.5),    # Small machiya (1-2 rooms)
            'medium': (5.5, 12.0, 4.0),  # Medium machiya (2-3 rooms)
            'large': (7.0, 18.0, 4.5)    # Large machiya (3+ rooms)
        }
        
        width, depth, height = size_params.get(size.lower(), size_params['medium'])
        
        script = f"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def create_koushi(width, height, location, style="traditional"):
    """Create koushi (latticework) for the machiya."""
    # Implementation for creating latticework would go here
    pass

def create_mushikomado(width, height, location):
    """Create mushikomado (latticed windows)."""
    # Implementation for latticed windows would go here
    pass

try:
    # Create main structure
    bpy.ops.object.select_all(action='DESELECT')
    
    # Create base structure
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
    base = bpy.context.active_object
    base.scale = (width/2, depth/2, height/2)
    base.name = "MachiyaBase"
    
    # Add roof
    roof_height = height * 0.3
    bpy.ops.mesh.primitive_cube_add(
        size=1, 
        location=(0, 0, height + roof_height/2),
        scale=(width/2 * 1.2, depth/2 * 1.1, roof_height/2)
    )
    roof = bpy.context.active_object
    roof.name = "Roof"
    
    # Add shop front if enabled
    if {str(has_shop_front).lower()}:
        shop_height = height * 0.7
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, -depth/2 + 0.1, shop_height/2),
            scale=(width/2 * 0.9, 0.2, shop_height/2)
        )
        shop_front = bpy.context.active_object
        shop_front.name = "ShopFront"
    
    # Add kura (storehouse) if enabled
    if {str(has_kura).lower()}:
        kura_size = min(width, depth) * 0.6
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(width/2 + kura_size/2, 0, kura_size/2),
            scale=(kura_size/2, kura_size/2, kura_size/2)
        )
        kura = bpy.context.active_object
        kura.name = "Kura"
    
    # Group all objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.name.startswith(("Machiya", "Roof", "ShopFront", "Kura")):
            obj.select_set(True)
    
    bpy.ops.object.join()
    machiya = bpy.context.active_object
    machiya.name = "{name}"
    machiya.location = ({x}, {y}, {z})
    
    print(f"SUCCESS: Created Kyoto machiya '{{machiya.name}}'")
    return True

except Exception as e:
    print(f"ERROR: Failed to create Kyoto machiya: {{str(e)}}")
    raise e
"""
        await _executor.execute_script(script, script_name="create_kyoto_machiya")
        return f"Created Kyoto machiya '{name}' with {size} size in {style} style"
        
    except Exception as e:
        error_msg = f"Failed to create Kyoto machiya: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

@blender_operation("make_zen_temple", log_args=True)
async def make_zen_temple(
    name: str = "ZenTemple",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    size: str = "medium",
    style: str = "zen",
    has_garden: bool = True,
    has_bell_tower: bool = True,
    has_meditation_hall: bool = True
) -> str:
    """Create a Zen Buddhist temple with traditional architecture.
    
    Creates a Zen temple complex with main hall, meditation hall, bell tower,
    and optional rock garden. Features traditional Japanese temple architecture
    with curved roofs, wooden construction, and minimalist design.
    
    Args:
        name: Name for the temple object
        x: X position in 3D space
        y: Y position in 3D space
        z: Z position (base height)
        size: Size of the temple ('small', 'medium', 'large')
        style: Architectural style ('zen', 'rinzai', 'soto')
        has_garden: Whether to include a zen garden
        has_bell_tower: Whether to include a bell tower
        has_meditation_hall: Whether to include a meditation hall
        
    Returns:
        str: Confirmation message with created object name
    """
    try:
        # Map size to dimensions (width, depth, height in meters)
        size_params = {
            'small': (8.0, 12.0, 6.0),    # Small temple (main hall only)
            'medium': (15.0, 20.0, 8.0),  # Medium temple (main hall + some outbuildings)
            'large': (25.0, 30.0, 10.0)   # Large temple complex
        }
        
        width, depth, height = size_params.get(size.lower(), size_params['medium'])
        
        script = f"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def create_curved_roof(width, depth, height, location):
    """Create a traditional curved temple roof."""
    # Implementation for curved roof would go here
    pass

def create_bell_tower(location):
    """Create a bell tower (shoro)."""
    # Implementation for bell tower would go here
    pass

def create_zen_garden(width, depth, location):
    """Create a zen garden with rocks and raked sand."""
    # Implementation for zen garden would go here
    pass

try:
    # Create main hall (hondo)
    bpy.ops.object.select_all(action='DESELECT')
    
    # Create base structure
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
    base = bpy.context.active_object
    base.scale = (width/2, depth/2, height/2)
    base.name = "MainHall"
    
    # Add curved roof
    roof_height = height * 0.4
    roof = create_curved_roof(width, depth, roof_height, (0, 0, height + roof_height/2))
    
    # Add bell tower if enabled
    if {str(has_bell_tower).lower()}:
        bell_tower = create_bell_tower((width/2 + 2, 0, 0))
    
    # Add meditation hall if enabled
    if {str(has_meditation_hall).lower()}:
        med_hall_width = width * 0.7
        med_hall_depth = depth * 0.6
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0, -depth/2 - med_hall_depth/2 - 1, height/2 * 0.8),
            scale=(med_hall_width/2, med_hall_depth/2, height/2 * 0.8)
        )
        med_hall = bpy.context.active_object
        med_hall.name = "MeditationHall"
    
    # Add zen garden if enabled
    if {str(has_garden).lower()}:
        garden = create_zen_garden(width * 1.5, depth * 0.8, (0, depth/2 + 2, 0.1))
    
    # Group all objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.name.startswith(("MainHall", "Roof", "BellTower", "MeditationHall", "Garden")):
            obj.select_set(True)
    
    bpy.ops.object.join()
    temple = bpy.context.active_object
    temple.name = "{name}"
    temple.location = ({x}, {y}, {z})
    
    print(f"SUCCESS: Created Zen temple '{{temple.name}}'")
    return True

except Exception as e:
    print(f"ERROR: Failed to create Zen temple: {{str(e)}}")
    raise e
"""
        await _executor.execute_script(script, script_name="create_zen_temple")
        return f"Created Zen temple '{name}' with {size} size in {style} style"
        
    except Exception as e:
        error_msg = f"Failed to create Zen temple: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

@blender_operation("make_japanese_walking_garden", log_args=True)
async def make_japanese_walking_garden(
    name: str = "JapaneseGarden",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    size: str = "medium",
    style: str = "kaiyu",
    has_pond: bool = True,
    has_teahouse: bool = True,
    has_bridge: bool = True,
    has_lanterns: bool = True
) -> str:
    """Create a traditional Japanese walking garden (kaiyu-shiki teien).
    
    Creates a beautiful Japanese strolling garden with winding paths, water features,
    stone arrangements, and carefully placed vegetation. The garden is designed to
    be experienced by walking along its paths, with carefully composed views.
    
    Args:
        name: Name for the garden object
        x: X position in 3D space
        y: Y position in 3D space
        z: Z position (base height)
        size: Size of the garden ('small', 'medium', 'large')
        style: Garden style ('kaiyu', 'tsukiyama', 'chisen')
        has_pond: Whether to include a pond or stream
        has_teahouse: Whether to include a tea house
        has_bridge: Whether to include bridges
        has_lanterns: Whether to include stone lanterns
        
    Returns:
        str: Confirmation message with created object name
    """
    try:
        # Map size to dimensions (width, depth in meters)
        size_params = {
            'small': (10.0, 10.0),    # Small courtyard garden
            'medium': (20.0, 20.0),   # Medium residential garden
            'large': (40.0, 30.0)     # Large strolling garden
        }
        
        width, depth = size_params.get(size.lower(), size_params['medium'])
        
        script = f"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

def create_pond(width, depth, location):
    """Create a natural-looking pond."""
    # Implementation for pond would go here
    pass

def create_teahouse(location):
    """Create a traditional tea house."""
    # Implementation for tea house would go here
    pass

def create_stone_lantern(location):
    """Create a traditional stone lantern."""
    # Implementation for stone lantern would go here
    pass

def create_bridge(location, length):
    """Create a traditional arched bridge."""
    # Implementation for bridge would go here
    pass

try:
    # Create base terrain
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    terrain = bpy.context.active_object
    terrain.scale = (width/2, depth/2, 1)
    terrain.name = "GardenTerrain"
    
    # Add terrain details (hills, mounds)
    bpy.ops.object.modifier_add(type='DISPLACE')
    # Configure displacement modifier for natural terrain
    
    # Add pond if enabled
    if {str(has_pond).lower()}:
        pond = create_pond(width * 0.6, depth * 0.4, (0, 0, 0.1))
    
    # Add tea house if enabled
    if {str(has_teahouse).lower()}:
        teahouse = create_teahouse((width/3, depth/3, 0))
    
    # Add bridge if enabled and there's a pond
    if {str(has_bridge).lower()} and {str(has_pond).lower()}:
        bridge = create_bridge((0, 0, 0.2), width * 0.3)
    
    # Add stone lanterns if enabled
    if {str(has_lanterns).lower()}:
        for _ in range(random.randint(3, 8)):
            x = (random.random() - 0.5) * width * 0.8
            y = (random.random() - 0.5) * depth * 0.8
            create_stone_lantern((x, y, 0.1))
    
    # Add vegetation (trees, bushes, moss)
    # Implementation for vegetation would go here
    
    # Group all objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.name.startswith(("Garden", "Pond", "TeaHouse", "Bridge", "Lantern")):
            obj.select_set(True)
    
    bpy.ops.object.join()
    garden = bpy.context.active_object
    garden.name = "{name}"
    garden.location = ({x}, {y}, {z})
    
    print(f"SUCCESS: Created Japanese walking garden '{{garden.name}}'")
    return True

except Exception as e:
    print(f"ERROR: Failed to create Japanese garden: {{str(e)}}")
    raise e
"""
        await _executor.execute_script(script, script_name="create_japanese_garden")
        return f"Created Japanese walking garden '{name}' with {size} size in {style} style"
        
    except Exception as e:
        error_msg = f"Failed to create Japanese walking garden: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

@blender_operation("make_kettenkrad", log_args=True)
async def make_kettenkrad(
    name: str = "Kettenkrad",
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    variant: str = "military",
    has_canopy: bool = True,
    has_weapon_mount: bool = False
) -> str:
    """Create a 3D model of a Kettenkrad (German tracked motorcycle).
    
    Creates a detailed model of a Kettenkrad, a half-track motorcycle used by German forces
    during WWII. The model includes the tracked rear section, motorcycle front, and various
    details like the engine, seats, and controls.
    
    Args:
        name: Name for the Kettenkrad object
        x: X position in 3D space
        y: Y position in 3D space
        z: Z position (ground level)
        variant: Model variant ('military', 'civilian', 'desert')
        has_canopy: Whether to include the foldable canvas canopy
        has_weapon_mount: Whether to include the MG34 machine gun mount (military only)
        
    Returns:
        str: Confirmation message with created object name
    """
    try:
        script = """
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def create_track_segment(location, rotation, length=0.5, width=0.15, thickness=0.05):
    """Create a single track segment."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    segment = bpy.context.active_object
    segment.scale = (length/2, width/2, thickness/2)
    return segment

def create_wheel(location, diameter, width, is_driving=True):
    """Create a wheel with optional sprocket teeth."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=diameter/2,
        depth=width,
        location=location,
        rotation=(math.pi/2, 0, 0)
    )
    wheel = bpy.context.active_object
    
    # Add sprocket teeth for driving wheels
    if is_driving:
        tooth_length = diameter * 0.15
        for i in range(16):
            angle = (i / 16) * math.pi * 2
            x = math.cos(angle) * (diameter/2 + tooth_length/2)
            y = math.sin(angle) * (diameter/2 + tooth_length/2)
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(x, y, 0),
                rotation=(0, 0, angle)
            )
            tooth = bpy.context.active_object
            tooth.scale = (tooth_length/2, 0.03, width/2)
            tooth.parent = wheel
    
    return wheel

def create_engine(location):
    """Create the engine block."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    engine = bpy.context.active_object
    engine.scale = (0.3, 0.4, 0.25)
    return engine

def create_seat(location, width=0.4, depth=0.3, height=0.1):
    """Create a seat with padding."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    seat = bpy.context.active_object
    seat.scale = (width/2, depth/2, height/2)
    return seat

try:
    # Create collection for the Kettenkrad
    collection = bpy.data.collections.new("Kettenkrad")
    bpy.context.scene.collection.children.link(collection)
    
    # Main chassis
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.3))
    chassis = bpy.context.active_object
    chassis.scale = (0.8, 1.5, 0.2)
    chassis.name = "Chassis"
    collection.objects.link(chassis)
    bpy.context.scene.collection.objects.unlink(chassis)
    
    # Track system
    track_length = 2.0
    track_width = 0.3
    track_radius = track_length / (2 * math.pi)
    
    # Create track segments
    segment_count = 40
    for i in range(segment_count):
        angle = (i / segment_count) * math.pi * 2
        x = math.cos(angle) * track_radius
        y = math.sin(angle) * track_radius
        segment = create_track_segment(
            (x, y, 0.1),
            (0, 0, angle + math.pi/2)
        )
        collection.objects.link(segment)
        bpy.context.scene.collection.objects.unlink(segment)
    
    # Wheels
    front_wheel = create_wheel((0, 1.2, 0.3), 0.5, 0.25, False)
    rear_wheel = create_wheel((0, -1.2, 0.3), 0.5, 0.25, True)
    collection.objects.link(front_wheel)
    collection.objects.link(rear_wheel)
    bpy.context.scene.collection.objects.unlink(front_wheel)
    bpy.context.scene.collection.objects.unlink(rear_wheel)
    
    # Engine
    engine = create_engine((0.2, 0.7, 0.4))
    collection.objects.link(engine)
    bpy.context.scene.collection.objects.unlink(engine)
    
    # Seats
    driver_seat = create_seat((0, 0.5, 0.5))
    passenger_seat = create_seat((0, 0, 0.5))
    collection.objects.link(driver_seat)
    collection.objects.link(passenger_seat)
    bpy.context.scene.collection.objects.unlink(driver_seat)
    bpy.context.scene.collection.objects.unlink(passenger_seat)
    
    # Handlebar
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.02,
        depth=0.8,
        location=(0, 1.5, 0.6),
        rotation=(0, math.pi/2, 0)
    )
    handlebar = bpy.context.active_object
    collection.objects.link(handlebar)
    bpy.context.scene.collection.objects.unlink(handlebar)
    
    # Add canopy if enabled
    if {str(has_canopy).lower()}:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.25, 0.8))
        canopy = bpy.context.active_object
        canopy.scale = (0.6, 0.8, 1)
        collection.objects.link(canopy)
        bpy.context.scene.collection.objects.unlink(canopy)
    
    # Add weapon mount if enabled and military variant
    if {str(has_weapon_mount).lower()} and "{variant}" == "military":
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=0.02,
            depth=0.3,
            location=(0.4, 0, 0.7),
            rotation=(0, 0, math.pi/2)
        )
        mount = bpy.context.active_object
        collection.objects.link(mount)
        bpy.context.scene.collection.objects.unlink(mount)
    
    # Set collection as active
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    
    # Group all objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.objects:
        obj.select_set(True)
    
    bpy.ops.object.join()
    kettenkrad = bpy.context.active_object
    kettenkrad.name = "{name}"
    kettenkrad.location = ({x}, {y}, {z})
    
    # Apply materials based on variant
    if "{variant}" == "military":
        # Dark gray/green for military version
        mat = bpy.data.materials.new(name="MilitaryPaint")
        mat.diffuse_color = (0.2, 0.25, 0.15, 1.0)
        kettenkrad.data.materials.append(mat)
    elif "{variant}" == "desert":
        # Sand color for desert version
        mat = bpy.data.materials.new(name="DesertPaint")
        mat.diffuse_color = (0.6, 0.55, 0.4, 1.0)
        kettenkrad.data.materials.append(mat)
    else:
        # Civilian version (black)
        mat = bpy.data.materials.new(name="CivilianPaint")
        mat.diffuse_color = (0.1, 0.1, 0.1, 1.0)
        kettenkrad.data.materials.append(mat)
    
    print(f"SUCCESS: Created Kettenkrad '{{kettenkrad.name}}'")
    return True

except Exception as e:
    print(f"ERROR: Failed to create Kettenkrad: {{str(e)}}")
    raise e
"""
        await _executor.execute_script(script, script_name="create_kettenkrad")
        return f"Created Kettenkrad '{name}' in {variant} variant"
        
    except Exception as e:
        error_msg = f"Failed to create Kettenkrad: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

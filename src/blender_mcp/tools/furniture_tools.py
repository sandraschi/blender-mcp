""
Furniture Creation Tools for Blender MCP

This module provides functions to create various furniture items in Blender.
"""

import bpy
import bmesh
from mathutils import Vector, Matrix
from math import radians

def create_basic_chair(name="Chair", location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    """Create a basic chair using Blender's bmesh.
    
    Args:
        name: Name for the chair object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        
    Returns:
        The created chair object
    """
    # Clear existing mesh data if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    
    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Chair dimensions (in meters)
    seat_height = 0.45
    seat_width = 0.5
    seat_depth = 0.5
    leg_thickness = 0.05
    backrest_height = 0.4
    
    # Create seat (a simple cube)
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, 0, seat_height/2 + leg_thickness/2),
            None,
            (seat_width, seat_depth, leg_thickness)
        )
    )
    
    # Create legs
    leg_positions = [
        ( seat_width/2 - leg_thickness/2,  seat_depth/2 - leg_thickness/2, 0),
        (-seat_width/2 + leg_thickness/2,  seat_depth/2 - leg_thickness/2, 0),
        ( seat_width/2 - leg_thickness/2, -seat_depth/2 + leg_thickness/2, 0),
        (-seat_width/2 + leg_thickness/2, -seat_depth/2 + leg_thickness/2, 0)
    ]
    
    for pos in leg_positions:
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                (pos[0], pos[1], seat_height/2),
                None,
                (leg_thickness, leg_thickness, seat_height)
            )
        )
    
    # Create backrest
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, -seat_depth/2 + leg_thickness/2, seat_height + backrest_height/2),
            None,
            (seat_width * 0.9, leg_thickness, backrest_height)
        )
    )
    
    # Update the mesh with the new geometry
    bm.to_mesh(mesh)
    bm.free()
    
    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale
    
    # Add smooth shading
    for face in obj.data.polygons:
        face.use_smooth = True
    
    # Add a subdivision surface modifier for smoother appearance
    mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod.levels = 2
    mod.render_levels = 2
    
    # Add a bevel modifier for rounded edges
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.01
    bevel.segments = 3
    bevel.limit_method = 'ANGLE'
    
    return obj

# ============================================================================
# Material Functions
# ============================================================================

def create_wood_material(name, color, roughness=0.7, specular=0.3):
    """Create a wood material with grain texture."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    mapping = nodes.new('ShaderNodeMapping')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    
    # Configure nodes
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Specular'].default_value = specular
    
    noise.inputs['Scale'].default_value = 10.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.9
    
    color_ramp.color_ramp.elements[0].color = tuple(c * 0.8 for c in color[:3]) + (1.0,)
    color_ramp.color_ramp.elements[1].color = color
    
    mapping.inputs['Scale'].default_value = (1.0, 3.0, 1.0)
    
    # Connect nodes
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], shader.inputs['Base Color'])
    links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_metal_material(name, color, roughness=0.2, metallic=1.0):
    """Create a metal material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Configure nodes
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    
    # Connect nodes
    links = mat.node_tree.links
    links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_fabric_material(name, color, roughness=0.9, specular=0.2):
    """Create a fabric material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    
    # Configure nodes
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Specular'].default_value = specular
    
    noise.inputs['Scale'].default_value = 50.0
    noise.inputs['Detail'].default_value = 2.0
    
    # Connect nodes
    links = mat.node_tree.links
    links.new(noise.outputs['Fac'], shader.inputs['Roughness'])
    links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def apply_material(obj, name, color, material_type="wood"):
    """Apply a material to an object.
    
    Args:
        obj: The object to apply the material to
        name: Name for the material
        color: RGBA color tuple (0-1)
        material_type: Type of material (wood, metal, fabric, plastic, glass)
    """
    # Create material based on type
    mat_name = f"{name}_{material_type}"
    
    if material_type.lower() == "wood":
        mat = create_wood_material(mat_name, color)
    elif material_type.lower() == "metal":
        mat = create_metal_material(mat_name, color)
    elif material_type.lower() == "fabric":
        mat = create_fabric_material(mat_name, color)
    elif material_type.lower() == "glass":
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes["Principled BSDF"].inputs["Base Color"].default_value = color
        nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.1
        nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 1.45
        nodes["Principled BSDF"].inputs["Transmission"].default_value = 0.9
        nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.05
    else:  # Default to plastic
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes["Principled BSDF"].inputs["Base Color"].default_value = color
        nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.3
        nodes["Principled BSDF"].inputs["Specular"].default_value = 0.5
    
    # Apply material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    return mat
    # Create material
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # Get the material output node
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create shader nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    
    # Different shader based on material type
    if material_type.lower() == "wood":
        # Simple wood-like shader
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        shader.inputs['Base Color'].default_value = color
        shader.inputs['Roughness'].default_value = 0.7
        shader.inputs['Specular'].default_value = 0.3
        
        # Add some wood grain using a noise texture
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 20.0
        noise.inputs['Detail'].default_value = 8.0
        noise.inputs['Roughness'].default_value = 0.9
        
        color_ramp = nodes.new('ShaderNodeValToRGB')
        color_ramp.color_ramp.elements[0].color = (0.5, 0.3, 0.1, 1.0)
        color_ramp.color_ramp.elements[1].color = (0.8, 0.6, 0.4, 1.0)
        
        mapping = nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (1.0, 3.0, 1.0)
        
        tex_coord = nodes.new('ShaderNodeTexCoord')
        
        # Connect nodes
        links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
        links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], shader.inputs['Base Color'])
        
    else:
        # Default to simple principled shader
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        shader.inputs['Base Color'].default_value = color
    
    # Connect to output
    links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    
    # Apply material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    return mat

# ============================================================================
# Furniture Creation Functions
# ============================================================================

def create_basic_table(
    name="Table",
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    scale=(1, 1, 1),
    table_type="dining",
    length=1.2,
    width=0.8,
    height=0.75,
    thickness=0.05,
    leg_thickness=0.05,
    leg_height=0.7
):
    """Create a basic table with legs.
    
    Args:
        name: Name for the table object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        table_type: Type of table (dining, coffee, side, etc.)
        length: Length of the table top
        width: Width of the table top
        height: Thickness of the table top
        thickness: Thickness of the table top edges
        leg_thickness: Thickness of the legs
        leg_height: Height of the legs
    """
    # Clear existing mesh data if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    
    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Create table top (a flat cuboid)
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, 0, height/2 + leg_height),
            None,
            (length, width, height)
        )
    )
    
    # Create legs
    leg_positions = [
        ( length/2 - leg_thickness,  width/2 - leg_thickness, leg_height/2),
        (-length/2 + leg_thickness,  width/2 - leg_thickness, leg_height/2),
        ( length/2 - leg_thickness, -width/2 + leg_thickness, leg_height/2),
        (-length/2 + leg_thickness, -width/2 + leg_thickness, leg_height/2)
    ]
    
    for pos in leg_positions:
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                pos,
                None,
                (leg_thickness, leg_thickness, leg_height)
            )
        )
    
    # Update the mesh with the new geometry
    bm.to_mesh(mesh)
    bm.free()
    
    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale
    
    # Add smooth shading
    for face in obj.data.polygons:
        face.use_smooth = True
    
    # Add modifiers
    mod = obj.modifiers.new(name="Edge Split", type='EDGE_SPLIT')
    mod.split_angle = 1.0472  # 60 degrees in radians
    
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.01
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'
    
    return obj

def create_basic_bed(
    name="Bed",
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    scale=(1, 1, 1),
    bed_type="double",
    length=2.0,
    width=1.5,
    height=0.4,
    headboard_height=0.8,
    footboard_height=0.4,
    has_footboard=True,
    has_headboard=True
):
    """Create a basic bed with optional headboard and footboard.
    
    Args:
        name: Name for the bed object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        bed_type: Type of bed (single, double, king, queen)
        length: Length of the bed
        width: Width of the bed
        height: Height of the mattress
        headboard_height: Height of the headboard
        footboard_height: Height of the footboard
        has_headboard: Whether to include a headboard
        has_footboard: Whether to include a footboard
    """
    # Clear existing mesh data if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    
    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Create mattress (a flat cuboid)
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, 0, height/2),
            None,
            (length, width, height)
        )
    )
    
    # Create bed frame
    frame_thickness = 0.1
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, 0, -frame_thickness/2),
            None,
            (length + frame_thickness*2, width + frame_thickness*2, frame_thickness)
        )
    )
    
    # Create headboard if specified
    if has_headboard:
        headboard_thickness = 0.05
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                (0, width/2 + headboard_thickness/2, headboard_height/2),
                None,
                (length, headboard_thickness, headboard_height)
            )
        )
    
    # Create footboard if specified
    if has_footboard:
        footboard_thickness = 0.05
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                (0, -width/2 - footboard_thickness/2, footboard_height/2),
                None,
                (length, footboard_thickness, footboard_height)
            )
        )
    
    # Create bed legs
    leg_thickness = 0.05
    leg_height = 0.1
    leg_positions = [
        ( length/2 - leg_thickness,  width/2 - leg_thickness, -frame_thickness - leg_height/2),
        (-length/2 + leg_thickness,  width/2 - leg_thickness, -frame_thickness - leg_height/2),
        ( length/2 - leg_thickness, -width/2 + leg_thickness, -frame_thickness - leg_height/2),
        (-length/2 + leg_thickness, -width/2 + leg_thickness, -frame_thickness - leg_height/2)
    ]
    
    for pos in leg_positions:
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                pos,
                None,
                (leg_thickness, leg_thickness, leg_height)
            )
        )
    
    # Update the mesh with the new geometry
    bm.to_mesh(mesh)
    bm.free()
    
    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale
    
    # Add smooth shading
    for face in obj.data.polygons:
        face.use_smooth = True
    
    # Add modifiers
    mod = obj.modifiers.new(name="Edge Split", type='EDGE_SPLIT')
    mod.split_angle = 1.0472  # 60 degrees in radians
    
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.01
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'
    
    return obj

def create_basic_sofa(
    name="Sofa",
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    scale=(1, 1, 1),
    length=1.8,
    width=0.9,
    height=0.8,
    seat_height=0.4,
    back_height=0.5,
    cushion_count=3
):
    """Create a basic sofa with cushions.
    
    Args:
        name: Name for the sofa object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        length: Length of the sofa
        width: Width of the sofa
        height: Total height of the sofa
        seat_height: Height of the seat from the ground
        back_height: Height of the backrest
        cushion_count: Number of seat cushions
    """
    # Clear existing mesh data if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    
    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Create base frame
    frame_thickness = 0.1
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, 0, seat_height/2),
            None,
            (length, width, seat_height)
        )
    )
    
    # Create backrest
    back_thickness = 0.15
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, -width/2 + back_thickness/2, seat_height + back_height/2),
            None,
            (length, back_thickness, back_height)
        )
    )
    
    # Create armrests
    armrest_width = 0.2
    armrest_height = 0.6
    armrest_positions = [
        (0, width/2 - armrest_width/2, seat_height + armrest_height/2),
        (0, -width/2 + armrest_width/2, seat_height + armrest_height/2)
    ]
    
    for pos in armrest_positions:
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                pos,
                None,
                (length, armrest_width, armrest_height)
            )
        )
    
    # Create legs
    leg_thickness = 0.05
    leg_height = 0.1
    leg_positions = [
        ( length/2 - leg_thickness,  width/2 - leg_thickness, -leg_height/2),
        (-length/2 + leg_thickness,  width/2 - leg_thickness, -leg_height/2),
        ( length/2 - leg_thickness, -width/2 + leg_thickness, -leg_height/2),
        (-length/2 + leg_thickness, -width/2 + leg_thickness, -leg_height/2)
    ]
    
    for pos in leg_positions:
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                pos,
                None,
                (leg_thickness, leg_thickness, leg_height)
            )
        )
    
    # Update the mesh with the new geometry
    bm.to_mesh(mesh)
    bm.free()
    
    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale
    
    # Add smooth shading
    for face in obj.data.polygons:
        face.use_smooth = True
    
    # Add modifiers
    mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod.levels = 2
    mod.render_levels = 2
    
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.01
    bevel.segments = 3
    bevel.limit_method = 'ANGLE'
    
    return obj

def create_simple_house(
    name="House",
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    scale=(1, 1, 1),
    width=5.0,
    depth=6.0,
    height=3.0,
    roof_height=2.0,
    wall_thickness=0.2,
    has_chimney=True,
    has_door=True,
    has_windows=True
):
    """Create a simple house structure.
    
    Args:
        name: Name for the house object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        width: Width of the house
        depth: Depth of the house
        height: Height of the walls
        roof_height: Height of the roof
        wall_thickness: Thickness of the walls
        has_chimney: Whether to add a chimney
        has_door: Whether to add a door
        has_windows: Whether to add windows
    """
    # Clear existing mesh data if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    
    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Create walls
    # Outer walls
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, 0, height/2),
            None,
            (width, depth, height)
        )
    )
    
    # Inner space (to create hollow walls)
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, 0, height/2 + wall_thickness),
            None,
            (width - wall_thickness*2, depth - wall_thickness*2, height)
        )
    )
    
    # Create roof
    roof_vertices = [
        (-width/2, -depth/2, height),
        (width/2, -depth/2, height),
        (width/2, depth/2, height),
        (-width/2, depth/2, height),
        (0, 0, height + roof_height)
    ]
    
    roof_faces = [
        (0, 1, 4),  # Front face
        (1, 2, 4),  # Right face
        (2, 3, 4),  # Back face
        (3, 0, 4)   # Left face
    ]
    
    # Add roof vertices and faces
    verts = [bm.verts.new(v) for v in roof_vertices]
    bm.faces.new([verts[i] for i in [0, 1, 2, 3]])  # Base
    
    for face in roof_faces:
        bm.faces.new([verts[i] for i in face])
    
    # Create chimney if specified
    if has_chimney:
        chimney_width = 0.3
        chimney_depth = 0.4
        chimney_height = 1.0
        
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                (width/4, 0, height + chimney_height/2),
                None,
                (chimney_width, chimney_depth, chimney_height)
            )
        )
    
    # Create door if specified
    if has_door:
        door_width = 0.9
        door_height = 2.0
        door_thickness = wall_thickness * 1.1
        
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                (0, -depth/2, door_height/2),
                None,
                (door_width, door_thickness, door_height)
            )
        )
    
    # Create windows if specified
    if has_windows:
        window_width = 0.8
        window_height = 0.6
        window_thickness = wall_thickness * 1.1
        
        window_positions = [
            (width/3, -depth/2, height/2),      # Front right
            (-width/3, -depth/2, height/2),     # Front left
            (width/2, 0, height/2),             # Right side
            (-width/2, 0, height/2)             # Left side
        ]
        
        for pos in window_positions:
            bmesh.ops.create_cube(
                bm,
                size=1,
                matrix=Matrix.LocRotScale(
                    (pos[0], pos[1] if abs(pos[1]) > 0.1 else (depth/2 * (1 if pos[1] >= 0 else -1)), pos[2]),
                    None,
                    (window_width, window_thickness, window_height)
                )
            )
    
    # Update the mesh with the new geometry
    bm.to_mesh(mesh)
    bm.free()
    
    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale
    
    # Add smooth shading
    for face in obj.data.polygons:
        face.use_smooth = True
    
    return obj

def create_room(
    name="Room",
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    scale=(1, 1, 1),
    room_type="living",
    length=5.0,
    width=4.0,
    height=2.7,
    wall_thickness=0.2,
    has_ceiling=True,
    has_floor=True,
    has_door=True,
    has_windows=True,
    window_count=2
):
    """Create a room with walls, floor, and ceiling.
    
    Args:
        name: Name for the room object
        location: (x, y, z) location in world space
        rotation: (x, y, z) rotation in degrees
        scale: (x, y, z) scale factors
        room_type: Type of room (living, bedroom, kitchen, etc.)
        length: Length of the room
        width: Width of the room
        height: Height of the room
        wall_thickness: Thickness of the walls
        has_ceiling: Whether to add a ceiling
        has_floor: Whether to add a floor
        has_door: Whether to add a door
        has_windows: Whether to add windows
        window_count: Number of windows to add
    """
    # Clear existing mesh data if it exists
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    
    # Create a new mesh and link it to the scene
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Create floor if specified
    if has_floor:
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                (0, 0, -wall_thickness/2),
                None,
                (length + wall_thickness*2, width + wall_thickness*2, wall_thickness)
            )
        )
    
    # Create walls
    wall_height = height
    wall_length = length
    wall_width = width
    
    # Front wall
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, -width/2, wall_height/2),
            None,
            (wall_length, wall_thickness, wall_height)
        )
    )
    
    # Back wall
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (0, width/2, wall_height/2),
            None,
            (wall_length, wall_thickness, wall_height)
        )
    )
    
    # Left wall
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (-length/2, 0, wall_height/2),
            None,
            (wall_thickness, wall_width, wall_height)
        )
    )
    
    # Right wall
    bmesh.ops.create_cube(
        bm,
        size=1,
        matrix=Matrix.LocRotScale(
            (length/2, 0, wall_height/2),
            None,
            (wall_thickness, wall_width, wall_height)
        )
    )
    
    # Create ceiling if specified
    if has_ceiling:
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                (0, 0, wall_height + wall_thickness/2),
                None,
                (length + wall_thickness*2, width + wall_thickness*2, wall_thickness)
            )
        )
    
    # Create door if specified
    if has_door:
        door_width = 0.9
        door_height = 2.0
        door_thickness = wall_thickness * 1.1
        
        # Create door opening in the front wall
        bmesh.ops.create_cube(
            bm,
            size=1,
            matrix=Matrix.LocRotScale(
                (0, -width/2, door_height/2),
                None,
                (door_width, door_thickness, door_height)
            )
        )
    
    # Create windows if specified
    if has_windows and window_count > 0:
        window_width = 1.2
        window_height = 0.8
        window_sill_height = 1.0
        window_thickness = wall_thickness * 1.1
        
        # Calculate window positions
        window_spacing = length / (window_count + 1)
        
        for i in range(window_count):
            x_pos = -length/2 + (i + 1) * window_spacing
            
            # Create window opening
            bmesh.ops.create_cube(
                bm,
                size=1,
                matrix=Matrix.LocRotScale(
                    (x_pos, width/2, window_sill_height + window_height/2),
                    None,
                    (window_width, window_thickness, window_height)
                )
            )
    
    # Update the mesh with the new geometry
    bm.to_mesh(mesh)
    bm.free()
    
    # Set object location, rotation, and scale
    obj.location = location
    obj.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    obj.scale = scale
    
    # Add smooth shading
    for face in obj.data.polygons:
        face.use_smooth = True
    
    return obj

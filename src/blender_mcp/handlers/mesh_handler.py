"""
Mesh creation and manipulation handler for Blender MCP.

Provides functions for creating basic mesh primitives and manipulating mesh objects.
"""

from typing import Tuple, Optional
from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation
from ..exceptions import BlenderMeshError

_executor = get_blender_executor()


@blender_operation("create_cube")
async def create_cube(
    name: str = "Cube",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1)
) -> str:
    """
    Create a cube primitive.

    Args:
        name: Name for the cube object
        location: Position coordinates (x, y, z)
        scale: Scale factors (x, y, z)

    Returns:
        Success message
    """
    script = f"""
import bpy

# Create cube
bpy.ops.mesh.primitive_cube_add(location={location}, scale={scale})
obj = bpy.context.active_object
obj.name = "{name}"

print(f"Created cube: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created cube '{name}' at {location}"


@blender_operation("create_sphere")
async def create_sphere(
    name: str = "Sphere",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1),
    radius: float = 1.0,
    segments: int = 32,
    rings: int = 16
) -> str:
    """
    Create a sphere primitive.

    Args:
        name: Name for the sphere object
        location: Position coordinates (x, y, z)
        scale: Scale factors (x, y, z)
        radius: Sphere radius
        segments: Number of horizontal segments
        rings: Number of vertical rings

    Returns:
        Success message
    """
    script = f"""
import bpy

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    location={location},
    scale={scale},
    radius={radius},
    segments={segments},
    ring_count={rings}
)
obj = bpy.context.active_object
obj.name = "{name}"

print(f"Created sphere: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created sphere '{name}' at {location}"


@blender_operation("create_cylinder")
async def create_cylinder(
    name: str = "Cylinder",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1),
    radius: float = 1.0,
    depth: float = 2.0,
    vertices: int = 32
) -> str:
    """
    Create a cylinder primitive.

    Args:
        name: Name for the cylinder object
        location: Position coordinates (x, y, z)
        scale: Scale factors (x, y, z)
        radius: Cylinder radius
        depth: Cylinder height
        vertices: Number of vertices

    Returns:
        Success message
    """
    script = f"""
import bpy

# Create cylinder
bpy.ops.mesh.primitive_cylinder_add(
    location={location},
    scale={scale},
    radius={radius},
    depth={depth},
    vertices={vertices}
)
obj = bpy.context.active_object
obj.name = "{name}"

print(f"Created cylinder: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created cylinder '{name}' at {location}"


@blender_operation("create_cone")
async def create_cone(
    name: str = "Cone",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1),
    radius1: float = 1.0,
    depth: float = 2.0,
    vertices: int = 32
) -> str:
    """
    Create a cone primitive.

    Args:
        name: Name for the cone object
        location: Position coordinates (x, y, z)
        scale: Scale factors (x, y, z)
        radius1: Cone base radius
        depth: Cone height
        vertices: Number of vertices

    Returns:
        Success message
    """
    script = f"""
import bpy

# Create cone
bpy.ops.mesh.primitive_cone_add(
    location={location},
    scale={scale},
    radius1={radius1},
    depth={depth},
    vertices={vertices}
)
obj = bpy.context.active_object
obj.name = "{name}"

print(f"Created cone: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created cone '{name}' at {location}"


@blender_operation("create_plane")
async def create_plane(
    name: str = "Plane",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1)
) -> str:
    """
    Create a plane primitive.

    Args:
        name: Name for the plane object
        location: Position coordinates (x, y, z)
        scale: Scale factors (x, y, z)

    Returns:
        Success message
    """
    script = f"""
import bpy

# Create plane
bpy.ops.mesh.primitive_plane_add(location={location}, scale={scale})
obj = bpy.context.active_object
obj.name = "{name}"

print(f"Created plane: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created plane '{name}' at {location}"


@blender_operation("create_torus")
async def create_torus(
    name: str = "Torus",
    location: Tuple[float, float, float] = (0, 0, 0),
    major_radius: float = 1.0,
    minor_radius: float = 0.25
) -> str:
    """
    Create a torus primitive.

    Args:
        name: Name for the torus object
        location: Position coordinates (x, y, z)
        major_radius: Major radius (distance from center to tube center)
        minor_radius: Minor radius (tube radius)

    Returns:
        Success message
    """
    script = f"""
import bpy

# Create torus
bpy.ops.mesh.primitive_torus_add(
    location={location},
    major_radius={major_radius},
    minor_radius={minor_radius}
)
obj = bpy.context.active_object
obj.name = "{name}"

print(f"Created torus: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created torus '{name}' at {location}"


@blender_operation("create_monkey")
async def create_monkey(
    name: str = "Suzanne",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1)
) -> str:
    """
    Create Suzanne (monkey) primitive.

    Args:
        name: Name for the monkey object
        location: Position coordinates (x, y, z)
        scale: Scale factors (x, y, z)

    Returns:
        Success message
    """
    script = f"""
import bpy

# Create monkey
bpy.ops.mesh.primitive_monkey_add(location={location}, scale={scale})
obj = bpy.context.active_object
obj.name = "{name}"

print(f"Created Suzanne: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created Suzanne '{name}' at {location}"


@blender_operation("duplicate_object")
async def duplicate_object(
    source_name: str,
    new_name: str
) -> str:
    """
    Duplicate an existing object.

    Args:
        source_name: Name of object to duplicate
        new_name: Name for the duplicated object

    Returns:
        Success message
    """
    script = f"""
import bpy

# Find source object
obj = bpy.data.objects.get("{source_name}")
if not obj:
    raise ValueError(f"Object '{{source_name}}' not found")

# Select and duplicate
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.duplicate()

# Rename duplicate
dup_obj = bpy.context.active_object
dup_obj.name = "{new_name}"

print(f"Duplicated object: {new_name}")
"""
    result = await _executor.execute_script(script)
    return f"Duplicated '{source_name}' as '{new_name}'"


@blender_operation("delete_object")
async def delete_object(name: str) -> str:
    """
    Delete an object by name.

    Args:
        name: Name of object to delete

    Returns:
        Success message
    """
    script = f"""
import bpy

# Find and delete object
obj = bpy.data.objects.get("{name}")
if obj:
    bpy.data.objects.remove(obj)
    print(f"Deleted object: {name}")
else:
    raise ValueError(f"Object '{name}' not found")
"""
    result = await _executor.execute_script(script)
    return f"Deleted object '{name}'"
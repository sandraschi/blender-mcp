"""
Mesh creation and manipulation handler for Blender MCP.

Provides functions for creating basic mesh primitives and manipulating mesh objects.
"""

from typing import Tuple
from loguru import logger
from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()


@blender_operation("create_cube")
async def create_cube(
    name: str = "Cube",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1),
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
    logger.info(f"Creating cube '{name}' at {location} with scale {scale}")

    script = f"""
import bpy

# Create cube
bpy.ops.mesh.primitive_cube_add(location={location!r}, scale={scale!r})
obj = bpy.context.active_object
obj.name = {name!r}
"""
    result = await _executor.execute_script(script)
    logger.info(f"Successfully created cube '{name}'")
    return f"Created cube '{name}' at {location}"


@blender_operation("create_sphere")
async def create_sphere(
    name: str = "Sphere",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1),
    radius: float = 1.0,
    segments: int = 32,
    rings: int = 16,
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
    logger.info(f"Creating sphere '{name}' at {location} with radius {radius}, segments {segments}")

    script = f"""
import bpy

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    location={location!r},
    scale={scale!r},
    radius={radius},
    segments={segments},
    ring_count={rings}
)
obj = bpy.context.active_object
obj.name = {name!r}
"""
    result = await _executor.execute_script(script)
    logger.info(f"✅ Successfully created sphere '{name}'")
    return f"Created sphere '{name}' at {location}"


@blender_operation("create_cylinder")
async def create_cylinder(
    name: str = "Cylinder",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1),
    radius: float = 1.0,
    depth: float = 2.0,
    vertices: int = 32,
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
    logger.info(f"Creating cylinder '{name}' at {location} with radius {radius}, depth {depth}")

    script = f"""
import bpy

# Create cylinder
bpy.ops.mesh.primitive_cylinder_add(
    location={location!r},
    scale={scale!r},
    radius={radius},
    depth={depth},
    vertices={vertices}
)
obj = bpy.context.active_object
obj.name = {name!r}
"""
    result = await _executor.execute_script(script)
    logger.info(f"✅ Successfully created cylinder '{name}'")
    return f"Created cylinder '{name}' at {location}"


@blender_operation("create_cone")
async def create_cone(
    name: str = "Cone",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1),
    radius1: float = 1.0,
    depth: float = 2.0,
    vertices: int = 32,
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
    logger.info(f"Creating cone '{name}' at {location} with base radius {radius1}, depth {depth}")

    script = f"""
import bpy

# Create cone
bpy.ops.mesh.primitive_cone_add(
    location={location!r},
    scale={scale!r},
    radius1={radius1},
    depth={depth},
    vertices={vertices}
)
obj = bpy.context.active_object
obj.name = {name!r}
"""
    result = await _executor.execute_script(script)
    logger.info(f"✅ Successfully created cone '{name}'")
    return f"Created cone '{name}' at {location}"


@blender_operation("create_plane")
async def create_plane(
    name: str = "Plane",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1),
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
    logger.info(f"Creating plane '{name}' at {location} with scale {scale}")

    script = f"""
import bpy

# Create plane
bpy.ops.mesh.primitive_plane_add(location={location!r}, scale={scale!r})
obj = bpy.context.active_object
obj.name = {name!r}
"""
    result = await _executor.execute_script(script)
    logger.info(f"✅ Successfully created plane '{name}'")
    return f"Created plane '{name}' at {location}"


@blender_operation("create_torus")
async def create_torus(
    name: str = "Torus",
    location: Tuple[float, float, float] = (0, 0, 0),
    major_radius: float = 1.0,
    minor_radius: float = 0.25,
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
    logger.info(
        f"Creating torus '{name}' at {location} with major radius {major_radius}, minor radius {minor_radius}"
    )

    script = f"""
import bpy

# Create torus
bpy.ops.mesh.primitive_torus_add(
    location={location!r},
    major_radius={major_radius},
    minor_radius={minor_radius}
)
obj = bpy.context.active_object
obj.name = {name!r}
"""
    result = await _executor.execute_script(script)
    logger.info(f"✅ Successfully created torus '{name}'")
    return f"Created torus '{name}' at {location}"


@blender_operation("create_monkey")
async def create_monkey(
    name: str = "Suzanne",
    location: Tuple[float, float, float] = (0, 0, 0),
    scale: Tuple[float, float, float] = (1, 1, 1),
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
    logger.info(f"Creating Suzanne '{name}' at {location} with scale {scale}")

    script = f"""
import bpy

# Create monkey
bpy.ops.mesh.primitive_monkey_add(location={location!r}, scale={scale!r})
obj = bpy.context.active_object
obj.name = {name!r}
"""
    result = await _executor.execute_script(script)
    logger.info(f"✅ Successfully created Suzanne '{name}'")
    return f"Created Suzanne '{name}' at {location}"


@blender_operation("duplicate_object")
async def duplicate_object(source_name: str, new_name: str) -> str:
    """
    Duplicate an existing object.

    Args:
        source_name: Name of object to duplicate
        new_name: Name for the duplicated object

    Returns:
        Success message
    """
    logger.info(f"Duplicating object '{source_name}' as '{new_name}'")

    script = f"""
import bpy

# Find source object
obj = bpy.data.objects.get({source_name!r})
if not obj:
    raise ValueError(f"Object {source_name!r} not found")

# Select and duplicate
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.duplicate()

# Rename duplicate
dup_obj = bpy.context.active_object
dup_obj.name = {new_name!r}
"""
    result = await _executor.execute_script(script)
    logger.info(f"✅ Successfully duplicated '{source_name}' as '{new_name}'")
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
    logger.info(f"Deleting object '{name}'")

    script = f"""
import bpy

# Find and delete object
obj = bpy.data.objects.get({name!r})
if obj:
    bpy.data.objects.remove(obj)
else:
    raise ValueError(f"Object {name!r} not found")
"""
    result = await _executor.execute_script(script)
    logger.info(f"✅ Successfully deleted object '{name}'")
    return f"Deleted object '{name}'"

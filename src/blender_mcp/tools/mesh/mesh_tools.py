"""
Mesh creation and manipulation tools for Blender MCP.

Provides portmanteau tools for creating basic mesh primitives and manipulating objects.
"""

from typing import Tuple

from pydantic import BaseModel, Field

from blender_mcp.app import get_app
from blender_mcp.compat import *


class CreatePrimitiveParams(BaseModel):
    """Parameters for creating mesh primitives."""

    primitive_type: str = Field(
        ..., description="Type of primitive: cube, sphere, cylinder, cone, plane, torus, monkey"
    )
    name: str = Field("Object", description="Name for the new object")
    location: Tuple[float, float, float] = Field(
        (0, 0, 0), description="Location coordinates (x, y, z)"
    )
    scale: Tuple[float, float, float] = Field((1, 1, 1), description="Scale factors (x, y, z)")


def _register_mesh_tools():
    """Register all mesh-related tools."""
    app = get_app()

    @app.tool
    async def blender_mesh(
        operation: str = "create_cube",
        name: str = "Object",
        primitive_type: str = "cube",
        location: Tuple[float, float, float] = (0, 0, 0),
        scale: Tuple[float, float, float] = (1, 1, 1),
        radius: float = 1.0,
        depth: float = 2.0,
        vertices: int = 32,
        source_name: str = "",
    ) -> str:
        """
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates 9 related mesh operations into single interface. Prevents tool explosion while maintaining
        full primitive creation and object management functionality. Follows FastMCP 2.14.3 best practices.

        Create and manipulate mesh objects in Blender with comprehensive primitive support.

        **Core Operations:**
        - **create_cube**: Generate cube primitive with customizable dimensions
        - **create_sphere**: Generate sphere primitive with vertex control
        - **create_cylinder**: Generate cylinder primitive with radius/depth control
        - **create_cone**: Generate cone primitive with radius/depth control
        - **create_plane**: Generate plane primitive for ground/floor surfaces
        - **create_torus**: Generate torus primitive with ring/tube radius control
        - **create_monkey**: Generate Suzanne (monkey) primitive for testing
        - **duplicate_object**: Create copies of existing objects with transforms
        - **delete_object**: Remove objects from scene by name

        Args:
            operation (str, required): The mesh operation to perform. Must be one of: "create_cube", "create_sphere",
                "create_cylinder", "create_cone", "create_plane", "create_torus", "create_monkey",
                "duplicate_object", "delete_object".
                - "create_*": Create new primitive objects (require: name, may use: location, scale, radius, depth, vertices)
                - "duplicate_object": Copy existing object (requires: source_name, name)
                - "delete_object": Remove object from scene (requires: name)
            name (str, required): Name for the new object or object to delete. Must be unique in scene.
            primitive_type (str | None): Type of primitive for create operations. One of: "cube", "sphere",
                "cylinder", "cone", "plane", "torus", "monkey". Auto-detected from operation if not specified.
            location (Tuple[float, float, float]): World-space coordinates (x, y, z) for object placement.
                Default: (0, 0, 0). Used for all create operations.
            scale (Tuple[float, float, float]): Scale factors along each axis (x, y, z).
                Default: (1, 1, 1). Applied after object creation.
            radius (float): Radius parameter for curved primitives (sphere, cylinder, cone, torus).
                Default: 1.0. Range: 0.01 to 100.0.
            depth (float): Height/depth parameter for 3D primitives (cylinder, cone).
                Default: 2.0. Range: 0.01 to 100.0.
            vertices (int): Vertex count for curved surfaces (sphere, cylinder).
                Default: 32. Range: 3 to 256. Higher values = smoother surfaces.
            source_name (str): Name of source object for duplication operations.
                Required for "duplicate_object" operation.

        Returns:
            str: Operation result message with success/failure status and object details.
                Format: "SUCCESS: {operation} - {object_name} created at {location}" or
                "ERROR: {operation} failed - {error_details}"

        Raises:
            ValueError: If operation parameters are invalid or object names conflict
            RuntimeError: If Blender operation fails due to scene state or resource issues

        Examples:
            Create basic cube: blender_mesh("create_cube", "MyCube", location=(5, 0, 0))
            Create high-res sphere: blender_mesh("create_sphere", "Ball", vertices=64, radius=2.0)
            Duplicate object: blender_mesh("duplicate_object", "Copy1", source_name="Original")
            Delete object: blender_mesh("delete_object", "OldObject")

        Note:
            All objects are created with default materials. Use blender_materials tools for texturing.
            Transform operations can be applied immediately after creation using blender_transform.
        """
        from loguru import logger

        from blender_mcp.handlers.mesh_handler import (
            create_cone,
            create_cube,
            create_cylinder,
            create_monkey,
            create_plane,
            create_sphere,
            create_torus,
            delete_object,
            duplicate_object,
        )

        logger.info(
            f"blender_mesh called with operation='{operation}', name='{name}', location={location}, radius={radius}, vertices={vertices}"
        )

        try:
            # Convert parameters to proper formats
            location_tuple = (
                tuple(float(x) for x in location)
                if hasattr(location, "__iter__") and not isinstance(location, str)
                else location
            )
            scale_tuple = (
                tuple(float(x) for x in scale)
                if hasattr(scale, "__iter__") and not isinstance(scale, str)
                else scale
            )

            # Ensure we have 3-tuples
            if len(location_tuple) != 3:
                return f"Error: location must be a 3-element array/tuple, got {len(location_tuple)} elements"
            if len(scale_tuple) != 3:
                return (
                    f"Error: scale must be a 3-element array/tuple, got {len(scale_tuple)} elements"
                )

            # Validate numeric parameters
            try:
                radius_val = float(radius)
                vertices_val = int(vertices)
                if radius_val <= 0:
                    return f"Error: radius must be positive, got {radius_val}"
                if vertices_val < 3:
                    return f"Error: vertices must be at least 3, got {vertices_val}"
            except (ValueError, TypeError) as e:
                return f"Error: invalid numeric parameters - radius: {radius}, vertices: {vertices} ({e})"

            if operation == "create_cube":
                return await create_cube(name=name, location=location_tuple, scale=scale_tuple)

            elif operation == "create_sphere":
                return await create_sphere(
                    name=name,
                    location=location_tuple,
                    scale=scale_tuple,
                    radius=radius_val,
                    segments=vertices_val,
                    rings=vertices_val // 2,
                )

            elif operation == "create_cylinder":
                return await create_cylinder(
                    name=name,
                    location=location_tuple,
                    scale=scale_tuple,
                    radius=radius_val,
                    depth=float(depth),
                    vertices=vertices_val,
                )

            elif operation == "create_cone":
                return await create_cone(
                    name=name,
                    location=location_tuple,
                    scale=scale_tuple,
                    radius1=radius_val,
                    depth=float(depth),
                    vertices=vertices_val,
                )

            elif operation == "create_plane":
                return await create_plane(name=name, location=location_tuple, scale=scale_tuple)

            elif operation == "create_torus":
                return await create_torus(
                    name=name,
                    location=location_tuple,
                    major_radius=radius_val,
                    minor_radius=radius_val * 0.25,
                )

            elif operation == "create_monkey":
                return await create_monkey(name=name, location=location_tuple, scale=scale_tuple)

            elif operation == "duplicate_object":
                if not source_name:
                    return "source_name parameter required for duplication"
                return await duplicate_object(source_name=source_name, new_name=name)

            elif operation == "delete_object":
                return await delete_object(name=name)

            else:
                return f"Unknown operation: {operation}"

        except Exception as e:
            logger.error(f"❌ Error in mesh operation '{operation}': {str(e)}")
            return f"Error in mesh operation '{operation}': {str(e)}"


_register_mesh_tools()

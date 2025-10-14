"""
Mesh creation and manipulation tools for Blender MCP.

Provides portmanteau tools for creating basic mesh primitives and manipulating objects.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Union
from blender_mcp.app import get_app


class CreatePrimitiveParams(BaseModel):
    """Parameters for creating mesh primitives."""
    primitive_type: str = Field(..., description="Type of primitive: cube, sphere, cylinder, cone, plane, torus, monkey")
    name: str = Field("Object", description="Name for the new object")
    location: Tuple[float, float, float] = Field((0, 0, 0), description="Location coordinates (x, y, z)")
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
        source_name: str = ""
    ) -> str:
        """
        Create and manipulate mesh objects in Blender.

        Supports multiple operations through the operation parameter:
        - create_cube: Create a cube primitive
        - create_sphere: Create a sphere primitive
        - create_cylinder: Create a cylinder primitive
        - create_cone: Create a cone primitive
        - create_plane: Create a plane primitive
        - create_torus: Create a torus primitive
        - create_monkey: Create Suzanne (monkey) primitive
        - duplicate_object: Duplicate an existing object
        - delete_object: Delete object by name

        Args:
            operation: Operation type
            name: Object name
            primitive_type: Type of primitive (for create operations)
            location: Location coordinates (x, y, z)
            scale: Scale factors (x, y, z)
            radius: Radius for spheres, cylinders, cones, tori
            depth: Depth/height for cylinders, cones
            vertices: Number of vertices for spheres, cylinders
            source_name: Name of source object for duplication

        Returns:
            Operation result message
        """
        from blender_mcp.handlers.mesh_handler import (
            create_cube, create_sphere, create_cylinder, create_cone,
            create_plane, create_torus, create_monkey,
            duplicate_object, delete_object
        )

        try:
            if operation == "create_cube":
                return await create_cube(name=name, location=location, scale=scale)

            elif operation == "create_sphere":
                return await create_sphere(name=name, location=location, scale=scale,
                                         radius=radius, segments=vertices, rings=vertices//2)

            elif operation == "create_cylinder":
                return await create_cylinder(name=name, location=location, scale=scale,
                                           radius=radius, depth=depth, vertices=vertices)

            elif operation == "create_cone":
                return await create_cone(name=name, location=location, scale=scale,
                                       radius1=radius, depth=depth, vertices=vertices)

            elif operation == "create_plane":
                return await create_plane(name=name, location=location, scale=scale)

            elif operation == "create_torus":
                return await create_torus(name=name, location=location,
                                        major_radius=radius, minor_radius=radius*0.25)

            elif operation == "create_monkey":
                return await create_monkey(name=name, location=location, scale=scale)

            elif operation == "duplicate_object":
                if not source_name:
                    return "source_name parameter required for duplication"
                return await duplicate_object(source_name=source_name, new_name=name)

            elif operation == "delete_object":
                return await delete_object(name=name)

            else:
                return f"Unknown operation: {operation}"

        except Exception as e:
            return f"Error in mesh operation '{operation}': {str(e)}"


_register_mesh_tools()

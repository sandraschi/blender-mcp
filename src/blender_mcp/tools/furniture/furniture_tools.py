"""
Furniture and complex object creation tools for Blender MCP.

Provides tools for creating complex objects like furniture, buildings, and structures.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Union
from blender_mcp.app import get_app


def get_app():
    from blender_mcp.app import app
    return app


def _register_furniture_tools():
    """Register all furniture and complex object tools."""
    app = get_app()

    @app.tool
    async def blender_furniture(
        operation: str = "create_chair",
        name: str = "Furniture",
        style: str = "modern",
        dimensions: Tuple[float, float, float] = (1, 1, 1),
        location: Tuple[float, float, float] = (0, 0, 0),
    material: str = "wood",
    chair_type: str = "dining",
    table_type: str = "dining",
    bed_type: str = "single",
    sofa_type: str = "three_seater",
    cabinet_type: str = "kitchen",
    desk_type: str = "office",
    shelf_type: str = "bookshelf",
    stool_type: str = "bar"
    ) -> str:
        """
        Create furniture and complex objects in Blender.

        Supports multiple operations through the operation parameter:
        - create_chair: Create chairs (dining, office, armchair, etc.)
        - create_table: Create tables (dining, coffee, desk, etc.)
        - create_bed: Create beds (single, double, bunk, etc.)
        - create_sofa: Create sofas and couches
        - create_cabinet: Create cabinets and storage
        - create_shelf: Create bookshelves and shelving
        - create_desk: Create desks and workstations
        - create_stool: Create stools and bar stools

        Args:
            operation: Furniture creation operation
            name: Name for the furniture object
            style: Style (modern, classic, rustic, industrial, etc.)
            dimensions: Base dimensions (width, depth, height)
            location: Position coordinates
            material: Material type (wood, metal, fabric, etc.)
            color: Primary color
            complexity: Detail level (simple, normal, detailed)

        Returns:
            Success message with creation details
        """
        from blender_mcp.handlers.furniture_handler import (
            create_chair, create_table, create_bed, create_sofa,
            create_cabinet, create_desk, create_shelf, create_stool
        )

        try:
            if operation == "create_chair":
                return await create_chair(
                    name=name,
                    chair_type=chair_type,
                    style=style,
                    dimensions=dimensions,
                    location=location,
                    material=material
                )

            elif operation == "create_table":
                return await create_table(
                    name=name,
                    table_type=table_type,
                    style=style,
                    dimensions=dimensions,
                    location=location,
                    material=material
                )

            elif operation == "create_bed":
                return await create_bed(
                    name=name,
                    bed_type=bed_type,
                    style=style,
                    dimensions=dimensions,
                    location=location,
                    material=material
                )

            elif operation == "create_sofa":
                return await create_sofa(
                    name=name,
                    sofa_type=sofa_type,
                    style=style,
                    dimensions=dimensions,
                    location=location,
                    material=material
                )

            elif operation == "create_cabinet":
                return await create_cabinet(
                    name=name,
                    cabinet_type=cabinet_type,
                    style=style,
                    dimensions=dimensions,
                    location=location,
                    material=material
                )

            elif operation == "create_desk":
                return await create_desk(
                    name=name,
                    desk_type=desk_type,
                    style=style,
                    dimensions=dimensions,
                    location=location,
                    material=material
                )

            elif operation == "create_shelf":
                return await create_shelf(
                    name=name,
                    shelf_type=shelf_type,
                    style=style,
                    dimensions=dimensions,
                    location=location,
                    material=material
                )

            elif operation == "create_stool":
                return await create_stool(
                    name=name,
                    stool_type=stool_type,
                    style=style,
                    dimensions=dimensions,
                    location=location,
                    material=material
                )

            else:
                return f"Unknown furniture operation: {operation}"

        except Exception as e:
            return f"Error in furniture operation '{operation}': {str(e)}"


_register_furniture_tools()

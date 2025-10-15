"""
Selection tools for Blender MCP.

Provides tools for selecting objects and elements in Blender scenes.
"""

from ..compat import *

from typing import List
from loguru import logger
from blender_mcp.app import get_app


def get_app():
    from blender_mcp.app import app

    return app


def _register_selection_tools():
    """Register all selection-related tools."""
    app = get_app()

    @app.tool
    async def blender_selection(
        operation: str = "select_objects",
        object_names: List[str] = [],
        object_type: str = "MESH",
        material_name: str = "",
        mode: str = "REPLACE",
        active_object: str = "",
    ) -> str:
        """
        Select objects and elements in Blender scenes.

        Supports multiple operations through the operation parameter:
        - select_objects: Select specific objects by name
        - select_by_type: Select all objects of a specific type
        - select_by_material: Select objects using a specific material
        - select_all: Select all objects in scene
        - select_none: Deselect all objects
        - invert_selection: Invert current selection

        Args:
            operation: Selection operation type
            object_names: List of object names to select
            object_type: Type of objects to select (MESH, CURVE, LIGHT, etc.)
            material_name: Material name to select objects by
            mode: Selection mode (REPLACE, ADD, SUBTRACT)
            active_object: Object to set as active after selection

        Returns:
            Success message with selection details
        """
        from blender_mcp.handlers.selection_handler import (
            select_objects,
            select_by_type,
            select_by_material,
        )

        try:
            if operation == "select_objects":
                if not object_names:
                    return "object_names parameter required for object selection"
                return await select_objects(
                    object_names=object_names,
                    mode=mode,
                    active_object=active_object if active_object else None,
                )

            elif operation == "select_by_type":
                return await select_by_type(object_type=object_type, mode=mode)

            elif operation == "select_by_material":
                if not material_name:
                    return "material_name parameter required for material selection"
                return await select_by_material(material_name=material_name, mode=mode)

            elif operation == "select_all":
                # Select all objects
                script = """
import bpy
bpy.ops.object.select_all(action='SELECT')
selected_count = len([obj for obj in bpy.context.selected_objects])
"""
                from ..utils.blender_executor import get_blender_executor

                executor = get_blender_executor()
                result = await executor.execute_script(script)
                len(
                    [obj for obj in result.split() if obj.isdigit()]
                )  # Extract count from result if needed
                logger.info("🎯 Selected all objects in scene")
                return "Selected all objects in scene"

            elif operation == "select_none":
                # Deselect all objects
                script = """
import bpy
bpy.ops.object.select_all(action='DESELECT')
"""
                from ..utils.blender_executor import get_blender_executor

                executor = get_blender_executor()
                result = await executor.execute_script(script)
                logger.info("🎯 Deselected all objects")
                return "Deselected all objects"

            elif operation == "invert_selection":
                # Invert selection
                script = """
import bpy
bpy.ops.object.select_all(action='INVERT')
selected_count = len([obj for obj in bpy.context.selected_objects])
"""
                from ..utils.blender_executor import get_blender_executor

                executor = get_blender_executor()
                result = await executor.execute_script(script)
                # Try to extract the count from the result or use a default message
                logger.info("🎯 Inverted object selection")
                return "Inverted object selection"

            else:
                return f"Unknown selection operation: {operation}. Available: select_objects, select_by_type, select_by_material, select_all, select_none, invert_selection"

        except Exception as e:
            return f"Error in selection operation '{operation}': {str(e)}"


_register_selection_tools()

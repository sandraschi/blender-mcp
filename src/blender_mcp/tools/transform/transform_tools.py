"""
Transform tools for Blender MCP.

Provides tools for positioning, rotating, and scaling objects.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Union
from blender_mcp.app import get_app


def get_app():
    from blender_mcp.app import app
    return app


def _register_transform_tools():
    """Register all transform-related tools."""
    app = get_app()

    @app.tool
    async def blender_transform(
        operation: str = "set_location",
        object_names: Union[str, List[str]] = "",
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        rotation_x: float = 0.0,
        rotation_y: float = 0.0,
        rotation_z: float = 0.0,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
    scale_z: float = 1.0,
    space: str = "WORLD",
    relative: bool = False
    ) -> str:
        """
        Transform objects in 3D space.

        Supports multiple operations through the operation parameter:
        - set_location: Set object position
        - set_rotation: Set object rotation (degrees)
        - set_scale: Set object scale
        - translate: Move object by offset
        - rotate: Rotate object by angle
        - scale: Scale object by factor
        - apply_transform: Apply transforms to mesh
        - reset_transform: Reset transforms to identity

        Args:
            operation: Transform operation type
            object_names: Name(s) of object(s) to transform
            x, y, z: Position coordinates
            rotation_x, rotation_y, rotation_z: Rotation angles in degrees
            scale_x, scale_y, scale_z: Scale factors
            space: Coordinate space (WORLD, LOCAL, CURSOR, PARENT)
            relative: Apply transformation relative to current values

        Returns:
            Success message with transform details
        """
        from blender_mcp.handlers.transform_handler import (
            set_transform, apply_transform
        )

        try:
            # Ensure object_names is a list
            if isinstance(object_names, str):
                if not object_names:
                    return "object_names parameter required"
                obj_list = [object_names]
            else:
                obj_list = object_names

            if operation == "set_location":
                return await set_transform(
                    object_names=obj_list,
                    transform_type="TRANSLATE",
                    values=[x, y, z],
                    space=space,
                    relative=relative
                )

            elif operation == "set_rotation":
                return await set_transform(
                    object_names=obj_list,
                    transform_type="ROTATE",
                    values=[rotation_x, rotation_y, rotation_z],
                    space=space,
                    relative=relative,
                    as_euler=True
                )

            elif operation == "set_scale":
                return await set_transform(
                    object_names=obj_list,
                    transform_type="SCALE",
                    values=[scale_x, scale_y, scale_z],
                    space=space,
                    relative=relative
                )

            elif operation == "translate":
                return await set_transform(
                    object_names=obj_list,
                    transform_type="TRANSLATE",
                    values=[x, y, z],
                    space=space,
                    relative=True
                )

            elif operation == "rotate":
                return await set_transform(
                    object_names=obj_list,
                    transform_type="ROTATE",
                    values=[rotation_x, rotation_y, rotation_z],
                    space=space,
                    relative=True,
                    as_euler=True
                )

            elif operation == "scale":
                return await set_transform(
                    object_names=obj_list,
                    transform_type="SCALE",
                    values=[scale_x, scale_y, scale_z],
                    space=space,
                    relative=True
                )

            elif operation == "apply_transform":
                if isinstance(object_names, list):
                    object_names = object_names[0] if object_names else ""
                if not object_names:
                    return "object_names parameter required for apply_transform"
                return await apply_transform(object_name=object_names)

            elif operation == "reset_transform":
                # Reset all transforms to identity
                location_result = await set_transform(
                    object_names=obj_list,
                    transform_type="TRANSLATE",
                    values=[0, 0, 0],
                    space="WORLD",
                    relative=False
                )
                rotation_result = await set_transform(
                    object_names=obj_list,
                    transform_type="ROTATE",
                    values=[0, 0, 0],
                    space="WORLD",
                    relative=False,
                    as_euler=True
                )
                scale_result = await set_transform(
                    object_names=obj_list,
                    transform_type="SCALE",
                    values=[1, 1, 1],
                    space="WORLD",
                    relative=False
                )
                return f"Reset transforms for {len(obj_list)} object(s)"

            else:
                return f"Unknown transform operation: {operation}. Available: set_location, set_rotation, set_scale, translate, rotate, scale, apply_transform, reset_transform"

        except Exception as e:
            return f"Error in transform operation '{operation}': {str(e)}"


_register_transform_tools()

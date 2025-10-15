"""
UV tools for Blender MCP.

Provides tools for UV mapping, unwrapping, and texture coordinate management.
"""

from blender_mcp.app import get_app


def get_app():
    from blender_mcp.app import app

    return app


def _register_uv_tools():
    """Register all UV-related tools."""
    app = get_app()

    @app.tool
    async def blender_uv(
        operation: str = "unwrap",
        object_name: str = "",
        unwrap_method: str = "ANGLE_BASED",
        margin: float = 0.001,
    ) -> str:
        """
        Manage UV mapping and texture coordinates.

        Supports multiple operations through the operation parameter:
        - unwrap: Unwrap UV coordinates
        - smart_project: Smart UV projection
        - cube_project: Cube projection
        - cylinder_project: Cylindrical projection
        - sphere_project: Spherical projection
        - reset_uvs: Reset UV coordinates
        - get_uv_info: Get UV mapping information

        Args:
            operation: UV operation type
            object_name: Name of object to work with
            unwrap_method: Unwrapping method (ANGLE_BASED, CONFORMAL, etc.)
            margin: Margin between UV islands

        Returns:
            Success message with UV operation details
        """
        from blender_mcp.handlers.uv_handler import (
            unwrap,
            project_from_view,
            reset_uvs,
            get_uv_info,
        )

        try:
            if operation == "unwrap":
                if not object_name:
                    return "object_name parameter required"
                return await unwrap(object_name=object_name, method=unwrap_method, margin=margin)

            elif operation == "smart_project":
                if not object_name:
                    return "object_name parameter required"
                return await project_from_view(
                    object_name=object_name, project_type="SMART_UV", margin=margin
                )

            elif operation == "cube_project":
                if not object_name:
                    return "object_name parameter required"
                return await project_from_view(
                    object_name=object_name, project_type="CUBE", margin=margin
                )

            elif operation == "cylinder_project":
                if not object_name:
                    return "object_name parameter required"
                return await project_from_view(
                    object_name=object_name, project_type="CYLINDER", margin=margin
                )

            elif operation == "sphere_project":
                if not object_name:
                    return "object_name parameter required"
                return await project_from_view(
                    object_name=object_name, project_type="SPHERE", margin=margin
                )

            elif operation == "reset_uvs":
                if not object_name:
                    return "object_name parameter required"
                return await reset_uvs(object_name=object_name)

            elif operation == "get_uv_info":
                if not object_name:
                    return "object_name parameter required"
                return await get_uv_info(object_name=object_name)

            else:
                return f"Unknown UV operation: {operation}. Available: unwrap, smart_project, cube_project, cylinder_project, sphere_project, reset_uvs, get_uv_info"

        except Exception as e:
            return f"Error in UV operation '{operation}': {str(e)}"


_register_uv_tools()

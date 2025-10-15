"""
Texture creation and management tools for Blender MCP.

Provides tools for creating procedural and image-based textures.
"""

from blender_mcp.app import get_app


def get_app():
    from blender_mcp.app import app

    return app


def _register_texture_tools():
    """Register all texture-related tools."""
    app = get_app()

    @app.tool
    async def blender_textures(
        operation: str = "create_noise",
        name: str = "Texture",
        texture_type: str = "NOISE",
        width: int = 1024,
        height: int = 1024,
        image_path: str = "",
        material_name: str = "",
        object_name: str = "",
    ) -> str:
        """
        Create and manage textures in Blender.

        Supports multiple operations through the operation parameter:
        - create_[type]: Create procedural textures (noise, voronoi, musgrave, wave, checker, brick, gradient)
        - assign_texture: Assign texture to material
        - bake_texture: Bake textures from objects

        Args:
            operation: Texture operation type
            name: Name for the texture
            texture_type: Type of procedural texture
            width: Texture width in pixels
            height: Texture height in pixels
            image_path: Path to image file for image textures
            scale: Texture scale factor
            detail: Texture detail level
            roughness: Texture roughness
            distortion: Texture distortion
            object_name: Name of object for UV operations

        Returns:
            Success message with texture details
        """
        from blender_mcp.handlers.texture_handler import (
            create_texture,
            assign_texture_to_material,
            bake_texture,
        )

        try:
            if operation.startswith("create_"):
                # Extract texture type from operation (e.g., "create_noise" -> "NOISE")
                texture_type = operation.replace("create_", "").upper()
                return await create_texture(
                    name=name, texture_type=texture_type, width=width, height=height
                )

            elif operation == "assign_texture":
                if not material_name:
                    return "material_name parameter required"
                return await assign_texture_to_material(
                    texture_name=name, material_name=material_name
                )

            elif operation == "bake_texture":
                if not object_name:
                    return "object_name parameter required for baking"
                return await bake_texture(
                    object_name=object_name, texture_name=name, width=width, height=height
                )

            else:
                return f"Unknown texture operation: {operation}. Available: create_[type], assign_texture, bake_texture"

        except Exception as e:
            return f"Error in texture operation '{operation}': {str(e)}"


_register_texture_tools()

"""
Import tools for Blender MCP.

Provides tools for importing various file formats into Blender.
"""

from blender_mcp.app import get_app


def get_app():
    from blender_mcp.app import app

    return app


def _register_import_tools():
    """Register all import-related tools."""
    app = get_app()

    @app.tool
    async def blender_import(
        operation: str = "import_fbx",
        filepath: str = "",
        file_format: str = "FBX",
        global_scale: float = 1.0,
        use_custom_normals: bool = True,
        import_shading: bool = True,
        asset_name: str = "LinkedAsset",
    ) -> str:
        """
        Import 3D files into Blender scenes.

        Supports multiple operations through the operation parameter:
        - import_[format]: Import files in any supported format (FBX, OBJ, GLTF, STL, PLY, etc.)
        - link_asset: Link external assets without importing

        Args:
            operation: Import operation type
            filepath: Path to the file to import
            file_format: Format of the file (FBX, OBJ, GLTF, etc.)
            global_scale: Global scale factor for import
            use_custom_normals: Import custom normals
            import_shading: Import material shading
            use_split_objects: Split objects on import (OBJ)
            use_manual_orientation: Use manual orientation (FBX)
            import_pack_images: Pack images into blend file (GLTF)

        Returns:
            Success message with import details
        """
        from blender_mcp.handlers.import_handler import import_file, link_asset

        try:
            if operation.startswith("import_"):
                # Extract format from operation (e.g., "import_fbx" -> "FBX")
                file_format = operation.replace("import_", "").upper()
                return await import_file(
                    filepath=filepath,
                    file_format=file_format,
                    global_scale=global_scale,
                    use_custom_normals=use_custom_normals,
                    import_shading=import_shading,
                )

            elif operation == "link_asset":
                return await link_asset(
                    filepath=filepath, name=kwargs.get("asset_name", "LinkedAsset")
                )

            else:
                return f"Unknown import operation: {operation}. Use import_[format] or link_asset"

        except Exception as e:
            return f"Error in import operation '{operation}': {str(e)}"


_register_import_tools()

"""
Export tools for Blender MCP.

Provides tools for exporting scenes and objects in various formats.
"""

from blender_mcp.compat import *

from typing import List, Optional
from blender_mcp.app import get_app


def _register_export_tools():
    """Register all export-related tools."""
    app = get_app()

    @app.tool
    async def blender_export(
        operation: str = "export_fbx",
        output_path: str = "",
        object_names: Optional[List[str]] = None,
        include_materials: bool = True,
        include_animations: bool = True,
        apply_transforms: bool = True,
        global_scale: float = 1.0,
        use_mesh_modifiers: bool = True,
    ) -> str:
        """
        Export Blender scenes and objects for Unity and VRChat.

        Supports multiple operations through the operation parameter:
        - export_unity: Export to Unity-compatible formats
        - export_vrchat: Export to VRChat-compatible formats

        Args:
            operation: Export operation type
            output_path: Path where to save the exported file
            object_names: List of specific object names to export (None = all objects)
            include_materials: Include materials in export
            include_animations: Include animations in export
            apply_transforms: Apply object transforms before export
            global_scale: Global scale factor for export
            use_mesh_modifiers: Apply mesh modifiers before export
            start_frame: Start frame for animation export
            end_frame: End frame for animation export
            export_format: Specific format options for FBX/GLTF/etc.

        Returns:
            Success message with export details
        """
        from blender_mcp.handlers.export_handler import export_for_unity, export_for_vrchat

        try:
            if operation == "export_unity":
                return await export_for_unity(output_path=output_path, object_names=object_names)

            elif operation == "export_vrchat":
                return await export_for_vrchat(output_path=output_path, object_names=object_names)

            else:
                return (
                    f"Unknown export operation: {operation}. Available: export_unity, export_vrchat"
                )

        except Exception as e:
            return f"Error in export operation '{operation}': {str(e)}"


_register_export_tools()

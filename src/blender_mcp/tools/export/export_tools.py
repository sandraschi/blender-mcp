"""
Export tools for Blender MCP.

Provides tools for exporting scenes and objects in various formats.
"""

import json

from blender_mcp.app import get_app
from blender_mcp.compat import *


def _register_export_tools():
    """Register all export-related tools."""
    app = get_app()

    @app.tool
    async def blender_export(
        operation: str = "export_glb",
        output_path: str = "",
        object_names: list[str] | None = None,
        file_format: str = "GLB",
        include_materials: bool = True,
        include_animations: bool = True,
        apply_transforms: bool = True,
        global_scale: float = 1.0,
        use_mesh_modifiers: bool = True,
    ) -> str:
        """
        Export Blender scenes and objects to interchange and game-engine formats.

        Operations:
        - export_gltf / export_glb / export_fbx / export_obj / export_stl / export_usd / export_vrm
        - export_unity / export_vrchat / export_unreal (platform presets)
        """
        from blender_mcp.handlers.export_handler import (
            export_for_unity,
            export_for_unreal,
            export_for_vrchat,
            export_scene_format,
        )

        format_ops = {
            "export_gltf": "GLTF",
            "export_glb": "GLB",
            "export_fbx": "FBX",
            "export_obj": "OBJ",
            "export_stl": "STL",
            "export_usd": "USD",
            "export_vrm": "VRM",
        }

        try:
            if operation in format_ops:
                if not output_path:
                    return json.dumps({"success": False, "error": "output_path is required"})
                fmt = file_format if file_format else format_ops[operation]
                result = await export_scene_format(
                    output_path=output_path,
                    file_format=fmt if operation == "export_gltf" else format_ops[operation],
                    object_names=object_names,
                    apply_modifiers=use_mesh_modifiers,
                    global_scale=global_scale,
                )
                return json.dumps(result, indent=2)

            if operation == "export_unity":
                if not output_path:
                    return json.dumps({"success": False, "error": "output_path is required"})
                message = await export_for_unity(output_path=output_path)
                return json.dumps({"success": True, "message": message, "output_path": output_path})

            if operation == "export_vrchat":
                if not output_path:
                    return json.dumps({"success": False, "error": "output_path is required"})
                message = await export_for_vrchat(output_path=output_path)
                return json.dumps({"success": True, "message": message, "output_path": output_path})

            if operation == "export_unreal":
                if not output_path:
                    return json.dumps({"success": False, "error": "output_path is required"})
                result = await export_for_unreal(
                    output_path=output_path,
                    object_names=object_names,
                    global_scale=global_scale,
                    apply_modifiers=use_mesh_modifiers,
                )
                return json.dumps(result, indent=2)

            return json.dumps(
                {
                    "success": False,
                    "error": f"Unknown export operation: {operation}",
                    "available_operations": [
                        *format_ops.keys(),
                        "export_unity",
                        "export_vrchat",
                        "export_unreal",
                    ],
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps({"success": False, "error": str(e), "operation": operation}, indent=2)


_register_export_tools()

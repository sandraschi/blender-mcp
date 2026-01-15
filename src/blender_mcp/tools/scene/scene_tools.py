"""
Scene management portmanteau tool for Blender MCP.

Provides a single comprehensive tool for scene, collection, view layer,
lighting, camera, and render settings management.
"""

from typing import List, Literal

from blender_mcp.compat import *


def get_app():
    from blender_mcp.app import app
    return app


def _register_scene_tools():
    """Register the blender_scene portmanteau tool."""
    app = get_app()

    @app.tool
    async def blender_scene(
        operation: Literal[
            "create_scene", "list_scenes", "clear_scene", "set_active_scene",
            "link_object_to_scene", "create_collection", "add_to_collection",
            "set_active_collection", "set_view_layer", "setup_lighting",
            "setup_camera", "set_render_settings"
        ] = "list_scenes",
        scene_name: str = "NewScene",
        object_name: str = "",
        collection_name: str = "",
        layer_name: str = "",
        light_type: str = "SUN",
        location: List[float] = [0, 0, 5],
        rotation: List[float] = [1.0, 0, 0],
        resolution_x: int = 1920,
        resolution_y: int = 1080,
    ) -> str:
        """
        Comprehensive scene management for Blender.

        Supports multiple operations through the operation parameter:
        - create_scene: Create a new scene
        - list_scenes: List all scenes in the file
        - clear_scene: Clear all objects from current scene
        - set_active_scene: Set the active scene
        - link_object_to_scene: Link object to a scene
        - create_collection: Create a new collection
        - add_to_collection: Add object to collection
        - set_active_collection: Set the active collection
        - set_view_layer: Set active view layer
        - setup_lighting: Set up scene lighting
        - setup_camera: Set up scene camera
        - set_render_settings: Configure render resolution

        Args:
            operation: Scene operation type
            scene_name: Name for scene operations
            object_name: Name of object for linking operations
            collection_name: Name for collection operations
            layer_name: Name for view layer operations
            light_type: Type of light (SUN, POINT, SPOT, AREA)
            location: Position as [x, y, z] for camera/light
            rotation: Rotation as [x, y, z] for camera
            resolution_x: Render width in pixels
            resolution_y: Render height in pixels

        Returns:
            Operation result message
        """
        from blender_mcp.handlers.scene_handler import (
            add_to_collection as _add_to_collection,
        )
        from blender_mcp.handlers.scene_handler import (
            clear_scene as _clear_scene,
        )
        from blender_mcp.handlers.scene_handler import (
            create_collection as _create_collection,
        )
        from blender_mcp.handlers.scene_handler import (
            create_scene as _create_scene,
        )
        from blender_mcp.handlers.scene_handler import (
            link_object_to_scene as _link_object_to_scene,
        )
        from blender_mcp.handlers.scene_handler import (
            list_scenes as _list_scenes,
        )
        from blender_mcp.handlers.scene_handler import (
            set_active_collection as _set_active_collection,
        )
        from blender_mcp.handlers.scene_handler import (
            set_active_scene as _set_active_scene,
        )
        from blender_mcp.handlers.scene_handler import (
            set_render_settings as _set_render_settings,
        )
        from blender_mcp.handlers.scene_handler import (
            set_view_layer as _set_view_layer,
        )
        from blender_mcp.handlers.scene_handler import (
            setup_camera as _setup_camera,
        )
        from blender_mcp.handlers.scene_handler import (
            setup_lighting as _setup_lighting,
        )

        try:
            if operation == "create_scene":
                return await _create_scene(scene_name)
            elif operation == "list_scenes":
                return await _list_scenes()
            elif operation == "clear_scene":
                return await _clear_scene()
            elif operation == "set_active_scene":
                return await _set_active_scene(scene_name)
            elif operation == "link_object_to_scene":
                if not object_name:
                    return "Error: object_name required for link_object_to_scene"
                return await _link_object_to_scene(object_name, scene_name)
            elif operation == "create_collection":
                if not collection_name:
                    return "Error: collection_name required for create_collection"
                return await _create_collection(collection_name)
            elif operation == "add_to_collection":
                if not collection_name or not object_name:
                    return "Error: collection_name and object_name required for add_to_collection"
                return await _add_to_collection(collection_name, object_name)
            elif operation == "set_active_collection":
                if not collection_name:
                    return "Error: collection_name required for set_active_collection"
                return await _set_active_collection(collection_name)
            elif operation == "set_view_layer":
                if not layer_name:
                    return "Error: layer_name required for set_view_layer"
                return await _set_view_layer(layer_name)
            elif operation == "setup_lighting":
                return await _setup_lighting(light_type, tuple(location))
            elif operation == "setup_camera":
                return await _setup_camera(tuple(location), tuple(rotation))
            elif operation == "set_render_settings":
                return await _set_render_settings(resolution_x, resolution_y)
            else:
                return f"Unknown operation: {operation}"
        except Exception as e:
            return f"Error in blender_scene({operation}): {str(e)}"


# Register tools when module is imported
_register_scene_tools()

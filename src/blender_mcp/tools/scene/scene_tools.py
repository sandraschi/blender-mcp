"""
Scene management tools for Blender MCP.

Provides tools for creating, managing, and manipulating Blender scenes,
collections, view layers, and basic scene setup operations.
"""

from ..compat import *

from typing import List
from pydantic import BaseModel, Field


# Import app lazily to avoid circular imports
def get_app():
    from blender_mcp.app import app

    return app


# Parameter schemas
class CreateSceneParams(BaseModel):
    """Parameters for creating a new scene."""

    scene_name: str = Field(default="NewScene", description="Name for the new scene")


class ListScenesParams(BaseModel):
    """Parameters for listing scenes (no parameters needed)."""

    pass


class ClearSceneParams(BaseModel):
    """Parameters for clearing scene (no parameters needed)."""

    pass


class SetActiveSceneParams(BaseModel):
    """Parameters for setting active scene."""

    scene_name: str = Field(..., description="Name of the scene to make active")


class LinkObjectToSceneParams(BaseModel):
    """Parameters for linking object to scene."""

    object_name: str = Field(..., description="Name of the object to link")
    scene_name: str = Field(..., description="Name of the scene to link to")


class CreateCollectionParams(BaseModel):
    """Parameters for creating a collection."""

    collection_name: str = Field(..., description="Name for the new collection")


class AddToCollectionParams(BaseModel):
    """Parameters for adding object to collection."""

    collection_name: str = Field(..., description="Name of the collection")
    object_name: str = Field(..., description="Name of the object to add")


class SetActiveCollectionParams(BaseModel):
    """Parameters for setting active collection."""

    collection_name: str = Field(..., description="Name of the collection to make active")


class SetViewLayerParams(BaseModel):
    """Parameters for setting active view layer."""

    layer_name: str = Field(..., description="Name of the view layer to set")


class SetupLightingParams(BaseModel):
    """Parameters for setting up scene lighting."""

    light_type: str = Field("SUN", description="Type of light (SUN, POINT, SPOT, AREA)")
    location: List[float] = Field(
        [0, 0, 5], description="Light location as [x, y, z]", min_length=3, max_length=3
    )


class SetupCameraParams(BaseModel):
    """Parameters for setting up scene camera."""

    location: List[float] = Field(
        [0, -5, 2], description="Camera location as [x, y, z]", min_length=3, max_length=3
    )
    rotation: List[float] = Field(
        [1.0, 0, 0], description="Camera rotation as [x, y, z]", min_length=3, max_length=3
    )


class SetRenderSettingsParams(BaseModel):
    """Parameters for setting render settings."""

    resolution_x: int = Field(1920, description="Render resolution width", ge=1, le=8192)
    resolution_y: int = Field(1080, description="Render resolution height", ge=1, le=8192)


# Tool registration functions
def _register_scene_tools():
    """Register all scene management tools with FastMCP."""
    app = get_app()

    @app.tool
    async def create_scene(scene_name: str = "NewScene") -> str:
        """
        Create a new Blender scene with the specified name.

        This tool creates a new scene in Blender, clears all existing objects,
        and sets up a basic scene structure. The new scene becomes the active scene.

        Args:
            scene_name: Name for the new scene (default: "NewScene")

        Returns:
            Confirmation message with scene creation details
        """
        from blender_mcp.handlers.scene_handler import create_scene

        return await create_scene(scene_name)

    @app.tool
    async def list_scenes() -> str:
        """
        List all scenes in the current Blender file.

        Returns a formatted list of all scenes with their object counts
        and active scene indicator.

        Returns:
            Formatted string listing all scenes and their properties
        """
        from blender_mcp.handlers.scene_handler import list_scenes

        return await list_scenes()

    @app.tool
    async def clear_scene() -> str:
        """
        Clear all objects from the current scene.

        Removes all mesh objects, lights, and cameras from the active scene,
        leaving only the scene structure intact.

        Returns:
            Confirmation message about scene clearing
        """
        from blender_mcp.handlers.scene_handler import clear_scene

        return await clear_scene()

    @app.tool
    async def set_active_scene(scene_name: str) -> str:
        """
        Switch to a different scene by name.

        Makes the specified scene the active scene for editing and rendering.

        Args:
            scene_name: Name of the scene to make active

        Returns:
            Confirmation message about scene switching
        """
        from blender_mcp.handlers.scene_handler import set_active_scene

        return await set_active_scene(scene_name)

    @app.tool
    async def link_object_to_scene(object_name: str, scene_name: str) -> str:
        """
        Link an existing object to a different scene.

        Objects can exist in multiple scenes. This tool links an object
        to the specified scene without moving it.

        Args:
            object_name: Name of the object to link
            scene_name: Name of the scene to link the object to

        Returns:
            Confirmation message about object linking
        """
        from blender_mcp.handlers.scene_handler import link_object_to_scene

        return await link_object_to_scene(object_name, scene_name)

    @app.tool
    async def create_collection(collection_name: str) -> str:
        """
        Create a new collection in the current scene.

        Collections are used to organize objects in Blender's outliner.
        New collections are created as children of the scene's master collection.

        Args:
            collection_name: Name for the new collection

        Returns:
            Confirmation message about collection creation
        """
        from blender_mcp.handlers.scene_handler import create_collection

        return await create_collection(collection_name)

    @app.tool
    async def add_to_collection(collection_name: str, object_name: str) -> str:
        """
        Add an object to a collection.

        Objects can belong to multiple collections. This tool adds the
        specified object to the specified collection.

        Args:
            collection_name: Name of the collection to add to
            object_name: Name of the object to add

        Returns:
            Confirmation message about adding object to collection
        """
        from blender_mcp.handlers.scene_handler import add_to_collection

        return await add_to_collection(collection_name, object_name)

    @app.tool
    async def set_active_collection(collection_name: str) -> str:
        """
        Set the active collection for new object creation.

        When you create new objects in Blender, they are added to the
        active collection. This tool changes which collection is active.

        Args:
            collection_name: Name of the collection to make active

        Returns:
            Confirmation message about collection activation
        """
        from blender_mcp.handlers.scene_handler import set_active_collection

        return await set_active_collection(collection_name)

    @app.tool
    async def set_view_layer(layer_name: str) -> str:
        """
        Set the active view layer.

        View layers control which objects are visible and renderable.
        This tool switches to the specified view layer.

        Args:
            layer_name: Name of the view layer to activate

        Returns:
            Confirmation message about view layer switching
        """
        from blender_mcp.handlers.scene_handler import set_view_layer

        return await set_view_layer(layer_name)

    @app.tool
    async def setup_lighting(light_type: str = "SUN", location: List[float] = [0, 0, 5]) -> str:
        """
        Set up basic lighting for the scene.

        Creates and positions a light source in the scene. Different light
        types provide different lighting characteristics.

        Args:
            light_type: Type of light to create ("SUN", "POINT", "SPOT", "AREA")
            location: Position to place the light as [x, y, z] coordinates

        Returns:
            Confirmation message about lighting setup
        """
        from blender_mcp.handlers.scene_handler import setup_lighting

        return await setup_lighting(light_type, tuple(location))

    @app.tool
    async def setup_camera(
        location: List[float] = [0, -5, 2], rotation: List[float] = [1.0, 0, 0]
    ) -> str:
        """
        Set up a camera for the scene.

        Creates and positions a camera in the scene with the specified
        location and rotation. The camera becomes the active camera.

        Args:
            location: Camera position as [x, y, z] coordinates
            rotation: Camera rotation as Euler angles [x, y, z] in radians

        Returns:
            Confirmation message about camera setup
        """
        from blender_mcp.handlers.scene_handler import setup_camera

        return await setup_camera(tuple(location), tuple(rotation))

    @app.tool
    async def set_render_settings(resolution_x: int = 1920, resolution_y: int = 1080) -> str:
        """
        Configure basic render settings for the scene.

        Sets the resolution and other basic render parameters for the scene.

        Args:
            resolution_x: Horizontal resolution in pixels (1-8192)
            resolution_y: Vertical resolution in pixels (1-8192)

        Returns:
            Confirmation message about render settings
        """
        from blender_mcp.handlers.scene_handler import set_render_settings

        return await set_render_settings(resolution_x, resolution_y)


# Register tools when this module is imported
_register_scene_tools()

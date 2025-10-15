"""Scene operations handler - manages Blender scenes.

This module provides scene management functions that can be registered as FastMCP tools.
"""

from ..compat import *

from blender_mcp.compat import *
from blender_mcp.utils.blender_executor import get_blender_executor
from blender_mcp.decorators import blender_operation
# from blender_mcp.app import app  # REMOVED to fix circular import

# Initialize the executor with default Blender executable
_executor = get_blender_executor()


# @app.tool  # Will be registered manually
@blender_operation("create_scene")
async def create_scene(scene_name: str = "NewScene") -> str:
    """Create a new Blender scene with the specified name.

    Args:
        scene_name: Name for the new scene (default: "NewScene")

    Returns:
        str: Confirmation message with the created scene name
    """
    script = f'''

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Rename current scene
bpy.context.scene.name = "{scene_name}"

print(f"Scene created: {{bpy.context.scene.name}}")
print(f"Objects in scene: {{len(bpy.context.scene.objects)}}")
'''

    await _executor.execute_script(script)
    return f"Created scene: {scene_name}"


# @app.tool  # Will be registered manually
@blender_operation("list_scenes")
async def list_scenes() -> str:
    """List all scenes in the current Blender file.

    Returns:
        str: Formatted list of all scenes with object counts
    """
    script = """

scenes = []
for scene in bpy.data.scenes:
    obj_count = len(scene.objects)
    scenes.append(f"{scene.name} ({obj_count} objects)")

print("SCENES:")
for scene in scenes:
    print(f"- {scene}")
"""
    await _executor.execute_script(script)
    return "Listed all scenes"


# @app.tool  # Will be registered manually
@blender_operation("clear_scene")
async def clear_scene() -> str:
    """Remove all objects from the current scene.

    Returns:
        str: Confirmation message
    """
    script = """

# Select and delete all objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Clear unused materials
for material in bpy.data.materials:
    if material.users == 0:
        bpy.data.materials.remove(material)

print("Scene cleared")
"""
    await _executor.execute_script(script)
    return "Cleared the current scene"


# @app.tool  # Will be registered manually
@blender_operation("set_active_scene")
async def set_active_scene(scene_name: str) -> str:
    """Set the active scene by name.

    Args:
        scene_name: Name of the scene to make active

    Returns:
        str: Confirmation message
    """
    script = f'''
if "{scene_name}" in bpy.data.scenes:
    bpy.context.window.scene = bpy.data.scenes["{scene_name}"]
    print(f"Set active scene to: {{bpy.context.scene.name}}")
else:
    print(f"Error: Scene '{scene_name}' not found")
'''
    await _executor.execute_script(script)
    return f"Set active scene to: {scene_name}"


# @app.tool  # Will be registered manually
@blender_operation("link_object_to_scene")
async def link_object_to_scene(object_name: str, scene_name: str) -> str:
    """Link an object to a scene.

    Args:
        object_name: Name of the object to link
        scene_name: Name of the target scene

    Returns:
        str: Confirmation message
    """
    script = f'''
if "{object_name}" not in bpy.data.objects:
    print(f"Error: Object '{object_name}' not found")
elif "{scene_name}" not in bpy.data.scenes:
    print(f"Error: Scene '{scene_name}' not found")
else:
    obj = bpy.data.objects["{object_name}"]
    scene = bpy.data.scenes["{scene_name}"]
    if obj.name not in scene.collection.objects:
        scene.collection.objects.link(obj)
    print(f"Linked object '{object_name}' to scene '{scene_name}'")
'''
    await _executor.execute_script(script)
    return f"Linked object to scene: {scene_name}"


# @app.tool  # Will be registered manually
@blender_operation("create_collection")
async def create_collection(collection_name: str) -> str:
    """Create a new collection.

    Args:
        collection_name: Name for the new collection

    Returns:
        str: Confirmation message
    """
    script = f'''
if "{collection_name}" not in bpy.data.collections:
    bpy.data.collections.new("{collection_name}")
    print(f"Created collection: {collection_name}")
else:
    print(f"Collection '{collection_name}' already exists")
'''
    await _executor.execute_script(script)
    return f"Created collection: {collection_name}"


# @app.tool  # Will be registered manually
@blender_operation("add_to_collection")
async def add_to_collection(collection_name: str, object_name: str) -> str:
    """Add an object to a collection.

    Args:
        collection_name: Name of the collection
        object_name: Name of the object to add

    Returns:
        str: Confirmation message
    """
    script = f'''
if "{object_name}" not in bpy.data.objects:
    print(f"Error: Object '{object_name}' not found")
elif "{collection_name}" not in bpy.data.collections:
    print(f"Error: Collection '{collection_name}' not found")
else:
    obj = bpy.data.objects["{object_name}"]
    collection = bpy.data.collections["{collection_name}"]
    
    # Unlink from current collections
    for col in obj.users_collection:
        col.objects.unlink(obj)
    
    # Link to target collection
    collection.objects.link(obj)
    print(f"Added '{object_name}' to collection '{collection_name}'")
'''
    await _executor.execute_script(script)
    return f"Added {object_name} to collection: {collection_name}"


# @app.tool  # Will be registered manually
@blender_operation("set_active_collection")
async def set_active_collection(collection_name: str) -> str:
    """Set the active collection.

    Args:
        collection_name: Name of the collection to make active

    Returns:
        str: Confirmation message
    """
    script = f'''
if "{collection_name}" in bpy.data.collections:
    layer_collection = bpy.context.view_layer.layer_collection
    layer_collection.children[collection_name].hide_viewport = False
    bpy.context.view_layer.active_layer_collection = layer_collection.children[collection_name]
    print(f"Set active collection to: {collection_name}")
else:
    print(f"Error: Collection '{collection_name}' not found")
'''
    await _executor.execute_script(script)
    return f"Set active collection to: {collection_name}"


# @app.tool  # Will be registered manually
@blender_operation("set_view_layer")
async def set_view_layer(layer_name: str) -> str:
    """Set the active view layer.

    Args:
        layer_name: Name of the view layer to make active

    Returns:
        str: Confirmation message
    """
    script = f'''
if "{layer_name}" in bpy.context.scene.view_layers:
    bpy.context.window.view_layer = bpy.context.scene.view_layers["{layer_name}"]
    print(f"Set active view layer to: {layer_name}")
else:
    print(f"Error: View layer '{layer_name}' not found")
'''
    await _executor.execute_script(script)
    return f"Set active view layer to: {layer_name}"


# @app.tool  # Will be registered manually
@blender_operation("setup_lighting")
async def setup_lighting(
    light_type: str = "SUN",
    location: tuple = (0, 0, 5),
    rotation: tuple = (0.785398, 0, 0),
    energy: float = 1.0,
) -> str:
    """Set up basic lighting in the scene.

    Args:
        light_type: Type of light (POINT, SUN, SPOT, AREA)
        location: Position of the light
        rotation: Rotation of the light in radians
        energy: Light intensity

    Returns:
        str: Confirmation message
    """
    script = f'''
import bpy

# Clear existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# Create new light
light_data = bpy.data.lights.new(name="New Light", type="{light_type}")
light_data.energy = {energy}
light_object = bpy.data.objects.new(name="New Light", object_data=light_data)
bpy.context.collection.objects.link(light_object)
light_object.location = {list(location)}
light_object.rotation_euler = {list(rotation)}

print(f"Added {{light_type}} light to scene")
'''
    await _executor.execute_script(script)
    return f"Set up {light_type} lighting in the scene"


# @app.tool  # Will be registered manually
@blender_operation("setup_camera")
async def setup_camera(
    location: tuple = (0, -5, 2), rotation: tuple = (1.0, 0, 0), lens: float = 50.0
) -> str:
    """Set up a camera in the scene.

    Args:
        location: Position of the camera
        rotation: Rotation of the camera in radians
        lens: Focal length of the camera in mm

    Returns:
        str: Confirmation message
    """
    script = f"""
import bpy

# Clear existing cameras
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        bpy.data.objects.remove(obj, do_unlink=True)

# Create new camera
camera_data = bpy.data.cameras.new(name="Camera")
camera_data.lens = {lens}
camera_object = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
camera_object.location = {list(location)}
camera_object.rotation_euler = {list(rotation)}

# Set as active camera
bpy.context.scene.camera = camera_object

print("Set up camera in the scene")
"""
    await _executor.execute_script(script)
    return "Set up camera in the scene"


# @app.tool  # Will be registered manually
@blender_operation("set_render_settings")
async def set_render_settings(
    resolution_x: int = 1920, resolution_y: int = 1080, engine: str = "CYCLES", samples: int = 128
) -> str:
    """Configure render settings.

    Args:
        resolution_x: Horizontal resolution
        resolution_y: Vertical resolution
        engine: Render engine (CYCLES, EEVEE, WORKBENCH)
        samples: Number of samples for rendering

    Returns:
        str: Confirmation message
    """
    script = f'''
import bpy

# Set render resolution
bpy.context.scene.render.resolution_x = {resolution_x}
bpy.context.scene.render.resolution_y = {resolution_y}

# Set render engine
bpy.context.scene.render.engine = "{engine}"

# Set samples based on engine
if "{engine}" == "CYCLES":
    bpy.context.scene.cycles.samples = {samples}
elif "{engine}" == "EEVEE":
    bpy.context.scene.eevee.taa_render_samples = {samples}

print(f"Render settings updated: {{resolution_x}}x{{resolution_y}} using {{engine}} with {{samples}} samples")
'''
    await _executor.execute_script(script)
    return f"Updated render settings: {resolution_x}x{resolution_y} using {engine} with {samples} samples"

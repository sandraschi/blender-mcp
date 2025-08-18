"""Scene operations handler - manages Blender scenes.

This module provides scene management functions that can be registered as FastMCP tools.
"""

from typing import List, Optional
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation
from ..app import app

# Initialize the executor with default Blender executable
_executor = get_blender_executor()

@app.tool
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
    
    output = await _executor.execute_script(script)
    return f"Created scene: {scene_name}"

@app.tool
@blender_operation("list_scenes")
async def list_scenes() -> str:
    """List all scenes in the current Blender file.
    
    Returns:
        str: Formatted list of all scenes with object counts
    """
    script = '''

scenes = []
for scene in bpy.data.scenes:
    obj_count = len(scene.objects)
    scenes.append(f"{scene.name} ({obj_count} objects)")

print("SCENES:")
for scene in scenes:
    print(f"- {scene}")
'''
    output = await _executor.execute_script(script)
    return "Listed all scenes"

@app.tool
@blender_operation("clear_scene")
async def clear_scene() -> str:
    """Remove all objects from the current scene.
    
    Returns:
        str: Confirmation message
    """
    script = '''

# Select and delete all objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Clear unused materials
for material in bpy.data.materials:
    if material.users == 0:
        bpy.data.materials.remove(material)

print("Scene cleared")
'''
    output = await _executor.execute_script(script)
    return "Cleared the current scene"

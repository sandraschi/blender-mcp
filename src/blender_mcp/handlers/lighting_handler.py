"""
Lighting creation and management handler for Blender MCP.

Provides functions for creating and managing lights in Blender scenes.
"""

from ..compat import *

from typing import Tuple, Optional
from loguru import logger
from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()


@blender_operation("create_sun_light")
async def create_sun_light(
    name: str = "Sun",
    location: Tuple[float, float, float] = (0, 0, 10),
    rotation: Tuple[float, float, float] = (0, 0, 0),
    energy: float = 5.0,
    color: Tuple[float, float, float] = (1, 1, 1),
    shadow_soft_size: float = 0.1,
) -> str:
    """
    Create a sun (directional) light.

    Args:
        name: Name for the light
        location: Light position (affects shadow direction)
        rotation: Light rotation angles in degrees
        energy: Light intensity
        color: Light color (RGB 0-1)
        shadow_soft_size: Shadow softness

    Returns:
        Success message
    """
    logger.info(f"Creating sun light '{name}' at {location} with energy {energy}")

    script = f"""
import bpy

# Create sun light
bpy.ops.object.light_add(type='SUN', location={location})
light_obj = bpy.context.active_object
light_obj.name = "{name}"
light = light_obj.data
light.name = "{name}_data"

# Set rotation (convert degrees to radians)
light_obj.rotation_euler = ({rotation[0]} * 3.14159/180, {rotation[1]} * 3.14159/180, {rotation[2]} * 3.14159/180)

# Set light properties
light.energy = {energy}
light.color = {color}
light.shadow_soft_size = {shadow_soft_size}

logger.info(f"Created sun light: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created sun light '{name}'"


@blender_operation("create_point_light")
async def create_point_light(
    name: str = "Point",
    location: Tuple[float, float, float] = (0, 0, 5),
    energy: float = 1000.0,
    color: Tuple[float, float, float] = (1, 1, 1),
) -> str:
    """
    Create a point (omnidirectional) light.

    Args:
        name: Name for the light
        location: Light position
        energy: Light intensity
        color: Light color (RGB 0-1)

    Returns:
        Success message
    """
    logger.info(f"Creating point light '{name}' at {location} with energy {energy}")

    script = f"""
import bpy

# Create point light
bpy.ops.object.light_add(type='POINT', location={location})
light_obj = bpy.context.active_object
light_obj.name = "{name}"
light = light_obj.data
light.name = "{name}_data"

# Set light properties
light.energy = {energy}
light.color = {color}

logger.info(f"Created point light: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created point light '{name}'"


@blender_operation("create_spot_light")
async def create_spot_light(
    name: str = "Spot",
    location: Tuple[float, float, float] = (0, 0, 5),
    rotation: Tuple[float, float, float] = (0, 0, 0),
    energy: float = 1000.0,
    color: Tuple[float, float, float] = (1, 1, 1),
    spot_size: float = 45.0,
    spot_blend: float = 0.15,
) -> str:
    """
    Create a spot light.

    Args:
        name: Name for the light
        location: Light position
        rotation: Light rotation angles in degrees
        energy: Light intensity
        color: Light color (RGB 0-1)
        spot_size: Beam angle in degrees
        spot_blend: Edge softness

    Returns:
        Success message
    """
    logger.info(f"Creating spot light '{name}' at {location} with energy {energy}")

    script = f"""
import bpy

# Create spot light
bpy.ops.object.light_add(type='SPOT', location={location})
light_obj = bpy.context.active_object
light_obj.name = "{name}"
light = light_obj.data
light.name = "{name}_data"

# Set rotation (convert degrees to radians)
light_obj.rotation_euler = ({rotation[0]} * 3.14159/180, {rotation[1]} * 3.14159/180, {rotation[2]} * 3.14159/180)

# Set light properties
light.energy = {energy}
light.color = {color}
light.spot_size = {spot_size} * 3.14159/180  # Convert degrees to radians
light.spot_blend = {spot_blend}

logger.info(f"Created spot light: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created spot light '{name}'"


@blender_operation("create_area_light")
async def create_area_light(
    name: str = "Area",
    location: Tuple[float, float, float] = (0, 0, 5),
    rotation: Tuple[float, float, float] = (0, 0, 0),
    energy: float = 100.0,
    color: Tuple[float, float, float] = (1, 1, 1),
    size: float = 1.0,
) -> str:
    """
    Create an area light.

    Args:
        name: Name for the light
        location: Light position
        rotation: Light rotation angles in degrees
        energy: Light intensity
        color: Light color (RGB 0-1)
        size: Light size

    Returns:
        Success message
    """
    logger.info(f"Creating area light '{name}' at {location} with energy {energy}")

    script = f"""
import bpy

# Create area light
bpy.ops.object.light_add(type='AREA', location={location})
light_obj = bpy.context.active_object
light_obj.name = "{name}"
light = light_obj.data
light.name = "{name}_data"

# Set rotation (convert degrees to radians)
light_obj.rotation_euler = ({rotation[0]} * 3.14159/180, {rotation[1]} * 3.14159/180, {rotation[2]} * 3.14159/180)

# Set light properties
light.energy = {energy}
light.color = {color}
light.size = {size}

logger.info(f"Created area light: {name}")
"""
    result = await _executor.execute_script(script)
    return f"Created area light '{name}'"


@blender_operation("setup_three_point_lighting")
async def setup_three_point_lighting() -> str:
    """
    Set up basic three-point lighting rig.

    Returns:
        Success message
    """
    logger.info("Setting up three-point lighting")

    script = """
import bpy

# Key light (main)
bpy.ops.object.light_add(type='SUN', location=(5, -5, 5))
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.rotation_euler = (0.785, 0, 0.785)  # 45 degrees
key_light.data.energy = 3.0

# Fill light
bpy.ops.object.light_add(type='POINT', location=(-3, 3, 2))
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 1.5
fill_light.data.color = (0.8, 0.9, 1.0)  # Slightly blue

# Rim light
bpy.ops.object.light_add(type='SPOT', location=(0, -8, 3))
rim_light = bpy.context.active_object
rim_light.name = "Rim_Light"
rim_light.rotation_euler = (0.5, 0, 0)
rim_light.data.energy = 2.0
rim_light.data.spot_size = 1.0  # Narrow beam

logger.info("Created three-point lighting setup")
"""
    result = await _executor.execute_script(script)
    return "Created three-point lighting setup (Key, Fill, Rim lights)"


@blender_operation("setup_hdri_environment")
async def setup_hdri_environment() -> str:
    """
    Set up HDRI environment lighting.

    Returns:
        Success message
    """
    logger.info("Setting up HDRI environment lighting")

    script = """
import bpy

# Create world with HDRI nodes
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("HDRI_World")
    bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links

# Clear existing nodes
for node in nodes:
    nodes.remove(node)

# Create HDRI nodes
tex_coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
env_tex = nodes.new(type='ShaderNodeTexEnvironment')
background = nodes.new(type='ShaderNodeBackground')
output = nodes.new(type='ShaderNodeOutputWorld')

# Link nodes
links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
links.new(env_tex.outputs['Color'], background.inputs['Color'])
links.new(background.outputs['Background'], output.inputs['Surface'])

# Note: User needs to load actual HDRI texture file
print("Set up HDRI environment lighting (add HDRI texture file to Environment Texture node)")
"""
    result = await _executor.execute_script(script)
    return "Set up HDRI environment lighting (add HDRI texture file to Environment Texture node)"


@blender_operation("adjust_light")
async def adjust_light(
    name: str,
    location: Optional[Tuple[float, float, float]] = None,
    rotation: Optional[Tuple[float, float, float]] = None,
    energy: Optional[float] = None,
    color: Optional[Tuple[float, float, float]] = None,
) -> str:
    """
    Adjust properties of existing light.

    Args:
        name: Name of light to adjust
        location: New position (optional)
        rotation: New rotation angles in degrees (optional)
        energy: New intensity (optional)
        color: New color (optional)

    Returns:
        Success message
    """
    logger.info(f"Adjusting light '{name}' - location: {location}, energy: {energy}")

    location_str = f"light_obj.location = {location}" if location else ""
    rotation_str = (
        f"light_obj.rotation_euler = ({rotation[0]} * 3.14159/180, {rotation[1]} * 3.14159/180, {rotation[2]} * 3.14159/180)"
        if rotation
        else ""
    )
    energy_str = f"light.energy = {energy}" if energy is not None else ""
    color_str = f"light.color = {color}" if color else ""

    script = f"""
import bpy

# Find light
light_obj = bpy.data.objects.get("{name}")
if not light_obj or light_obj.type != 'LIGHT':
    raise ValueError(f"Light '{{name}}' not found")

light = light_obj.data

# Apply adjustments
{location_str}
{rotation_str}
{energy_str}
{color_str}

print(f"Adjusted light: {{name}}")
"""
    result = await _executor.execute_script(script)
    return f"Adjusted light '{name}' properties"

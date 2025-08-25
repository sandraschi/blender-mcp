from ..compat import *

"""Lighting operations handler for Blender MCP.

This module provides lighting creation and manipulation functions that can be registered as FastMCP tools.
"""

from typing import Optional, Tuple, Dict, Any, Union, Literal
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

# Initialize the executor with default Blender executable
_executor = get_blender_executor()

class LightType(str, Enum):
    """Supported light types."""
    POINT = "POINT"
    SUN = "SUN"
    SPOT = "SPOT"
    AREA = "AREA"

@blender_operation("create_light", log_args=True)
async def create_light(
    name: str = "Light",
    light_type: Union[LightType, str] = LightType.POINT,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    energy: float = 10.0,
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a light in the scene.
    
    Args:
        name: Name for the light object
        light_type: Type of light (POINT, SUN, SPOT, AREA)
        location: Light location (x, y, z)
        rotation: Light rotation in radians (x, y, z)
        energy: Light energy (intensity)
        color: Light color (RGB, 0.0-1.0)
        **kwargs: Additional light properties
            - radius: For point/spot lights
            - angle: For spot lights (in radians)
            - size: For area lights (size in Blender units)
            - size_x, size_y: For rectangular area lights
            - blend_factor: For soft shadows
            
    Returns:
        Dict containing operation status and light details
    """
    # Handle light-specific parameters
    radius = kwargs.get('radius', 0.0)
    angle = kwargs.get('angle', 0.0)
    size = kwargs.get('size', 0.1)
    size_x = kwargs.get('size_x', size)
    size_y = kwargs.get('size_y', size)
    blend_factor = kwargs.get('blend_factor', 0.2)
    
    script = f"""
import math
from mathutils import Color, Euler

def create_light():
    # Create light data
    light_data = bpy.data.lights.new(name='{name}_data', type='{light_type}')
    light_data.energy = {energy}
    light_data.color = {list(color)}
    
    # Set light type specific properties
    if '{light_type}' in ['POINT', 'SPOT']:
        light_data.shadow_soft_size = {radius}
    
    if '{light_type}' == 'SPOT':
        light_data.spot_size = {angle}
        light_data.spot_blend = {blend_factor}
    
    if '{light_type}' == 'AREA':
        light_data.size = {size_x}
        if {size_x} != {size_y}:
            light_data.shape = 'RECTANGLE'
            light_data.size_y = {size_y}
    
    # Create light object
    light = bpy.data.objects.new('{name}', light_data)
    light.location = {list(location)}
    light.rotation_euler = {list(rotation)}
    
    # Link to scene
    bpy.context.collection.objects.link(light)
    return light

try:
    light = create_light()
    result = {{
        'status': 'SUCCESS',
        'light_name': light.name,
        'light_type': '{light_type}',
        'location': {list(location)},
        'rotation': {list(rotation)},
        'energy': {energy},
        'color': {list(color)}
    }}
    if '{light_type}' in ['POINT', 'SPOT']:
        result['radius'] = {radius}
    if '{light_type}' == 'SPOT':
        result.update({{
            'angle': {angle},
            'blend_factor': {blend_factor}
        }})
    if '{light_type}' == 'AREA':
        result.update({{
            'size_x': {size_x},
            'size_y': {size_y}
        }})
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(str(result))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create light: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("set_light_energy", log_args=True)
async def set_light_energy(
    light_name: str,
    energy: float,
    **kwargs: Any
) -> Dict[str, Any]:
    """Set the energy (intensity) of a light.
    
    Args:
        light_name: Name of the light object
        energy: Light energy value
        **kwargs: Additional parameters
            
    Returns:
        Dict containing operation status
    """
    script = f"""

light = bpy.data.objects.get('{light_name}')
if light and light.type == 'LIGHT':
    light.data.energy = {energy}
    print({{'status': 'SUCCESS', 'light': light.name, 'energy': {energy}}})
else:
    print({{'status': 'ERROR', 'error': 'Light not found or invalid'}})
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to set light energy: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("set_light_color", log_args=True)
async def set_light_color(
    light_name: str,
    color: Tuple[float, float, float],
    **kwargs: Any
) -> Dict[str, Any]:
    """Set the color of a light.
    
    Args:
        light_name: Name of the light object
        color: RGB color values (0.0-1.0)
        **kwargs: Additional parameters
            
    Returns:
        Dict containing operation status
    """
    script = f"""
from mathutils import Color

light = bpy.data.objects.get('{light_name}')
if light and light.type == 'LIGHT':
    light.data.color = {list(color)}
    print({{'status': 'SUCCESS', 'light': light.name, 'color': {list(color)}}})
else:
    print({{'status': 'ERROR', 'error': 'Light not found or invalid'}})
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to set light color: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

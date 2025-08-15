"""Camera operations handler for Blender MCP.

This module provides camera creation and manipulation functions that can be registered as FastMCP tools.
"""

from typing import Optional, Tuple, Dict, Any, Union, Literal
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

# Initialize the executor with default Blender executable
_executor = get_blender_executor()

class CameraType(str, Enum):
    """Supported camera types."""
    PERSP = "PERSP"
    ORTHO = "ORTHO"
    PANO = "PANO"

@blender_operation("create_camera", log_args=True)
async def create_camera(
    name: str = "Camera",
    camera_type: Union[CameraType, str] = CameraType.PERSP,
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    lens: float = 50.0,
    sensor_width: float = 36.0,
    clip_start: float = 0.1,
    clip_end: float = 100.0,
    sensor_fit: str = "AUTO",
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a camera in the scene.
    
    Args:
        name: Name for the camera object
        camera_type: Type of camera (PERSP, ORTHO, PANO)
        location: Camera location (x, y, z)
        rotation: Camera rotation in radians (x, y, z)
        lens: Focal length in millimeters
        sensor_width: Sensor width in millimeters
        clip_start: Near clipping distance
        clip_end: Far clipping distance
        sensor_fit: Sensor fit mode (AUTO, HORIZONTAL, VERTICAL)
        **kwargs: Additional camera properties
            
    Returns:
        Dict containing operation status and camera details
    """
    script = f"""
import bpy
import math
from mathutils import Euler

# Create new camera
def create_camera():
    # Create camera data
    cam_data = bpy.data.cameras.new(name='{name}_data')
    cam_data.lens = {lens}
    cam_data.sensor_width = {sensor_width}
    cam_data.clip_start = {clip_start}
    cam_data.clip_end = {clip_end}
    cam_data.sensor_fit = '{sensor_fit}'
    
    # Set camera type
    cam_data.type = '{camera_type}'
    
    # Create camera object
    cam_obj = bpy.data.objects.new('{name}', cam_data)
    cam_obj.location = {list(location)}
    cam_obj.rotation_euler = {list(rotation)}
    
    # Link to scene
    bpy.context.collection.objects.link(cam_obj)
    
    # Set as active camera if no active camera exists
    if not bpy.context.scene.camera:
        bpy.context.scene.camera = cam_obj
    
    return cam_obj

# Execute creation
try:
    camera = create_camera()
    result = {{
        'status': 'SUCCESS',
        'camera_name': camera.name,
        'camera_type': '{camera_type}',
        'location': {list(location)},
        'rotation': {list(rotation)},
        'lens': {lens},
        'sensor_width': {sensor_width}
    }}
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
        logger.error(f"Failed to create camera: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("set_active_camera", log_args=True)
async def set_active_camera(
    camera_name: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Set the active camera for the scene.
    
    Args:
        camera_name: Name of the camera to set as active
        **kwargs: Additional parameters
            
    Returns:
        Dict containing operation status
    """
    script = f"""
import bpy

camera = bpy.data.objects.get('{camera_name}')
if camera and camera.type == 'CAMERA':
    bpy.context.scene.camera = camera
    print({{'status': 'SUCCESS', 'camera': camera.name}})
else:
    print({{'status': 'ERROR', 'error': 'Camera not found or invalid'}})
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to set active camera: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("set_camera_lens", log_args=True)
async def set_camera_lens(
    camera_name: str,
    lens: float,
    **kwargs: Any
) -> Dict[str, Any]:
    """Set the lens/focal length of a camera.
    
    Args:
        camera_name: Name of the camera
        lens: Focal length in millimeters
        **kwargs: Additional parameters
            
    Returns:
        Dict containing operation status
    """
    script = f"""
import bpy

camera = bpy.data.objects.get('{camera_name}')
if camera and camera.type == 'CAMERA':
    camera.data.lens = {lens}
    print({{'status': 'SUCCESS', 'camera': camera.name, 'lens': {lens}}})
else:
    print({{'status': 'ERROR', 'error': 'Camera not found or invalid'}})
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to set camera lens: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

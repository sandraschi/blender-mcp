from ..compat import *

"""UV mapping operations handler for Blender MCP."""

from typing import Optional, List, Dict, Any, Tuple, Union
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()

class UVUnwrapMethod(str, Enum):
    """UV unwrapping methods."""
    ANGLE_BASED = "ANGLE_BASED"
    CONFORMAL = "CONFORMAL"
    SMART = "SMART"

class UVProjectionMethod(str, Enum):
    """UV projection methods."""
    VIEW = "VIEW"
    SPHERE = "SPHERE"
    CYLINDER = "CYLINDER"
    CUBE = "CUBE"
    CLIP = "CLIP"

@blender_operation("unwrap", log_args=True)
async def unwrap(
    object_name: str,
    method: Union[UVUnwrapMethod, str] = UVUnwrapMethod.SMART,
    seam_margin: float = 66.0,
    fill_holes: bool = True,
    correct_aspect: bool = True,
    use_subsurf_data: bool = False,
    margin: float = 0.001
) -> Dict[str, Any]:
    """Unwrap the mesh for UV mapping.
    
    Args:
        object_name: Name of the object to unwrap
        method: Unwrapping method to use
        seam_margin: For angle-based unwrapping, angle limit (default: 66.0)
        fill_holes: Fill holes in the UV map (default: True)
        correct_aspect: Correct UV aspect (default: True)
        use_subsurf_data: Use subdivision surface data (default: False)
        margin: Space between UV islands (default: 0.001)
            
    Returns:
        Dict containing unwrap status and details
    """
    script = f"""

def unwrap_mesh():
    obj = bpy.data.objects.get('{object_name}')
    if not obj or obj.type != 'MESH':
        return {{"status": "ERROR", "error": "Mesh object not found"}}
    
    # Make the object active and in edit mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select all faces for unwrapping
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Perform the unwrap
    try:
        if '{method}' == 'SMART':
            bpy.ops.uv.smart_project(
                angle_limit={seam_margin * (3.14159265359 / 180.0)},
                margin={margin},
                correct_aspect={str(correct_aspect).lower()},
                use_subsurf_data={str(use_subsurf_data).lower()}
            )
        elif '{method}' == 'ANGLE_BASED':
            bpy.ops.uv.unwrap(
                method='ANGLE_BASED',
                margin={margin},
                correct_aspect={str(correct_aspect).lower()},
                use_subsurf_data={str(use_subsurf_data).lower()}
            )
        elif '{method}' == 'CONFORMAL':
            bpy.ops.uv.unwrap(
                method='CONFORMAL',
                margin={margin},
                correct_aspect={str(correct_aspect).lower()},
                use_subsurf_data={str(use_subsurf_data).lower()}
            )
        else:
            return {{"status": "ERROR", "error": f"Unsupported unwrap method: {method}"}}
        
        # Fill holes if requested
        if {str(fill_holes).lower()} and '{method}' != 'SMART':
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.pack_islands(margin={margin})
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return {{
            "status": "SUCCESS",
            "method": '{method}',
            "object": obj.name,
            "margin": {margin},
            "seam_margin": {seam_margin},
            "fill_holes": {str(fill_holes).lower()},
            "correct_aspect": {str(correct_aspect).lower()},
            "use_subsurf_data": {str(use_subsurf_data).lower()}
        }}
    except Exception as e:
        bpy.ops.object.mode_set(mode='OBJECT')
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = unwrap_mesh()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to unwrap UVs: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("project_from_view", log_args=True)
async def project_from_view(
    object_name: str,
    camera_name: Optional[str] = None,
    orthographic: bool = False,
    margin: float = 0.0
) -> Dict[str, Any]:
    """Project UVs from the current view or camera.
    
    Args:
        object_name: Name of the object to project UVs for
        camera_name: Optional camera to use for projection
        orthographic: Use orthographic projection (default: False)
        margin: Space between UV islands (default: 0.0)
            
    Returns:
        Dict containing projection status and details
    """
    script = f"""

def project_uvs():
    obj = bpy.data.objects.get('{object_name}')
    if not obj or obj.type != 'MESH':
        return {{"status": "ERROR", "error": "Mesh object not found"}}
    
    # Store current active object and mode
    prev_active = bpy.context.view_layer.objects.active
    prev_mode = obj.mode if obj.mode else 'OBJECT'
    
    # Make the object active and in edit mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select all faces for projection
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Set the camera if specified
    camera = None
    if '{camera_name}':
        camera = bpy.data.objects.get('{camera_name}')
        if not camera or camera.type != 'CAMERA':
            return {{"status": "ERROR", "error": "Camera not found"}}
        
        # Store current camera
        prev_camera = bpy.context.scene.camera
        bpy.context.scene.camera = camera
    
    try:
        # Project from view or camera
        bpy.ops.uv.project_from_view(
            orthographic={str(orthographic).lower()},
            camera_bounds=True,
            correct_aspect=True,
            scale_to_bounds=True,
            margin={margin}
        )
        
        # Return to object mode
        bpy.ops.object.mode_set(mode=prev_mode)
        
        # Restore previous camera if changed
        if '{camera_name}' and camera:
            bpy.context.scene.camera = prev_camera
        
        # Restore previous active object
        if prev_active:
            bpy.context.view_layer.objects.active = prev_active
        
        return {{
            "status": "SUCCESS",
            "object": obj.name,
            "camera": camera.name if camera else 'ACTIVE_VIEW',
            "orthographic": {str(orthographic).lower()},
            "margin": {margin}
        }}
    except Exception as e:
        # Clean up in case of error
        bpy.ops.object.mode_set(mode=prev_mode)
        if '{camera_name}' and camera and 'prev_camera' in locals():
            bpy.context.scene.camera = prev_camera
        if prev_active:
            bpy.context.view_layer.objects.active = prev_active
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = project_uvs()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    
    try:
        result = await _executor.execute_script(script)
        return result
    except Exception as e:
        logger.error(f"Failed to project UVs: {str(e)}")
        return {{"status": "ERROR", "error": str(e)}}

@blender_operation("reset_uvs", log_args=True)
async def reset_uvs(
    object_name: str
) -> Dict[str, Any]:
    """Reset UV coordinates to default.
    
    Args:
        object_name: Name of the object to reset UVs for
        
    Returns:
        Dict containing reset status
    """
    script = f"""

def reset_uvs():
    obj = bpy.data.objects.get('{object_name}')
    if not obj or obj.type != 'MESH':
        return {{"status": "ERROR", "error": "Mesh object not found"}}
    
    # Store current mode
    current_mode = obj.mode
    
    try:
        # Make sure we're in object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Get the mesh data
        mesh = obj.data
        
        # Ensure UV layer exists
        if not mesh.uv_layers:
            mesh.uv_layers.new()
        
        # Reset UVs to default (0-1 range)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.reset()
        bpy.ops.object.mode_set(mode=current_mode)
        
        return {{
            "status": "SUCCESS",
            "object": obj.name,
            "uv_layers": [uv.name for uv in mesh.uv_layers]
        }}
    except Exception as e:
        # Ensure we return to the original mode on error
        if obj.mode != current_mode:
            bpy.ops.object.mode_set(mode=current_mode)
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = reset_uvs()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to reset UVs: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("get_uv_info", log_args=True)
async def get_uv_info(
    object_name: str
) -> Dict[str, Any]:
    """Get information about UV mapping for an object.
    
    Args:
        object_name: Name of the object to get UV info for
        
    Returns:
        Dict containing UV information
    """
    script = f"""

def get_uv_data():
    obj = bpy.data.objects.get('{object_name}')
    if not obj or obj.type != 'MESH':
        return {{"status": "ERROR", "error": "Mesh object not found"}}
    
    # Store current active object and mode
    prev_active = bpy.context.view_layer.objects.active
    prev_mode = obj.mode if obj.mode else 'OBJECT'
    
    result = {{
        "status": "SUCCESS",
        "object": obj.name,
        "uv_layers": [],
        "active_uv_layer": obj.data.uv_layers.active.name if obj.data.uv_layers.active else None
    }}
    
    # Get UV layer information
    for uv_layer in obj.data.uv_layers:
        result["uv_layers"].append({{
            "name": uv_layer.name,
            "active_render": uv_layer.active_render,
            "active_clone": uv_layer.active_clone,
            "active": uv_layer == obj.data.uv_layers.active
        }})
    
    # Restore previous state
    if prev_active:
        bpy.context.view_layer.objects.active = prev_active
    
    return result

try:
    result = get_uv_data()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    
    try:
        result = await _executor.execute_script(script)
        return result
    except Exception as e:
        logger.error(f"Failed to get UV info: {str(e)}")
        return {{"status": "ERROR", "error": str(e)}}

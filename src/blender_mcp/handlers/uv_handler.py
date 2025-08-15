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
    **kwargs: Any
) -> Dict[str, Any]:
    """Unwrap the mesh for UV mapping.
    
    Args:
        object_name: Name of the object to unwrap
        method: Unwrapping method to use
        **kwargs: Additional unwrap parameters
            - seam_margin: For angle-based unwrapping, angle limit (default: 66.0)
            - fill_holes: Fill holes in the UV map (default: True)
            - correct_aspect: Correct UV aspect (default: True)
            - use_subsurf_data: Use subdivision surface data (default: False)
            - margin: Space between UV islands (default: 0.001)
            
    Returns:
        Dict containing unwrap status and details
    """
    # Get parameters with defaults
    seam_margin = kwargs.get('seam_margin', 66.0)
    fill_holes = kwargs.get('fill_holes', True)
    correct_aspect = kwargs.get('correct_aspect', True)
    use_subsurf_data = kwargs.get('use_subsurf_data', False)
    margin = kwargs.get('margin', 0.001)
    
    script = f"""
import bpy

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
                correct_aspect={str(correct_aspect).lower()}
            )
        elif '{method}' == 'ANGLE_BASED':
            bpy.ops.uv.unwrap(
                method='ANGLE_BASED',
                margin={margin},
                correct_aspect={str(correct_aspect).lower()}
            )
        elif '{method}' == 'CONFORMAL':
            bpy.ops.uv.unwrap(
                method='CONFORMAL',
                margin={margin},
                correct_aspect={str(correct_aspect).lower()}
            )
        else:
            return {{"status": "ERROR", "error": f"Unsupported unwrap method: {{method}}"}}
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return {{
            "status": "SUCCESS",
            "method": '{method}',
            "object": obj.name,
            "margin": {margin}
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
    **kwargs: Any
) -> Dict[str, Any]:
    """Project UVs from the current view or camera.
    
    Args:
        object_name: Name of the object to project UVs for
        camera_name: Optional camera to use for projection
        **kwargs: Additional projection parameters
            - orthographic: Use orthographic projection (default: False)
            - margin: Space between UV islands (default: 0.0)
            
    Returns:
        Dict containing projection status and details
    """
    orthographic = kwargs.get('orthographic', False)
    margin = kwargs.get('margin', 0.0)
    
    script = f"""
import bpy

def project_from_view():
    obj = bpy.data.objects.get('{object_name}')
    if not obj or obj.type != 'MESH':
        return {{"status": "ERROR", "error": "Mesh object not found"}}
    
    # Store current view settings
    current_mode = obj.mode
    current_area = bpy.context.area
    current_region = bpy.context.region
    
    try:
        # Set up view if camera is specified
        if '{camera_name}':
            cam = bpy.data.objects.get('{camera_name}')
            if not cam or cam.type != 'CAMERA':
                return {{"status": "ERROR", "error": "Camera not found"}}
            
            # Store current camera
            current_camera = bpy.context.scene.camera
            bpy.context.scene.camera = cam
        
        # Make the object active and in edit mode
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Select all faces for projection
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Project from view
        bpy.ops.uv.project_from_view(
            orthographic={str(orthographic).lower()},
            camera_bounds=True,
            correct_aspect=True,
            scale_to_bounds=True,
            margin={margin}
        )
        
        # Return to object mode
        bpy.ops.object.mode_set(mode=current_mode)
        
        # Restore camera if changed
        if '{camera_name}' and 'current_camera' in locals():
            bpy.context.scene.camera = current_camera
        
        return {{
            "status": "SUCCESS",
            "object": obj.name,
            "camera": '{camera_name}' if '{camera_name}' else 'ACTIVE_VIEW',
            "orthographic": {str(orthographic).lower()},
            "margin": {margin}
        }}
    except Exception as e:
        # Ensure we return to object mode on error
        if obj.mode != current_mode:
            bpy.ops.object.mode_set(mode=current_mode)
        # Restore camera if changed
        if '{camera_name}' and 'current_camera' in locals():
            bpy.context.scene.camera = current_camera
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = project_from_view()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to project UVs from view: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("reset_uvs", log_args=True)
async def reset_uvs(
    object_name: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Reset UV coordinates to default.
    
    Args:
        object_name: Name of the object to reset UVs for
        
    Returns:
        Dict containing reset status
    """
    script = f"""
import bpy

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
    object_name: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Get information about UV mapping for an object.
    
    Args:
        object_name: Name of the object to get UV info for
        
    Returns:
        Dict containing UV information
    """
    script = f"""
import bpy

def get_uv_info():
    obj = bpy.data.objects.get('{object_name}')
    if not obj or obj.type != 'MESH':
        return {{"status": "ERROR", "error": "Mesh object not found"}}
    
    mesh = obj.data
    
    # Get UV layer information
    uv_layers = []
    for i, uv_layer in enumerate(mesh.uv_layers):
        uv_layers.append({{
            "name": uv_layer.name,
            "active": uv_layer.active,
            "active_render": uv_layer.active_render,
            "index": i
        }})
    
    # Get active UV layer index
    active_uv_index = mesh.uv_layers.active_index if mesh.uv_layers.active else -1
    
    # Count UV vertices and faces
    uv_vertex_count = 0
    uv_face_count = 0
    uv_bounds = None
    
    if mesh.uv_layers.active and mesh.polygons:
        # Get UV coordinates
        uv_layer = mesh.uv_layers.active.data
        uv_vertex_count = len(uv_layer)
        uv_face_count = len(mesh.polygons)
        
        # Calculate UV bounds
        min_u = min(uv.uv[0] for uv in uv_layer)
        max_u = max(uv.uv[0] for uv in uv_layer)
        min_v = min(uv.uv[1] for uv in uv_layer)
        max_v = max(uv.uv[1] for uv in uv_layer)
        
        uv_bounds = {{
            "min_u": min_u,
            "max_u": max_u,
            "min_v": min_v,
            "max_v": max_v,
            "width": max_u - min_u,
            "height": max_v - min_v
        }}
    
    return {{
        "status": "SUCCESS",
        "object": obj.name,
        "uv_layers": uv_layers,
        "active_uv_index": active_uv_index,
        "uv_vertex_count": uv_vertex_count,
        "uv_face_count": uv_face_count,
        "uv_bounds": uv_bounds
    }}

try:
    result = get_uv_info()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to get UV info: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

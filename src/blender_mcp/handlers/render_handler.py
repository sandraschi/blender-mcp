"""Render handler for Blender MCP server.

This module provides rendering functions that can be registered as FastMCP tools.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation
from ..exceptions import BlenderRenderError
from ..app import app

# Initialize the executor with default Blender executable
_executor = get_blender_executor()

@app.tool
@blender_operation("render_turntable", log_args=True)
async def render_turntable(
    output_dir: str,
    frames: int = 60,
    resolution_x: int = 1280,
    resolution_y: int = 720,
    format: str = "PNG"
) -> str:
    """Render 360-degree turntable animation of the current scene.
    
    Args:
        output_dir: Directory where rendered frames will be saved
        frames: Number of frames for the animation (default: 60)
        resolution_x: Horizontal resolution in pixels (default: 1280)
        resolution_y: Vertical resolution in pixels (default: 720)
        format: Output image format (default: "PNG")
        
    Returns:
        str: Success message with render details
        
    Raises:
        BlenderRenderError: If rendering fails
    """
    try:
        # Ensure output directory exists
        output_dir = str(Path(output_dir).absolute())
        os.makedirs(output_dir, exist_ok=True)
        
        script = f"""
import os
import math
from mathutils import Vector

try:
    scene = bpy.context.scene
    
    # Setup animation
    scene.frame_start = 1
    scene.frame_end = {frames}
    scene.frame_current = 1
    
    # Find or create camera
    camera = scene.camera
    if not camera:
        # Create a new camera if none exists
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW')
        camera = bpy.context.active_object
        scene.camera = camera
        
        # Position camera to see the entire scene
        camera.location = (5.0, -5.0, 3.0)
        camera.rotation_euler = (1.0, 0, 0.8)
        
        # Create empty at origin for camera to look at
        bpy.ops.object.empty_add(location=(0, 0, 0))
        empty = bpy.context.active_object
        empty.name = 'CameraTarget'
        
        # Add track-to constraint
        constraint = camera.constraints.new(type='TRACK_TO')
        constraint.target = empty
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
    
    # Set render settings
    scene.render.resolution_x = {resolution_x}
    scene.render.resolution_y = {resolution_y}
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = '{format}'
    
    # Ensure output directory exists
    os.makedirs(r"{output_dir}", exist_ok=True)
    scene.render.filepath = os.path.join(r"{output_dir}", 'turntable_')
    
    # Setup animation to rotate camera around the scene
    for frame in range(1, {frames} + 1):
        scene.frame_set(frame)
        angle = (frame / {frames}) * 2 * math.pi
        radius = 5.0  # Fixed distance from center
        
        # Calculate camera position in a circle around the origin
        camera.location.x = radius * math.cos(angle)
        camera.location.y = radius * math.sin(angle)
        camera.location.z = 3.0  # Fixed height
        
        # Insert keyframe
        camera.keyframe_insert(data_path="location", frame=frame)
    
    # Render animation
    print(f"Rendering {{frames}} frame turntable to {{r'{output_dir}'}}")
    bpy.ops.render.render(animation=True)
    
    print("SUCCESS: Turntable animation rendered!")
    return True

except Exception as e:
    print(f"ERROR: Failed to render turntable: {{str(e)}}")
    raise e
"""

        await _executor.execute_script(script)
        return f"Rendered {frames}-frame turntable animation to {output_dir}"
        
    except Exception as e:
        raise BlenderRenderError("turntable_animation", f"Failed to render turntable: {str(e)}")

@app.tool
@blender_operation("render_preview", log_args=True)
async def render_preview(
    output_path: str,
    resolution_x: int = 1920,
    resolution_y: int = 1080,
    samples: int = 256,
    use_denoising: bool = True,
    use_adaptive_sampling: bool = True,
    format: str = "PNG",
    quality: int = 90,
    camera_name: Optional[str] = None,
    use_environment: bool = True,
    use_film_transparent: bool = False
) -> str:
    """Render a high-quality preview of the current scene.
    
    Args:
        output_path: Full path where the rendered image will be saved
        resolution_x: Horizontal resolution in pixels (default: 1920)
        resolution_y: Vertical resolution in pixels (default: 1080)
        samples: Number of samples per pixel (default: 256)
        use_denoising: Whether to use AI denoising (default: True)
        use_adaptive_sampling: Whether to use adaptive sampling (default: True)
        format: Output image format (default: "PNG")
        quality: Output quality (1-100) for lossy formats (default: 90)
        camera_name: Name of the camera to use (default: active camera)
        use_environment: Whether to use environment lighting (default: True)
        use_film_transparent: Whether to render with transparent background (default: False)
        
    Returns:
        str: Success message with render details
        
    Raises:
        BlenderRenderError: If rendering fails or camera is not found
    """
    try:
        # Ensure output directory exists
        output_path = str(Path(output_path).absolute())
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        script = f"""
import os
from mathutils import Vector

try:
    scene = bpy.context.scene
    
    # Set active camera if specified
    if "{camera_name}" and "{camera_name}" in bpy.data.objects and bpy.data.objects["{camera_name}"].type == 'CAMERA':
        scene.camera = bpy.data.objects["{camera_name}"]
    
    # Verify camera exists
    if not scene.camera:
        raise Exception("No camera found in the scene")
    
    # Set render engine to Cycles for best quality
    scene.render.engine = 'CYCLES'
    
    # Configure Cycles settings
    cycles = scene.cycles
    cycles.samples = {samples}
    cycles.use_denoising = {str(use_denoising).lower()}
    cycles.denoiser = 'OPTIX' if bpy.app.version >= (2, 90, 0) else 'NLM'
    cycles.use_adaptive_sampling = {str(use_adaptive_sampling).lower()}
    
    if use_adaptive_sampling:
        cycles.adaptive_threshold = 0.01
        cycles.adaptive_min_samples = 32
    
    # Configure render settings
    scene.render.resolution_x = {resolution_x}
    scene.render.resolution_y = {resolution_y}
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "{format}"
    scene.render.image_settings.quality = {quality}
    scene.render.film_transparent = {str(use_film_transparent).lower()}
    
    # Set color management for better color accuracy
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = 0.2
    scene.view_settings.gamma = 1.0
    
    # Configure film settings
    scene.render.film_transparent = {str(use_film_transparent).lower()}
    
    # Set output path
    scene.render.filepath = r"{output_path}"
    
    # Setup environment lighting if enabled
    if {str(use_environment).lower()} and not scene.world:
        # Create a simple environment world if none exists
        bpy.ops.world.new()
        scene.world = bpy.data.worlds['World']
        scene.world.use_nodes = True
        
        # Get the world nodes
        world_nodes = scene.world.node_tree.nodes
        world_links = scene.world.node_tree.links
        
        # Clear default nodes
        world_nodes.clear()
        
        # Add environment texture node
        bg_node = world_nodes.new('ShaderNodeBackground')
        env_tex = world_nodes.new('ShaderNodeTexEnvironment')
        output = world_nodes.new('ShaderNodeOutputWorld')
        
        # Link nodes
        world_links.new(env_tex.outputs['Color'], bg_node.inputs['Color'])
        world_links.new(bg_node.outputs['Background'], output.inputs['Surface'])
        
        # Set default environment strength
        bg_node.inputs['Strength'].default_value = 1.0
        
        # Position nodes
        env_tex.location = (-300, 0)
        bg_node.location = (-100, 0)
        output.location = (100, 0)
    
    # Ensure we're in rendered viewport shading
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'RENDERED'
    
    # Render the image
    print(f"Rendering preview to {{r'{output_path}'}}")
    bpy.ops.render.render(write_still=True)
    
    print("SUCCESS: Preview render complete!")
    return True

except Exception as e:
    print(f"ERROR: Failed to render preview: {{str(e)}}")
    raise e
"""
        # Execute the render script
        await _executor.execute_script(script, script_name="render_preview")
        return f"Rendered preview to {output_path}"
        
    except Exception as e:
        raise BlenderRenderError("preview_render", f"Failed to render preview: {str(e)}")

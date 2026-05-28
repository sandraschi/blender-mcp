"""Render handler for Blender MCP server.

This module provides rendering functions that can be registered as FastMCP tools.
"""

import os
from pathlib import Path

from ..compat import *
from ..decorators import blender_operation
from ..exceptions import BlenderRenderError
from ..utils.blender_executor import get_blender_executor

# Initialize the executor with default Blender executable
_executor = get_blender_executor()


@blender_operation("render_turntable", log_args=True)
async def render_turntable(
    output_dir: str,
    frames: int = 60,
    resolution_x: int = 1280,
    resolution_y: int = 720,
    format: str = "PNG",
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
        raise BlenderRenderError("turntable_animation", f"Failed to render turntable: {e!s}")


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
    camera_name: str | None = None,
    use_environment: bool = True,
    use_film_transparent: bool = False,
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
        raise BlenderRenderError("preview_render", f"Failed to render preview: {e!s}")


def _parse_script_lines(output: str) -> dict[str, str]:
    """Parse KEY: value lines printed by generated Blender scripts."""
    parsed: dict[str, str] = {}
    for line in (output or "").splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            parsed[key.strip()] = value.strip()
    return parsed


@blender_operation("screenshot_viewport", log_args=True)
async def screenshot_viewport(
    output_path: str,
    resolution_x: int = 1280,
    resolution_y: int = 720,
    shading_mode: str = "SOLID",
    prefer_session: bool = True,
) -> dict[str, Any]:
    """Capture the 3D viewport or a still render for agent vision feedback.

    Prefers a live Blender GUI session (bridge addon) so the user sees the same
    scene the agent is inspecting. Falls back to headless still render.
    """
    import base64
    from pathlib import Path

    from ..utils.blender_runtime import execute_bpy_script

    output_path = str(Path(output_path).absolute())
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    script = f"""
import os
import bpy

output_path = r"{output_path}"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
scene = bpy.context.scene
scene.render.resolution_x = {resolution_x}
scene.render.resolution_y = {resolution_y}
scene.render.filepath = output_path
scene.render.image_settings.file_format = 'PNG'

captured = False
if bpy.context.screen:
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    try:
                        space.shading.type = '{shading_mode}'
                    except Exception:
                        pass
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = bpy.context.copy()
                    override['area'] = area
                    override['region'] = region
                    with bpy.context.temp_override(**override):
                        bpy.ops.render.opengl(write_still=True)
                    captured = True
                    break
        if captured:
            break

if not captured or not os.path.exists(output_path):
    bpy.ops.render.render(write_still=True)

print("SCREENSHOT_PATH:" + output_path)
print("SCREENSHOT_MODE:" + ("viewport" if captured else "render"))
"""

    result = await execute_bpy_script(
        script,
        script_name="screenshot_viewport",
        timeout=90,
        prefer_session=prefer_session,
        headless_fallback=True,
    )
    if not result.get("success"):
        raise BlenderRenderError("screenshot_viewport", result.get("error") or "Capture failed")

    meta = _parse_script_lines(result.get("output", ""))
    image_path = meta.get("SCREENSHOT_PATH", output_path)
    payload: dict[str, Any] = {
        "success": True,
        "output_path": image_path,
        "capture_mode": meta.get("SCREENSHOT_MODE", result.get("mode", "unknown")),
        "session_used": result.get("session_used", False),
        "execution_mode": result.get("mode"),
        "resolution": [resolution_x, resolution_y],
    }
    try:
        image_bytes = Path(image_path).read_bytes()
        payload["image_base64"] = base64.b64encode(image_bytes).decode("ascii")
        payload["mime_type"] = "image/png"
    except OSError as exc:
        payload["warning"] = f"Image saved but could not read for base64: {exc}"
    return payload


@blender_operation("render_multi_angle", log_args=True)
async def render_multi_angle(
    output_dir: str,
    angles: int = 4,
    elevation_deg: float = 25.0,
    radius: float = 5.0,
    resolution_x: int = 1024,
    resolution_y: int = 1024,
    prefer_session: bool = True,
) -> dict[str, Any]:
    """Render the scene from multiple camera angles for vision / review loops."""
    import json
    from pathlib import Path

    from ..utils.blender_runtime import execute_bpy_script

    output_dir = str(Path(output_dir).absolute())
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    script = f"""
import json
import math
import os
import bpy

output_dir = r"{output_dir}"
angles = {angles}
elevation = math.radians({elevation_deg})
radius = {radius}
scene = bpy.context.scene
scene.render.resolution_x = {resolution_x}
scene.render.resolution_y = {resolution_y}
scene.render.image_settings.file_format = 'PNG'

cam = scene.camera
if not cam:
    bpy.ops.object.camera_add(location=(radius, -radius, radius * 0.6))
    cam = bpy.context.active_object
    scene.camera = cam

paths = []
for i in range(angles):
    angle = (i / angles) * 2 * math.pi
    x = radius * math.cos(angle) * math.cos(elevation)
    y = radius * math.sin(angle) * math.cos(elevation)
    z = radius * math.sin(elevation)
    cam.location = (x, y, z)
    import mathutils
    cam.rotation_euler = (mathutils.Vector((0.0, 0.0, 0.0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    frame_path = os.path.join(output_dir, f"angle_{{i:02d}}.png")
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    paths.append(frame_path)

print("MULTI_ANGLE_PATHS:" + json.dumps(paths))
"""

    result = await execute_bpy_script(
        script,
        script_name="render_multi_angle",
        timeout=max(120, angles * 45),
        prefer_session=prefer_session,
        headless_fallback=True,
    )
    if not result.get("success"):
        raise BlenderRenderError("render_multi_angle", result.get("error") or "Multi-angle render failed")

    meta = _parse_script_lines(result.get("output", ""))
    paths_raw = meta.get("MULTI_ANGLE_PATHS", "[]")
    try:
        paths = json.loads(paths_raw)
    except json.JSONDecodeError:
        paths = []

    return {
        "success": True,
        "output_dir": output_dir,
        "image_paths": paths,
        "angle_count": len(paths),
        "session_used": result.get("session_used", False),
        "execution_mode": result.get("mode"),
    }


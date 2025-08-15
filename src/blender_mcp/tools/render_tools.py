"""
Render Tools for Blender-MCP.

This module provides tools for advanced rendering controls and settings.
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from fastmcp.types import JSONType

from blender_mcp.handlers.render_handler import (
    set_render_engine,
    set_render_resolution,
    set_render_samples,
    set_render_denoising,
    setup_compositor,
    setup_light_paths,
    setup_motion_blur,
    setup_depth_of_field,
    setup_ambient_occlusion,
    setup_volumetrics,
    setup_render_output,
    render_animation,
    render_still,
    setup_gpu_rendering
)
from blender_mcp.tools import register_tool, validate_with
from blender_mcp.utils.error_handling import handle_errors
from blender_mcp.utils.validation import BaseValidator

# Enums
class RenderEngine(str, Enum):
    CYCLES = "CYCLES"
    EEVEE = "BLENDER_EEVEE"
    WORKBENCH = "BLENDER_WORKBENCH"

class DenoiserType(str, Enum):
    NONE = "NONE"
    OPENIMAGEDENOISE = "OPENIMAGEDENOISE"
    OPTIX = "OPTIX"

# Parameter Models
class RenderEngineParams(BaseValidator):
    engine: RenderEngine = Field(..., description="Render engine to use")

class RenderResolutionParams(BaseValidator):
    resolution_x: int = Field(1920, ge=1, le=32768)
    resolution_y: int = Field(1080, ge=1, le=32768)
    resolution_percentage: int = Field(100, ge=1, le=10000)

class RenderSamplesParams(BaseValidator):
    render_samples: int = Field(128, ge=1)
    preview_samples: int = Field(32, ge=1)
    use_adaptive_sampling: bool = Field(True)
    adaptive_threshold: float = Field(0.01, ge=0.0, le=1.0)

class DenoisingParams(BaseValidator):
    use_denoising: bool = Field(True)
    denoiser: DenoiserType = Field(DenoiserType.OPENIMAGEDENOISE)

class CompositorParams(BaseValidator):
    use_compositing: bool = Field(True)
    use_sequencer: bool = Field(False)
    use_nodes: bool = Field(True)

class LightPathsParams(BaseValidator):
    max_bounces: int = Field(12, ge=0)
    diffuse_bounces: int = Field(4, ge=0)
    glossy_bounces: int = Field(4, ge=0)
    transmission_bounces: int = Field(12, ge=0)
    volume_bounces: int = Field(0, ge=0)

class MotionBlurParams(BaseValidator):
    use_motion_blur: bool = Field(False)
    motion_blur_shutter: float = Field(0.5, ge=0.0)

class DepthOfFieldParams(BaseValidator):
    use_dof: bool = Field(False)
    focus_object: Optional[str] = Field(None)
    focus_distance: float = Field(10.0, gt=0.0)
    fstop: float = Field(2.8, gt=0.0)

class AmbientOcclusionParams(BaseValidator):
    use_ao: bool = Field(True)
    ao_factor: float = Field(1.0, ge=0.0)
    ao_distance: float = Field(0.2, gt=0.0)

class VolumetricsParams(BaseValidator):
    use_volumetrics: bool = Field(True)
    volumetric_samples: int = Field(64, ge=1)

class RenderOutputParams(BaseValidator):
    filepath: str = Field("//render_output")
    file_format: str = Field("PNG")
    color_mode: str = Field("RGBA")
    quality: int = Field(90, ge=0, le=100)

class RenderAnimationParams(BaseValidator):
    frame_start: int = Field(1)
    frame_end: int = Field(250)
    frame_step: int = Field(1, ge=1)

class GPURenderingParams(BaseValidator):
    use_gpu: bool = Field(True)
    device_type: str = Field("CUDA")

# Tool Definitions
@register_tool(name="set_render_engine", description="Set the render engine")
@handle_errors
@validate_with(RenderEngineParams)
async def set_render_engine_tool(params: Dict[str, Any]) -> JSONType:
    result = await set_render_engine(engine=params["engine"].value)
    return {"status": "SUCCESS", "result": result}

@register_tool(name="set_render_resolution", description="Set the render resolution")
@handle_errors
@validate_with(RenderResolutionParams)
async def set_render_resolution_tool(params: Dict[str, Any]) -> JSONType:
    result = await set_render_resolution(
        resolution_x=params["resolution_x"],
        resolution_y=params["resolution_y"],
        resolution_percentage=params["resolution_percentage"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="set_render_samples", description="Set the number of render samples")
@handle_errors
@validate_with(RenderSamplesParams)
async def set_render_samples_tool(params: Dict[str, Any]) -> JSONType:
    result = await set_render_samples(
        render_samples=params["render_samples"],
        preview_samples=params["preview_samples"],
        use_adaptive_sampling=params["use_adaptive_sampling"],
        adaptive_threshold=params["adaptive_threshold"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="set_render_denoising", description="Set render denoising settings")
@handle_errors
@validate_with(DenoisingParams)
async def set_render_denoising_tool(params: Dict[str, Any]) -> JSONType:
    result = await set_render_denoising(
        use_denoising=params["use_denoising"],
        denoiser=params["denoiser"].value
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="setup_compositor", description="Set up the compositor")
@handle_errors
@validate_with(CompositorParams)
async def setup_compositor_tool(params: Dict[str, Any]) -> JSONType:
    result = await setup_compositor(
        use_compositing=params["use_compositing"],
        use_sequencer=params["use_sequencer"],
        use_nodes=params["use_nodes"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="setup_light_paths", description="Set up light paths")
@handle_errors
@validate_with(LightPathsParams)
async def setup_light_paths_tool(params: Dict[str, Any]) -> JSONType:
    result = await setup_light_paths(
        max_bounces=params["max_bounces"],
        diffuse_bounces=params["diffuse_bounces"],
        glossy_bounces=params["glossy_bounces"],
        transmission_bounces=params["transmission_bounces"],
        volume_bounces=params["volume_bounces"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="setup_motion_blur", description="Set up motion blur")
@handle_errors
@validate_with(MotionBlurParams)
async def setup_motion_blur_tool(params: Dict[str, Any]) -> JSONType:
    result = await setup_motion_blur(
        use_motion_blur=params["use_motion_blur"],
        motion_blur_shutter=params["motion_blur_shutter"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="setup_depth_of_field", description="Set up depth of field")
@handle_errors
@validate_with(DepthOfFieldParams)
async def setup_depth_of_field_tool(params: Dict[str, Any]) -> JSONType:
    result = await setup_depth_of_field(
        use_dof=params["use_dof"],
        focus_object=params["focus_object"],
        focus_distance=params["focus_distance"],
        fstop=params["fstop"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="setup_ambient_occlusion", description="Set up ambient occlusion")
@handle_errors
@validate_with(AmbientOcclusionParams)
async def setup_ambient_occlusion_tool(params: Dict[str, Any]) -> JSONType:
    result = await setup_ambient_occlusion(
        use_ao=params["use_ao"],
        ao_factor=params["ao_factor"],
        ao_distance=params["ao_distance"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="setup_volumetrics", description="Set up volumetrics")
@handle_errors
@validate_with(VolumetricsParams)
async def setup_volumetrics_tool(params: Dict[str, Any]) -> JSONType:
    result = await setup_volumetrics(
        use_volumetrics=params["use_volumetrics"],
        volumetric_samples=params["volumetric_samples"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="setup_render_output", description="Set up render output")
@handle_errors
@validate_with(RenderOutputParams)
async def setup_render_output_tool(params: Dict[str, Any]) -> JSONType:
    result = await setup_render_output(
        filepath=params["filepath"],
        file_format=params["file_format"],
        color_mode=params["color_mode"],
        quality=params["quality"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="render_animation", description="Render an animation")
@handle_errors
@validate_with(RenderAnimationParams)
async def render_animation_tool(params: Dict[str, Any]) -> JSONType:
    result = await render_animation(
        frame_start=params["frame_start"],
        frame_end=params["frame_end"],
        frame_step=params["frame_step"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(name="render_still", description="Render a still image")
@handle_errors
@validate_with(BaseValidator)
async def render_still_tool(params: Dict[str, Any]) -> JSONType:
    result = await render_still()
    return {"status": "SUCCESS", "result": result}

@register_tool(name="setup_gpu_rendering", description="Set up GPU rendering")
@handle_errors
@validate_with(GPURenderingParams)
async def setup_gpu_rendering_tool(params: Dict[str, Any]) -> JSONType:
    result = await setup_gpu_rendering(
        use_gpu=params["use_gpu"],
        device_type=params["device_type"]
    )
    return {"status": "SUCCESS", "result": result}

def register() -> None:
    """Register all render tools."""
    # Tools are registered via decorators
    pass

# Auto-register tools when module is imported
register()

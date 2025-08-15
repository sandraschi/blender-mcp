"""
MCP Tools for rendering operations.

This module exposes rendering functionality through MCP tools.
"""
from typing import Dict, Any, List, Literal, Optional

from fastmcp.types import JSONType
from pydantic import BaseModel, Field

from blender_mcp.handlers.rendering_handler import (
    set_render_engine,
    configure_render_layers,
    setup_post_processing
)
from blender_mcp.tools import register_tool

# Common parameter schemas
class Vector3D(BaseModel):
    """3D vector with x, y, z components."""
    x: float = Field(..., description="X component")
    y: float = Field(..., description="Y component")
    z: float = Field(..., description="Z component")

class ColorRGB(BaseModel):
    """RGB color with values 0-1."""
    r: float = Field(0.0, ge=0.0, le=1.0, description="Red component (0-1)")
    g: float = Field(0.0, ge=0.0, le=1.0, description="Green component (0-1)")
    b: float = Field(0.0, ge=0.0, le=1.0, description="Blue component (0-1)")

# Tool parameter schemas
class RenderEngineParams(BaseModel):
    """Parameters for setting the render engine."""
    engine: Literal["BLENDER_EEVEE", "CYCLES", "BLENDER_WORKBENCH"] = Field(
        ...,
        description="The render engine to use"
    )
    use_gpu: bool = Field(
        True,
        description="Whether to use GPU for rendering"
    )
    samples: int = Field(
        64,
        ge=1,
        le=4096,
        description="Number of samples per pixel"
    )
    denoising: bool = Field(
        True,
        description="Whether to enable denoising"
    )
    motion_blur: bool = Field(
        False,
        description="Whether to enable motion blur"
    )
    bloom: bool = Field(
        True,
        description="Whether to enable bloom (EEVEE only)"
    )
    ambient_occlusion: bool = Field(
        True,
        description="Whether to enable ambient occlusion"
    )
    screen_space_reflections: bool = Field(
        True,
        description="Whether to enable screen space reflections"
    )
    volumetrics: bool = Field(
        True,
        description="Whether to enable volumetric effects"
    )

class RenderLayerParams(BaseModel):
    """Parameters for configuring render layers."""
    use_pass_combined: bool = Field(True, description="Enable combined pass")
    use_pass_z: bool = Field(False, description="Enable Z depth pass")
    use_pass_normal: bool = Field(False, description="Enable normal pass")
    use_pass_diffuse_direct: bool = Field(False, description="Enable direct diffuse pass")
    use_pass_diffuse_color: bool = Field(False, description="Enable diffuse color pass")
    use_pass_glossy_direct: bool = Field(False, description="Enable direct glossy pass")
    use_pass_glossy_color: bool = Field(False, description="Enable glossy color pass")
    use_pass_ambient_occlusion: bool = Field(False, description="Enable AO pass")
    use_pass_shadow: bool = Field(False, description="Enable shadow pass")
    use_pass_emit: bool = Field(False, description="Enable emission pass")
    use_pass_environment: bool = Field(False, description="Enable environment pass")
    use_pass_indirect: bool = Field(False, description="Enable indirect pass")
    use_pass_reflection: bool = Field(False, description="Enable reflection pass")
    use_pass_refraction: bool = Field(False, description="Enable refraction pass")
    use_pass_uv: bool = Field(False, description="Enable UV pass")
    use_pass_mist: bool = Field(False, description="Enable mist pass")
    use_pass_cryptomatte_object: bool = Field(False, description="Enable cryptomatte object pass")
    use_pass_cryptomatte_material: bool = Field(False, description="Enable cryptomatte material pass")
    use_pass_cryptomatte_asset: bool = Field(False, description="Enable cryptomatte asset pass")
    use_pass_shadow_catcher: bool = Field(False, description="Enable shadow catcher pass")

class PostProcessingParams(BaseModel):
    """Parameters for post-processing effects."""
    use_bloom: bool = Field(True, description="Enable bloom effect")
    use_ssao: bool = Field(True, description="Enable screen space ambient occlusion")
    use_motion_blur: bool = Field(False, description="Enable motion blur")
    use_dof: bool = Field(False, description="Enable depth of field")
    
    # Bloom settings
    bloom_threshold: float = Field(1.0, ge=0.0, description="Bloom intensity threshold")
    bloom_radius: float = Field(6.5, ge=0.1, le=50.0, description="Bloom radius")
    bloom_color: ColorRGB = Field(
        default_factory=lambda: ColorRGB(r=1.0, g=1.0, b=1.0),
        description="Bloom color"
    )
    
    # SSAO settings
    ssao_factor: float = Field(1.0, ge=0.0, le=10.0, description="SSAO intensity")
    ssao_distance: float = Field(0.2, ge=0.0, description="SSAO distance")
    
    # Motion blur settings
    motion_blur_shutter: float = Field(0.5, ge=0.0, description="Motion blur shutter speed")
    
    # Depth of field settings
    dof_focus_object: Optional[str] = Field(None, description="Object to focus on")
    dof_focus_distance: float = Field(10.0, ge=0.0, description="Manual focus distance")
    dof_fstop: float = Field(2.8, gt=0.0, description="Aperture f-stop")
    dof_blades: int = Field(0, ge=0, le=16, description="Aperture blades (0 for circular)")
    
    # Quality settings
    shadow_quality: Literal["LOW", "MEDIUM", "HIGH", "ULTRA"] = Field(
        "HIGH",
        description="Shadow quality preset"
    )
    
    # Color management
    exposure: float = Field(0.0, description="Exposure compensation")
    gamma: float = Field(1.0, gt=0.0, description="Gamma correction")
    contrast: float = Field(1.0, gt=0.0, description="Contrast adjustment")
    saturation: float = Field(1.0, ge=0.0, description="Saturation adjustment")
    
    # Mist/atmosphere
    mist_start: float = Field(5.0, ge=0.0, description="Mist start distance")
    mist_depth: float = Field(25.0, gt=0.0, description="Mist depth")
    mist_falloff: Literal["QUADRATIC", "LINEAR", "INVERSE_QUADRATIC"] = Field(
        "QUADRATIC",
        description="Mist falloff type"
    )

# Tool for setting render engine
@register_tool(
    name="set_render_engine",
    description="Set the active render engine and configure its settings",
    parameters=RenderEngineParams.schema()
)
async def set_render_engine_tool(params: Dict[str, Any]) -> JSONType:
    """Set the active render engine and configure its settings.
    
    Args:
        params: Parameters for the render engine configuration
        
    Returns:
        Dict containing the operation status and result
    """
    try:
        # Validate input parameters
        engine_params = RenderEngineParams(**params)
        
        # Call the handler function
        result = await set_render_engine(
            engine=engine_params.engine,
            use_gpu=engine_params.use_gpu,
            samples=engine_params.samples,
            denoising=engine_params.denoising,
            motion_blur=engine_params.motion_blur,
            bloom=engine_params.bloom,
            ambient_occlusion=engine_params.ambient_occlusion,
            screen_space_reflections=engine_params.screen_space_reflections,
            volumetrics=engine_params.volumetrics
        )
        
        return {"status": "SUCCESS", "result": result}
        
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# Tool for configuring render layers
@register_tool(
    name="configure_render_layers",
    description="Configure render layers and passes",
    parameters=RenderLayerParams.schema()
)
async def configure_render_layers_tool(params: Dict[str, Any]) -> JSONType:
    """Configure render layers and passes.
    
    Args:
        params: Parameters for render layer configuration
        
    Returns:
        Dict containing the operation status and result
    """
    try:
        # Validate input parameters
        layer_params = RenderLayerParams(**params)
        
        # Call the handler function
        result = await configure_render_layers(
            **layer_params.dict()
        )
        
        return {"status": "SUCCESS", "result": result}
        
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# Tool for setting up post-processing
@register_tool(
    name="setup_post_processing",
    description="Configure post-processing effects",
    parameters=PostProcessingParams.schema()
)
async def setup_post_processing_tool(params: Dict[str, Any]) -> JSONType:
    """Configure post-processing effects.
    
    Args:
        params: Parameters for post-processing configuration
        
    Returns:
        Dict containing the operation status and result
    """
    try:
        # Validate input parameters
        post_params = PostProcessingParams(**params)
        
        # Call the handler function
        result = await setup_post_processing(
            **post_params.dict()
        )
        
        return {"status": "SUCCESS", "result": result}
        
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# Register all tools
def register() -> None:
    """Register all rendering tools."""
    # Tools are registered via decorators
    pass

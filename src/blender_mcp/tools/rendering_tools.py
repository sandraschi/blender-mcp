from ..compat import *

"""
Rendering-related MCP tools for Blender.

This module exposes rendering functionality through MCP tools.
"""
from typing import Dict, Any, List, Optional, Union
from blender_mcp.compat import Tool, FunctionTool
from blender_mcp.handlers.rendering_handler import (
    set_render_engine,
    configure_render_layers,
    setup_post_processing
)
from blender_mcp.app import app

# Common parameter schemas
class Vector3D:
    """3D vector with x, y, z components."""
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

class ColorRGB:
    """RGB color with values 0-1."""
    def __init__(self, r: float, g: float, b: float):
        self.r = r
        self.g = g
        self.b = b

# Tool parameter schemas
class RenderEngineParams:
    """Parameters for setting the render engine."""
    def __init__(self, engine: str, use_gpu: bool, samples: int, denoising: bool, motion_blur: bool, bloom: bool, ambient_occlusion: bool, screen_space_reflections: bool, volumetrics: bool):
        self.engine = engine
        self.use_gpu = use_gpu
        self.samples = samples
        self.denoising = denoising
        self.motion_blur = motion_blur
        self.bloom = bloom
        self.ambient_occlusion = ambient_occlusion
        self.screen_space_reflections = screen_space_reflections
        self.volumetrics = volumetrics

class RenderLayerParams:
    """Parameters for configuring render layers."""
    def __init__(self, use_pass_combined: bool, use_pass_z: bool, use_pass_normal: bool, use_pass_diffuse_direct: bool, use_pass_diffuse_color: bool, use_pass_glossy_direct: bool, use_pass_glossy_color: bool, use_pass_ambient_occlusion: bool, use_pass_shadow: bool, use_pass_emit: bool, use_pass_environment: bool, use_pass_indirect: bool, use_pass_reflection: bool, use_pass_refraction: bool, use_pass_uv: bool, use_pass_mist: bool, use_pass_cryptomatte_object: bool, use_pass_cryptomatte_material: bool, use_pass_cryptomatte_asset: bool, use_pass_shadow_catcher: bool):
        self.use_pass_combined = use_pass_combined
        self.use_pass_z = use_pass_z
        self.use_pass_normal = use_pass_normal
        self.use_pass_diffuse_direct = use_pass_diffuse_direct
        self.use_pass_diffuse_color = use_pass_diffuse_color
        self.use_pass_glossy_direct = use_pass_glossy_direct
        self.use_pass_glossy_color = use_pass_glossy_color
        self.use_pass_ambient_occlusion = use_pass_ambient_occlusion
        self.use_pass_shadow = use_pass_shadow
        self.use_pass_emit = use_pass_emit
        self.use_pass_environment = use_pass_environment
        self.use_pass_indirect = use_pass_indirect
        self.use_pass_reflection = use_pass_reflection
        self.use_pass_refraction = use_pass_refraction
        self.use_pass_uv = use_pass_uv
        self.use_pass_mist = use_pass_mist
        self.use_pass_cryptomatte_object = use_pass_cryptomatte_object
        self.use_pass_cryptomatte_material = use_pass_cryptomatte_material
        self.use_pass_cryptomatte_asset = use_pass_cryptomatte_asset
        self.use_pass_shadow_catcher = use_pass_shadow_catcher

class PostProcessingParams:
    """Parameters for post-processing effects."""
    def __init__(self, use_bloom: bool, use_ssao: bool, use_motion_blur: bool, use_dof: bool, bloom_threshold: float, bloom_radius: float, bloom_color: ColorRGB, ssao_factor: float, ssao_distance: float, motion_blur_shutter: float, dof_focus_object: Optional[str], dof_focus_distance: float, dof_fstop: float, dof_blades: int, shadow_quality: str, exposure: float, gamma: float, contrast: float, saturation: float, mist_start: float, mist_depth: float, mist_falloff: str):
        self.use_bloom = use_bloom
        self.use_ssao = use_ssao
        self.use_motion_blur = use_motion_blur
        self.use_dof = use_dof
        self.bloom_threshold = bloom_threshold
        self.bloom_radius = bloom_radius
        self.bloom_color = bloom_color
        self.ssao_factor = ssao_factor
        self.ssao_distance = ssao_distance
        self.motion_blur_shutter = motion_blur_shutter
        self.dof_focus_object = dof_focus_object
        self.dof_focus_distance = dof_focus_distance
        self.dof_fstop = dof_fstop
        self.dof_blades = dof_blades
        self.shadow_quality = shadow_quality
        self.exposure = exposure
        self.gamma = gamma
        self.contrast = contrast
        self.saturation = saturation
        self.mist_start = mist_start
        self.mist_depth = mist_depth
        self.mist_falloff = mist_falloff

# Register rendering tools using the @app.tool decorator

@app.tool
def set_render_engine_tool(
    engine: str = "CYCLES",
    device: str = "GPU" if True else "CPU",
    use_denoising: bool = True,
    use_adaptive_sampling: bool = True
) -> Dict[str, Any]:
    """Set the render engine and basic settings.
    
    Args:
        engine: Render engine to use (CYCLES, EEVEE, WORKBENCH)
        device: Device to use for rendering (CPU/GPU)
        use_denoising: Enable denoising
        use_adaptive_sampling: Enable adaptive sampling
        
    Returns:
        Dict with status and message
    """
    return set_render_engine(engine, device, use_denoising, use_adaptive_sampling)

@app.tool
def configure_render_layers_tool(
    layers: List[Dict[str, Any]],
    use_freestyle: bool = False,
    use_pass_ambient_occlusion: bool = False,
    use_pass_combined: bool = True,
    use_pass_z: bool = False,
    use_pass_mist: bool = False,
    use_pass_position: bool = False,
    use_pass_normal: bool = False,
    use_pass_vector: bool = False,
    use_pass_uv: bool = False,
    use_pass_object_index: bool = False,
    use_pass_material_index: bool = False,
    use_pass_shadow: bool = False,
    use_pass_emit: bool = False,
    use_pass_environment: bool = False,
    use_pass_diffuse_direct: bool = False,
    use_pass_diffuse_indirect: bool = False,
    use_pass_diffuse_color: bool = False,
    use_pass_glossy_direct: bool = False,
    use_pass_glossy_indirect: bool = False,
    use_pass_glossy_color: bool = False,
    use_pass_transmission_direct: bool = False,
    use_pass_transmission_indirect: bool = False,
    use_pass_transmission_color: bool = False,
    use_pass_volume_direct: bool = False,
    use_pass_volume_indirect: bool = False,
) -> Dict[str, Any]:
    """Configure render layers and passes.
    
    Args:
        layers: List of layer configurations
        use_freestyle: Enable Freestyle rendering
        use_pass_*: Various render passes to enable
        
    Returns:
        Dict with status and message
    """
    return configure_render_layers(
        layers, use_freestyle, use_pass_ambient_occlusion, use_pass_combined,
        use_pass_z, use_pass_mist, use_pass_position, use_pass_normal,
        use_pass_vector, use_pass_uv, use_pass_object_index, use_pass_material_index,
        use_pass_shadow, use_pass_ambient_occlusion, use_pass_emit, use_pass_environment,
        use_pass_diffuse_direct, use_pass_diffuse_indirect, use_pass_diffuse_color,
        use_pass_glossy_direct, use_pass_glossy_indirect, use_pass_glossy_color,
        use_pass_transmission_direct, use_pass_transmission_indirect, use_pass_transmission_color,
        use_pass_volume_direct, use_pass_volume_indirect
    )

@app.tool
def setup_post_processing_tool(
    use_compositing: bool = True,
    use_sequencer: bool = False,
    use_nodes: bool = True,
    dither: float = 0.0,
    exposure: float = 0.0,
    gamma: float = 1.0,
    use_curve_mapping: bool = False,
    use_highlight_clamp: bool = False,
    use_highlight_clamp_high: bool = False,
    use_highlight_clamp_low: bool = False,
    use_highlight_clamp_medium: bool = False,
    use_highlight_clamp_very_high: bool = False,
    use_highlight_clamp_very_low: bool = False,
    use_highlight_clamp_zero: bool = False,
    use_mist: bool = False,
    use_motion_blur: bool = False,
    use_sky: bool = True,
    use_ssr: bool = False,
    use_ssr_refraction: bool = False,
) -> Dict[str, Any]:
    """Configure post-processing effects.
    
    Args:
        use_compositing: Enable node-based compositing
        use_sequencer: Enable video sequence editor
        use_nodes: Enable node-based compositing
        dither: Dithering amount
        exposure: Exposure value
        gamma: Gamma correction
        use_*: Various post-processing effects
        
    Returns:
        Dict with status and message
    """
    return setup_post_processing(
        use_compositing, use_sequencer, use_nodes, dither, exposure, gamma,
        use_curve_mapping, use_highlight_clamp, use_highlight_clamp_high,
        use_highlight_clamp_low, use_highlight_clamp_medium, use_highlight_clamp_very_high,
        use_highlight_clamp_very_low, use_highlight_clamp_zero, use_mist,
        use_motion_blur, use_sky, use_ssr, use_ssr_refraction
    )

# Register other rendering tools in a similar way
# ... rest of the tools ...

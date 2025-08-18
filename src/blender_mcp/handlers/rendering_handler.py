"""
Rendering Handler for Blender-MCP

This module provides advanced rendering functionality for Blender scenes,
including EEVEE and Cycles render engine configuration, post-processing effects,
render layer management, and output configuration.
"""
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import logging

from blender_mcp.fastmcp import blender_operation
from blender_mcp.utils.blender_executor import BlenderExecutor

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize Blender executor
_executor = BlenderExecutor()

# Constants for render engines
RENDER_ENGINE_EEVEE = 'BLENDER_EEVEE'
RENDER_ENGINE_CYCLES = 'CYCLES'
RENDER_ENGINE_WORKBENCH = 'BLENDER_WORKBENCH'

class RenderEngineType:
    """Enum for render engine types."""
    EEVEE = RENDER_ENGINE_EEVEE
    CYCLES = RENDER_ENGINE_CYCLES
    WORKBENCH = RENDER_ENGINE_WORKBENCH

@blender_operation("set_render_engine", log_args=True)
async def set_render_engine(
    engine: Union[RenderEngineType, str] = RENDER_ENGINE_EEVEE,
    device: str = 'GPU',
    use_denoising: bool = True,
    samples: int = 64,
    **kwargs: Any
) -> Dict[str, Any]:
    """Set the active render engine and its basic configuration.
    
    Args:
        engine: Render engine to use (EEVEE, CYCLES, or WORKBENCH)
        device: Compute device to use ('CPU', 'GPU', or 'GPU_COMPATIBLE')
        use_denoising: Enable denoising for supported engines
        samples: Number of samples per pixel
        **kwargs: Additional engine-specific settings
            - use_adaptive_sampling: For Cycles (default: True)
            - adaptive_threshold: For Cycles (default: 0.01)
            - tile_size: For Cycles (default: 2048)
            - use_motion_blur: For EEVEE (default: True)
            - motion_blur_steps: For EEVEE (default: 1)
            - use_bloom: For EEVEE (default: True)
            - bloom_threshold: For EEVEE (default: 1.0)
            
    Returns:
        Dict containing operation status and render settings
    """
    engine = str(engine).upper()
    valid_engines = [RENDER_ENGINE_EEVEE, RENDER_ENGINE_CYCLES, RENDER_ENGINE_WORKBENCH]
    if engine not in valid_engines:
        return {
            "status": "ERROR",
            "error": f"Invalid render engine. Must be one of: {', '.join(valid_engines)}"
        }
    
    # Get additional settings with defaults
    use_adaptive_sampling = kwargs.get('use_adaptive_sampling', True)
    adaptive_threshold = kwargs.get('adaptive_threshold', 0.01)
    tile_size = kwargs.get('tile_size', 2048)
    use_motion_blur = kwargs.get('use_motion_blur', True)
    motion_blur_steps = kwargs.get('motion_blur_steps', 1)
    use_bloom = kwargs.get('use_bloom', True)
    bloom_threshold = kwargs.get('bloom_threshold', 1.0)
    
    script = f"""

def configure_render_engine():
    scene = bpy.context.scene
    
    # Set the render engine
    scene.render.engine = '{engine}'
    
    # Common settings
    scene.render.resolution_x = {scene.render.resolution_x}
    scene.render.resolution_y = {scene.render.resolution_y}
    scene.render.resolution_percentage = 100
    
    if '{engine}' == '{RENDER_ENGINE_CYCLES}':
        # Cycles specific settings
        scene.cycles.device = '{device}'
        scene.cycles.samples = {samples}
        scene.cycles.use_denoising = {str(use_denoising).lower()}
        scene.cycles.use_adaptive_sampling = {str(use_adaptive_sampling).lower()}
        scene.cycles.adaptive_threshold = {adaptive_threshold}
        scene.cycles.tile_size = {tile_size}
        
        # Enable GPU if available
        if bpy.app.version >= (2, 80, 0):
            if '{device}'.upper() in ['GPU', 'GPU_COMPATIBLE']:
                bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
                bpy.context.preferences.addons['cycles'].preferences.get_devices()
                for d in bpy.context.preferences.addons['cycles'].preferences.devices:
                    d['use'] = 1
    
    elif '{engine}' == '{RENDER_ENGINE_EEVEE}':
        # EEVEE specific settings
        scene.eevee.taa_render_samples = {samples}
        scene.eevee.use_bloom = {str(use_bloom).lower()}
        scene.eevee.bloom_threshold = {bloom_threshold}
        scene.eevee.use_motion_blur = {str(use_motion_blur).lower()}
        scene.eevee.motion_blur_steps = {motion_blur_steps}
    
    return {{
        'status': 'SUCCESS',
        'engine': '{engine}',
        'device': '{device}',
        'samples': {samples},
        'use_denoising': {str(use_denoising).lower()}
    }}

try:
    result = configure_render_engine()
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
        logger.error(f"Failed to set render engine: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("configure_render_layers", log_args=True)
async def configure_render_layers(
    layer_name: str = "RenderLayer",
    use_pass_combined: bool = True,
    use_pass_z: bool = True,
    use_pass_normal: bool = True,
    use_pass_diffuse: bool = True,
    use_pass_glossy: bool = True,
    use_pass_ambient_occlusion: bool = True,
    use_pass_shadow: bool = True,
    use_pass_emit: bool = True,
    use_pass_environment: bool = True,
    use_pass_indirect: bool = True,
    use_pass_reflection: bool = True,
    use_pass_refraction: bool = True,
    use_pass_uv: bool = False,
    use_pass_mist: bool = False,
    use_pass_object_index: bool = False,
    use_pass_material_index: bool = False,
    use_pass_vector: bool = False,
    use_pass_cryptomatte_object: bool = False,
    use_pass_cryptomatte_material: bool = False,
    use_pass_cryptomatte_asset: bool = False,
    use_pass_shadow_catcher: bool = False,
    **kwargs: Any
) -> Dict[str, Any]:
    """Configure render layers and passes for advanced rendering.
    
    Args:
        layer_name: Name of the render layer to configure
        use_pass_*: Enable/disable specific render passes
        **kwargs: Additional render layer settings
            - use_solid: Enable solid geometry (default: True)
            - use_halo: Enable halo effects (default: True)
            - use_ztransp: Use Z transparency (default: True)
            - use_strand: Enable strand rendering (default: True)
            - use_freestyle: Enable Freestyle rendering (default: False)
            - use_sky: Use world background (default: True)
            - use_edge_enhance: Enable edge enhancement (default: False)
            - use_all_z: Use all Z values (default: False)
            - exclude_raytrace: Exclude from raytracing (default: False)
            - light_override: Override light settings (default: None)
            
    Returns:
        Dict containing operation status and render layer configuration
    """
    # Get additional settings with defaults
    use_solid = kwargs.get('use_solid', True)
    use_halo = kwargs.get('use_halo', True)
    use_ztransp = kwargs.get('use_ztransp', True)
    use_strand = kwargs.get('use_strand', True)
    use_freestyle = kwargs.get('use_freestyle', False)
    use_sky = kwargs.get('use_sky', True)
    use_edge_enhance = kwargs.get('use_edge_enhance', False)
    use_all_z = kwargs.get('use_all_z', False)
    exclude_raytrace = kwargs.get('exclude_raytrace', False)
    light_override = kwargs.get('light_override', None)
    
    script = f"""

def configure_layers():
    scene = bpy.context.scene
    
    # Get or create the render layer
    rl = scene.view_layers.get('{layer_name}')
    if not rl:
        rl = scene.view_layers.new('{layer_name}')
    
    # Set as active render layer
    scene.view_layers.active = rl
    
    # Basic layer settings
    rl.use_solid = {str(use_solid).lower()}
    rl.use_halo = {str(use_halo).lower()}
    rl.use_ztransp = {str(use_ztransp).lower()}
    rl.use_strand = {str(use_strand).lower()}
    rl.use_freestyle = {str(use_freestyle).lower()}
    rl.use_sky = {str(use_sky).lower()}
    rl.use_edge_enhance = {str(use_edge_enhance).lower()}
    rl.use_all_z = {str(use_all_z).lower()}
    rl.exclude_raytraced = {str(exclude_raytrace).lower()}
    
    # Configure render passes
    rl.cycles.use_pass_combined = {str(use_pass_combined).lower()}
    rl.cycles.use_pass_z = {str(use_pass_z).lower()}
    rl.cycles.use_pass_normal = {str(use_pass_normal).lower()}
    rl.cycles.use_pass_diffuse_direct = {str(use_pass_diffuse).lower()}
    rl.cycles.use_pass_diffuse_indirect = {str(use_pass_diffuse).lower()}
    rl.cycles.use_pass_diffuse_color = {str(use_pass_diffuse).lower()}
    rl.cycles.use_pass_glossy_direct = {str(use_pass_glossy).lower()}
    rl.cycles.use_pass_glossy_indirect = {str(use_pass_glossy).lower()}
    rl.cycles.use_pass_glossy_color = {str(use_pass_glossy).lower()}
    rl.cycles.use_pass_ambient_occlusion = {str(use_pass_ambient_occlusion).lower()}
    rl.cycles.use_pass_shadow = {str(use_pass_shadow).lower()}
    rl.cycles.use_pass_emit = {str(use_pass_emit).lower()}
    rl.cycles.use_pass_environment = {str(use_pass_environment).lower()}
    rl.cycles.use_pass_indirect = {str(use_pass_indirect).lower()}
    rl.cycles.use_pass_reflection = {str(use_pass_reflection).lower()}
    rl.cycles.use_pass_refraction = {str(use_pass_refraction).lower()}
    rl.cycles.use_pass_uv = {str(use_pass_uv).lower()}
    rl.cycles.use_pass_mist = {str(use_pass_mist).lower()}
    rl.cycles.use_pass_object_index = {str(use_pass_object_index).lower()}
    rl.cycles.use_pass_material_index = {str(use_pass_material_index).lower()}
    rl.cycles.use_pass_vector = {str(use_pass_vector).lower()}
    rl.cycles.use_pass_cryptomatte_object = {str(use_pass_cryptomatte_object).lower()}
    rl.cycles.use_pass_cryptomatte_material = {str(use_pass_cryptomatte_material).lower()}
    rl.cycles.use_pass_cryptomatte_asset = {str(use_pass_cryptomatte_asset).lower()}
    rl.cycles.use_pass_shadow_catcher = {str(use_pass_shadow_catcher).lower()}
    
    # Light override
    if '{light_override}' is not None:
        rl.light_override = bpy.data.objects.get('{light_override}')
    
    return {{
        'status': 'SUCCESS',
        'render_layer': rl.name,
        'settings': {{
            'use_solid': {str(use_solid).lower()},
            'use_halo': {str(use_halo).lower()},
            'use_ztransp': {str(use_ztransp).lower()},
            'use_strand': {str(use_strand).lower()},
            'use_freestyle': {str(use_freestyle).lower()},
            'use_sky': {str(use_sky).lower()},
            'use_edge_enhance': {str(use_edge_enhance).lower()},
            'use_all_z': {str(use_all_z).lower()},
            'exclude_raytraced': {str(exclude_raytrace).lower()},
            'light_override': '{light_override}'
        }}
    }}

try:
    result = configure_layers()
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(str(result))
""".format(
        layer_name=layer_name,
        use_solid=use_solid,
        use_halo=use_halo,
        use_ztransp=use_ztransp,
        use_strand=use_strand,
        use_freestyle=use_freestyle,
        use_sky=use_sky,
        use_edge_enhance=use_edge_enhance,
        use_all_z=use_all_z,
        exclude_raytrace=exclude_raytrace,
        light_override=light_override or '',
        use_pass_combined=use_pass_combined,
        use_pass_z=use_pass_z,
        use_pass_normal=use_pass_normal,
        use_pass_diffuse=use_pass_diffuse,
        use_pass_glossy=use_pass_glossy,
        use_pass_ambient_occlusion=use_pass_ambient_occlusion,
        use_pass_shadow=use_pass_shadow,
        use_pass_emit=use_pass_emit,
        use_pass_environment=use_pass_environment,
        use_pass_indirect=use_pass_indirect,
        use_pass_reflection=use_pass_reflection,
        use_pass_refraction=use_pass_refraction,
        use_pass_uv=use_pass_uv,
        use_pass_mist=use_pass_mist,
        use_pass_object_index=use_pass_object_index,
        use_pass_material_index=use_pass_material_index,
        use_pass_vector=use_pass_vector,
        use_pass_cryptomatte_object=use_pass_cryptomatte_object,
        use_pass_cryptomatte_material=use_pass_cryptomatte_material,
        use_pass_cryptomatte_asset=use_pass_cryptomatte_asset,
        use_pass_shadow_catcher=use_pass_shadow_catcher
    )
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to configure render layers: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("setup_post_processing", log_args=True)
async def setup_post_processing(
    use_bloom: bool = True,
    use_ssao: bool = True,
    use_motion_blur: bool = False,
    use_dof: bool = False,
    **kwargs: Any
) -> Dict[str, Any]:
    """Configure post-processing effects for the render.
    
    Args:
        use_bloom: Enable bloom effect (default: True)
        use_ssao: Enable screen space ambient occlusion (default: True)
        use_motion_blur: Enable motion blur (default: False)
        use_dof: Enable depth of field (default: False)
        **kwargs: Additional post-processing settings
            - bloom_threshold: Bloom intensity threshold (default: 1.0)
            - bloom_radius: Bloom radius (default: 6.5)
            - bloom_color: Bloom color (RGB tuple, default: (1.0, 1.0, 1.0))
            - ssao_factor: SSAO factor (default: 1.0)
            - ssao_distance: SSAO distance (default: 0.2)
            - motion_blur_shutter: Motion blur shutter speed (default: 0.5)
            - dof_focus_object: Object to focus on (name string, default: None)
            - dof_focus_distance: Manual focus distance (default: 10.0)
            - dof_fstop: Aperture f-stop (default: 2.8)
            - dof_blades: Aperture blades (default: 0 for circular)
            - use_volumetric_lights: Enable volumetric lighting (default: True)
            - use_volumetric_shadows: Enable volumetric shadows (default: True)
            - volumetric_tile_size: Volumetric tile size (default: '2')
            - volumetric_samples: Volumetric samples (default: 4)
            - use_subsurface_scattering: Enable SSS (default: True)
            - sss_samples: SSS samples (default: 4)
            - use_screen_space_reflections: Enable SSR (default: True)
            - ssr_quality: SSR quality (0.0-1.0, default: 0.5)
            - ssr_thickness: SSR thickness (default: 0.2)
            - ssr_max_roughness: SSR max roughness (0.0-1.0, default: 0.5)
            - use_taa: Enable temporal anti-aliasing (default: True)
            - taa_samples: TAA samples (default: 16)
            - use_fxaa: Enable FXAA (default: False)
            - use_high_quality_normals: Use high quality normals (default: True)
            - use_soft_shadows: Use soft shadows (default: True)
            - shadow_quality: Shadow quality ('LOW', 'MEDIUM', 'HIGH', 'ULTRA')
            - use_ambient_occlusion: Enable ambient occlusion (default: True)
            - ao_factor: AO factor (default: 1.0)
            - ao_distance: AO distance (default: 0.2)
            - use_glow: Enable glow effect (default: False)
            - glow_threshold: Glow threshold (default: 1.0)
            - glow_color: Glow color (RGB tuple, default: (1.0, 1.0, 1.0))
            - glow_radius: Glow radius (default: 3.0)
            - use_vignette: Enable vignette (default: False)
            - vignette_scale: Vignette scale (default: 1.0)
            - use_color_grading: Enable color grading (default: False)
            - exposure: Exposure compensation (default: 0.0)
            - gamma: Gamma correction (default: 1.0)
            - contrast: Contrast (default: 1.0)
            - saturation: Saturation (default: 1.0)
            - brightness: Brightness (default: 1.0)
            - rgb_curves: RGB curves as list of control points
            - use_lens_distortion: Enable lens distortion (default: False)
            - distortion: Lens distortion amount (-1.0 to 1.0, default: 0.0)
            - dispersion: Chromatic aberration (0.0-1.0, default: 0.0)
            - use_film_grain: Enable film grain (default: False)
            - grain_scale: Grain scale (default: 1.0)
            - grain_strength: Grain strength (default: 0.1)
            - use_color_ramp: Enable color ramp (default: False)
            - color_ramp: Color ramp as list of (position, (r,g,b)) tuples
            - use_z_combine: Enable Z-combine for mist/atmosphere (default: False)
            - mist_start: Mist start distance (default: 5.0)
            - mist_depth: Mist depth (default: 25.0)
            - mist_falloff: Mist falloff type ('QUADRATIC', 'LINEAR', 'INVERSE_QUADRATIC')
            - use_freestyle: Enable Freestyle rendering (default: False)
            - freestyle_line_sets: List of line set configurations
            - use_stereo: Enable stereo rendering (default: False)
            - stereo_mode: Stereo mode ('STEREO', 'ANAGLYPH', 'INTERLACED')
            - stereo_eye_separation: Eye separation (default: 0.065)
            - use_high_bitdepth: Use high bit-depth output (default: False)
            - use_transparent: Enable transparent background (default: False)
            - use_sequencer: Enable sequencer (default: False)
            - use_compositing: Enable node-based compositing (default: True)
            - use_auto_tile: Enable auto-tile rendering (default: False)
            - tile_size: Tile size for rendering (default: 2048)
    
    Returns:
        Dict containing operation status and post-processing settings
    """
    # Get all settings with defaults
    settings = {
        # Bloom
        'bloom_threshold': kwargs.get('bloom_threshold', 1.0),
        'bloom_radius': kwargs.get('bloom_radius', 6.5),
        'bloom_color': kwargs.get('bloom_color', (1.0, 1.0, 1.0)),
        
        # SSAO
        'ssao_factor': kwargs.get('ssao_factor', 1.0),
        'ssao_distance': kwargs.get('ssao_distance', 0.2),
        
        # Motion Blur
        'motion_blur_shutter': kwargs.get('motion_blur_shutter', 0.5),
        
        # Depth of Field
        'dof_focus_object': kwargs.get('dof_focus_object', ''),
        'dof_focus_distance': kwargs.get('dof_focus_distance', 10.0),
        'dof_fstop': kwargs.get('dof_fstop', 2.8),
        'dof_blades': kwargs.get('dof_blades', 0),
        
        # Volumetrics
        'use_volumetric_lights': kwargs.get('use_volumetric_lights', True),
        'use_volumetric_shadows': kwargs.get('use_volumetric_shadows', True),
        'volumetric_tile_size': kwargs.get('volumetric_tile_size', '2'),
        'volumetric_samples': kwargs.get('volumetric_samples', 4),
        
        # SSS
        'use_subsurface_scattering': kwargs.get('use_subsurface_scattering', True),
        'sss_samples': kwargs.get('sss_samples', 4),
        
        # Screen Space Reflections
        'use_screen_space_reflections': kwargs.get('use_screen_space_reflections', True),
        'ssr_quality': kwargs.get('ssr_quality', 0.5),
        'ssr_thickness': kwargs.get('ssr_thickness', 0.2),
        'ssr_max_roughness': kwargs.get('ssr_max_roughness', 0.5),
        
        # Anti-aliasing
        'use_taa': kwargs.get('use_taa', True),
        'taa_samples': kwargs.get('taa_samples', 16),
        'use_fxaa': kwargs.get('use_fxaa', False),
        
        # Quality
        'use_high_quality_normals': kwargs.get('use_high_quality_normals', True),
        'use_soft_shadows': kwargs.get('use_soft_shadows', True),
        'shadow_quality': kwargs.get('shadow_quality', 'HIGH'),
        
        # Ambient Occlusion
        'use_ambient_occlusion': kwargs.get('use_ambient_occlusion', True),
        'ao_factor': kwargs.get('ao_factor', 1.0),
        'ao_distance': kwargs.get('ao_distance', 0.2),
        
        # Glow
        'glow_threshold': kwargs.get('glow_threshold', 1.0),
        'glow_color': kwargs.get('glow_color', (1.0, 1.0, 1.0)),
        'glow_radius': kwargs.get('glow_radius', 3.0),
        
        # Vignette
        'vignette_scale': kwargs.get('vignette_scale', 1.0),
        
        # Color Grading
        'exposure': kwargs.get('exposure', 0.0),
        'gamma': kwargs.get('gamma', 1.0),
        'contrast': kwargs.get('contrast', 1.0),
        'saturation': kwargs.get('saturation', 1.0),
        'brightness': kwargs.get('brightness', 1.0),
        'rgb_curves': kwargs.get('rgb_curves', []),
        
        # Lens Effects
        'distortion': kwargs.get('distortion', 0.0),
        'dispersion': kwargs.get('dispersion', 0.0),
        
        # Film Grain
        'grain_scale': kwargs.get('grain_scale', 1.0),
        'grain_strength': kwargs.get('grain_strength', 0.1),
        
        # Mist/Atmosphere
        'mist_start': kwargs.get('mist_start', 5.0),
        'mist_depth': kwargs.get('mist_depth', 25.0),
        'mist_falloff': kwargs.get('mist_falloff', 'QUADRATIC'),
        
        # Stereo
        'stereo_mode': kwargs.get('stereo_mode', 'STEREO'),
        'stereo_eye_separation': kwargs.get('stereo_eye_separation', 0.065),
        
        # Rendering
        'tile_size': kwargs.get('tile_size', 2048)
    }
    
    # Convert settings to strings for the script
    settings_str = '\n'.join(f'    {k} = {repr(v)}' for k, v in settings.items())
    
    script = f"""

def setup_post_processing():
    scene = bpy.context.scene
    eevee = scene.eevee
    
    # Basic settings
    {settings_str}
    
    # Bloom
    eevee.use_bloom = {str(use_bloom).lower()}
    if {str(use_bloom).lower()}:
        eevee.bloom_threshold = bloom_threshold
        eevee.bloom_radius = bloom_radius
        eevee.bloom_color = bloom_color
    
    # SSAO
    eevee.use_gtao = {str(use_ssao).lower()}
    if {str(use_ssao).lower()}:
        eevee.gtao_factor = ssao_factor
        eevee.gtao_distance = ssao_distance
    
    # Motion Blur
    eevee.use_motion_blur = {str(use_motion_blur).lower()}
    if {str(use_motion_blur).lower()}:
        eevee.motion_blur_shutter = motion_blur_shutter
    
    # Depth of Field
    eevee.use_dof = {str(use_dof).lower()}
    if {str(use_dof).lower()}:
        if dof_focus_object:
            focus_obj = bpy.data.objects.get(dof_focus_object)
            if focus_obj:
                scene.camera.data.dof.focus_object = focus_obj
        else:
            scene.camera.data.dof.focus_distance = dof_focus_distance
        scene.camera.data.dof.aperture_fstop = dof_fstop
        scene.camera.data.dof.aperture_blades = dof_blades
    
    # Volumetrics
    eevee.use_volumetric_lights = {str(settings['use_volumetric_lights']).lower()}
    eevee.use_volumetric_shadows = {str(settings['use_volumetric_shadows']).lower()}
    eevee.volumetric_tile_size = volumetric_tile_size
    eevee.volumetric_samples = volumetric_samples
    
    # SSS
    eevee.sss_samples = sss_samples
    
    # Screen Space Reflections
    eevee.use_ssr = {str(settings['use_screen_space_reflections']).lower()}
    eevee.use_ssr_refraction = {str(settings['use_screen_space_reflections']).lower()}
    eevee.ssr_quality = ssr_quality
    eevee.ssr_thickness = ssr_thickness
    eevee.ssr_max_roughness = ssr_max_roughness
    
    # Anti-aliasing
    eevee.taa_render_samples = taa_samples
    eevee.use_taa_reprojection = {str(settings['use_taa']).lower()}
    eevee.use_taa = {str(settings['use_taa']).lower()}
    eevee.use_gtao = {str(settings['use_ambient_occlusion']).lower()}
    
    # Shadows
    eevee.shadow_cube_size = '1024' if shadow_quality in ['HIGH', 'ULTRA'] else '512'
    eevee.shadow_cascade_size = '1024' if shadow_quality == 'ULTRA' else '512'
    
    # Color Management
    scene.view_settings.exposure = exposure
    scene.view_settings.gamma = gamma
    scene.sequencer_colorspace_settings.name = 'sRGB'  # Default color space
    
    # Update the viewport
    bpy.context.view_layer.update()
    
    return {{
        'status': 'SUCCESS',
        'settings': {{
            'bloom': {str(use_bloom).lower()},
            'ssao': {str(use_ssao).lower()},
            'motion_blur': {str(use_motion_blur).lower()},
            'dof': {str(use_dof).lower()}
        }}
    }}

try:
    result = setup_post_processing()
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
        logger.error(f"Failed to setup post-processing: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

from ..compat import *

"""Comprehensive material system handler with extensive error handling.

This module provides material creation functions that can be registered as FastMCP tools.
Supports physically-based rendering (PBR) materials with advanced node setups.
"""

from typing import Dict, Tuple, List, Optional, Union
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation
from ..exceptions import BlenderMaterialError

# Import app lazily to avoid circular imports
def get_app():
    from ..app import app
    return app
from typing import Tuple, Optional, Union

# Initialize the executor with default Blender executable
_executor = get_blender_executor()

class MaterialType(str, Enum):
    """Supported material types for type hints and validation."""
    FABRIC = "fabric"
    METAL = "metal"
    WOOD = "wood"
    GLASS = "glass"
    CERAMIC = "ceramic"
    LEATHER = "leather"
    STONE = "stone"
    EMISSIVE = "emissive"

class MaterialPreset(str, Enum):
    """Available presets for each material type."""
    # Fabric presets
    VELVET = "velvet"
    SILK = "silk"
    COTTON = "cotton"
    LINEN = "linen"
    BROCADE = "brocade"
    SATIN = "satin"
    WOOL = "wool"
    
    # Metal presets
    GOLD = "gold"
    SILVER = "silver"
    BRASS = "brass"
    COPPER = "copper"
    IRON = "iron"
    ALUMINUM = "aluminum"
    CHROME = "chrome"
    
    # Wood presets
    OAK = "oak"
    MAHOGANY = "mahogany"
    PINE = "pine"
    WALNUT = "walnut"
    CHERRY = "cherry"
    MAPLE = "maple"
    
    # Glass presets
    CLEAR_GLASS = "clear_glass"
    FROSTED_GLASS = "frosted_glass"
    STAINED_GLASS = "stained_glass"
    
    # Ceramic presets
    PORCELAIN = "porcelain"
    TERRA_COTTA = "terra_cotta"
    
    # Leather presets
    LEATHER = "leather"
    PATENT_LEATHER = "patent_leather"
    SUEDE = "suede"
    
    # Stone presets
    MARBLE = "marble"
    GRANITE = "granite"
    SLATE = "slate"
    
    # Emissive presets
    LIGHT_BULB = "light_bulb"
    NEON = "neon"
    GLOW = "glow"

@blender_operation
def _create_base_material_script(name: str, material_type: Union[str, MaterialType]) -> str:
    """Generate a base material creation script with error handling.
    
    Args:
        name: Name for the new material
        material_type: Type of material (from MaterialType or string)
        
    Returns:
        str: Python script to create the base material
    """
    return f"""
import math
from mathutils import Color

try:
    # Remove existing material if it exists
    if "{name}" in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials["{name}"])
    
    # Create new material with nodes
    mat = bpy.data.materials.new(name="{name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Add output and shader nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    
    # Connect BSDF to output
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Add texture coordinate and mapping nodes as they're commonly used
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-400, 0)
    
    # Connect texture coordinate to mapping
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    
    # Store material type as custom property
    mat["material_type"] = "{material_type}"
    
    # Return all created nodes for further processing
    return {{
        'mat': mat,
        'nodes': nodes,
        'links': links,
        'bsdf': bsdf,
        'tex_coord': tex_coord,
        'mapping': mapping
    }}
    
except Exception as e:
    print(f"ERROR: Failed to create base material: {{str(e)}}")
    import traceback
    traceback.print_exc()
    raise e
"""

# Register tools after app is created to avoid circular imports
def _register_material_tools():
    app = get_app()

    @app.tool
    @blender_operation("create_fabric_material", log_args=True)
    async def create_fabric_material_tool(
        name: str = "ElegantFabric",
        fabric_type: Union[str, MaterialPreset] = MaterialPreset.VELVET,
        base_color: Tuple[float, float, float] = (0.8, 0.75, 0.7),
        roughness: float = 0.8,
        sub_surface: float = 0.2,
        normal_strength: float = 0.5,
        velvet_softness: float = 0.5,
        silk_sheen: float = 0.8,
        weave_scale: float = 1.0
    ) -> str:
        """Create comprehensive fabric material with PBR properties.

        Args:
            name: Name for the new material
            fabric_type: Type of fabric (velvet, silk, cotton, linen, brocade, satin, wool)
            base_color: Base color as RGB tuple (0-1)
            roughness: Roughness value (0-1)
            sub_surface: Subsurface scattering amount (0-1)
            normal_strength: Normal map strength (0-1)
            velvet_softness: For velvet materials (0-1)
            silk_sheen: For silk materials (0-1)
            weave_scale: For woven fabrics (0.1-10.0)

        Returns:
            str: Confirmation message
        """
        return await create_fabric_material(
            name=name,
            fabric_type=fabric_type,
            base_color=base_color,
            roughness=roughness,
            sub_surface=sub_surface,
            normal_strength=normal_strength,
            velvet_softness=velvet_softness,
            silk_sheen=silk_sheen,
            weave_scale=weave_scale
        )

# Keep the original function for backward compatibility
@blender_operation("create_fabric_material", log_args=True)
async def create_fabric_material(
    name: str = "ElegantFabric",
    fabric_type: Union[str, MaterialPreset] = MaterialPreset.VELVET,
    base_color: Tuple[float, float, float] = (0.8, 0.75, 0.7),
    roughness: float = 0.8,
    sub_surface: float = 0.2,
    normal_strength: float = 0.5,
    velvet_softness: float = 0.5,
    silk_sheen: float = 0.8,
    weave_scale: float = 1.0
) -> str:
    """Create comprehensive fabric material with PBR properties.
    
    Args:
        name: Name for the new material
        fabric_type: Type of fabric (velvet, silk, cotton, linen, brocade, satin, wool)
        base_color: Base color as RGB tuple (0-1)
        roughness: Roughness value (0-1)
        sub_surface: Subsurface scattering amount (0-1)
        normal_strength: Normal map strength (0-1)
        velvet_softness: For velvet materials (0-1)
        silk_sheen: For silk materials (0-1)
        weave_scale: For woven fabrics (0.1-10.0)
            
    Returns:
        str: Confirmation message with created material name
        
    Raises:
        BlenderMaterialError: If fabric type is invalid or creation fails
    """
    # Convert string to MaterialPreset if needed
    if isinstance(fabric_type, str):
        fabric_type = MaterialPreset(fabric_type.lower())
    
    # Validate fabric type
    valid_fabrics = [
        MaterialPreset.VELVET, MaterialPreset.SILK, MaterialPreset.COTTON,
        MaterialPreset.LINEN, MaterialPreset.BROCADE, MaterialPreset.SATIN,
        MaterialPreset.WOOL
    ]
    
    if fabric_type not in valid_fabrics:
        raise BlenderMaterialError(
            name, "fabric_create", 
            f"Invalid fabric type: {fabric_type}. Must be one of: {', '.join(f.value for f in valid_fabrics)}"
        )
    
    # Unpack base color
    base_r, base_g, base_b = base_color
    
    # Use fabric-specific parameters (already passed as explicit parameters)
    
    try:
        script = _create_base_material_script(name, f"fabric_{fabric_type.value}")
        script += f"""
# Unpack nodes
mat = result['mat']
nodes = result['nodes']
links = result['links']
bsdf = result['bsdf']
mapping = result['mapping']

# Configure fabric-specific settings
bsdf.inputs['Base Color'].default_value = ({base_r}, {base_g}, {base_b}, 1.0)
bsdf.inputs['Roughness'].default_value = {roughness}
bsdf.inputs['Sheen Tint'].default_value = 0.0  # More accurate for fabrics

# Fabric-specific properties
mat["fabric_type"] = "{fabric_type.value}"
mat["is_fabric"] = True
"""
        # Add fabric-specific node setups
        if fabric_type == MaterialPreset.VELVET:
            script += f"""
# Velvet specific settings
bsdf.inputs['Sheen'].default_value = {velvet_softness}
bsdf.inputs['Sheen Tint'].default_value = 0.5
bsdf.inputs['Specular'].default_value = 0.2
bsdf.inputs['Specular Tint'].default_value = 0.0
bsdf.inputs['Subsurface'].default_value = 0.5
bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1)  # Reddish subsurface scattering
"""
        elif fabric_type == MaterialPreset.SILK:
            script += f"""
# Silk specific settings
bsdf.inputs['Sheen'].default_value = {silk_sheen}
bsdf.inputs['Sheen Tint'].default_value = 0.0
bsdf.inputs['Specular'].default_value = 0.5
bsdf.inputs['Specular Tint'].default_value = 0.0
bsdf.inputs['Clearcoat'].default_value = 0.2
bsdf.inputs['Clearcoat Roughness'].default_value = 0.1
"""
        elif fabric_type in [MaterialPreset.COTTON, MaterialPreset.LINEN]:
            script += f"""
# Woven fabric settings
noise_tex = nodes.new(type='ShaderNodeTexNoise')
noise_tex.inputs['Scale'].default_value = {weave_scale}
noise_tex.inputs['Detail'].default_value = 2.0
noise_tex.location = (-400, -200)

# Create subtle weave pattern
bump = nodes.new(type='ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.05
bump.location = (0, -100)

# Connect nodes
links.new(mapping.outputs['Vector'], noise_tex.inputs['Vector'])
links.new(noise_tex.outputs['Fac'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
"""
        elif fabric_type == MaterialPreset.BROCADE:
            script += f"""
# Brocade fabric with pattern
wave_tex = nodes.new(type='ShaderNodeTexWave')
wave_tex.wave_type = 'RINGS'
wave_tex.inputs['Scale'].default_value = 10.0
wave_tex.inputs['Distortion'].default_value = 5.0
wave_tex.location = (-400, -200)

color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].color = (0.8, 0.7, 0.6, 1.0)  # Base color
color_ramp.color_ramp.elements[1].color = (0.5, 0.4, 0.3, 1.0)  # Pattern color
color_ramp.location = (-200, -200)

# Connect pattern
links.new(mapping.outputs['Vector'], wave_tex.inputs['Vector'])
links.new(wave_tex.outputs['Color'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
"""
        # Add common fabric properties
        script += f"""
# Common fabric properties
bsdf.inputs['Subsurface'].default_value = {sub_surface}
bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.2, 0.1)  # Reddish subsurface for skin-like scattering

# Normal map for fabric weave (subtle)
normal_map = nodes.new(type='ShaderNodeNormalMap')
normal_map.inputs['Strength'].default_value = {normal_strength}
normal_map.location = (-200, -400)

# Connect normal map
links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])

# Set material blend mode for transparency if needed
if {sub_surface} > 0.3:
    mat.blend_method = 'BLEND'
    mat.shadow_method = 'HASHED'
    mat.use_screen_refraction = True
    mat.refraction_depth = 0.1

print(f"SUCCESS: Created {{'{fabric_type.value}'}} fabric material: {{mat.name}}")
"""
        await _executor.execute_script(script, script_name=f"fabric_{name}")
        return f"Created {fabric_type.value} fabric material: {name}"
        
    except Exception as e:
        error_msg = f"Failed to create fabric material {name}: {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(name, "fabric_create", error_msg)

@blender_operation("create_metal_material", log_args=True)
async def create_metal_material(
    name: str = "OrnateMetal",
    metal_type: Union[str, MaterialPreset] = MaterialPreset.GOLD,
    roughness: float = 0.2,
    anisotropic: float = 0.0,
    clearcoat: float = 0.0,
    clearcoat_roughness: float = 0.1,
    oxidation: float = 0.0,
    fingerprint: float = 0.0,
    edge_wear: float = 0.0
) -> str:
    """Create physically accurate metallic material with advanced PBR properties.
    
    Args:
        name: Name for the new material
        metal_type: Type of metal (gold, silver, brass, copper, iron, aluminum, chrome)
        roughness: Roughness value (0-1)
        anisotropic: Anisotropic reflection amount (0-1)
        clearcoat: Clearcoat layer intensity (0-1)
        clearcoat_roughness: Clearcoat roughness (0-1)
        oxidation: For aged/weathered metals (0-1)
        fingerprint: Add fingerprint smudges (0-1)
        edge_wear: Edge wear amount (0-1)
            
    Returns:
        str: Confirmation message with created material name
        
    Raises:
        BlenderMaterialError: If metal type is invalid or creation fails
    """
    # Convert string to MaterialPreset if needed
    if isinstance(metal_type, str):
        metal_type = MaterialPreset(metal_type.lower())
    
    # Define metal properties
    metal_properties = {
        MaterialPreset.GOLD: {
            'color': (0.8, 0.6, 0.2, 1.0),
            'roughness': 0.2,
            'metallic': 1.0,
            'specular': 0.5,
            'anisotropic': 0.3,
            'clearcoat': 0.2
        },
        MaterialPreset.SILVER: {
            'color': (0.95, 0.95, 0.97, 1.0),
            'roughness': 0.15,
            'metallic': 1.0,
            'specular': 0.5,
            'anisotropic': 0.2,
            'clearcoat': 0.3
        },
        MaterialPreset.BRASS: {
            'color': (0.88, 0.78, 0.5, 1.0),
            'roughness': 0.25,
            'metallic': 1.0,
            'specular': 0.5,
            'anisotropic': 0.1,
            'clearcoat': 0.1
        },
        MaterialPreset.COPPER: {
            'color': (0.95, 0.64, 0.54, 1.0),
            'roughness': 0.3,
            'metallic': 1.0,
            'specular': 0.5,
            'anisotropic': 0.1,
            'clearcoat': 0.1
        },
        MaterialPreset.IRON: {
            'color': (0.56, 0.57, 0.58, 1.0),
            'roughness': 0.4,
            'metallic': 1.0,
            'specular': 0.5,
            'anisotropic': 0.05,
            'clearcoat': 0.0
        },
        MaterialPreset.ALUMINUM: {
            'color': (0.91, 0.92, 0.92, 1.0),
            'roughness': 0.15,
            'metallic': 1.0,
            'specular': 0.5,
            'anisotropic': 0.7,
            'clearcoat': 0.2
        },
        MaterialPreset.CHROME: {
            'color': (0.98, 0.98, 0.99, 1.0),
            'roughness': 0.05,
            'metallic': 1.0,
            'specular': 0.5,
            'anisotropic': 0.5,
            'clearcoat': 0.5
        }
    }
    
    if metal_type not in metal_properties:
        valid_metals = [m.value for m in [
            MaterialPreset.GOLD, MaterialPreset.SILVER, MaterialPreset.BRASS,
            MaterialPreset.COPPER, MaterialPreset.IRON, MaterialPreset.ALUMINUM,
            MaterialPreset.CHROME
        ]]
        raise BlenderMaterialError(
            name, "metal_create",
            f"Invalid metal type: {metal_type}. Must be one of: {', '.join(valid_metals)}"
        )
    
    # Get metal properties with overrides from kwargs
    props = metal_properties[metal_type].copy()
    props.update({
        'roughness': roughness or props['roughness'],
        'anisotropic': anisotropic if anisotropic is not None else props['anisotropic'],
        'clearcoat': clearcoat if clearcoat is not None else props['clearcoat']
    })
    
    # Additional parameters are now explicit function parameters
    
    try:
        script = _create_base_material_script(name, f"metal_{metal_type.value}")
        script += f"""
# Unpack nodes
mat = result['mat']
nodes = result['nodes']
links = result['links']
bsdf = result['bsdf']
mapping = result['mapping']

# Base metal properties
bsdf.inputs['Base Color'].default_value = {props['color']}
bsdf.inputs['Metallic'].default_value = {props['metallic']}
bsdf.inputs['Roughness'].default_value = {props['roughness']}
bsdf.inputs['Specular'].default_value = {props['specular']}
bsdf.inputs['Anisotropic'].default_value = {props['anisotropic']}
bsdf.inputs['Anisotropic Rotation'].default_value = 0.2
bsdf.inputs['Clearcoat'].default_value = {props['clearcoat']}
bsdf.inputs['Clearcoat Roughness'].default_value = {clearcoat_roughness}

# Metal-specific properties
mat["metal_type"] = "{metal_type.value}"
mat["is_metal"] = True
"""
        # Add oxidation effect if needed
        if oxidation > 0:
            script += f"""
# Add oxidation effect
oxidation_mix = nodes.new(type='ShaderNodeMixRGB')
oxidation_mix.blend_type = 'MIX'
oxidation_mix.inputs['Fac'].default_value = {oxidation}
oxidation_mix.location = (-200, -200)

# Create oxidized color based on metal type
if "{metal_type.value}" == "copper":
    oxidized_color = (0.4, 0.6, 0.3, 1.0)  # Verdigris
elif "{metal_type.value}" == "iron":
    oxidized_color = (0.5, 0.5, 0.5, 1.0)  # Rust
else:
    oxidized_color = (0.6, 0.6, 0.6, 1.0)  # Generic tarnish

offset = 0.2  # Base offset for node positioning
oxidation_mix.inputs['Color1'].default_value = oxidized_color
oxidation_mix.inputs['Color2'].default_value = {props['color']}

# Connect to base color
links.new(oxidation_mix.outputs['Color'], bsdf.inputs['Base Color'])
"""
        # Add fingerprint smudges
        if fingerprint > 0:
            script += f"""
# Add fingerprint smudges
fingerprint_tex = nodes.new(type='ShaderNodeTexNoise')
fingerprint_tex.inputs['Scale'].default_value = 50.0
fingerprint_tex.inputs['Detail'].default_value = 16.0
fingerprint_tex.inputs['Distortion'].default_value = 1.0
fingerprint_tex.location = (-600, -400)

fingerprint_bump = nodes.new(type='ShaderNodeBump')
fingerprint_bump.inputs['Strength'].default_value = 0.1 * {fingerprint}
fingerprint_bump.location = (-400, -400)

# Connect fingerprint nodes
links.new(mapping.outputs['Vector'], fingerprint_tex.inputs['Vector'])
links.new(fingerprint_tex.outputs['Fac'], fingerprint_bump.inputs['Height'])
links.new(fingerprint_bump.outputs['Normal'], bsdf.inputs['Normal'])
"""
        # Add edge wear
        if edge_wear > 0:
            script += f"""
# Add edge wear
edge_wear = nodes.new(type='ShaderNodeAmbientOcclusion')
edge_wear.inside = True
edge_wear.only_local = True
edge_wear.location = (-600, -600)

edge_wear_ramp = nodes.new(type='ShaderNodeValToRGB')
edge_wear_ramp.color_ramp.elements[0].position = 0.0
edge_wear_ramp.color_ramp.elements[1].position = 1.0
edge_wear_ramp.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)  # Worn edges
edge_wear_ramp.color_ramp.elements[1].color = (0.8, 0.8, 0.8, 1.0)  # Base color
edge_wear_ramp.location = (-400, -600)

edge_wear_mix = nodes.new(type='ShaderNodeMixRGB')
edge_wear_mix.blend_type = 'MULTIPLY'
edge_wear_mix.inputs['Fac'].default_value = {edge_wear}
edge_wear_mix.location = (-200, -400)

# Connect edge wear nodes
links.new(edge_wear.outputs['Color'], edge_wear_ramp.inputs['Fac'])
links.new(edge_wear_ramp.outputs['Color'], edge_wear_mix.inputs['Color1'])
links.new(bsdf.outputs['Base Color'], edge_wear_mix.inputs['Color2'])
links.new(edge_wear_mix.outputs['Color'], bsdf.inputs['Base Color'])
"""
        script += f"""
print(f"SUCCESS: Created {{'{metal_type.value}'}} metal material: {{mat.name}}")
"""
        await _executor.execute_script(script, script_name=f"metal_{name}")
        return f"Created {metal_type.value} metal material: {name}"
        
    except Exception as e:
        error_msg = f"Failed to create metal material {name}: {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(name, "metal_create", error_msg)

@blender_operation("create_wood_material", log_args=True)
async def create_wood_material(
    name: str = "WoodMaterial",
    wood_type: str = "oak",
    grain_scale: float = 5.0,
    roughness: float = 0.7,
    bump_strength: float = 0.1
) -> str:
    """Create realistic wood material with grain texture.
    
    Args:
        name: Material name
        wood_type: Type of wood (oak, mahogany, pine, walnut, cherry, maple)
        grain_scale: Scale of wood grain (0.1-20.0)
        roughness: Surface roughness (0-1)
        bump_strength: Bump strength (0-1)
    """
    wood_colors = {
        "oak": {"base": (0.4,0.25,0.15), "ring": (0.3,0.2,0.1)},
        "mahogany": {"base": (0.3,0.15,0.1), "ring": (0.2,0.1,0.05)},
        "pine": {"base": (0.6,0.45,0.3), "ring": (0.5,0.35,0.2)},
        "walnut": {"base": (0.25,0.15,0.1), "ring": (0.15,0.1,0.05)},
        "cherry": {"base": (0.35,0.15,0.1), "ring": (0.25,0.1,0.05)},
        "maple": {"base": (0.7,0.6,0.5), "ring": (0.6,0.5,0.4)}
    }
    
    wood_type = wood_type.lower()
    if wood_type not in wood_colors:
        valid = ", ".join(wood_colors.keys())
        raise BlenderMaterialError(name, "wood_create", f"Invalid wood type. Use one of: {valid}")
    
    base_r, base_g, base_b = wood_colors[wood_type]["base"]
    ring_r, ring_g, ring_b = wood_colors[wood_type]["ring"]
    
    try:
        script = _create_base_material_script(name, f"wood_{wood_type}")
        script += f"""
# Create wood grain
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = {grain_scale}
noise.inputs['Detail'].default_value = 8.0
noise.location = (-600, 0)

# Create wood rings
wave = nodes.new('ShaderNodeTexWave')
wave.wave_type = 'RINGS'
wave.inputs['Scale'].default_value = {grain_scale * 0.2}
wave.location = (-400, 0)

# Mix colors
color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].color = ({base_r}, {base_g}, {base_b}, 1.0)
color_ramp.color_ramp.elements[1].color = ({ring_r}, {ring_g}, {ring_b}, 1.0)
color_ramp.location = (-200, 0)

# Bump mapping
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = {bump_strength}
bump.location = (0, 0)

# Connect nodes
links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
links.new(noise.outputs['Fac'], bump.inputs['Height'])
links.new(wave.outputs['Color'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

# Material properties
bsdf.inputs['Roughness'].default_value = {roughness}
bsdf.inputs['Specular'].default_value = 0.2
mat["wood_type"] = "{wood_type}"

print(f"SUCCESS: Created {{'{wood_type}'}} wood material: {{mat.name}}")
"""
        await _executor.execute_script(script, script_name=f"wood_{name}")
        return f"Created {wood_type} wood material: {name}"
        
    except Exception as e:
        error_msg = f"Failed to create wood material {name}: {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(name, "wood_create", error_msg)


@blender_operation("create_glass_material", log_args=True)
async def create_glass_material(
    name: str = "GlassMaterial",
    glass_type: Union[str, MaterialPreset] = MaterialPreset.CLEAR_GLASS,
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    roughness: float = 0.0,
    ior: float = 1.45,
    **kwargs
) -> str:
    """Create realistic glass material with customizable properties.
    
    Args:
        name: Material name
        glass_type: Type of glass (clear_glass, frosted_glass, stained_glass)
        color: Base color of the glass (RGB, 0-1)
        roughness: Surface roughness (0-1)
        ior: Index of Refraction (1.0-2.5)
        **kwargs: Additional parameters:
            - transmission: Amount of light transmitted (0-1, default: 1.0)
            - dispersion: Chromatic aberration amount (0-0.1)
            - thickness: Glass thickness for absorption (0-1)
            - normal: Custom normal map strength (0-1)
    """
    # Convert string to MaterialPreset if needed
    if isinstance(glass_type, str):
        glass_type = MaterialPreset(glass_type.lower())
    
    # Validate glass type
    valid_glass_types = [
        MaterialPreset.CLEAR_GLASS,
        MaterialPreset.FROSTED_GLASS,
        MaterialPreset.STAINED_GLASS
    ]
    
    if glass_type not in valid_glass_types:
        valid = ", ".join([t.value for t in valid_glass_types])
        raise BlenderMaterialError(
            name, "glass_create", 
            f"Invalid glass type. Use one of: {valid}"
        )
    
    # Get additional parameters with defaults
    transmission = kwargs.get('transmission', 1.0)
    dispersion = kwargs.get('dispersion', 0.0)
    thickness = kwargs.get('thickness', 0.1)
    normal_strength = kwargs.get('normal', 0.0)
    
    # Unpack color
    r, g, b = color
    
    try:
        script = _create_base_material_script(name, f"glass_{glass_type.value}")
        script += f"""
# Configure glass properties
bsdf.inputs['Base Color'].default_value = ({r}, {g}, {b}, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Specular'].default_value = 0.5
bsdf.inputs['Roughness'].default_value = {roughness}
bsdf.inputs['Transmission'].default_value = {transmission}
bsdf.inputs['IOR'].default_value = {ior}
bsdf.inputs['Alpha'].default_value = 1.0

# Enable screen space refraction for better quality
mat.blend_method = 'BLEND'
mat.use_backface_culling = True
mat.use_screen_refraction = True
mat.refraction_depth = {thickness * 0.1}
mat.shadow_method = 'HASHED'

# Store material type
mat["glass_type"] = "{glass_type.value}"
"""
        # Add effects based on glass type
        if glass_type == MaterialPreset.FROSTED_GLASS:
            script += """
# Frosted glass effect
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.1
bump.location = (-200, -200)

noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 50.0
noise.inputs['Detail'].default_value = 8.0
noise.location = (-400, -200)

# Connect nodes
links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

# Adjust roughness for frosted look
bsdf.inputs['Roughness'].default_value = max(0.3, bsdf.inputs['Roughness'].default_value)
"""
        elif glass_type == MaterialPreset.STAINED_GLASS:
            script += """
# Stained glass effect
bsdf.inputs['Emission Color'].default_value = bsdf.inputs['Base Color'].default_value
bsdf.inputs['Emission Strength'].default_value = 0.1
bsdf.inputs['Alpha'].default_value = 0.8

# Add subtle noise for hand-painted look
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 5.0
noise.inputs['Detail'].default_value = 2.0
noise.location = (-400, -400)

color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].position = 0.4
color_ramp.color_ramp.elements[1].position = 0.6
color_ramp.location = (-200, -400)

# Connect nodes
links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
"""
        # Add dispersion effect if enabled
        if dispersion > 0:
            script += f"""
# Chromatic aberration effect
dispersion_group = nodes.new('ShaderNodeGroup')
dispersion_group.node_tree = bpy.data.node_groups.new('Dispersion', 'ShaderNodeTree')
dispersion_group.location = (200, 0)

# Create dispersion node group
group = dispersion_group.node_tree
group_inputs = group.nodes.new('NodeGroupInput')
group_outputs = group.nodes.new('NodeGroupOutput')

# Add dispersion shader logic here...

# Connect dispersion
try:
    links.new(bsdf.outputs['BSDF'], dispersion_group.inputs[0])
    links.new(dispersion_group.outputs[0], output.inputs['Surface'])
except:
    pass  # Fallback if dispersion setup fails
"""
        script += f"""
# Final material setup
bsdf.inputs['Roughness'].default_value = min(0.3, bsdf.inputs['Roughness'].default_value)
mat.blend_method = 'BLEND'
mat.use_screen_refraction = True

print(f"SUCCESS: Created {{'{glass_type.value}'}} glass material: {{mat.name}}")
"""
        await _executor.execute_script(script, script_name=f"glass_{name}")
        return f"Created {glass_type.value} glass material: {name}"
        
    except Exception as e:
        error_msg = f"Failed to create glass material {name}: {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(name, "glass_create", error_msg)


@blender_operation("create_ceramic_material", log_args=True)
async def create_ceramic_material(
    name: str = "CeramicMaterial",
    ceramic_type: Union[str, MaterialPreset] = MaterialPreset.PORCELAIN,
    base_color: Tuple[float, float, float] = (0.9, 0.9, 0.9),
    roughness: float = 0.1,
    **kwargs
) -> str:
    """Create realistic ceramic/porcelain material with customizable properties.
    
    Args:
        name: Material name
        ceramic_type: Type of ceramic (porcelain, earthenware, stoneware, terracotta)
        base_color: Base color of the ceramic (RGB, 0-1)
        roughness: Surface roughness (0-1)
        **kwargs: Additional parameters:
            - glaze_strength: Amount of glaze (0-1)
            - glaze_roughness: Glaze layer roughness (0-1)
            - glaze_color: Glaze color (RGB, 0-1)
    """
    # Convert string to MaterialPreset if needed
    if isinstance(ceramic_type, str):
        ceramic_type = MaterialPreset(ceramic_type.lower())
    
    # Validate ceramic type
    valid_ceramic_types = [
        MaterialPreset.PORCELAIN,
        MaterialPreset.EARTHENWARE,
        MaterialPreset.STONEWARE,
        MaterialPreset.TERRACOTTA
    ]
    
    if ceramic_type not in valid_ceramic_types:
        valid = ", ".join([t.value for t in valid_ceramic_types])
        raise BlenderMaterialError(
            name, "ceramic_create", 
            f"Invalid ceramic type. Use one of: {valid}"
        )
    
    # Get additional parameters with defaults
    glaze_strength = kwargs.get('glaze_strength', 0.8)
    glaze_roughness = kwargs.get('glaze_roughness', 0.2)
    glaze_color = kwargs.get('glaze_color', (1.0, 1.0, 1.0))
    
    # Unpack colors
    r, g, b = base_color
    gr, gg, gb = glaze_color
    
    try:
        script = _create_base_material_script(name, f"ceramic_{ceramic_type.value}")
        script += f"""
# Configure base ceramic properties
bsdf.inputs['Base Color'].default_value = ({r}, {g}, {b}, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Specular'].default_value = 0.5
bsdf.inputs['Roughness'].default_value = {roughness}
bsdf.inputs['Sheen Weight'].default_value = 0.1

# Add surface detail
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 100.0
noise.inputs['Detail'].default_value = 8.0
noise.location = (-400, -100)

bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.1
bump.location = (-200, -100)

# Connect nodes
links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
"""
        # Add glaze layer if enabled
        if glaze_strength > 0:
            script += f"""
# Add glaze layer
mix_shader = nodes.new('ShaderNodeMixShader')
mix_shader.inputs['Fac'].default_value = {glaze_strength}
mix_shader.location = (400, 0)

glaze_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
glaze_bsdf.location = (200, 200)
glaze_bsdf.inputs['Base Color'].default_value = ({gr}, {gg}, {gb}, 1.0)
glaze_bsdf.inputs['Roughness'].default_value = {glaze_roughness}

# Connect glaze
links.new(bsdf.outputs['BSDF'], mix_shader.inputs[1])
links.new(glaze_bsdf.outputs['BSDF'], mix_shader.inputs[2])
links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
"""
        script += f"""
# Final material setup
mat.blend_method = 'OPAQUE'
print(f"SUCCESS: Created {{'{ceramic_type.value}'}} ceramic material: {{mat.name}}")
"""
        await _executor.execute_script(script, script_name=f"ceramic_{name}")
        return f"Created {ceramic_type.value} ceramic material: {name}"
        
    except Exception as e:
        error_msg = f"Failed to create ceramic material {name}: {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(name, "ceramic_create", error_msg)


@blender_operation("create_leather_material", log_args=True)
async def create_leather_material(
    name: str = "LeatherMaterial",
    leather_type: Union[str, MaterialPreset] = MaterialPreset.LEATHER,
    base_color: Tuple[float, float, float] = (0.15, 0.05, 0.02),
    roughness: float = 0.7,
    **kwargs
) -> str:
    """Create realistic leather material with customizable properties.
    
    Args:
        name: Material name
        leather_type: Type of leather (genuine, bonded, faux, suede, patent)
        base_color: Base color of the leather (RGB, 0-1)
        roughness: Surface roughness (0-1)
        **kwargs: Additional parameters:
            - wear_amount: Amount of wear/aging (0-1)
            - bump_strength: Strength of surface details (0-1)
            - specular: Specular intensity (0-1)
            - sheen: Sheen intensity (0-1)
            - stitch_effect: Add stitching effect (True/False)
    """
    # Convert string to MaterialPreset if needed
    if isinstance(leather_type, str):
        leather_type = MaterialPreset(leather_type.lower())
    
    # Validate leather type
    valid_leather_types = [
        MaterialPreset.LEATHER,
        MaterialPreset.PATENT_LEATHER,
        MaterialPreset.SUEDE
    ]
    
    if leather_type not in valid_leather_types:
        valid = ", ".join([t.value for t in valid_leather_types])
        raise BlenderMaterialError(
            name, "leather_create", 
            f"Invalid leather type. Use one of: {valid}"
        )
    
    # Get additional parameters with defaults
    wear_amount = kwargs.get('wear_amount', 0.3)
    bump_strength = kwargs.get('bump_strength', 0.5)
    specular = kwargs.get('specular', 0.5)
    sheen = kwargs.get('sheen', 0.3)
    stitch_effect = kwargs.get('stitch_effect', False)
    
    # Unpack color
    r, g, b = base_color
    
    try:
        script = _create_base_material_script(name, f"leather_{leather_type.value}")
        script += f"""
# Configure base leather properties
bsdf.inputs['Base Color'].default_value = ({r}, {g}, {b}, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Specular'].default_value = {specular}
bsdf.inputs['Roughness'].default_value = {roughness}
bsdf.inputs['Sheen Weight'].default_value = {sheen}
bsdf.inputs['Sheen Tint'].default_value = 0.0

# Add leather texture
noise1 = nodes.new('ShaderNodeTexNoise')
noise1.inputs['Scale'].default_value = 50.0
noise1.inputs['Detail'].default_value = 8.0
noise1.inputs['Roughness'].default_value = 0.7
noise1.location = (-600, 0)

noise2 = nodes.new('ShaderNodeTexNoise')
noise2.inputs['Scale'].default_value = 200.0
noise2.inputs['Detail'].default_value = 16.0
noise2.location = (-600, -200)

mix = nodes.new('ShaderNodeMixRGB')
mix.blend_type = 'MULTIPLY'
mix.inputs['Fac'].default_value = 0.3
mix.location = (-400, 0)

bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = {bump_strength}
bump.location = (-200, 0)

# Connect nodes
links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
links.new(noise1.outputs['Fac'], mix.inputs[1])
links.new(noise2.outputs['Fac'], mix.inputs[2])
links.new(mix.outputs['Color'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
"""
        # Add wear effect if needed
        if wear_amount > 0:
            script += f"""
# Add wear effect
wear = nodes.new('ShaderNodeTexVoronoi')
wear.inputs['Scale'].default_value = 10.0
wear.location = (-800, -400)

wear_ramp = nodes.new('ShaderNodeValToRGB')
wear_ramp.color_ramp.elements[0].position = 0.4
wear_ramp.color_ramp.elements[1].position = 0.6
wear_ramp.location = (-600, -400)

wear_mix = nodes.new('ShaderNodeMixRGB')
wear_mix.inputs['Fac'].default_value = {wear_amount}
wear_mix.location = (-400, -400)

# Connect wear nodes
links.new(mapping.outputs['Vector'], wear.inputs['Vector'])
links.new(wear.outputs['Distance'], wear_ramp.inputs['Fac'])
links.new(bsdf.inputs['Base Color'].default_value, wear_mix.inputs[1])
links.new(wear_ramp.outputs['Color'], wear_mix.inputs[2])
links.new(wear_mix.outputs['Color'], bsdf.inputs['Base Color'])
"""
        # Add stitching if needed
        if stitch_effect:
            script += """
# Add stitching effect
stitch = nodes.new('ShaderNodeTexWave')
stitch.wave_type = 'RINGS'
stitch.inputs['Scale'].default_value = 50.0
stitch.inputs['Distortion'].default_value = 5.0
stitch.location = (-800, -600)

stitch_ramp = nodes.new('ShaderNodeValToRGB')
stitch_ramp.color_ramp.elements[0].position = 0.49
stitch_ramp.color_ramp.elements[1].position = 0.51
stitch_ramp.location = (-600, -600)

stitch_bump = nodes.new('ShaderNodeBump')
stitch_bump.inputs['Strength'].default_value = 0.1
stitch_bump.location = (-400, -600)

# Connect stitching nodes
links.new(mapping.outputs['Vector'], stitch.inputs['Vector'])
links.new(stitch.outputs['Fac'], stitch_ramp.inputs['Fac'])
links.new(stitch_ramp.outputs['Color'], stitch_bump.inputs['Height'])
links.new(stitch_bump.outputs['Normal'], bsdf.inputs['Normal'])
"""
        script += f"""
# Final material setup
mat.blend_method = 'OPAQUE'
print(f"SUCCESS: Created {{'{leather_type.value}'}} leather material: {{mat.name}}")
"""
        await _executor.execute_script(script, script_name=f"leather_{name}")
        return f"Created {leather_type.value} leather material: {name}"
        
    except Exception as e:
        error_msg = f"Failed to create leather material {name}: {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(name, "leather_create", error_msg)


@blender_operation("create_stone_material", log_args=True)
async def create_stone_material(
    name: str = "StoneMaterial",
    stone_type: Union[str, MaterialPreset] = MaterialPreset.MARBLE,
    base_color: Tuple[float, float, float] = (0.8, 0.8, 0.8),
    secondary_color: Optional[Tuple[float, float, float]] = None,
    roughness: float = 0.2,
    **kwargs
) -> str:
    """Create realistic stone/marble material with customizable properties.
    
    Args:
        name: Material name
        stone_type: Type of stone (marble, granite, slate, sandstone, limestone, onyx)
        base_color: Primary color of the stone (RGB, 0-1)
        secondary_color: Secondary/vein color (RGB, 0-1)
        roughness: Surface roughness (0-1)
        **kwargs: Additional parameters:
            - vein_scale: Scale of the veining pattern (0.1-10.0)
            - vein_contrast: Contrast of the veins (0-1)
            - polish: Surface polish amount (0-1)
            - normal_strength: Strength of surface details (0-1)
            - displacement: Height displacement amount (0-0.1)
    """
    # Convert string to MaterialPreset if needed
    if isinstance(stone_type, str):
        stone_type = MaterialPreset(stone_type.lower())
    
    # Validate stone type
    valid_stone_types = [
        MaterialPreset.MARBLE,
        MaterialPreset.GRANITE,
        MaterialPreset.SLATE,
        MaterialPreset.SANDSTONE,
        MaterialPreset.LIMESTONE,
        MaterialPreset.ONYX
    ]
    
    if stone_type not in valid_stone_types:
        valid = ", ".join([t.value for t in valid_stone_types])
        raise BlenderMaterialError(
            name, "stone_create", 
            f"Invalid stone type. Use one of: {valid}"
        )
    
    # Set default secondary color if not provided
    if secondary_color is None:
        if stone_type == MaterialPreset.MARBLE:
            secondary_color = (0.15, 0.15, 0.15)  # Dark gray for marble
        elif stone_type == MaterialPreset.GRANITE:
            secondary_color = (0.4, 0.3, 0.25)    # Brown for granite
        else:
            secondary_color = (base_color[0]*0.7, base_color[1]*0.7, base_color[2]*0.7)
    
    # Get additional parameters with defaults
    vein_scale = kwargs.get('vein_scale', 5.0)
    vein_contrast = kwargs.get('vein_contrast', 0.8)
    polish = kwargs.get('polish', 0.5)
    normal_strength = kwargs.get('normal_strength', 0.3)
    displacement = kwargs.get('displacement', 0.02)
    
    # Unpack colors
    r1, g1, b1 = base_color
    r2, g2, b2 = secondary_color
    
    try:
        script = _create_base_material_script(name, f"stone_{stone_type.value}")
        script += f"""
# Configure base stone properties
bsdf.inputs['Base Color'].default_value = ({r1}, {g1}, {b1}, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Specular'].default_value = 0.5
bsdf.inputs['Roughness'].default_value = {roughness}

# Create veining/wave pattern
wave = nodes.new('ShaderNodeTexWave')
wave.wave_type = 'RINGS'
wave.inputs['Scale'].default_value = {vein_scale}
wave.inputs['Distortion'].default_value = 5.0
wave.inputs['Detail Scale'].default_value = 2.0
wave.location = (-800, 0)

# Add noise for organic variation
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 10.0
noise.inputs['Detail'].default_value = 16.0
noise.location = (-800, -200)

# Mix patterns
mix_pattern = nodes.new('ShaderNodeMixRGB')
mix_pattern.blend_type = 'MULTIPLY'
mix_pattern.inputs['Fac'].default_value = 0.8
mix_pattern.location = (-600, 0)

# Create color ramp for veins
color_ramp = nodes.new('ShaderNodeValToRGB')
ramp = color_ramp.color_ramp
elements = ramp.elements

# Adjust ramp based on stone type
if '{stone_type.value}' == 'marble':
    elements[0].position = 0.4
    elements[1].position = 0.6
    elements[0].color = ({r1}, {g1}, {b1}, 1.0)
    elements[1].color = ({r2}, {g2}, {b2}, 1.0)
elif '{stone_type.value}' == 'granite':
    elements[0].position = 0.3
    elements[1].position = 0.7
    elements[0].color = ({r1}, {g1}, {b1}, 1.0)
    elements[1].color = ({r2}, {g2}, {b2}, 1.0)
    # Add a third color for granite
    elements.new(0.5)
    elements[2].color = (0.1, 0.1, 0.1, 1.0)

color_ramp.location = (-400, 0)

# Create bump map
bump = nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value = {normal_strength}
bump.location = (-200, 0)

# Connect nodes
links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
links.new(wave.outputs['Fac'], mix_pattern.inputs[1])
links.new(noise.outputs['Fac'], mix_pattern.inputs[2])
links.new(mix_pattern.outputs['Color'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(mix_pattern.outputs['Color'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
"""
        # Add displacement if enabled
        if displacement > 0:
            script += f"""
# Add displacement
disp = nodes.new('ShaderNodeDisplacement')
disp.inputs['Scale'].default_value = {displacement}
disp.location = (200, -200)

# Connect displacement
links.new(bump.outputs['Normal'], disp.inputs['Normal'])
links.new(disp.outputs['Displacement'], output.inputs['Displacement'])
"""
        # Add polish effect
        script += f"""
# Adjust roughness based on polish
bsdf.inputs['Roughness'].default_value = bsdf.inputs['Roughness'].default_value * (1.0 - {polish * 0.8})

# Add clearcoat for polished look
bsdf.inputs['Clearcoat'].default_value = {polish * 0.5}
bsdf.inputs['Clearcoat Roughness'].default_value = 0.1

# Final material setup
mat.blend_method = 'OPAQUE'
if {displacement} > 0:
    mat.cycles.displacement_method = 'BOTH'
    mat.cycles.use_displacement = True

print(f"SUCCESS: Created {{'{stone_type.value}'}} stone material: {{mat.name}}")
"""
        await _executor.execute_script(script, script_name=f"stone_{name}")
        return f"Created {stone_type.value} stone material: {name}"
        
    except Exception as e:
        error_msg = f"Failed to create stone material {name}: {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(name, "stone_create", error_msg)


@blender_operation
def assign_material(
    object_name: str,
    material_name: str,
    material_index: int = 0
) -> str:
    """Assign a material to an object.
    
    Args:
        object_name: Name of the object to assign material to
        material_name: Name of the material to assign
        material_index: Material slot index (0-based)
        
    Returns:
        str: Status message
    """
    script = f"""

# Get the object and material
obj = bpy.data.objects.get('{object_name}')
mat = bpy.data.materials.get('{material_name}')

if not obj:
    raise Exception(f"Object '{object_name}' not found")
if not mat:
    raise Exception(f"Material '{material_name}' not found")

# Ensure object has enough material slots
while len(obj.material_slots) <= {material_index}:
    obj.data.materials.append(None)

# Assign material to the slot
obj.material_slots[{material_index}].material = mat

# If object has no materials, assign to all faces
if hasattr(obj.data, 'polygons') and len(obj.material_slots) > 0:
    for poly in obj.data.polygons:
        poly.material_index = {material_index}

print(f"SUCCESS: Assigned material '{{material_name}}' to object '{{object_name}}' at slot {{material_index}}")
"""
    return script


@blender_operation
def remove_material(
    object_name: str,
    material_index: int = 0
) -> str:
    """Remove a material from an object.
    
    Args:
        object_name: Name of the object to remove material from
        material_index: Material slot index to clear (0-based)
        
    Returns:
        str: Status message
    """
    script = f"""

# Get the object
obj = bpy.data.objects.get('{object_name}')

if not obj:
    raise Exception(f"Object '{object_name}' not found")

# Check if material slot exists
if {material_index} >= len(obj.material_slots):
    raise Exception(f"Material slot {{material_index}} does not exist")

# Clear the material slot
obj.material_slots[{material_index}].material = None

# Remove the slot if it's not the last one
if len(obj.material_slots) > 1:
    obj.active_material_index = {material_index}
    bpy.ops.object.material_slot_remove()

print(f"SUCCESS: Removed material from slot {{material_index}} of object '{{object_name}}'")
"""
    return script


@blender_operation
def get_material_assignments(
    object_name: str
) -> str:
    """Get all materials assigned to an object.
    
    Args:
        object_name: Name of the object to check
        
    Returns:
        str: Status message with material assignments
    """
    script = f"""

# Get the object
obj = bpy.data.objects.get('{object_name}')

if not obj:
    raise Exception(f"Object '{object_name}' not found")

# Get material assignments
materials = []
for i, slot in enumerate(obj.material_slots):
    mat_name = slot.material.name if slot.material else "<empty>"
    materials.append(f"Slot {{i}}: {{mat_name}}")

if not materials:
    print(f"Object '{{object_name}}' has no material assignments")
else:
    print("Material assignments for object '{{object_name}}':")
    for mat in materials:
        print(f"  - {{mat}}")
"""
    return script


@blender_operation("assign_material", log_args=True)
async def assign_material_async(
    object_name: str,
    material_name: str,
    material_index: int = 0
) -> str:
    """Assign a material to an object asynchronously.
    
    Args:
        object_name: Name of the object to assign material to
        material_name: Name of the material to assign
        material_index: Material slot index (0-based)
        
    Returns:
        str: Status message
    """
    try:
        script = assign_material(object_name, material_name, material_index)
        await _executor.execute_script(script, script_name=f"assign_material_{object_name}_{material_name}")
        return f"Assigned material '{material_name}' to object '{object_name}' at slot {material_index}"
    except Exception as e:
        error_msg = f"Failed to assign material to object: {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(object_name, "assign_material", error_msg)


@blender_operation("remove_material", log_args=True)
async def remove_material_async(
    object_name: str,
    material_index: int = 0
) -> str:
    """Remove a material from an object asynchronously.
    
    Args:
        object_name: Name of the object to remove material from
        material_index: Material slot index to clear (0-based)
        
    Returns:
        str: Status message
    """
    try:
        script = remove_material(object_name, material_index)
        await _executor.execute_script(script, script_name=f"remove_material_{object_name}_{material_index}")
        return f"Removed material from slot {material_index} of object '{object_name}'"
    except Exception as e:
        error_msg = f"Failed to remove material from object: {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(object_name, "remove_material", error_msg)


@blender_operation("get_material_assignments", log_args=True)
async def get_material_assignments_async(
    object_name: str
) -> str:
    """Get all materials assigned to an object asynchronously.
    
    Args:
        object_name: Name of the object to check
        
    Returns:
        str: Status message with material assignments
    """
    try:
        script = get_material_assignments(object_name)
        result = await _executor.execute_script(script, script_name=f"get_material_assignments_{object_name}")
        return result or f"No material assignments found for object '{object_name}'"
    except Exception as e:
        error_msg = f"Failed to get material assignments: {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(object_name, "get_material_assignments", error_msg)


class MaterialLibrary:
    """A class to manage a library of material presets."""
    
    def __init__(self, library_name: str = "default"):
        """Initialize the material library.
        
        Args:
            library_name: Name of the library
        """
        self.library_name = library_name
        self.presets = {}
        
    def add_preset(
        self, 
        name: str, 
        material_type: str, 
        parameters: Dict[str, Any],
        category: str = "uncategorized"
    ) -> None:
        """Add a material preset to the library.
        
        Args:
            name: Name of the preset
            material_type: Type of material (e.g., 'fabric', 'metal', 'wood')
            parameters: Dictionary of material parameters
            category: Category for organization
        """
        if not name:
            raise ValueError("Preset name cannot be empty")
            
        self.presets[name] = {
            'type': material_type,
            'parameters': parameters,
            'category': category,
            'created_at': datetime.datetime.now().isoformat()
        }
    
    def get_preset(self, name: str) -> Dict[str, Any]:
        """Get a material preset by name.
        
        Args:
            name: Name of the preset to retrieve
            
        Returns:
            Dict containing the preset data
        """
        if name not in self.presets:
            raise KeyError(f"Preset '{name}' not found in library")
        return self.presets[name]
    
    def list_presets(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all presets, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of preset dictionaries with name and metadata
        """
        result = []
        for name, preset in self.presets.items():
            if category is None or preset['category'] == category:
                result.append({
                    'name': name,
                    'type': preset['type'],
                    'category': preset['category'],
                    'created_at': preset['created_at']
                })
        return result
    
    def remove_preset(self, name: str) -> None:
        """Remove a preset from the library.
        
        Args:
            name: Name of the preset to remove
        """
        if name in self.presets:
            del self.presets[name]
    
    def save_to_file(self, filepath: str) -> None:
        """Save the library to a JSON file.
        
        Args:
            filepath: Path to save the library file
        """
        with open(filepath, 'w') as f:
            json.dump({
                'name': self.library_name,
                'presets': self.presets
            }, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'MaterialLibrary':
        """Load a library from a JSON file.
        
        Args:
            filepath: Path to the library file
            
        Returns:
            Loaded MaterialLibrary instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        library = cls(data.get('name', 'imported_library'))
        library.presets = data.get('presets', {})
        return library


# Global default library
_default_library = MaterialLibrary("default")


def get_default_library() -> MaterialLibrary:
    """Get the default material library.
    
    Returns:
        The default MaterialLibrary instance
    """
    return _default_library


@blender_operation("create_material_from_preset", log_args=True)
async def create_material_from_preset(
    preset_name: str,
    material_name: Optional[str] = None,
    library: Optional[MaterialLibrary] = None
) -> str:
    """Create a material from a preset in the library.
    
    Args:
        preset_name: Name of the preset to use
        material_name: Optional name for the new material
        library: Optional library to use (defaults to default library)
        
    Returns:
        str: Name of the created material
        
    Raises:
        BlenderMaterialError: If preset not found or material creation fails
    """
    if library is None:
        library = get_default_library()
    
    try:
        # Get the preset
        preset = library.get_preset(preset_name)
        material_type = preset['type']
        params = preset['parameters']
        
        # Generate a name if not provided
        if material_name is None:
            material_name = f"{preset_name}_{int(time.time())}"
        
        # Create the material based on type
        if material_type == 'fabric':
            return await create_fabric_material(
                name=material_name,
                **params
            )
        elif material_type == 'metal':
            return await create_metal_material(
                name=material_name,
                **params
            )
        elif material_type == 'wood':
            return await create_wood_material(
                name=material_name,
                **params
            )
        elif material_type == 'glass':
            return await create_glass_material(
                name=material_name,
                **params
            )
        elif material_type == 'ceramic':
            return await create_ceramic_material(
                name=material_name,
                **params
            )
        elif material_type == 'leather':
            return await create_leather_material(
                name=material_name,
                **params
            )
        elif material_type == 'stone':
            return await create_stone_material(
                name=material_name,
                **params
            )
        else:
            raise ValueError(f"Unsupported material type: {material_type}")
            
    except Exception as e:
        error_msg = f"Failed to create material from preset '{preset_name}': {str(e)}"
        logger.error(error_msg)
        raise BlenderMaterialError(preset_name, "create_from_preset", error_msg)

# Register tools when this module is imported
_register_material_tools()

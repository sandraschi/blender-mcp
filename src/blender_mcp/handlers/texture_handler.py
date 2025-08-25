from ..compat import *

"""Texture operations handler for Blender MCP."""

from typing import Optional, List, Dict, Any, Union, Tuple
from enum import Enum
from pathlib import Path
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()

class TextureType(str, Enum):
    """Supported texture types."""
    IMAGE = "IMAGE"
    NOISE = "NOISE"
    VORONOI = "VORONOI"
    MUSGRAVE = "MUSGRAVE"
    DISTORTED_NOISE = "DISTORTED_NOISE"
    MAGIC = "MAGIC"
    WAVE = "WAVE"
    CHECKER = "CHECKER"
    BRICK = "BRICK"
    GRADIENT = "GRADIENT"
    VOXEL_DATA = "VOXEL_DATA"
    ENVIRONMENT_MAP = "ENVIRONMENT_MAP"
    POINT_DENSITY = "POINT_DENSITY"

class ImageSourceType(str, Enum):
    """Image source types for textures."""
    FILE = "FILE"
    GENERATED = "GENERATED"
    MOVIE = "MOVIE"
    SEQUENCE = "SEQUENCE"
    TILED = "TILED"
    VIEWER = "VIEWER"

@blender_operation("create_texture", log_args=True)
async def create_texture(
    name: str,
    texture_type: Union[TextureType, str],
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a new texture.
    
    Args:
        name: Name for the new texture
        texture_type: Type of texture to create
        **kwargs: Additional parameters
            - width: Width for generated textures (default: 1024)
            - height: Height for generated textures (default: 1024)
            - color: Base color for generated textures (default: [0.8, 0.8, 0.8, 1.0])
            - filepath: Path to image file for IMAGE type
            
    Returns:
        Dict containing texture creation status and details
    """
    width = kwargs.get('width', 1024)
    height = kwargs.get('height', 1024)
    color = kwargs.get('color', [0.8, 0.8, 0.8, 1.0])
    filepath = kwargs.get('filepath')
    
    script = f"""
import os

def create_texture():
    # Check if texture with this name already exists
    if '{name}' in bpy.data.textures:
        return {{"status": "ERROR", "error": f"Texture '{{name}}' already exists"}}
    
    try:
        # Create the texture
        if '{texture_type}' == 'IMAGE':
            # Create a new image texture
            if not '{filepath}':
                return {{"status": "ERROR", "error": "Filepath is required for IMAGE texture type"}}
                
            # Check if file exists
            if not os.path.exists('{filepath}'):
                return {{"status": "ERROR", "error": f"File not found: {{filepath}}"}}
                
            # Load the image
            try:
                img = bpy.data.images.load('{filepath}')
                img.name = '{name}'
            except Exception as e:
                return {{"status": "ERROR", "error": f"Failed to load image: {{str(e)}}"}}
                
            # Create texture using the image
            tex = bpy.data.textures.new('{name}', 'IMAGE')
            tex.image = img
            
        else:
            # Create a procedural texture
            tex = bpy.data.textures.new('{name}', type='{texture_type}')
            
            # Set common properties
            if hasattr(tex, 'color'):
                tex.color = {color[:3]}  # Only RGB for color property
            
            # Set type-specific properties
            if hasattr(tex, 'noise_scale'):
                tex.noise_scale = 0.25
            if hasattr(tex, 'noise_intensity'):
                tex.noise_intensity = 1.0
            if hasattr(tex, 'contrast'):
                tex.contrast = 1.0
            if hasattr(tex, 'brightness'):
                tex.brightness = 1.0
        
        return {{
            "status": "SUCCESS",
            "texture": tex.name,
            "type": tex.type,
            "is_procedural": tex.type != 'IMAGE',
            "dimensions": getattr(tex, 'size', [0, 0])
        }}
    except Exception as e:
        # Clean up if something went wrong
        if '{name}' in bpy.data.textures:
            bpy.data.textures.remove(bpy.data.textures['{name}'])
        if '{name}' in bpy.data.images:
            bpy.data.images.remove(bpy.data.images['{name}'])
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = create_texture()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create texture: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("assign_texture_to_material", log_args=True)
async def assign_texture_to_material(
    material_name: str,
    texture_name: str,
    texture_slot: str = "Base Color",
    **kwargs: Any
) -> Dict[str, Any]:
    """Assign a texture to a material slot.
    
    Args:
        material_name: Name of the material
        texture_name: Name of the texture to assign
        texture_slot: Which slot to assign to (e.g., 'Base Color', 'Metallic', 'Roughness')
        **kwargs: Additional parameters
            - node_group: Node group to use (default: 'ShaderNodeTexImage' for image textures)
            - strength: Influence strength (default: 1.0)
            
    Returns:
        Dict containing assignment status and details
    """
    node_group = kwargs.get('node_group')
    strength = kwargs.get('strength', 1.0)
    
    script = f"""

def assign_texture():
    # Get material and texture
    mat = bpy.data.materials.get('{material_name}')
    if not mat:
        return {{"status": "ERROR", "error": f"Material '{{material_name}}' not found"}}
    
    tex = bpy.data.textures.get('{texture_name}')
    if not tex:
        return {{"status": "ERROR", "error": f"Texture '{{texture_name}}' not found"}}
    
    try:
        # Enable use nodes
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear existing nodes if requested
        if {str(kwargs.get('clear_nodes', False)).lower()}:
            nodes.clear()
        
        # Get or create Principled BSDF
        principled = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
                break
        
        if not principled:
            principled = nodes.new('ShaderNodeBsdfPrincipled')
        
        # Create texture node
        node_type = '{node_group}' if '{node_group}' else 'ShaderNodeTexImage' if tex.type == 'IMAGE' else 'ShaderNodeTexNoise'
        tex_node = nodes.new(node_type)
        tex_node.name = f"{tex.name}_node"
        
        # Set texture properties
        if tex.type == 'IMAGE' and hasattr(tex_node, 'image') and hasattr(tex, 'image'):
            tex_node.image = tex.image
        elif hasattr(tex_node, 'texture'):
            tex_node.texture = tex
        
        # Position nodes
        output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if not output:
            output = nodes.new('ShaderNodeOutputMaterial')
        
        # Position nodes
        output.location = (400, 0)
        principled.location = (200, 0)
        tex_node.location = (0, 0)
        
        # Connect nodes based on slot
        slot = '{texture_slot}'.upper()
        if slot in ['BASE COLOR', 'BASE_COLOR', 'COLOR']:
            links.new(tex_node.outputs['Color'], principled.inputs['Base Color'])
        elif slot in ['METALLIC', 'METALNESS']:
            links.new(tex_node.outputs['Color'], principled.inputs['Metallic'])
        elif slot in ['ROUGHNESS']:
            links.new(tex_node.outputs['Color'], principled.inputs['Roughness'])
        elif slot in ['NORMAL']:
            # Add normal map node
            normal_map = nodes.new('ShaderNodeNormalMap')
            normal_map.location = (200, -200)
            links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
            links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])
        else:
            # Try to connect to any matching input
            for input in principled.inputs:
                if slot in input.name.upper():
                    links.new(tex_node.outputs[0], input)
                    break
        
        # Connect to output if not already connected
        if not any(link.to_node == output for link in principled.outputs[0].links):
            links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        return {{
            "status": "SUCCESS",
            "material": mat.name,
            "texture": tex.name,
            "slot": '{texture_slot}',
            "node": tex_node.name
        }}
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = assign_texture()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to assign texture to material: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("bake_texture", log_args=True)
async def bake_texture(
    bake_type: str = "DIFFUSE",
    width: int = 1024,
    height: int = 1024,
    margin: int = 16,
    use_selected_to_active: bool = False,
    cage_extrusion: float = 0.1,
    filepath: str = ""
) -> Dict[str, Any]:
    """Bake textures for selected objects.
    
    Args:
        bake_type: Type of baking ('DIFFUSE', 'NORMAL', 'ROUGHNESS', 'METALLIC', 'EMIT', etc.)
        width: Width of the baked texture (default: 1024)
        height: Height of the baked texture (default: 1024)
        margin: Margin in pixels (default: 16)
        use_selected_to_active: Bake from selected to active (default: False)
        cage_extrusion: Cage extrusion for ray casting (default: 0.1)
        filepath: Where to save the baked texture (default: "")
            
    Returns:
        Dict containing baking status and details
    """
    script = f"""
import os

def bake_texture():
    # Store current render engine
    current_engine = bpy.context.scene.render.engine
    
    try:
        # Set to Cycles for baking
        bpy.context.scene.render.engine = 'CYCLES'
        
        # Set bake settings
        bpy.context.scene.render.bake.margin = {margin}
        bpy.context.scene.render.bake.use_selected_to_active = {str(use_selected_to_active).lower()}
        bpy.context.scene.render.bake.cage_extrusion = {cage_extrusion}
        
        # Set bake type
        bake_type = '{bake_type}'.upper()
        bpy.context.scene.cycles.bake_type = bake_type
        
        # Get selected objects
        selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            return {{"status": "ERROR", "error": "No mesh objects selected"}}
        
        # Create image for baking if not provided
        if not '{filepath}':
            img_name = f"baked_{{bake_type.lower()}}"
            if img_name in bpy.data.images:
                img = bpy.data.images[img_name]
            else:
                img = bpy.data.images.new(
                    img_name,
                    width={width},
                    height={height},
                    alpha=True,
                    float_buffer=False
                )
        else:
            # Ensure directory exists
            os.makedirs(os.path.dirname('{filepath}'), exist_ok=True)
            img = bpy.data.images.new(
                os.path.basename('{filepath}'),
                width={width},
                height={height},
                alpha=True,
                float_buffer=False
            )
        
        # Assign image to all selected objects' materials
        for obj in selected_objects:
            if not obj.material_slots:
                continue
                
            for slot in obj.material_slots:
                if not slot.material:
                    continue
                    
                mat = slot.material
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                
                # Find or create image node
                img_node = None
                for node in nodes:
                    if node.type == 'TEX_IMAGE' and node.image == img:
                        img_node = node
                        break
                
                if not img_node:
                    img_node = nodes.new('ShaderNodeTexImage')
                    img_node.image = img
                
                # Set as active for baking
                nodes.active = img_node
        
        # Perform the bake
        bpy.ops.object.bake(type=bake_type)
        
        # Save the image if filepath is provided
        if '{filepath}':
            img.filepath_raw = '{filepath}'
            img.file_format = 'PNG'
            img.save()
        
        return {{
            "status": "SUCCESS",
            "bake_type": bake_type,
            "image": img.name,
            "filepath": img.filepath_raw if '{filepath}' else '',
            "dimensions": (img.size[0], img.size[1])
        }}
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}
    finally:
        # Restore original render engine
        bpy.context.scene.render.engine = current_engine

try:
    result = bake_texture()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""
    
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to bake texture: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

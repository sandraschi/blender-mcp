"""Compositor operations handler for Blender MCP."""

from enum import Enum
from typing import Any, Dict, Tuple, Union

from loguru import logger

from ..compat import *
from ..decorators import blender_operation
from ..utils.blender_executor import get_blender_executor

_executor = get_blender_executor()


class CompositorNodeType(str, Enum):
    """Common compositor node types."""

    BLUR = "CompositorNodeBlur"
    RGB = "CompositorNodeRGB"
    MIX = "CompositorNodeMixRGB"
    ALPHA_OVER = "CompositorNodeAlphaOver"
    GLOW = "CompositorNodeGlare"
    COLOR_BALANCE = "CompositorNodeColorBalance"
    LENS_DIST = "CompositorNodeLensdist"
    VECTOR_BLUR = "CompositorNodeVecBlur"
    DEFOCUS = "CompositorNodeBokehBlur"
    CORNER_PIN = "CompositorNodeCornerPin"
    CRYPTOMATTE = "CompositorNodeCryptomatteV2"
    DENOISE = "CompositorNodeDenoise"
    DIFF_MATTE = "CompositorNodeDiffMatte"
    DILATE_ERODE = "CompositorNodeDilateErode"
    DIRECTIONAL_BLUR = "CompositorNodeDBlur"
    DISPLACE = "CompositorNodeDisplace"
    DISTORT = "CompositorNodeMapUV"
    ELLIPSE_MASK = "CompositorNodeEllipseMask"
    FILTER = "CompositorNodeFilter"
    FLIP = "CompositorNodeFlip"
    GAMMA = "CompositorNodeGamma"
    HUE_SAT = "CompositorNodeHueSat"
    ID_MASK = "CompositorNodeIDMask"
    INVERT = "CompositorNodeInvert"
    KEYING = "CompositorNodeKeying"
    KEYING_SCREEN = "CompositorNodeKeyingScreen"
    LENSDIST = "CompositorNodeLensdist"
    LEVELS = "CompositorNodeLevels"
    LUMA_MATTE = "CompositorNodeLumaMatte"
    MAP_RANGE = "CompositorNodeMapRange"
    MAP_VALUE = "CompositorNodeMapValue"
    MASK = "CompositorNodeMask"
    MATH = "CompositorNodeMath"
    MOVIECLIP = "CompositorNodeMovieClip"
    MOVIEDISTORTION = "CompositorNodeMovieDistortion"
    NORMAL = "CompositorNodeNormal"
    NORMALIZE = "CompositorNodeNormalize"
    PIXELATE = "CompositorNodePixelate"
    PREMULKEY = "CompositorNodePremulKey"
    RGBTOBW = "CompositorNodeRGBToBW"
    ROTATE = "CompositorNodeRotate"
    SCALE = "CompositorNodeScale"
    SEPARATE_XYZ = "CompositorNodeSeparateXYZ"
    SEPCOMBINE_XYZ = "CompositorNodeCombineXYZ"
    SEPARATE_COLOR = "CompositorNodeSepRGBA"
    SEPCOMBINE_COLOR = "CompositorNodeCombRGBA"
    SEPARATE_HSVA = "CompositorNodeSepHSVA"
    SEPCOMBINE_HSVA = "CompositorNodeCombHSVA"
    SEPARATE_HSI = "CompositorNodeSepHSI"
    SEPCOMBINE_HSI = "CompositorNodeCombHSI"
    SEPARATE_HSL = "CompositorNodeSepHSL"
    SEPCOMBINE_HSL = "CompositorNodeCombHSL"
    SEPARATE_YCCA = "CompositorNodeSepYCCA"
    SEPCOMBINE_YCCA = "CompositorNodeCombYCCA"
    SEPARATE_YUVA = "CompositorNodeSepYUVA"
    SEPCOMBINE_YUVA = "CompositorNodeCombYUVA"
    SET_ALPHA = "CompositorNodeSetAlpha"
    SPLITVIEWER = "CompositorNodeSplitViewer"
    STABILIZE2D = "CompositorNodeStabilize"
    SUNBEAMS = "CompositorNodeSunBeams"
    TEXTURE = "CompositorNodeTexture"
    TONEMAP = "CompositorNodeTonemap"
    TRACKPOS = "CompositorNodeTrackPos"
    TRANSFORM = "CompositorNodeTransform"
    TRANSLATE = "CompositorNodeTranslate"
    VALTORGB = "CompositorNodeValToRGB"
    VECBLUR = "CompositorNodeVecBlur"
    VECTORMATH = "CompositorNodeVectorBlur"
    VIEW_LEVELS = "CompositorNodeViewLevels"
    ZCOMBINE = "CompositorNodeZcombine"
    ZCOMBINE_VEC = "CompositorNodeZcombineVector"
    ZCOMBINE_NORMAL = "CompositorNodeZcombineNormal"
    ZCOMBINE_ALPHA = "CompositorNodeZcombineAlpha"
    ZCOMBINE_DIFF = "CompositorNodeZcombineDiff"
    ZCOMBINE_PREMUL = "CompositorNodeZcombinePremul"
    ZCOMBINE_ALPHA_PREMUL = "CompositorNodeZcombineAlphaPremul"
    ZCOMBINE_NORMAL_PREMUL = "CompositorNodeZcombineNormalPremul"
    ZCOMBINE_DIFF_PREMUL = "CompositorNodeZcombineDiffPremul"
    ZCOMBINE_ALPHA_DIFF_PREMUL = "CompositorNodeZcombineAlphaDiffPremul"
    ZCOMBINE_NORMAL_DIFF_PREMUL = "CompositorNodeZcombineNormalDiffPremul"


@blender_operation("enable_compositor", log_args=True)
async def enable_compositor(
    use_nodes: bool = True, use_sequencer: bool = False, **kwargs: Any
) -> Dict[str, Any]:
    """Enable the compositor and configure basic settings."""
    script = f"""

def enable_compositor():
    scene = bpy.context.scene
    scene.use_nodes = {str(use_nodes).lower()}
    scene.render.use_compositing = {str(use_nodes).lower()}
    scene.render.use_sequencer = {str(use_sequencer).lower()}
    
    # Clear existing nodes if needed
    if scene.node_tree:
        for node in scene.node_tree.nodes:
            scene.node_tree.nodes.remove(node)
    
    # Create input and output nodes
    if {str(use_nodes).lower()} and not scene.node_tree:
        scene.node_tree = bpy.data.node_groups.new('CompositorNodeTree', 'CompositorNodeTree')
        
        # Create input node
        input_node = scene.node_tree.nodes.new('CompositorNodeRLayers')
        input_node.location = (-200, 0)
        
        # Create output node
        output_node = scene.node_tree.nodes.new('CompositorNodeComposite')
        output_node.location = (200, 0)
        
        # Link them
        scene.node_tree.links.new(
            input_node.outputs[0],
            output_node.inputs[0]
        )
    
    return {{
        'status': 'SUCCESS',
        'use_nodes': scene.use_nodes,
        'use_sequencer': scene.render.use_sequencer
    }}

try:
    result = enable_compositor()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to enable compositor: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("add_compositor_node", log_args=True)
async def add_compositor_node(
    node_type: Union[CompositorNodeType, str],
    node_name: str = None,
    location: Tuple[float, float] = (0.0, 0.0),
    **kwargs: Any,
) -> Dict[str, Any]:
    """Add a node to the compositor."""
    script = f"""

def add_node():
    scene = bpy.context.scene
    if not scene.node_tree:
        return {{'status': 'ERROR', 'error': 'Compositor not enabled'}}
    
    # Create the node
    node = scene.node_tree.nodes.new('{node_type}')
    if '{node_name}':
        node.name = '{node_name}'
    node.location = {list(location)}
    
    # Set node properties from kwargs
    for key, value in {kwargs}.items():
        if hasattr(node, key):
            try:
                setattr(node, key, value)
            except Exception as e:
                print(f"Could not set {{key}}: {{str(e)}}")
    
    return {{
        'status': 'SUCCESS',
        'node_name': node.name,
        'node_type': node.type,
        'location': node.location[:]  # Convert to list for JSON serialization
    }}

try:
    result = add_node()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to add compositor node: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("connect_compositor_nodes", log_args=True)
async def connect_compositor_nodes(
    from_node: str, from_socket: str, to_node: str, to_socket: str, **kwargs: Any
) -> Dict[str, Any]:
    """Connect two nodes in the compositor."""
    script = f"""

def connect_nodes():
    scene = bpy.context.scene
    if not scene.node_tree:
        return {{'status': 'ERROR', 'error': 'Compositor not enabled'}}
    
    # Get the nodes
    node_from = scene.node_tree.nodes.get('{from_node}')
    node_to = scene.node_tree.nodes.get('{to_node}')
    
    if not node_from or not node_to:
        return {{'status': 'ERROR', 'error': 'One or both nodes not found'}}
    
    # Get the sockets
    socket_from = None
    socket_to = None
    
    # Check outputs
    for output in node_from.outputs:
        if output.name == '{from_socket}':
            socket_from = output
            break
    
    # Check inputs
    for input in node_to.inputs:
        if input.name == '{to_socket}':
            socket_to = input
            break
    
    if not socket_from or not socket_to:
        return {{'status': 'ERROR', 'error': 'One or both sockets not found'}}
    
    # Connect the nodes
    scene.node_tree.links.new(socket_from, socket_to)
    
    return {{
        'status': 'SUCCESS',
        'connection': {{
            'from': f"{{node_from.name}}.{{socket_from.name}}",
            'to': f"{{node_to.name}}.{{socket_to.name}}"
        }}
    }}

try:
    result = connect_nodes()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to connect compositor nodes: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("create_glow_effect", log_args=True)
async def create_glow_effect(
    threshold: float = 0.8, size: int = 10, quality: int = 2, **kwargs: Any
) -> Dict[str, Any]:
    """Create a glow effect in the compositor."""
    script = f"""

def create_glow():
    scene = bpy.context.scene
    if not scene.node_tree:
        return {{'status': 'ERROR', 'error': 'Compositor not enabled'}}
    
    # Get or create input and output nodes
    rl_node = next((n for n in scene.node_tree.nodes if n.type == 'R_LAYERS'), None)
    if not rl_node:
        rl_node = scene.node_tree.nodes.new('CompositorNodeRLayers')
        rl_node.location = (-400, 0)
    
    output_node = next((n for n in scene.node_tree.nodes if n.type == 'COMPOSITE'), None)
    if not output_node:
        output_node = scene.node_tree.nodes.new('CompositorNodeComposite')
        output_node.location = (400, 0)
    
    # Create glow nodes
    rgb_node = scene.node_tree.nodes.new('CompositorNodeRGB')
    rgb_node.location = (0, 0)
    
    color_mix = scene.node_tree.nodes.new('CompositorNodeMixRGB')
    color_mix.location = (200, 0)
    color_mix.blend_type = 'ADD'
    
    glare_node = scene.node_tree.nodes.new('CompositorNodeGlare')
    glare_node.location = (0, -200)
    glare_node.glare_type = 'FOG_GLOW'
    glare_node.quality = '{quality}'
    glare_node.threshold = {threshold}
    glare_node.size = {size}
    
    # Link nodes
    links = scene.node_tree.links
    
    # Connect render layer to glare and mix
    links.new(rl_node.outputs[0], glare_node.inputs[0])
    links.new(rl_node.outputs[0], color_mix.inputs[1])
    
    # Connect glare to mix
    links.new(glare_node.outputs[0], color_mix.inputs[2])
    
    # Connect mix to output
    links.new(color_mix.outputs[0], output_node.inputs[0])
    
    return {{
        'status': 'SUCCESS',
        'nodes_created': [
            rgb_node.name,
            color_mix.name,
            glare_node.name
        ]
    }}

try:
    result = create_glow()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create glow effect: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

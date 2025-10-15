"""Shader and material operations handler for Blender MCP.

This module provides functionality for creating and manipulating shader nodes, connecting them,
and managing materials in Blender through the MCP interface.
"""

from __future__ import annotations

from ..compat import *
from enum import Enum
from typing import Any, Dict, Literal, Optional, Tuple, Union, TypeVar

from loguru import logger
from pydantic import BaseModel

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

# Type variable for generic type hints
T = TypeVar("T")

# Initialize the Blender executor
_executor = get_blender_executor()


class ShaderOperationResult(BaseModel):
    """Standard response model for shader operations."""

    status: Literal["SUCCESS", "ERROR"]
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    @classmethod
    def success(cls, message: str = None, **data: Any) -> "ShaderOperationResult":
        """Create a success response."""
        return cls(
            status="SUCCESS", message=message or "Operation completed successfully", data=data or {}
        )

    @classmethod
    def error(cls, message: str, error: Exception = None) -> "ShaderOperationResult":
        """Create an error response."""
        return cls(
            status="ERROR",
            message=message,
            error=str(error) if error else message,
            data={"error_type": error.__class__.__name__} if error else {},
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.dict().items() if v is not None}


class ShaderType(str, Enum):
    """Supported shader types in Blender."""

    PRINCIPLED_BSDF = "BSDF_PRINCIPLED"
    DIFFUSE = "BSDF_DIFFUSE"
    GLOSSY = "BSDF_GLOSSY"
    GLASS = "BSDF_GLASS"
    TRANSLUCENT = "BSDF_TRANSLUCENT"
    EMISSION = "EMISSION"
    MIX = "MIX_SHADER"
    ADD = "ADD_SHADER"


class NodeLocation(BaseModel):
    """2D location for node placement in the shader editor."""

    x: float = 0.0
    y: float = 0.0

    def to_tuple(self) -> Tuple[float, float]:
        """Convert to Blender-compatible tuple."""
        return (self.x, self.y)


@blender_operation("create_shader_node", log_args=True, log_result=True)
async def create_shader_node(
    material_name: str,
    node_type: Union[ShaderType, str],
    node_name: Optional[str] = None,
    location: Union[NodeLocation, Tuple[float, float]] = (0.0, 0.0),
) -> ShaderOperationResult:
    """Create a shader node in a material.

    Args:
        material_name: Name of the material to add the node to
        node_type: Type of shader node to create (from ShaderType enum or string)
        node_name: Optional name for the new node
        location: X, Y coordinates for node placement in the shader editor

    Returns:
        ShaderOperationResult with status and node information
    """
    # Convert location to NodeLocation if it's a tuple
    if isinstance(location, tuple):
        location = NodeLocation(x=location[0], y=location[1])

    # Convert ShaderType enum to string if needed
    node_type_str = node_type.value if isinstance(node_type, ShaderType) else str(node_type)

    script = f"""
import json

def create_shader_node():
    # Input validation
    material = bpy.data.materials.get('{material_name}')
    if not material:
        return {{
            'status': 'ERROR', 
            'error': 'Material not found',
            'material_name': '{material_name}'
        }}
    
    # Enable use nodes if not already
    material.use_nodes = True
    nodes = material.node_tree.nodes
    
    try:
        # Create the node
        node = nodes.new(type='{node_type_str}')
        if '{node_name}':
            node.name = '{node_name}'
        
        # Set node location
        node.location = {[location.x, location.y]}
        
        # Log node creation
        print(f"🔹 Created node: {{node.name}} ({{node.type}})")
        
        # Set node properties from kwargs
        properties = {json.dumps(properties) if properties else "{}"}
        properties_set = {{}}
        
        for key, value in properties.items():
            if hasattr(node, key):
                try:
                    setattr(node, key, value)
                    properties_set[key] = value
                except Exception as e:
                    print(f"⚠️ Could not set {{key}}: {{str(e)}}")
        
        # Update the material
        material.update_tag()
        
        return {{
            'status': 'SUCCESS',
            'node': {{
                'name': node.name,
                'type': node.type,
                'location': list(node.location),
                'properties_set': list(properties_set.keys())
            }},
            'material': material.name
        }}
        
    except Exception as e:
        return {{
            'status': 'ERROR',
            'error': str(e),
            'node_type': '{node_type_str}',
            'material': material.name
        }}

# Execute and handle errors
try:
    result = create_shader_node()
except Exception as e:
    import traceback
    result = {{
        'status': 'ERROR',
        'error': str(e),
        'traceback': traceback.format_exc(),
        'node_type': '{node_type_str}'
    }}

print(json.dumps(result))
"""
    try:
        logger.debug(
            f"Creating shader node of type '{node_type_str}' in material '{material_name}'"
        )
        logger.trace(f"Node properties: {properties}")

        # Execute the script in Blender
        output = await _executor.execute_script(script)
        result = ShaderOperationResult.parse_raw(output)

        if result.status == "SUCCESS":
            logger.success(
                f"✅ Created shader node: {result.data.get('node', {}).get('name')} "
                f"({result.data.get('node', {}).get('type')}) in material '{material_name}'"
            )
        else:
            logger.error(
                f"❌ Failed to create shader node: {result.error}",
                material=material_name,
                node_type=node_type_str,
                error=result.error,
            )

        return result

    except Exception as e:
        error_msg = f"Unexpected error creating shader node: {str(e)}"
        logger.opt(exception=e).error(error_msg, material=material_name, node_type=node_type_str)
        return ShaderOperationResult.error(error_msg, e)


class NodeConnection(BaseModel):
    """Represents a connection between two shader nodes."""

    from_node: str
    from_socket: str
    to_node: str
    to_socket: str

    def __str__(self) -> str:
        return f"{self.from_node}.{self.from_socket} → {self.to_node}.{self.to_socket}"


@blender_operation("connect_shader_nodes", log_args=True, log_result=True)
async def connect_shader_nodes(
    material_name: str, from_node: str, from_socket: str, to_node: str, to_socket: str
) -> ShaderOperationResult:
    """Connect two shader nodes in a material.

    Args:
        material_name: Name of the material containing the nodes
        from_node: Name of the source node
        from_socket: Name of the output socket on the source node
        to_node: Name of the target node
        to_socket: Name of the input socket on the target node

    Returns:
        ShaderOperationResult with status and connection details
    """
    connection = NodeConnection(
        from_node=from_node, from_socket=from_socket, to_node=to_node, to_socket=to_socket
    )

    script = f"""
import json

def connect_nodes():
    # Input validation
    material = bpy.data.materials.get('{material_name}')
    if not material:
        return {{
            'status': 'ERROR',
            'error': 'Material not found',
            'material': '{material_name}'
        }}
    
    if not material.use_nodes:
        return {{
            'status': 'ERROR',
            'error': 'Material does not use nodes',
            'material': material.name
        }}
    
    node_tree = material.node_tree
    nodes = node_tree.nodes
    
    # Get the nodes
    node_from = nodes.get('{from_node}')
    node_to = nodes.get('{to_node}')
    
    if not node_from or not node_to:
        return {{
            'status': 'ERROR',
            'error': 'One or both nodes not found',
            'from_node': '{from_node}',
            'to_node': '{to_node}',
            'nodes_found': [n.name for n in nodes if n.name in ('{from_node}', '{to_node}')]
        }}
    
    # Get the output socket from source node
    socket_from = None
    for output in node_from.outputs:
        if output.name == '{from_socket}':
            socket_from = output
            break
    
    # Get the input socket from target node
    socket_to = None
    for input_socket in node_to.inputs:
        if input_socket.name == '{to_socket}':
            socket_to = input_socket
            break
    
    if not socket_from:
        return {{
            'status': 'ERROR',
            'error': f"Output socket '{{from_socket}}' not found on node '{{from_node}}'",
            'available_outputs': [s.name for s in node_from.outputs],
            'node_type': node_from.type
        }}
    
    if not socket_to:
        return {{
            'status': 'ERROR',
            'error': f"Input socket '{{to_socket}}' not found on node '{{to_node}}'",
            'available_inputs': [s.name for s in node_to.inputs],
            'node_type': node_to.type
        }}
    
    try:
        # Create the connection
        link = node_tree.links.new(socket_from, socket_to)
        
        # Update the material
        material.update_tag()
        
        return {{
            'status': 'SUCCESS',
            'connection': {{
                'from': f"{{node_from.name}}.{{socket_from.name}}",
                'to': f"{{node_to.name}}.{{socket_to.name}}",
                'from_type': node_from.type,
                'to_type': node_to.type
            }},
            'material': material.name
        }}
        
    except Exception as e:
        return {{
            'status': 'ERROR',
            'error': str(e),
            'connection': str({{
                'from': f"{{node_from.name}}.{{socket_from.name}}",
                'to': f"{{node_to.name}}.{{socket_to.name}}"
            }})
        }}

# Execute and handle errors
try:
    result = connect_nodes()
except Exception as e:
    import traceback
    result = {{
        'status': 'ERROR',
        'error': str(e),
        'traceback': traceback.format_exc(),
        'connection': {{
            'from': f"{{from_node}}.{{from_socket}}",
            'to': f"{{to_node}}.{{to_socket}}"
        }}
    }}

print(json.dumps(result))
"""
    try:
        logger.debug(f"Connecting shader nodes: {connection}")

        # Execute the script in Blender
        output = await _executor.execute_script(script)
        result = ShaderOperationResult.parse_raw(output)

        if result.status == "SUCCESS":
            logger.success(
                f"🔌 Connected shader nodes: {result.data.get('connection', {}).get('from')} → "
                f"{result.data.get('connection', {}).get('to')}"
            )
        else:
            logger.error(
                f"🔌 Failed to connect shader nodes: {result.error}",
                material=material_name,
                connection=str(connection),
                error=result.error,
            )

        return result

    except Exception as e:
        error_msg = f"Unexpected error connecting shader nodes: {str(e)}"
        logger.opt(exception=e).error(error_msg, material=material_name, connection=str(connection))
        return ShaderOperationResult.error(error_msg, e)


class MaterialProperties(BaseModel):
    """Properties for creating a new material."""

    name: str
    shader_type: Union[ShaderType, str] = ShaderType.PRINCIPLED_BSDF
    use_nodes: bool = True
    clear_nodes: bool = True
    make_node_tree: bool = True
    is_grease_pencil: bool = False

    class Config:
        json_encoders = {ShaderType: lambda v: v.value}


@blender_operation("create_shader_material", log_args=True, log_result=True)
async def create_shader_material(
    name: str,
    shader_type: Union[ShaderType, str] = ShaderType.PRINCIPLED_BSDF,
    clear_nodes: bool = True,
    is_grease_pencil: bool = False,
) -> ShaderOperationResult:
    """Create a new material with a shader node setup.

    Args:
        name: Name of the material to create
        shader_type: Type of shader node to create (from ShaderType enum or string)
        clear_nodes: Whether to clear existing nodes in the material
        is_grease_pencil: Whether this is a Grease Pencil material

    Returns:
        ShaderOperationResult with status and material information
    """
    # Convert ShaderType enum to string if needed
    shader_type_str = shader_type.value if isinstance(shader_type, ShaderType) else str(shader_type)

    script = f"""
import json

def create_material():
    # Input validation
    if not isinstance('{name}', str) or not '{name}':
        return {{
            'status': 'ERROR',
            'error': 'Material name must be a non-empty string',
            'name': '{name}'
        }}
    
    # Create or get existing material
    material = bpy.data.materials.get('{name}')
    material_created = not bool(material)
    
    if material_created:
        material = bpy.data.materials.new(name='{name}')
        print(f"✨ Created new material: {{material.name}}")
    else:
        print(f"ℹ️ Using existing material: {{material.name}}")
    
    # Configure material settings
    material.use_nodes = True
    material.is_grease_pencil = {str(is_grease_pencil).lower()}
    
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Clear existing nodes if requested
    if {str(clear_nodes).lower()} and nodes:
        print(f"🧹 Cleared {{len(nodes)}} existing nodes")
        nodes.clear()
    
    # Create output node if it doesn't exist
    output_node = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if not output_node:
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (400, 0)
        print(f"➕ Created output node: {{output_node.name}}")
    
    # Create shader node
    shader_node = None
    try:
        shader_node = nodes.new(type='{shader_type_str}')
        shader_node.location = (0, 0)
        print(f"🎨 Created shader node: {{shader_node.name}} ({{shader_node.type}})")
        
        # Set shader properties
        properties = {json.dumps(shader_properties) if shader_properties else "{}"}
        properties_set = {{}}
        
        for key, value in properties.items():
            if hasattr(shader_node, key):
                try:
                    setattr(shader_node, key, value)
                    properties_set[key] = value
                    print(f"   • Set {{key}} = {{value}}")
                except Exception as e:
                    print(f"⚠️ Could not set {{key}}: {{str(e)}}")
        
        # Connect shader to output if possible
        if shader_node.outputs:
            # Try to find a suitable output socket
            output_socket = None
            for output in shader_node.outputs:
                if output.type == 'SHADER':
                    output_socket = output
                    break
            
            if output_socket and output_node.inputs:
                # Try to find a suitable input socket on the output node
                input_socket = None
                for input_sock in output_node.inputs:
                    if input_sock.type == 'SHADER':
                        input_socket = input_sock
                        break
                
                if input_socket:
                    links.new(output_socket, input_socket)
                    print(f"🔌 Connected {{shader_node.name}} → {{output_node.name}}")
        
        # Update the material
        material.update_tag()
        
        return {{
            'status': 'SUCCESS',
            'material': {{
                'name': material.name,
                'created': material_created,
                'node_count': len(nodes),
                'shader_node': {{
                    'name': shader_node.name,
                    'type': shader_node.type,
                    'properties_set': list(properties_set.keys())
                }}
            }}
        }}
        
    except Exception as e:
        error_info = {{
            'status': 'ERROR',
            'error': str(e),
            'material': material.name if material else None,
            'shader_type': '{shader_type_str}'
        }}
        
        if shader_node:
            error_info['shader_node'] = {{
                'name': shader_node.name,
                'type': shader_node.type
            }}
            
        return error_info

# Execute and handle errors
try:
    result = create_material()
except Exception as e:
    import traceback
    result = {{
        'status': 'ERROR',
        'error': str(e),
        'traceback': traceback.format_exc(),
        'material_name': '{name}',
        'shader_type': '{shader_type_str}'
    }}

print(json.dumps(result))
"""
    try:
        logger.debug(f"Creating shader material '{name}' with type '{shader_type_str}'")

        # Execute the script in Blender
        output = await _executor.execute_script(script)
        result = ShaderOperationResult.parse_raw(output)

        if result.status == "SUCCESS":
            material_data = result.data.get("material", {})
            logger.success(
                f"✅ Created shader material: {material_data.get('name', 'unknown')} "
                f"({material_data.get('shader_node', {}).get('type', 'unknown')})"
            )
        else:
            logger.error(
                f"❌ Failed to create shader material: {result.error}",
                material=name,
                shader_type=shader_type_str,
                error=result.error,
            )

        return result

    except Exception as e:
        error_msg = f"Unexpected error creating shader material: {str(e)}"
        logger.opt(exception=e).error(error_msg, material=name, shader_type=shader_type_str)
        return ShaderOperationResult.error(error_msg, e)

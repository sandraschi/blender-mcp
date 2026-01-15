"""Modifier operations handler for Blender MCP."""

from enum import Enum
from typing import Any, Dict, Optional, Union

from loguru import logger

from ..decorators import blender_operation
from ..utils.blender_executor import get_blender_executor

_executor = get_blender_executor()


from ..compat import *


class ModifierType(str, Enum):
    """Types of modifiers."""

    ARRAY = "ARRAY"
    BEVEL = "BEVEL"
    BOOLEAN = "BOOLEAN"
    BUILD = "BUILD"
    DECIMATE = "DECIMATE"
    EDGE_SPLIT = "EDGE_SPLIT"
    MASK = "MASK"
    MIRROR = "MIRROR"
    MULTIRES = "MULTIRES"
    REMESH = "REMESH"
    SCREW = "SCREW"
    SKIN = "SKIN"
    SOLIDIFY = "SOLIDIFY"
    SUBSURF = "SUBSURF"
    TRIANGULATE = "TRIANGULATE"
    WIREFRAME = "WIREFRAME"
    ARMATURE = "ARMATURE"
    CAST = "CAST"
    CURVE = "CURVE"
    DISPLACE = "DISPLACE"
    HOOK = "HOOK"
    LAPLACIANDEFORM = "LAPLACIANDEFORM"
    LAPLACIANSMOOTH = "LAPLACIANSMOOTH"
    LATTICE = "LATTICE"
    MESH_DEFORM = "MESH_DEFORM"
    SHRINKWRAP = "SHRINKWRAP"
    SIMPLE_DEFORM = "SIMPLE_DEFORM"
    SMOOTH = "SMOOTH"
    WARP = "WARP"
    WAVE = "WAVE"
    CLOTH = "CLOTH"
    COLLISION = "COLLISION"
    DYNAMIC_PAINT = "DYNAMIC_PAINT"
    EXPLODE = "EXPLODE"
    FLUID = "FLUID"
    OCEAN = "OCEAN"
    PARTICLE_INSTANCE = "PARTICLE_INSTANCE"
    PARTICLE_SYSTEM = "PARTICLE_SYSTEM"
    SOFT_BODY = "SOFT_BODY"
    SURFACE = "SURFACE"


@blender_operation("add_modifier", log_args=True)
async def add_modifier(
    object_name: str,
    modifier_type: Union[ModifierType, str],
    name: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Add a modifier to an object.

    Args:
        object_name: Name of the object to add the modifier to
        modifier_type: Type of modifier to add
        name: Name for the new modifier (optional)
        **kwargs: Modifier properties to set

    Returns:
        Dict containing modifier creation status and details
    """
    if not name:
        name = f"{modifier_type.lower()}_mod"

    # Convert kwargs to a string representation of a dictionary
    # that can be used in the Blender script
    props_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())

    script = f"""

def add_modifier():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{"status": "ERROR", "error": "Object not found"}}
    
    try:
        # Check if modifier with this name already exists
        if '{name}' in obj.modifiers:
            return {{"status": "ERROR", "error": f"Modifier '{{name}}' already exists"}}
        
        # Add the modifier
        mod = obj.modifiers.new('{name}', '{modifier_type}')
        if not mod:
            return {{"status": "ERROR", "error": f"Failed to create modifier of type '{{modifier_type}}'"}}
        
        # Set properties if any
        {f"for k, v in {{{props_str}}}.items(): setattr(mod, k, v)" if props_str else ""}
        
        return {{
            "status": "SUCCESS",
            "modifier": mod.name,
            "type": mod.type,
            "object": obj.name
        }}
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = add_modifier()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to add modifier: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("remove_modifier", log_args=True)
async def remove_modifier(object_name: str, modifier_name: str, **kwargs: Any) -> Dict[str, Any]:
    """Remove a modifier from an object.

    Args:
        object_name: Name of the object
        modifier_name: Name of the modifier to remove

    Returns:
        Dict containing removal status
    """
    script = f"""

def remove_modifier():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{"status": "ERROR", "error": "Object not found"}}
    
    if '{modifier_name}' not in obj.modifiers:
        return {{"status": "ERROR", "error": f"Modifier '{{modifier_name}}' not found"}}
    
    try:
        # Store modifier info before removal
        mod = obj.modifiers['{modifier_name}']
        mod_info = {{
            "name": mod.name,
            "type": mod.type,
            "show_viewport": getattr(mod, 'show_viewport', True),
            "show_render": getattr(mod, 'show_render', True),
            "show_in_editmode": getattr(mod, 'show_in_editmode', False)
        }}
        
        # Remove the modifier
        obj.modifiers.remove(mod)
        
        return {{
            "status": "SUCCESS",
            "removed_modifier": mod_info,
            "remaining_modifiers": [m.name for m in obj.modifiers]
        }}
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = remove_modifier()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to remove modifier: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("get_modifiers", log_args=True)
async def get_modifiers(
    object_name: str, modifier_type: Optional[Union[ModifierType, str]] = None, **kwargs: Any
) -> Dict[str, Any]:
    """Get information about modifiers on an object.

    Args:
        object_name: Name of the object
        modifier_type: Optional filter for modifier type

    Returns:
        Dict containing modifier information
    """
    script = f"""

def get_modifiers():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{"status": "ERROR", "error": "Object not found"}}
    
    try:
        modifiers = []
        for mod in obj.modifiers:
            # Skip if type filter is specified and doesn't match
            if '{modifier_type}' and mod.type != '{modifier_type}':
                continue
                
            # Get common properties
            mod_info = {{
                "name": mod.name,
                "type": mod.type,
                "show_viewport": getattr(mod, 'show_viewport', True),
                "show_render": getattr(mod, 'show_render', True),
                "show_in_editmode": getattr(mod, 'show_in_editmode', False),
                "show_on_cage": getattr(mod, 'show_on_cage', False),
                "show_expanded": getattr(mod, 'show_expanded', True)
            }}
            
            # Add type-specific properties
            if hasattr(mod, 'levels'):
                mod_info['levels'] = mod.levels
            if hasattr(mod, 'render_levels'):
                mod_info['render_levels'] = mod.render_levels
            if hasattr(mod, 'strength'):
                mod_info['strength'] = mod.strength
                
            modifiers.append(mod_info)
        
        return {{
            "status": "SUCCESS",
            "object": obj.name,
            "modifiers": modifiers,
            "count": len(modifiers)
        }}
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = get_modifiers()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to get modifiers: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("apply_modifier", log_args=True)
async def apply_modifier(object_name: str, modifier_name: str, **kwargs: Any) -> Dict[str, Any]:
    """Apply a modifier to the object's geometry.

    Args:
        object_name: Name of the object
        modifier_name: Name of the modifier to apply

    Returns:
        Dict containing apply status
    """
    script = f"""

def apply_modifier():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{"status": "ERROR", "error": "Object not found"}}
    
    if '{modifier_name}' not in obj.modifiers:
        return {{"status": "ERROR", "error": f"Modifier '{{modifier_name}}' not found"}}
    
    try:
        # Store modifier info before applying
        mod = obj.modifiers['{modifier_name}']
        mod_info = {{
            "name": mod.name,
            "type": mod.type
        }}
        
        # Make the object active
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Apply the modifier
        bpy.ops.object.modifier_apply(modifier=mod.name)
        
        return {{
            "status": "SUCCESS",
            "applied_modifier": mod_info,
            "remaining_modifiers": [m.name for m in obj.modifiers]
        }}
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = apply_modifier()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to apply modifier: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

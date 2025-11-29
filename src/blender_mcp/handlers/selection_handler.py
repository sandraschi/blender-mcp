"""Selection operations handler for Blender MCP."""

from typing import List, Dict, Any, Union
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()


from ..compat import *


class SelectMode(str, Enum):
    """Selection modes."""

    REPLACE = "REPLACE"
    ADD = "ADD"
    SUBTRACT = "SUB"
    INVERT = "INVERT"
    NONE = "NONE"
    AND = "AND"
    XOR = "XOR"


class SelectableType(str, Enum):
    """Types of selectable elements."""

    OBJECT = "OBJECT"
    VERTEX = "VERT"
    EDGE = "EDGE"
    FACE = "FACE"
    CURVE = "CURVE"
    SURFACE = "SURFACE"
    LATTICE = "LATTICE"
    METABALL = "META"
    TEXT = "TEXT"
    ARMATURE = "ARMATURE"
    LATTICE_POINT = "LATTICE_POINT"
    CONTROL_POINT = "CONTROL_POINT"
    SEGMENT = "SEGMENT"
    GPENCIL = "GPENCIL"


@blender_operation("select_objects", log_args=True)
async def select_objects(
    object_names: List[str], mode: Union[SelectMode, str] = SelectMode.REPLACE, **kwargs: Any
) -> Dict[str, Any]:
    """Select objects in the scene.

    Args:
        object_names: List of object names to select
        mode: Selection mode (REPLACE, ADD, SUBTRACT, etc.)
        **kwargs: Additional options
            - active_object: Set as active object after selection
            - deselect_others: Deselect all other objects first (default: True for REPLACE mode)

    Returns:
        Dict containing selection status and details
    """
    active_object = kwargs.get("active_object")
    deselect_others = kwargs.get("deselect_others", mode == SelectMode.REPLACE)

    script = f"""

def select_objects():
    # Store current selection state
    prev_selection = [obj.name for obj in bpy.context.selected_objects]
    prev_active = bpy.context.active_object.name if bpy.context.active_object else None
    
    # Deselect all if needed
    if {str(deselect_others).lower()} and '{mode}' == 'REPLACE':
        bpy.ops.object.select_all(action='DESELECT')
    
    # Select objects based on mode
    selected = []
    for name in {object_names}:
        obj = bpy.data.objects.get(name)
        if obj:
            if '{mode}' == 'REPLACE':
                obj.select_set(True)
                selected.append(name)
            elif '{mode}' == 'ADD' and not obj.select_get():
                obj.select_set(True)
                selected.append(name)
            elif '{mode}' == 'SUBTRACT' and obj.select_get():
                obj.select_set(False)
            elif '{mode}' == 'INVERT':
                obj.select_set(not obj.select_get())
                if obj.select_get():
                    selected.append(name)
    
    # Set active object if specified
    if '{active_object}':
        active_obj = bpy.data.objects.get('{active_object}')
        if active_obj:
            bpy.context.view_layer.objects.active = active_obj
    
    return {{
        'selected': selected,
        'previous_selection': prev_selection,
        'previous_active': prev_active,
        'active_object': bpy.context.active_object.name if bpy.context.active_object else None,
        'mode': '{mode}'
    }}

try:
    result = select_objects()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to select objects: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("select_by_type", log_args=True)
async def select_by_type(
    type: Union[SelectableType, str],
    mode: Union[SelectMode, str] = SelectMode.REPLACE,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Select objects by type.

    Args:
        type: Type of objects to select
        mode: Selection mode (REPLACE, ADD, SUBTRACT, etc.)
        **kwargs: Additional options
            - select_children: Also select child objects (default: True)
            - select_hidden: Include hidden objects (default: False)

    Returns:
        Dict containing selection status and details
    """
    select_children = kwargs.get("select_children", True)
    select_hidden = kwargs.get("select_hidden", False)

    script = f"""

def select_by_type():
    # Store current selection state
    prev_selection = [obj.name for obj in bpy.context.selected_objects]
    
    # Get objects of specified type
    objects = []
    for obj in bpy.data.objects:
        if obj.type == '{type}':
            if not select_hidden and obj.hide_viewport:
                continue
            objects.append(obj)
    
    # Select objects based on mode
    selected = []
    if '{mode}' == 'REPLACE':
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.select_set(True)
            selected.append(obj.name)
    elif '{mode}' == 'ADD':
        for obj in objects:
            if not obj.select_get():
                obj.select_set(True)
                selected.append(obj.name)
    elif '{mode}' == 'SUBTRACT':
        for obj in objects:
            if obj.select_get():
                obj.select_set(False)
    elif '{mode}' == 'INVERT':
        for obj in objects:
            obj.select_set(not obj.select_get())
            if obj.select_get():
                selected.append(obj.name)
    
    # Handle child objects if needed
    if {str(select_children).lower()} and '{mode}' != 'SUBTRACT':
        for obj in objects:
            if obj.select_get():
                for child in obj.children_recursive:
                    if not select_hidden and child.hide_viewport:
                        continue
                    child.select_set(True)
                    if child.name not in selected:
                        selected.append(child.name)
    
    return {{
        'selected': selected,
        'previous_selection': prev_selection,
        'type': '{type}',
        'mode': '{mode}'
    }}

try:
    result = select_by_type()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to select by type: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("select_by_material", log_args=True)
async def select_by_material(
    material_name: str, mode: Union[SelectMode, str] = SelectMode.REPLACE, **kwargs: Any
) -> Dict[str, Any]:
    """Select objects using a specific material.

    Args:
        material_name: Name of the material to select by
        mode: Selection mode (REPLACE, ADD, SUBTRACT, etc.)
        **kwargs: Additional options
            - partial_match: Also select objects where material is one of many (default: True)

    Returns:
        Dict containing selection status and details
    """
    partial_match = kwargs.get("partial_match", True)

    script = f"""

def select_by_material():
    # Store current selection state
    prev_selection = [obj.name for obj in bpy.context.selected_objects]
    
    # Find objects using the material
    objects = []
    for obj in bpy.data.objects:
        if hasattr(obj.data, 'materials'):
            if {str(partial_match).lower()}:
                # Check if material is in object's material slots
                for slot in obj.material_slots:
                    if slot.material and slot.material.name == '{material_name}':
                        objects.append(obj)
                        break
            else:
                # Only select if material is the only one
                if len(obj.material_slots) == 1 and obj.material_slots[0].material:
                    if obj.material_slots[0].material.name == '{material_name}':
                        objects.append(obj)
    
    # Select objects based on mode
    selected = []
    if '{mode}' == 'REPLACE':
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.select_set(True)
            selected.append(obj.name)
    elif '{mode}' == 'ADD':
        for obj in objects:
            if not obj.select_get():
                obj.select_set(True)
                selected.append(obj.name)
    elif '{mode}' == 'SUBTRACT':
        for obj in objects:
            if obj.select_get():
                obj.select_set(False)
    elif '{mode}' == 'INVERT':
        for obj in objects:
            obj.select_set(not obj.select_get())
            if obj.select_get():
                selected.append(obj.name)
    
    return {{
        'selected': selected,
        'previous_selection': prev_selection,
        'material': '{material_name}',
        'mode': '{mode}'
    }}

try:
    result = select_by_material()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to select by material: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

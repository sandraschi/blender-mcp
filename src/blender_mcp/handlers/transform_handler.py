"""Transform operations handler for Blender MCP."""

from typing import List, Dict, Any, Union
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()


class TransformSpace(str, Enum):
    """Coordinate spaces for transformations."""

from ..compat import *

    WORLD = "WORLD"
    LOCAL = "LOCAL"
    CURSOR = "CURSOR"
    PARENT = "PARENT"


class TransformType(str, Enum):
    """Types of transformations."""

    TRANSLATE = "TRANSLATE"
    ROTATE = "ROTATE"
    SCALE = "SCALE"


@blender_operation("set_transform", log_args=True)
async def set_transform(
    object_names: Union[str, List[str]],
    transform_type: Union[TransformType, str],
    values: Union[List[float], Dict[str, float]],
    space: Union[TransformSpace, str] = TransformSpace.WORLD,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Set transform values for objects."""
    if isinstance(object_names, str):
        object_names = [object_names]

    relative = kwargs.get("relative", False)
    as_euler = kwargs.get("as_euler", False)

    # Process values based on transform type
    if transform_type == TransformType.TRANSLATE:
        if isinstance(values, dict):
            values = [values.get("x", 0), values.get("y", 0), values.get("z", 0)]
        values_str = f"Vector({values})"
        op = f"obj.location = {values_str} if not {relative} else obj.location + {values_str}"

    script = f"""
from mathutils import Vector, Matrix, Quaternion, Euler

def set_transform():
    results = {{}}
    for name in {object_names}:
        obj = bpy.data.objects.get(name)
        if not obj:
            results[name] = {{"status": "ERROR", "error": "Object not found"}}
            continue
            
        try:
            prev_loc = tuple(obj.location)
            {op}
            bpy.context.view_layer.update()
            results[name] = {{
                "status": "SUCCESS",
                "previous_location": prev_loc,
                "new_location": tuple(obj.location)
            }}
        except Exception as e:
            results[name] = {{"status": "ERROR", "error": str(e)}}
    return results

try:
    result = set_transform()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Transform failed: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("apply_transform", log_args=True)
async def apply_transform(
    object_names: Union[str, List[str]],
    transform_types: Union[str, List[str]] = "ALL",
    **kwargs: Any,
) -> Dict[str, Any]:
    """Apply transform to objects."""
    if isinstance(object_names, str):
        object_names = [object_names]

    if isinstance(transform_types, str):
        transform_types = [transform_types]

    script = f"""

def apply_transform():
    results = {{}}
    for name in {object_names}:
        obj = bpy.data.objects.get(name)
        if not obj:
            results[name] = {{"status": "ERROR", "error": "Object not found"}}
            continue
            
        try:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            
            for t in {transform_types}:
                if t.upper() in ['ALL', 'LOCATION']:
                    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
                if t.upper() in ['ALL', 'ROTATION']:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                if t.upper() in ['ALL', 'SCALE']:
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            
            results[name] = {{"status": "SUCCESS"}}
        except Exception as e:
            results[name] = {{"status": "ERROR", "error": str(e)}}
    return results

try:
    result = apply_transform()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Apply transform failed: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

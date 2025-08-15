"""Particle system operations handler for Blender MCP."""

from typing import Optional, Tuple, Dict, Any, Union, List, Literal
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()

class ParticleType(str, Enum):
    EMITTER = "EMITTER"
    HAIR = "HAIR"
    KEYED = "KEYED"
    FLUID_FLOW = "FLUID_FLOW"

class ParticleEmitFrom(str, Enum):
    VERT = "VERT"
    FACE = "FACE"
    VOLUME = "VOLUME"

@blender_operation("create_particle_system", log_args=True)
async def create_particle_system(
    object_name: str,
    system_name: str = "ParticleSystem",
    particle_type: Union[ParticleType, str] = ParticleType.EMITTER,
    count: int = 1000,
    frame_start: int = 1,
    frame_end: int = 200,
    lifetime: float = 50.0,
    emit_from: Union[ParticleEmitFrom, str] = ParticleEmitFrom.FACE,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a particle system on an object."""
    script = f"""
import bpy

def create_particle_system():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    if obj.particle_systems:
        bpy.ops.object.particle_system_add()
    
    ps = obj.particle_systems[-1]
    ps.name = '{system_name}'
    settings = ps.settings
    
    settings.type = '{particle_type}'
    settings.count = {count}
    settings.frame_start = {frame_start}
    settings.frame_end = {frame_end}
    settings.lifetime = {lifetime}
    settings.particle_size = {kwargs.get('size', 0.1)}
    settings.emit_from = '{emit_from}'
    
    return {{'status': 'SUCCESS', 'system': ps.name}}

try:
    result = create_particle_system()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create particle system: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("bake_particles", log_args=True)
async def bake_particles(
    object_name: str,
    system_name: str = None,
    frame_start: int = 1,
    frame_end: int = 250,
    **kwargs: Any
) -> Dict[str, Any]:
    """Bake particle simulation."""
    script = f"""
import bpy

def bake_particles():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    systems_to_bake = []
    if '{system_name}':
        ps = obj.particle_systems.get('{system_name}')
        if ps:
            systems_to_bake.append(ps)
    else:
        systems_to_bake = list(obj.particle_systems)
    
    if not systems_to_bake:
        return {{'status': 'ERROR', 'error': 'No particle systems found'}}
    
    results = []
    for ps in systems_to_bake:
        obj.particle_systems.active = ps
        bpy.ops.ptcache.free_bake()
        bpy.ops.ptcache.bake(
            bake=True,
            frame_start={frame_start},
            frame_end={frame_end},
            use_memory_cache={str(kwargs.get('use_memory_cache', True)).lower()}
        )
        results.append(ps.name)
    
    return {{
        'status': 'SUCCESS',
        'baked_systems': results,
        'frame_range': ({frame_start}, {frame_end})
    }}

try:
    result = bake_particles()
except Exception as e:
    result = {{'status': 'ERROR', 'error': str(e)}}

print(str(result))
"""
    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to bake particles: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

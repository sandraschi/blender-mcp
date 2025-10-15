"""Simulation operations handler for Blender MCP."""

from typing import Optional, Dict, Any, Union
from enum import Enum

from loguru import logger

from ..compat import *
from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()


class SimulationType(str, Enum):
    """Supported simulation types."""

    CLOTH = "CLOTH"
    FLUID = "FLUID"
    SMOKE = "SMOKE"
    DYNAMIC_PAINT = "DYNAMIC_PAINT"
    SOFT_BODY = "SOFT_BODY"
    RIGID_BODY = "RIGID_BODY"
    PARTICLE_SYSTEM = "PARTICLE_SYSTEM"
    FLUID_FLIP = "FLUID_FLIP"
    OCEAN = "OCEAN"


@blender_operation("add_simulation", log_args=True)
async def add_simulation(
    object_name: str, simulation_type: Union[SimulationType, str], **kwargs: Any
) -> Dict[str, Any]:
    """Add a physics simulation to an object.

    Args:
        object_name: Name of the object to add simulation to
        simulation_type: Type of simulation to add
        **kwargs: Simulation parameters specific to each type
            - For CLOTH: mass, tension, compression, bending, etc.
            - For FLUID: type (DOMAIN, FLOW, EFFECTOR), resolution, etc.
            - For RIGID_BODY: type (ACTIVE, PASSIVE), mass, friction, etc.

    Returns:
        Dict containing simulation creation status and details
    """
    simulation_type = simulation_type.upper()

    script = f"""

def add_simulation():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{"status": "ERROR", "error": "Object not found"}}
    
    try:
        # Make the object active
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Add the appropriate physics simulation
        if '{simulation_type}' == 'CLOTH':
            bpy.ops.object.modifier_add(type='CLOTH')
            mod = obj.modifiers[-1]
            
            # Set cloth settings from kwargs
            if 'mass' in {kwargs}:
                mod.settings.mass = {kwargs["mass"]}
            if 'tension' in {kwargs}:
                mod.settings.tension_stiffness = {kwargs["tension"]}
            if 'compression' in {kwargs}:
                mod.settings.compression_stiffness = {kwargs["compression"]}
            if 'bending' in {kwargs}:
                mod.settings.bending_stiffness = {kwargs["bending"]}
            if 'damping' in {kwargs}:
                mod.settings.air_damping = {kwargs["damping"]}
            
            # Enable self-collision if requested
            if {kwargs.get("self_collision", False)}:
                mod.settings.use_self_collision = True
            
            # Add collision settings
            if 'collision' in {kwargs} and {kwargs["collision"]}:
                mod.collision_settings.use_collision = True
        
        elif '{simulation_type}' == 'FLUID':
            fluid_type = {kwargs.get("fluid_type", "DOMAIN").upper()}
            
            if fluid_type == 'DOMAIN':
                bpy.ops.object.quick_fluid()
                domain = bpy.context.active_object
                
                # Set domain settings
                if 'resolution' in {kwargs}:
                    domain.modifiers[-1].domain_settings.resolution = {kwargs["resolution"]}
                if 'time_scale' in {kwargs}:
                    domain.modifiers[-1].domain_settings.time_scale = {kwargs["time_scale"]}
                
                return {{
                    "status": "SUCCESS",
                    "simulation_type": '{simulation_type}',
                    "domain_object": domain.name,
                    "settings": dict(domain.modifiers[-1].domain_settings.items())
                }}
            
            else:  # FLOW or EFFECTOR
                bpy.ops.object.quick_fluid(style=fluid_type)
                flow = bpy.context.active_object
                
                # Set flow settings
                if 'flow_type' in {kwargs}:
                    flow.modifiers[-1].flow_settings.flow_type = {kwargs["flow_type"]}
                if 'initial_velocity' in {kwargs}:
                    flow.modifiers[-1].flow_settings.initial_velocity = {kwargs["initial_velocity"]}
                
                return {{
                    "status": "SUCCESS",
                    "simulation_type": '{simulation_type}',
                    "flow_object": flow.name,
                    "flow_type": flow.modifiers[-1].flow_settings.flow_type
                }}
        
        elif '{simulation_type}' == 'RIGID_BODY':
            # Add rigid body physics
            bpy.ops.rigidbody.object_add()
            
            # Set rigid body type (ACTIVE or PASSIVE)
            rb_type = {kwargs.get("rigid_body_type", "ACTIVE").upper()}
            obj.rigid_body.type = rb_type
            
            # Set mass and other properties
            if 'mass' in {kwargs}:
                obj.rigid_body.mass = {kwargs["mass"]}
            if 'friction' in {kwargs}:
                obj.rigid_body.friction = {kwargs["friction"]}
            if 'restitution' in {kwargs}:
                obj.rigid_body.restitution = {kwargs["restitution"]}
            
            return {{
                "status": "SUCCESS",
                "simulation_type": '{simulation_type}',
                "rigid_body_type": rb_type,
                "mass": obj.rigid_body.mass
            }}
        
        elif '{simulation_type}' == 'SOFT_BODY':
            bpy.ops.object.modifier_add(type='SOFT_BODY')
            mod = obj.modifiers[-1]
            
            # Set soft body settings
            if 'mass' in {kwargs}:
                mod.settings.mass = {kwargs["mass"]}
            if 'stiffness' in {kwargs}:
                mod.settings.bend = {kwargs["stiffness"]}
            if 'damping' in {kwargs}:
                mod.settings.drag = {kwargs["damping"]}
            
            # Add goal settings
            if 'goal' in {kwargs} and {kwargs["goal"]}:
                mod.settings.use_goal = True
                if 'goal_strength' in {kwargs}:
                    mod.settings.goal_default = {kwargs["goal_strength"]}
        
        elif '{simulation_type}' == 'PARTICLE_SYSTEM':
            bpy.ops.object.particle_system_add()
            ps = obj.particle_systems[-1]
            
            # Set particle settings
            if 'count' in {kwargs}:
                ps.settings.count = {kwargs["count"]}
            if 'lifetime' in {kwargs}:
                ps.settings.lifetime = {kwargs["lifetime"]}
            if 'size' in {kwargs}:
                ps.settings.particle_size = {kwargs["size"]}
            
            # Set emission type
            if 'emission_type' in {kwargs}:
                ps.settings.emit_from = {kwargs["emission_type"]}
        
        elif '{simulation_type}' == 'OCEAN':
            bpy.ops.object.modifier_add(type='OCEAN')
            mod = obj.modifiers[-1]
            
            # Set ocean settings
            if 'resolution' in {kwargs}:
                mod.resolution = {kwargs["resolution"]}
            if 'wave_scale' in {kwargs}:
                mod.wave_scale = {kwargs["wave_scale"]}
            if 'choppiness' in {kwargs}:
                mod.choppiness = {kwargs["choppiness"]}
            if 'wind_velocity' in {kwargs}:
                mod.wind_velocity = {kwargs["wind_velocity"]}
        
        else:
            return {{"status": "ERROR", "error": f"Unsupported simulation type: {simulation_type}"}}
        
        return {{
            "status": "SUCCESS",
            "simulation_type": '{simulation_type}',
            "object": obj.name,
            "modifier": obj.modifiers[-1].name if obj.modifiers else None
        }}
    
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = add_simulation()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to add simulation: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("bake_simulation", log_args=True)
async def bake_simulation(
    object_name: str, simulation_type: Optional[Union[SimulationType, str]] = None, **kwargs: Any
) -> Dict[str, Any]:
    """Bake a physics simulation.

    Args:
        object_name: Name of the object with the simulation
        simulation_type: Type of simulation to bake (optional, will detect if None)
        **kwargs: Additional parameters
            - start_frame: Start frame for baking (default: 1)
            - end_frame: End frame for baking (default: 250)
            - cache_path: Path to save the cache (for fluid/particles)
            - use_disk_cache: Save cache to disk (default: False)

    Returns:
        Dict containing bake status and details
    """
    start_frame = kwargs.get("start_frame", 1)
    end_frame = kwargs.get("end_frame", 250)
    cache_path = kwargs.get("cache_path")
    kwargs.get("use_disk_cache", False)

    script = f"""
import os

def bake_simulation():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{"status": "ERROR", "error": "Object not found"}}
    
    # Determine simulation type if not specified
    sim_type = '{simulation_type}'.upper() if '{simulation_type}' else None
    if not sim_type:
        for mod in obj.modifiers:
            if mod.type in ['CLOTH', 'SOFT_BODY', 'FLUID', 'FLUID_SIMULATION', 'DYNAMIC_PAINT', 'SMOKE', 'PARTICLE_SYSTEM', 'OCEAN']:
                sim_type = mod.type
                break
        
        if not sim_type and obj.rigid_body:
            sim_type = 'RIGID_BODY'
        
        if not sim_type:
            return {{"status": "ERROR", "error": "No simulation found on object"}}
    
    try:
        # Make the object active
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Set frame range
        scene = bpy.context.scene
        scene.frame_start = {start_frame}
        scene.frame_end = {end_frame}
        
        # Bake based on simulation type
        if sim_type in ['CLOTH', 'SOFT_BODY']:
            # Find the modifier
            mod = None
            for m in obj.modifiers:
                if m.type == sim_type:
                    mod = m
                    break
            
            if not mod:
                return {{"status": "ERROR", "error": f"No {{sim_type}} modifier found"}}
            
            # Bake the simulation
            if sim_type == 'CLOTH':
                bpy.ops.ptcache.bake(bake=True)
            else:  # SOFT_BODY
                bpy.ops.ptcache.bake(bake=True)
            
            return {{
                "status": "SUCCESS",
                "simulation_type": sim_type,
                "object": obj.name,
                "modifier": mod.name,
                "frame_range": ({start_frame}, {end_frame})
            }}
        
        elif sim_type in ['FLUID', 'FLUID_SIMULATION', 'SMOKE']:
            # For fluid simulations, we need to find the domain object
            domain = None
            if obj.modifiers and hasattr(obj.modifiers[0], 'domain_settings'):
                domain = obj
            else:
                # Look for domain in the scene
                for o in bpy.data.objects:
                    if o.modifiers and hasattr(o.modifiers[0], 'domain_settings'):
                        domain = o
                        break
            
            if not domain:
                return {{"status": "ERROR", "error": "Fluid domain not found"}}
            
            # Set cache path if provided
            if '{cache_path}':
                domain.modifiers[0].domain_settings.cache_directory = '{cache_path}'
            
            # Bake the simulation
            bpy.context.view_layer.objects.active = domain
            domain.select_set(True)
            
            if sim_type == 'SMOKE':
                bpy.ops.fluid.bake()
            else:
                bpy.ops.fluid.bake()
            
            return {{
                "status": "SUCCESS",
                "simulation_type": sim_type,
                "domain_object": domain.name,
                "cache_path": domain.modifiers[0].domain_settings.cache_directory,
                "frame_range": ({start_frame}, {end_frame})
            }}
        
        elif sim_type == 'RIGID_BODY':
            if not obj.rigid_body:
                return {{"status": "ERROR", "error": "No rigid body found on object"}}
            
            # Bake rigid body simulation
            bpy.ops.rigidbody.bake_to_keyframes(frame_start={start_frame}, frame_end={end_frame})
            
            return {{
                "status": "SUCCESS",
                "simulation_type": sim_type,
                "object": obj.name,
                "frame_range": ({start_frame}, {end_frame})
            }}
        
        elif sim_type == 'PARTICLE_SYSTEM':
            if not obj.particle_systems:
                return {{"status": "ERROR", "error": "No particle system found on object"}}
            
            # Bake particle system
            for ps in obj.particle_systems:
                ps.point_cache.frame_start = {start_frame}
                ps.point_cache.frame_end = {end_frame}
            
            bpy.ops.ptcache.bake(bake=True)
            
            return {
        "status": "SUCCESS",
                "simulation_type": sim_type,
                "object": obj.name,
                "particle_systems": [ps.name for ps in obj.particle_systems],
                "frame_range": ({start_frame}, {end_frame})
            }
        
        else:
            return {{"status": "ERROR", "error": f"Baking not implemented for simulation type: {{sim_type}}"}}
    
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = bake_simulation()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to bake simulation: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("set_simulation_visibility", log_args=True)
async def set_simulation_visibility(
    object_name: str,
    visible: bool = True,
    viewport: bool = True,
    render: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Set the visibility of a simulation in viewport and render.

    Args:
        object_name: Name of the object with the simulation
        visible: Overall visibility of the simulation
        viewport: Show in viewport
        render: Show in render
        **kwargs: Additional parameters
            - simulation_type: Specific simulation type to affect (optional)

    Returns:
        Dict containing visibility status
    """
    simulation_type = kwargs.get("simulation_type")

    script = f"""

def set_sim_visibility():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{"status": "ERROR", "error": "Object not found"}}
    
    sim_type = '{simulation_type}'.upper() if '{simulation_type}' else None
    
    try:
        # Set visibility for all matching simulations
        modified = []
        
        # Check modifiers
        for mod in obj.modifiers:
            if not sim_type or mod.type == sim_type:
                mod.show_viewport = {str(viewport).lower()}
                mod.show_render = {str(render).lower()}
                modified.append(mod.name)
        
        # Check particle systems
        if not sim_type or sim_type == 'PARTICLE_SYSTEM':
            for ps in obj.particle_systems:
                ps.settings.use_render = {str(render).lower()}
                ps.settings.use_render_emitter = {str(render).lower()}
                modified.append(f"ParticleSystem:{ps.name}")
        
        # Check rigid body
        if obj.rigid_body and (not sim_type or sim_type == 'RIGID_BODY'):
            obj.rigid_body.kinematic = not {str(visible).lower()}
            modified.append("RigidBody")
        
        return {{
            "status": "SUCCESS",
            "object": obj.name,
            "visible": {str(visible).lower()},
            "viewport_visible": {str(viewport).lower()},
            "render_visible": {str(render).lower()},
            "modified_simulations": modified
        }}
    
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = set_sim_visibility()
    print(str(result))
except Exception as e:
    print(str({{'status': 'ERROR', 'error': str(e)}}))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to set simulation visibility: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

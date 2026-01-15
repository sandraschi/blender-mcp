"""Physics operations handler for Blender MCP.

This module provides physics simulation and rigid body functions that can be registered as FastMCP tools.
"""
from enum import Enum
from typing import Any, Dict, Optional, Tuple, Union

from loguru import logger

from ..compat import *
from ..decorators import blender_operation
from ..utils.blender_executor import get_blender_executor

# Initialize the executor with default Blender executable
_executor = get_blender_executor()


class PhysicsType(str, Enum):
    """Supported physics types."""

    RIGID_BODY = "RIGID_BODY"
    SOFT_BODY = "SOFT_BODY"
    CLOTH = "CLOTH"
    FLUID = "FLUID"
    SMOKE = "SMOKE"
    DYNAMIC_PAINT = "DYNAMIC_PAINT"


class RigidBodyType(str, Enum):
    """Rigid body types."""

    ACTIVE = "ACTIVE"
    PASSIVE = "PASSIVE"


class RigidBodyConstraintType(str, Enum):
    """Rigid body constraint types."""

    FIXED = "FIXED"
    POINT = "POINT"
    HINGE = "HINGE"
    SLIDER = "SLIDER"
    PISTON = "PISTON"
    GENERIC = "GENERIC"
    GENERIC_SPRING = "GENERIC_SPRING"
    MOTOR = "MOTOR"


class CollisionShapeType(str, Enum):
    """Collision shape types for rigid bodies."""

    BOX = "BOX"
    SPHERE = "SPHERE"
    CAPSULE = "CAPSULE"
    CYLINDER = "CYLINDER"
    CONE = "CONE"
    CONVEX_HULL = "CONVEX_HULL"
    MESH = "MESH"
    COMPOUND = "COMPOUND"


@blender_operation("enable_physics", log_args=True)
async def enable_physics(
    object_name: str,
    physics_type: Union[PhysicsType, str] = PhysicsType.RIGID_BODY,
    rigid_body_type: Union[RigidBodyType, str] = RigidBodyType.ACTIVE,
    mass: float = 1.0,
    friction: float = 0.5,
    bounciness: float = 0.5,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Enable physics simulation for an object.

    Args:
        object_name: Name of the object to enable physics for
        physics_type: Type of physics to enable (RIGID_BODY, SOFT_BODY, CLOTH, etc.)
        rigid_body_type: Type of rigid body (ACTIVE or PASSIVE) - only for RIGID_BODY
        mass: Mass of the object in kg
        friction: Friction coefficient (0.0-1.0)
        bounciness: Bounciness/restitution (0.0-1.0)
        **kwargs: Additional physics properties
            - collision_shape: Shape for collision detection (e.g., 'MESH', 'BOX', 'SPHERE')
            - damping_linear/angular: Linear/angular damping (0.0-1.0)
            - use_margin: Enable collision margin (bool)
            - collision_margin: Collision margin distance

    Returns:
        Dict containing operation status and physics settings
    """
    collision_shape = kwargs.get("collision_shape", "MESH")
    damping_linear = kwargs.get("damping_linear", 0.1)
    damping_angular = kwargs.get("damping_angular", 0.1)
    use_margin = kwargs.get("use_margin", False)
    collision_margin = kwargs.get("collision_margin", 0.04)

    script = f"""
import math

def setup_physics():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    # Make sure the object is selected and active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Enable rigid body physics
    if '{physics_type}' == 'RIGID_BODY':
        bpy.ops.rigidbody.object_add()
        
        # Set rigid body type and properties
        obj.rigid_body.type = '{rigid_body_type}'
        obj.rigid_body.mass = {mass}
        obj.rigid_body.friction = {friction}
        obj.rigid_body.restitution = {bounciness}
        obj.rigid_body.linear_damping = {damping_linear}
        obj.rigid_body.angular_damping = {damping_angular}
        obj.rigid_body.collision_shape = '{collision_shape}'
        obj.rigid_body.use_margin = {str(use_margin).lower()}
        obj.rigid_body.collision_margin = {collision_margin}
        
        # Set collision group/mask if provided
        if {kwargs.get("collision_groups", None)} is not None:
            for i, enabled in enumerate({kwargs.get("collision_groups", [])}):
                if i < 20:  # Blender supports 20 collision groups
                    obj.rigid_body.collision_groups[i] = bool(enabled)
    
    # Enable cloth simulation
    elif '{physics_type}' == 'CLOTH':
        # Add cloth modifier if it doesn't exist
        if 'Cloth' not in obj.modifiers:
            bpy.ops.object.modifier_add(type='CLOTH')
        
        # Get the cloth modifier
        cloth = obj.modifiers['Cloth']
        
        # Configure cloth settings
        settings = cloth.settings
        settings.quality = {kwargs.get("quality", 5)}  # Default quality level
        settings.mass = {mass}
        settings.air_damping = {kwargs.get("air_damping", 1.0)}
        settings.tension_stiffness = {kwargs.get("tension_stiffness", 15.0)}
        settings.compression_stiffness = {kwargs.get("compression_stiffness", 15.0)}
        settings.shear_stiffness = {kwargs.get("shear_stiffness", 5.0)}
        settings.bending_stiffness = {kwargs.get("bending_stiffness", 0.5)}
        
        # Collision settings
        settings.use_collision = {str(kwargs.get("use_collision", True)).lower()}
        settings.use_self_collision = {str(kwargs.get("use_self_collision", True)).lower()}
        settings.self_collision_quality = {kwargs.get("self_collision_quality", 5)}
        settings.self_collision_distance = {kwargs.get("self_collision_distance", 0.015)}
        
        # Cache settings
        if 'cache' not in settings:
            settings.use_internal_springs = {str(kwargs.get("use_internal_springs", True)).lower()}
        
        # Pin group for cloth (vertex group to pin parts of the cloth)
        if '{kwargs.get("pin_group", "")}':
            settings.vertex_group_mass = '{kwargs["pin_group"]}'
            settings.pin_stiffness = {kwargs.get("pin_stiffness", 0.5)}
    
    return {{
        'status': 'SUCCESS',
        'object': obj.name,
        'physics_type': '{physics_type}',
        'mass': {mass},
        'friction': {friction},
        'bounciness': {bounciness}
    }}

try:
    result = setup_physics()
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
        logger.error(f"Failed to enable physics: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("bake_physics_simulation", log_args=True)
async def bake_physics_simulation(
    frame_start: int = 1, frame_end: int = 250, step: int = 1, **kwargs: Any
) -> Dict[str, Any]:
    """Bake physics simulation to keyframes.

    Args:
        frame_start: First frame to bake
        frame_end: Last frame to bake
        step: Frame step for baking
        **kwargs: Additional parameters
            - only_selected: Only bake selected objects (bool, default: False)
            - clear_cached: Clear cached simulation data (bool, default: True)

    Returns:
        Dict containing operation status and bake details
    """
    only_selected = kwargs.get("only_selected", False)
    clear_cached = kwargs.get("clear_cached", True)

    script = f"""

def bake_simulation():
    # Set the frame range
    scene = bpy.context.scene
    scene.frame_start = {frame_start}
    scene.frame_end = {frame_end}
    
    # Select objects if needed
    if {str(only_selected).lower()} and not bpy.context.selected_objects:
        return {{'status': 'ERROR', 'error': 'No objects selected'}}
    
    # Clear existing animation data if needed
    if {str(clear_cached).lower()}:
        bpy.ops.ptcache.free_bake()
        bpy.ops.ptcache.free_bake_all()
    
    # Bake the simulation
    bpy.ops.ptcache.bake(
        bake=True,
        frame_start={frame_start},
        frame_end={frame_end},
        step={step},
        only_selected={str(only_selected).lower()}
    )
    
    return {{
        'status': 'SUCCESS',
        'frame_range': ({frame_start}, {frame_end}),
        'step': {step},
        'baked_frames': list(range({frame_start}, {frame_end} + 1, {step}))
    }}

try:
    result = bake_simulation()
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
        logger.error(f"Failed to bake physics simulation: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("add_force_field", log_args=True)
async def add_force_field(
    field_type: str = "FORCE",
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    strength: float = 1.0,
    falloff: float = 2.0,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Add a force field to the scene.

    Args:
        field_type: Type of force field (FORCE, WIND, VORTEX, etc.)
        location: Location of the force field (x, y, z)
        strength: Strength of the force field
        falloff: Falloff power for the force field
        **kwargs: Additional force field properties
            - direction: Direction vector for directional forces
            - flow: Flow type for wind/turbulence
            - use_max_distance: Enable maximum distance
            - max_distance: Maximum distance of effect

    Returns:
        Dict containing operation status and force field details
    """
    direction = kwargs.get("direction", (0.0, 0.0, 1.0))
    flow = kwargs.get("flow", 0)
    use_max_distance = kwargs.get("use_max_distance", False)
    max_distance = kwargs.get("max_distance", 10.0)

    script = f"""
from mathutils import Vector

def add_force_field():
    # Create an empty object for the force field
    bpy.ops.object.empty_add(
        type='ARROWS',
        location={list(location)},
        scale=(0.5, 0.5, 0.5)
    )
    
    empty = bpy.context.active_object
    empty.name = 'ForceField_{field_type}'
    
    # Add a force field to the empty
    bpy.ops.object.effects_add(type='{field_type}')
    field = empty.field
    
    # Configure the force field
    field.strength = {strength}
    field.falloff_power = {falloff}
    field.flow = {flow}
    field.direction = {list(direction)}
    field.use_max_distance = {str(use_max_distance).lower()}
    field.distance_max = {max_distance}
    
    # Additional field type specific settings
    if '{field_type}' == 'WIND':
        field.noise = {kwargs.get("noise", 0.0)}
    elif '{field_type}' == 'VORTEX':
        field.falloff_type = '{kwargs.get("falloff_type", "TUBE")}'
    
    return {{
        'status': 'SUCCESS',
        'field_name': empty.name,
        'field_type': '{field_type}',
        'location': {list(location)},
        'strength': {strength}
    }}

try:
    result = add_force_field()
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
        logger.error(f"Failed to add force field: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("configure_cloth_simulation", log_args=True)
async def configure_cloth_simulation(
    object_name: str,
    quality: int = 5,
    mass: float = 0.3,
    air_damping: float = 1.0,
    tension_stiffness: float = 15.0,
    compression_stiffness: float = 15.0,
    shear_stiffness: float = 5.0,
    bending_stiffness: float = 0.5,
    use_collision: bool = True,
    use_self_collision: bool = True,
    self_collision_quality: int = 5,
    self_collision_distance: float = 0.015,
    use_internal_springs: bool = True,
    pin_group: str = "",
    pin_stiffness: float = 0.5,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Configure cloth simulation settings for an object.

    Args:
        object_name: Name of the object with cloth simulation
        quality: Simulation quality (1-10)
        mass: Mass of the cloth material
        air_damping: Air damping factor (0.0-10.0)
        tension_stiffness: Stiffness for tension (0.0-100.0)
        compression_stiffness: Stiffness for compression (0.0-100.0)
        shear_stiffness: Stiffness for shearing (0.0-100.0)
        bending_stiffness: Stiffness for bending (0.0-100.0)
        use_collision: Enable collision with other objects
        use_self_collision: Enable self-collision
        self_collision_quality: Quality of self-collision (1-10)
        self_collision_distance: Minimum distance for self-collision
        use_internal_springs: Use internal spring system
        pin_group: Vertex group name for pinned vertices
        pin_stiffness: Stiffness of pin constraints (0.0-1.0)
        **kwargs: Additional cloth settings
            - pressure: Pressure for closed meshes (0.0-10.0)
            - shrink_min: Minimum shrink factor (0.0-1.0)
            - shrink_max: Maximum shrink factor (0.0-1.0)

    Returns:
        Dict containing operation status and cloth settings
    """
    pressure = kwargs.get("pressure", 0.0)
    shrink_min = kwargs.get("shrink_min", 0.0)
    shrink_max = kwargs.get("shrink_max", 1.0)

    script = f"""

def configure_cloth():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    # Get or add cloth modifier
    if 'Cloth' not in obj.modifiers:
        return {{'status': 'ERROR', 'error': 'Cloth modifier not found'}}
    
    cloth = obj.modifiers['Cloth']
    settings = cloth.settings
    
    # Basic settings
    settings.quality = {quality}
    settings.mass = {mass}
    settings.air_damping = {air_damping}
    
    # Stiffness settings
    settings.tension_stiffness = {tension_stiffness}
    settings.compression_stiffness = {compression_stiffness}
    settings.shear_stiffness = {shear_stiffness}
    settings.bending_stiffness = {bending_stiffness}
    
    # Collision settings
    settings.use_collision = {str(use_collision).lower()}
    settings.use_self_collision = {str(use_self_collision).lower()}
    settings.self_collision_quality = {self_collision_quality}
    settings.self_collision_distance = {self_collision_distance}
    
    # Cache and internal springs
    settings.use_internal_springs = {str(use_internal_springs).lower()}
    
    # Pin group settings
    if '{pin_group}':
        settings.vertex_group_mass = '{pin_group}'
        settings.pin_stiffness = {pin_stiffness}
    
    # Pressure settings (for closed meshes)
    settings.use_pressure = {str(pressure > 0).lower()}
    settings.uniform_pressure_force = {pressure}
    settings.shrink_min = {shrink_min}
    settings.shrink_max = {shrink_max}
    
    # Additional settings from kwargs
    for key, value in {kwargs}.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    return {{
        'status': 'SUCCESS',
        'object': obj.name,
        'cloth_settings': {{
            'quality': {quality},
            'mass': {mass},
            'tension_stiffness': {tension_stiffness},
            'compression_stiffness': {compression_stiffness},
            'shear_stiffness': {shear_stiffness},
            'bending_stiffness': {bending_stiffness},
            'use_collision': {str(use_collision).lower()},
            'use_self_collision': {str(use_self_collision).lower()}
        }}
    }}

try:
    result = configure_cloth()
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
        logger.error(f"Failed to configure cloth simulation: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("bake_cloth_simulation", log_args=True)
async def bake_cloth_simulation(
    object_name: str,
    frame_start: int = 1,
    frame_end: int = 250,
    step: int = 1,
    clear_previous: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Bake cloth simulation to keyframes.

    Args:
        object_name: Name of the object with cloth simulation
        frame_start: First frame to bake
        frame_end: Last frame to bake
        step: Frame step (1 = every frame, 2 = every other frame, etc.)
        clear_previous: Whether to clear existing keyframes before baking
        **kwargs: Additional bake settings
            - use_gravity: Apply gravity during bake (default: True)
            - use_subsurf: Apply subdivision surface during bake (default: True)
            - use_shape_keys: Bake to shape keys (default: False)

    Returns:
        Dict containing operation status and bake information
    """
    use_gravity = kwargs.get("use_gravity", True)
    kwargs.get("use_subsurf", True)
    use_shape_keys = kwargs.get("use_shape_keys", False)

    script = f"""

def bake_cloth():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    # Get cloth modifier
    cloth_mod = next((m for m in obj.modifiers if m.type == 'CLOTH'), None)
    if not cloth_mod:
        return {{'status': 'ERROR', 'error': 'Cloth modifier not found'}}
    
    # Set up scene for baking
    scene = bpy.context.scene
    scene.frame_start = {frame_start}
    scene.frame_end = {frame_end}
    scene.frame_step = {step}
    
    # Store original frame
    original_frame = scene.frame_current
    
    # Clear existing keyframes if requested
    if {str(clear_previous).lower()}:
        for fcurve in obj.data.shape_keys.animation_data.action.fcurves if obj.data.shape_keys and obj.data.shape_keys.animation_data and obj.data.shape_keys.animation_data.action else []:
            obj.data.shape_keys.animation_data.action.fcurves.remove(fcurve)
    
    # Set up bake settings
    settings = cloth_mod.settings
    settings.point_cache.frame_start = {frame_start}
    settings.point_cache.frame_end = {frame_end}
    
    # Select the object and make it active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Bake the simulation
    try:
        bpy.ops.ptcache.bake(bake=True, frame_start={frame_start}, frame_end={frame_end}, 
                            step={step}, use_gravity={str(use_gravity).lower()})
        
        # Convert to mesh if requested
        if {str(use_shape_keys).lower()} and obj.data.shape_keys:
            # Create basis shape key if it doesn't exist
            if not obj.data.shape_keys.key_blocks.get('Basis'):
                basis = obj.shape_key_add(name='Basis')
                basis.interpolation = 'KEY_LINEAR'
            
            # Create shape key for each frame
            for frame in range({frame_start}, {frame_end} + 1, {step}):
                scene.frame_set(frame)
                key_name = f'Frame_{{frame:04d}}'
                if key_name not in obj.data.shape_keys.key_blocks:
                    shape_key = obj.shape_key_add(name=key_name, from_mix=True)
                    shape_key.interpolation = 'KEY_LINEAR'
                    
                    # Add keyframe
                    shape_key.value = 1.0
                    shape_key.keyframe_insert(data_path='value', frame=frame)
                    
                    # Reset for next frame
                    shape_key.value = 0.0
    
    except Exception as e:
        return {{'status': 'ERROR', 'error': f'Baking failed: {{str(e)}}'}}
    finally:
        # Restore original frame
        scene.frame_set(original_frame)
    
    return {{
        'status': 'SUCCESS',
        'object': obj.name,
        'frame_start': {frame_start},
        'frame_end': {frame_end},
        'step': {step},
        'baked_frames': list(range({frame_start}, {frame_end} + 1, {step}))
    }}

try:
    result = bake_cloth()
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
        logger.error(f"Failed to bake cloth simulation: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("add_rigid_body_constraint", log_args=True)
async def add_rigid_body_constraint(
    object_a: str,
    object_b: str,
    constraint_type: Union[RigidBodyConstraintType, str],
    pivot_a: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    pivot_b: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    use_spring: bool = False,
    spring_stiffness: float = 10.0,
    spring_damping: float = 0.5,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Add a constraint between two rigid bodies.

    Args:
        object_a: Name of the first rigid body
        object_b: Name of the second rigid body (or empty for world)
        constraint_type: Type of constraint (FIXED, POINT, HINGE, etc.)
        pivot_a: Pivot point in object A's local space
        pivot_b: Pivot point in object B's local space (or world space if object_b is empty)
        use_spring: Enable spring for the constraint
        spring_stiffness: Spring stiffness when use_spring is True
        spring_damping: Spring damping when use_spring is True
        **kwargs: Additional constraint parameters
            - use_limit_*: Enable limits for specific axes (x, y, z, ang_x, ang_y, ang_z)
            - limit_*_min/max: Minimum/maximum limits for each axis
            - use_motor: Enable motor for the constraint
            - motor_velocity: Target velocity for the motor
            - motor_max_impulse: Maximum impulse for the motor

    Returns:
        Dict containing operation status and constraint details
    """
    script = f"""
from mathutils import Matrix, Vector, Quaternion, Euler

def add_constraint():
    # Get the objects
    obj_a = bpy.data.objects.get('{object_a}')
    if not obj_a:
        return {{'status': 'ERROR', 'error': f'Object A ({{object_a}}) not found'}}
        
    obj_b = None
    if '{object_b}':
        obj_b = bpy.data.objects.get('{object_b}')
        if not obj_b:
            return {{'status': 'ERROR', 'error': f'Object B ({{object_b}}) not found'}}
    
    # Create an empty to hold the constraint
    bpy.ops.object.empty_add(type='ARROWS', location=(0, 0, 0))
    empty = bpy.context.active_object
    empty.name = f'RBC_{object_a}_to_{object_b or "WORLD"}'
    
    # Add rigid body constraint
    bpy.ops.rigidbody.constraint_add()
    constraint = empty.rigid_body_constraint
    constraint.type = '{constraint_type}'
    
    # Set up the constraint
    constraint.object1 = obj_a
    if obj_b:
        constraint.object2 = obj_b
    
    # Set pivot points
    constraint.pivot_type = 'ACTIVE' if obj_b else 'CENTER'
    constraint.pivot_x = {pivot_a[0]}
    constraint.pivot_y = {pivot_a[1]}
    constraint.pivot_z = {pivot_a[2]}
    
    if obj_b:
        constraint.pivot_x = {pivot_b[0]}
        constraint.pivot_y = {pivot_b[1]}
        constraint.pivot_z = {pivot_b[2]}
    
    # Spring settings
    constraint.use_spring = {str(use_spring).lower()}
    if {str(use_spring).lower()}:
        constraint.spring_stiffness = {spring_stiffness}
        constraint.spring_damping = {spring_damping}
    
    # Set up limits from kwargs
    for axis in ['x', 'y', 'z', 'ang_x', 'ang_y', 'ang_z']:
        use_limit = {kwargs}.get(f'use_limit_{{axis}}', False)
        limit_min = {kwargs}.get(f'limit_{{axis}}_min', -1.0)
        limit_max = {kwargs}.get(f'limit_{{axis}}_max', 1.0)
        
        setattr(constraint, f'use_limit_{axis}', use_limit)
        if use_limit:
            setattr(constraint, f'limit_{axis}_min', limit_min)
            setattr(constraint, f'limit_{axis}_max', limit_max)
    
    # Motor settings
    use_motor = {kwargs}.get('use_motor', False)
    if hasattr(constraint, 'use_motor'):  # Only some constraint types support motors
        constraint.use_motor = use_motor
        if use_motor:
            constraint.motor_velocity = {kwargs}.get('motor_velocity', 1.0)
            constraint.motor_max_impulse = {kwargs}.get('motor_max_impulse', 0.1)
    
    return {{
        'status': 'SUCCESS',
        'constraint': empty.name,
        'type': '{constraint_type}',
        'object_a': '{object_a}',
        'object_b': '{object_b or "WORLD"}',
        'pivot_a': {list(pivot_a)},
        'pivot_b': {list(pivot_b)}
    }}

try:
    result = add_constraint()
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
        logger.error(f"Failed to add rigid body constraint: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("configure_rigid_body_world", log_args=True)
async def configure_rigid_body_world(
    gravity: Tuple[float, float, float] = (0.0, 0.0, -9.81),
    time_scale: float = 1.0,
    substeps_per_frame: int = 10,
    solver_iterations: int = 10,
    use_split_impulse: bool = True,
    split_impulse_threshold: float = 0.01,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Configure the rigid body world simulation settings.

    Args:
        gravity: Gravity vector (x, y, z)
        time_scale: Time scale for the simulation (0.1 = slow motion, 1.0 = normal, 2.0 = double speed)
        substeps_per_frame: Number of simulation steps per frame (higher = more accurate but slower)
        solver_iterations: Number of solver iterations per step (higher = more stable but slower)
        use_split_impulse: Use split impulse for better stability
        split_impulse_threshold: Threshold for split impulse
        **kwargs: Additional simulation settings
            - use_deactivation: Enable deactivation of resting objects (default: True)
            - deactivate_linear_threshold: Linear velocity threshold for deactivation (default: 0.1)
            - deactivate_angular_threshold: Angular velocity threshold for deactivation (default: 0.1)
            - deactivate_time: Time before deactivation (default: 2.0)
            - use_continuous_collision: Enable continuous collision detection (default: False)
            - ccd_mode: Continuous collision detection mode ('NONE', 'STATIC', 'DYNAMIC', 'ALL')
            - ccd_threshold: Threshold for CCD (default: 0.1)

    Returns:
        Dict containing operation status and simulation settings
    """
    use_deactivation = kwargs.get("use_deactivation", True)
    deactivate_linear_threshold = kwargs.get("deactivate_linear_threshold", 0.1)
    deactivate_angular_threshold = kwargs.get("deactivate_angular_threshold", 0.1)
    deactivate_time = kwargs.get("deactivate_time", 2.0)
    use_continuous_collision = kwargs.get("use_continuous_collision", False)
    ccd_mode = kwargs.get("ccd_mode", "NONE")
    ccd_threshold = kwargs.get("ccd_threshold", 0.1)

    script = f"""

def configure_world():
    scene = bpy.context.scene
    
    # Enable rigid body world if not already enabled
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    rb_world = scene.rigidbody_world
    
    # Set basic simulation parameters
    rb_world.gravity = {list(gravity)}
    rb_world.time_scale = {time_scale}
    rb_world.substeps_per_frame = {substeps_per_frame}
    rb_world.solver_iterations = {solver_iterations}
    
    # Split impulse settings
    rb_world.use_split_impulse = {str(use_split_impulse).lower()}
    if {str(use_split_impulse).lower()}:
        rb_world.split_impulse_threshold = {split_impulse_threshold}
    
    # Deactivation settings
    rb_world.use_deactivation = {str(use_deactivation).lower()}
    if {str(use_deactivation).lower()}:
        rb_world.deactivate_linear_threshold = {deactivate_linear_threshold}
        rb_world.deactivate_angular_threshold = {deactivate_angular_threshold}
        rb_world.deactivate_time = {deactivate_time}
    
    # Continuous collision detection
    rb_world.use_continuous_collision = {str(use_continuous_collision).lower()}
    if {str(use_continuous_collision).lower()}:
        rb_world.ccd_mode = '{ccd_mode}'
        rb_world.ccd_threshold = {ccd_threshold}
    
    return {{
        'status': 'SUCCESS',
        'gravity': {list(gravity)},
        'time_scale': {time_scale},
        'substeps_per_frame': {substeps_per_frame},
        'solver_iterations': {solver_iterations},
        'use_split_impulse': {str(use_split_impulse).lower()},
        'use_deactivation': {str(use_deactivation).lower()},
        'use_continuous_collision': {str(use_continuous_collision).lower()}
    }}

try:
    result = configure_world()
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
        logger.error(f"Failed to configure rigid body world: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("set_rigid_body_collision_shape", log_args=True)
async def set_rigid_body_collision_shape(
    object_name: str,
    shape_type: Union[CollisionShapeType, str],
    source_object: Optional[str] = None,
    use_deform: bool = False,
    use_mesh: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Set the collision shape for a rigid body.

    Args:
        object_name: Name of the object to set collision shape for
        shape_type: Type of collision shape (BOX, SPHERE, CAPSULE, etc.)
        source_object: Optional source object for MESH or CONVEX_HULL shapes
        use_deform: Use deformed mesh for collision (only for MESH/CONVEX_HULL)
        use_mesh: Use the actual mesh for collision (only for MESH type)
        **kwargs: Additional shape parameters
            - radius: For SPHERE, CAPSULE, CYLINDER, CONE (default: auto-calculated)
            - height: For CAPSULE, CYLINDER, CONE (default: auto-calculated)
            - margin: Collision margin (default: 0.04)
            - use_compound: Use compound collision shape (default: False)
            - use_scale: Apply object scale to collision shape (default: True)

    Returns:
        Dict containing operation status and collision shape details
    """
    radius = kwargs.get("radius", "AUTO")  # 'AUTO' will calculate from bounds
    height = kwargs.get("height", "AUTO")
    margin = kwargs.get("margin", 0.04)
    use_compound = kwargs.get("use_compound", False)
    use_scale = kwargs.get("use_scale", True)

    script = f"""
import mathutils

def set_collision_shape():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    if not obj.rigid_body:
        return {{'status': 'ERROR', 'error': 'Object does not have rigid body physics'}}
    
    # Get the shape type
    shape_type = '{shape_type}'.upper()
    
    # Set the collision shape
    if shape_type in ['MESH', 'CONVEX_HULL']:
        source_obj = None
        if '{source_object}':
            source_obj = bpy.data.objects.get('{source_object}')
            if not source_obj:
                return {{'status': 'ERROR', 'error': f'Source object {{source_object}} not found'}}
        
        if shape_type == 'MESH':
            if not source_obj and not obj.data:
                return {{'status': 'ERROR', 'error': 'No mesh data or source object provided'}}
            
            # Use source object or self
            mesh_obj = source_obj if source_obj else obj
            
            # Set collision shape to mesh
            obj.rigid_body.collision_shape = 'MESH'
            obj.rigid_body.mesh_source = 'DEFORM' if {str(use_deform).lower()} else 'BASE'
            obj.rigid_body.use_mesh = {str(use_mesh).lower()}
            
            # If using a source object, set up the collision mesh
            if source_obj:
                # Make sure the source object is not visible in renders
                source_obj.hide_render = True
                source_obj.hide_viewport = True
                
                # Set the source object as the collision mesh
                obj.rigid_body.collision_mesh = source_obj.data
        
        elif shape_type == 'CONVEX_HULL':
            if not source_obj and not obj.data:
                return {{'status': 'ERROR', 'error': 'No mesh data or source object provided'}}
            
            # Use source object or self
            mesh_obj = source_obj if source_obj else obj
            
            # Set collision shape to convex hull
            obj.rigid_body.collision_shape = 'CONVEX_HULL'
            obj.rigid_body.use_deform = {str(use_deform).lower()}
            
            # If using a source object, set it as the convex hull source
            if source_obj:
                source_obj.hide_render = True
                source_obj.hide_viewport = True
                obj.rigid_body.collision_mesh = source_obj.data
    
    else:  # Primitive shapes
        obj.rigid_body.collision_shape = shape_type
        
        # Set shape dimensions if provided
        if shape_type == 'SPHERE' and isinstance({radius}, (int, float)):
            # For sphere, we need to adjust the object scale
            if {radius} > 0:
                # Calculate the scale factor to match the desired radius
                bbox = [obj.dimensions.x, obj.dimensions.y, obj.dimensions.z]
                max_dim = max(bbox) if any(bbox) else 1.0
                scale_factor = {radius} / (max_dim / 2) if max_dim > 0 else 1.0
                obj.scale = (scale_factor, scale_factor, scale_factor)
        
        elif shape_type in ['CAPSULE', 'CYLINDER', 'CONE']:
            # For capsules, cylinders, and cones, we might need to adjust height/radius
            if isinstance({height}, (int, float)) and {height} > 0:
                # Adjust Z scale to match desired height
                bbox_z = obj.dimensions.z
                if bbox_z > 0:
                    z_scale = {height} / bbox_z
                    obj.scale.z = z_scale
            
            if isinstance({radius}, (int, float)) and {radius} > 0:
                # Adjust X and Y scale to match desired radius
                bbox_xy = max(obj.dimensions.x, obj.dimensions.y)
                if bbox_xy > 0:
                    xy_scale = {radius} / (bbox_xy / 2) if bbox_xy > 0 else 1.0
                    obj.scale.x = xy_scale
                    obj.scale.y = xy_scale
    
    # Set common properties
    obj.rigid_body.collision_margin = {margin}
    obj.rigid_body.use_compound = {str(use_compound).lower()}
    obj.rigid_body.use_deactivation = True
    
    # Apply scale if needed
    if {str(use_scale).lower()} and obj.rigid_body.collision_shape != 'MESH':
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(scale=True)
    
    return {{
        'status': 'SUCCESS',
        'object': obj.name,
        'collision_shape': shape_type,
        'source_object': '{source_object}' if '{source_object}' else None,
        'margin': {margin},
        'use_compound': {str(use_compound).lower()}
    }}

try:
    result = set_collision_shape()
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
        logger.error(f"Failed to set rigid body collision shape: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("create_particle_system", log_args=True)
async def create_particle_system(
    object_name: str,
    system_name: str = "ParticleSystem",
    particle_type: str = "EMITTER",
    count: int = 1000,
    frame_start: int = 1,
    frame_end: int = 50,
    lifetime: float = 50.0,
    emit_from: str = "FACE",
    physics_type: str = "NEWTONIAN",
    **kwargs: Any,
) -> Dict[str, Any]:
    """Create and configure a particle system on an object.

    Args:
        object_name: Name of the object to add the particle system to
        system_name: Name for the particle system
        particle_type: Type of particle system ('EMITTER', 'HAIR', 'KEYED')
        count: Number of particles to emit
        frame_start: Frame to start emitting particles
        frame_end: Frame to stop emitting particles
        lifetime: Lifetime of particles in frames
        emit_from: Where to emit particles from ('VERT', 'FACE', 'VOLUME')
        physics_type: Physics type ('NEWTONIAN', 'KEYED', 'BOIDS', 'FLUID')
        **kwargs: Additional particle system settings
            - use_emit_random: Randomize emission (default: True)
            - use_even_distribution: Distribute emission evenly (default: True)
            - use_modifier_stack: Use modifier stack (default: True)
            - normal_factor: Emission normal factor (default: 0.0)
            - size: Particle size (default: 0.05)
            - size_random: Randomize particle size (0.0-1.0, default: 0.0)
            - mass: Particle mass (default: 1.0)
            - use_multiply_size_mass: Scale mass with size (default: False)
            - use_rotations: Enable particle rotations (default: False)
            - rotation_factor: Rotation amount (0.0-1.0, default: 0.0)
            - phase_factor: Phase factor (0.0-1.0, default: 0.0)
            - use_dynamic_rotation: Dynamic rotation (default: False)
            - angular_velocity_mode: Angular velocity mode ('NONE', 'VELOCITY', 'HORIZONTAL', 'VERTICAL')
            - angular_velocity_factor: Angular velocity factor (default: 0.0)

    Returns:
        Dict containing operation status and particle system details
    """
    # Get kwargs with defaults
    use_emit_random = kwargs.get("use_emit_random", True)
    use_even_distribution = kwargs.get("use_even_distribution", True)
    use_modifier_stack = kwargs.get("use_modifier_stack", True)
    normal_factor = kwargs.get("normal_factor", 0.0)
    size = kwargs.get("size", 0.05)
    size_random = kwargs.get("size_random", 0.0)
    mass = kwargs.get("mass", 1.0)
    use_multiply_size_mass = kwargs.get("use_multiply_size_mass", False)
    use_rotations = kwargs.get("use_rotations", False)
    rotation_factor = kwargs.get("rotation_factor", 0.0)
    phase_factor = kwargs.get("phase_factor", 0.0)
    use_dynamic_rotation = kwargs.get("use_dynamic_rotation", False)
    angular_velocity_mode = kwargs.get("angular_velocity_mode", "NONE")
    angular_velocity_factor = kwargs.get("angular_velocity_factor", 0.0)

    script = f"""

def create_particles():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    # Add a new particle system
    if obj.particle_systems:
        # If object already has particle systems, add a new one
        bpy.ops.object.particle_system_add()
    else:
        # Otherwise, add a new particle system with the settings
        bpy.ops.object.particle_system_add()
    
    # Get the particle system and its settings
    particle_system = obj.particle_systems.active
    settings = particle_system.settings
    
    # Basic settings
    settings.name = '{system_name}'
    settings.type = '{particle_type}'
    settings.count = {count}
    settings.frame_start = {frame_start}
    settings.frame_end = {frame_end}
    settings.lifetime = {lifetime}
    settings.emit_from = '{emit_from}'
    settings.physics_type = '{physics_type}'
    
    # Emission settings
    settings.use_emit_random = {str(use_emit_random).lower()}
    settings.use_even_distribution = {str(use_even_distribution).lower()}
    settings.use_modifier_stack = {str(use_modifier_stack).lower()}
    settings.normal_factor = {normal_factor}
    
    # Render settings
    settings.render_type = 'HALO'  # Default, can be overridden by kwargs
    settings.particle_size = {size}
    settings.size_random = {size_random}
    
    # Physics settings
    settings.mass = {mass}
    settings.use_multiply_size_mass = {str(use_multiply_size_mass).lower()}
    
    # Rotation settings
    settings.use_rotations = {str(use_rotations).lower()}
    if {str(use_rotations).lower()}:
        settings.rotation_factor = {rotation_factor}
        settings.phase_factor = {phase_factor}
        settings.use_dynamic_rotation = {str(use_dynamic_rotation).lower()}
        settings.angular_velocity_mode = '{angular_velocity_mode}'
        settings.angular_velocity_factor = {angular_velocity_factor}
    
    # Apply additional settings from kwargs
    for key, value in {kwargs}.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    # Update the viewport
    bpy.context.view_layer.update()
    
    return {{
        'status': 'SUCCESS',
        'object': obj.name,
        'particle_system': particle_system.name,
        'settings': settings.name,
        'particle_count': {count},
        'frame_range': ({frame_start}, {frame_end}),
        'lifetime': {lifetime}
    }}

try:
    result = create_particles()
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
        logger.error(f"Failed to configure particle physics: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("control_particle_emission", log_args=True)
async def control_particle_emission(
    object_name: str, system_name: str = "ParticleSystem", action: str = "PAUSE", **kwargs: Any
) -> Dict[str, Any]:
    """Control particle emission and caching.

    Args:
        object_name: Name of the object with the particle system
        system_name: Name of the particle system to control
        action: Action to perform ('PLAY', 'PAUSE', 'RESTART', 'FREE_CACHE', 'BAKE')
        **kwargs: Additional parameters
            - frame_start: Start frame for baking (default: 1)
            - frame_end: End frame for baking (default: 250)
            - clear_bake: Clear existing bake before baking (default: True)
            - use_disk_cache: Use disk cache (default: False)
            - cache_directory: Directory for disk cache
            - use_render_emitter: Show emitter in renders (default: True)
            - use_emit_random: Randomize emission (default: True)
            - use_even_distribution: Distribute emission evenly (default: True)
            - use_rotations: Enable particle rotations (default: False)
            - use_dynamic_rotation: Dynamic rotation (default: False)

    Returns:
        Dict containing operation status and control details
    """
    frame_start = kwargs.get("frame_start", 1)
    frame_end = kwargs.get("frame_end", 250)
    clear_bake = kwargs.get("clear_bake", True)
    use_disk_cache = kwargs.get("use_disk_cache", False)
    cache_directory = kwargs.get("cache_directory", "")
    use_render_emitter = kwargs.get("use_render_emitter", True)
    use_emit_random = kwargs.get("use_emit_random", True)
    use_even_distribution = kwargs.get("use_even_distribution", True)
    use_rotations = kwargs.get("use_rotations", False)
    use_dynamic_rotation = kwargs.get("use_dynamic_rotation", False)

    script = f"""

def control_emission():
    obj = bpy.data.objects.get('{object_name}')
    if not obj:
        return {{'status': 'ERROR', 'error': 'Object not found'}}
    
    # Find the particle system
    particle_system = None
    for ps in obj.particle_systems:
        if ps.name == '{system_name}':
            particle_system = ps
            break
    
    if not particle_system:
        return {{'status': 'ERROR', 'error': f'Particle system {{system_name}} not found'}}
    
    settings = particle_system.settings
    action = '{action}'.upper()
    
    # Apply settings
    settings.use_render_emitter = {str(use_render_emitter).lower()}
    settings.use_emit_random = {str(use_emit_random).lower()}
    settings.use_even_distribution = {str(use_even_distribution).lower()}
    settings.use_rotations = {str(use_rotations).lower()}
    settings.use_dynamic_rotation = {str(use_dynamic_rotation).lower()}
    
    # Handle disk cache
    if {str(use_disk_cache).lower()} and '{cache_directory}':
        settings.use_disk_cache = True
        settings.disk_cache_dir = '{cache_directory}'
    
    # Execute action
    result = {{'status': 'SUCCESS', 'action': action, 'system': particle_system.name}}
    
    if action == 'PLAY':
        particle_system.point_cache.is_baked = True
        particle_system.point_cache.frame_start = {frame_start}
        particle_system.point_cache.frame_end = {frame_end}
        bpy.ops.ptcache.free_bake({"point_cache": particle_system.point_cache})
        bpy.ops.ptcache.bake({"point_cache": particle_system.point_cache}, bake=True)
        result['message'] = 'Particle system playing'
    
    elif action == 'PAUSE':
        if particle_system.point_cache.is_baked:
            bpy.ops.ptcache.free_bake({{"point_cache": particle_system.point_cache}})
        result['message'] = 'Particle system paused'
    
    elif action == 'RESTART':
        bpy.ops.ptcache.free_bake({{"point_cache": particle_system.point_cache}})
        particle_system.point_cache.is_baked = False
        result['message'] = 'Particle system restarted'
    
    elif action == 'FREE_CACHE':
        bpy.ops.ptcache.free_bake({{"point_cache": particle_system.point_cache}})
        particle_system.point_cache.is_baked = False
        result['message'] = 'Particle cache cleared'
    
    elif action == 'BAKE':
        if {str(clear_bake).lower()}:
            bpy.ops.ptcache.free_bake({{"point_cache": particle_system.point_cache}})
        
        particle_system.point_cache.frame_start = {frame_start}
        particle_system.point_cache.frame_end = {frame_end}
        
        # Bake the simulation
        bpy.ops.ptcache.bake({{"point_cache": particle_system.point_cache}}, bake=True)
        
        result.update({{
            'baked': particle_system.point_cache.is_baked,
            'frame_range': ({frame_start}, {frame_end}),
            'use_disk_cache': {str(use_disk_cache).lower()},
            'cache_directory': '{cache_directory}'
        }})
    
    else:
        return {{'status': 'ERROR', 'error': f'Unknown action: {{action}}'}}
    
    # Update the viewport
    bpy.context.view_layer.update()
    return result

try:
    result = control_emission()
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
        logger.error(f"Failed to control particle emission: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

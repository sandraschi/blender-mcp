"""
Enhanced Physics Tools for Blender MCP.

This module provides physics tools with comprehensive error handling and validation.
"""
from typing import Dict, Any, List, Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
from ..compat import JSONType
# Temporarily commented out until handler functions are implemented
# from blender_mcp.handlers.physics_handler import (
#     enable_physics,
#     bake_physics_simulation,
#     add_force_field,
#     configure_cloth_simulation,
#     add_rigid_body_constraint
# )
from blender_mcp.tools import register_tool
from blender_mcp.utils.error_handling import handle_errors, validate_with, BlenderOperationError
# from blender_mcp.utils.validation import (
#     validate_object_exists, 
#     validate_vertex_group,
#     validate_frame_range,
#     validate_positive,
#     validate_range,
#     BaseValidator,
#     ObjectValidator,
#     FrameRangeValidator
# )

# Enums for physics types
class PhysicsType(str, Enum):
    RIGID_BODY = "RIGID_BODY"
    CLOTH = "CLOTH"
    SOFT_BODY = "SOFT_BODY"
    FLUID = "FLUID"
    SMOKE = "SMOKE"
    DYNAMIC_PAINT = "DYNAMIC_PAINT"

class RigidBodyType(str, Enum):
    ACTIVE = "ACTIVE"
    PASSIVE = "PASSIVE"

class CollisionShapeType(str, Enum):
    BOX = "BOX"
    SPHERE = "SPHERE"
    CAPSULE = "CAPSULE"
    CYLINDER = "CYLINDER"
    CONE = "CONE"
    CONVEX_HULL = "CONVEX_HULL"
    MESH = "MESH"
    COMPOUND = "COMPOUND"

# Parameter Models
class EnablePhysicsParams(BaseValidator, ObjectValidator):
    """Parameters for enabling physics on an object."""
    physics_type: PhysicsType = Field(..., description="Type of physics to enable")
    rigid_body_type: RigidBodyType = Field(RigidBodyType.ACTIVE, description="Type of rigid body")
    mass: float = Field(1.0, gt=0, description="Mass of the object in kg")
    friction: float = Field(0.5, ge=0, le=1, description="Friction coefficient (0-1)")
    bounciness: float = Field(0.3, ge=0, le=1, description="Bounciness (0-1)")
    collision_shape: CollisionShapeType = Field(
        CollisionShapeType.CONVEX_HULL, 
        description="Shape for collision detection"
    )
    use_margin: bool = Field(True, description="Use collision margin")
    collision_margin: float = Field(0.04, ge=0, description="Collision margin")
    damping_linear: float = Field(0.1, ge=0, le=1, description="Linear damping (0-1)")
    damping_angular: float = Field(0.1, ge=0, le=1, description="Angular damping (0-1)")
    
    @validator('collision_margin')
    def validate_margin(cls, v, values):
        if v < 0:
            raise ValueError("Collision margin cannot be negative")
        return v

class BakePhysicsParams(FrameRangeValidator):
    """Parameters for baking physics simulation."""
    object_names: List[str] = Field(
        default_factory=list,
        description="List of object names to bake (empty for all)"
    )
    step: int = Field(1, ge=1, description="Frame step (1=every frame)")
    only_selected: bool = Field(False, description="Only bake selected objects")
    clear_cached: bool = Field(True, description="Clear cached simulation data")
    
    @validator('object_names', each_item=True)
    def validate_objects(cls, v):
        if v:  # Only validate if list is not empty
            validate_object_exists(v)
        return v

class AddForceFieldParams(BaseValidator):
    """Parameters for adding a force field."""
    object_name: str = Field(..., description="Name of the object to add force field to")
    field_type: str = Field(..., description="Type of force field")
    strength: float = Field(1.0, description="Strength of the force field")
    flow: float = Field(0.0, description="Flow amount")
    use_max_distance: bool = Field(False, description="Use maximum distance")
    distance_max: float = Field(10.0, ge=0, description="Maximum distance of effect")
    
    @validator('object_name')
    def validate_object(cls, v):
        validate_object_exists(v)
        return v

class ClothSimulationParams(BaseValidator, ObjectValidator):
    """Parameters for configuring cloth simulation."""
    quality: int = Field(5, ge=1, le=10, description="Simulation quality (1-10)")
    mass: float = Field(0.3, gt=0, description="Mass of the cloth")
    tension_stiffness: float = Field(15.0, ge=0, le=100, description="Tension stiffness")
    compression_stiffness: float = Field(15.0, ge=0, le=100, description="Compression stiffness")
    pin_group: str = Field("", description="Vertex group for pinned vertices")
    
    @validator('pin_group')
    def validate_pin_group(cls, v, values):
        if v:  # Only validate if pin_group is provided
            validate_vertex_group(values['object_name'], v)
        return v

# Tool Definitions
@register_tool(
    name="enable_physics",
    description="Enable physics simulation for an object",
    parameters=EnablePhysicsParams.schema()
)
@handle_errors
@validate_with(EnablePhysicsParams)
async def enable_physics_tool(params: Dict[str, Any]) -> JSONType:
    """Enable physics simulation for an object.
    
    Args:
        params: Validated parameters from EnablePhysicsParams
        
    Returns:
        Dict containing the operation status and result
    """
    result = await enable_physics(
        object_name=params['object_name'],
        physics_type=params['physics_type'],
        rigid_body_type=params['rigid_body_type'],
        mass=params['mass'],
        friction=params['friction'],
        bounciness=params['bounciness'],
        collision_shape=params['collision_shape'],
        use_margin=params['use_margin'],
        collision_margin=params['collision_margin']
    )
    
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="bake_physics_simulation",
    description="Bake physics simulation to keyframes",
    parameters=BakePhysicsParams.schema()
)
@handle_errors
@validate_with(BakePhysicsParams)
async def bake_physics_simulation_tool(params: Dict[str, Any]) -> JSONType:
    """Bake physics simulation to keyframes.
    
    Args:
        params: Validated parameters from BakePhysicsParams
        
    Returns:
        Dict containing the operation status and result
    """
    result = await bake_physics_simulation(
        frame_start=params['frame_start'],
        frame_end=params['frame_end'],
        step=params['step'],
        object_names=params['object_names'] or None,  # Convert empty list to None
        only_selected=params['only_selected'],
        clear_cached=params['clear_cached']
    )
    
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="configure_cloth_simulation",
    description="Configure cloth simulation settings",
    parameters=ClothSimulationParams.schema()
)
@handle_errors
@validate_with(ClothSimulationParams)
async def configure_cloth_simulation_tool(params: Dict[str, Any]) -> JSONType:
    """Configure cloth simulation settings.
    
    Args:
        params: Validated parameters from ClothSimulationParams
        
    Returns:
        Dict containing the operation status and result
    """
    result = await configure_cloth_simulation(
        object_name=params['object_name'],
        quality=params['quality'],
        mass=params['mass'],
        tension_stiffness=params['tension_stiffness'],
        compression_stiffness=params['compression_stiffness'],
        pin_group=params['pin_group'] or None
    )
    
    return {"status": "SUCCESS", "result": result}

# Register all tools
def register() -> None:
    """Register all physics tools."""
    # Tools are registered via decorators
    pass

# Auto-register tools when module is imported
register()

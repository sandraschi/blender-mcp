"""
MCP Tools for physics operations.

This module exposes physics functionality through MCP tools.
"""
from typing import Dict, Any, Optional, List, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field
from fastmcp.types import JSONType

from blender_mcp.handlers.physics_handler import (
    enable_physics,
    bake_physics_simulation,
    add_force_field,
    configure_cloth_simulation,
    add_rigid_body_constraint,
    configure_rigid_body_world
)
from blender_mcp.tools import register_tool

# Enums
class PhysicsType(str, Enum):
    RIGID_BODY = "RIGID_BODY"
    CLOTH = "CLOTH"
    SOFT_BODY = "SOFT_BODY"
    FLUID = "FLUID"

class RigidBodyType(str, Enum):
    ACTIVE = "ACTIVE"
    PASSIVE = "PASSIVE"

class CollisionShapeType(str, Enum):
    BOX = "BOX"
    SPHERE = "SPHERE"
    CAPSULE = "CAPSULE"
    CONVEX_HULL = "CONVEX_HULL"
    MESH = "MESH"

# Parameter Models
class Vector3D(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

class EnablePhysicsParams(BaseModel):
    object_name: str = Field(..., description="Name of the object")
    physics_type: PhysicsType = Field(..., description="Type of physics to enable")
    rigid_body_type: RigidBodyType = Field(RigidBodyType.ACTIVE)
    mass: float = Field(1.0, gt=0)
    friction: float = Field(0.5, ge=0, le=1)
    bounciness: float = Field(0.5, ge=0, le=1)
    collision_shape: CollisionShapeType = Field(CollisionShapeType.CONVEX_HULL)

class BakePhysicsParams(BaseModel):
    frame_start: int = Field(1, ge=0)
    frame_end: int = Field(250, ge=1)
    step: int = Field(1, ge=1)
    only_selected: bool = False

# Tool Definitions
@register_tool(
    name="enable_physics",
    description="Enable physics simulation for an object",
    parameters=EnablePhysicsParams.schema()
)
async def enable_physics_tool(params: Dict[str, Any]) -> JSONType:
    try:
        p = EnablePhysicsParams(**params)
        result = await enable_physics(
            object_name=p.object_name,
            physics_type=p.physics_type.value,
            rigid_body_type=p.rigid_body_type.value if p.physics_type == PhysicsType.RIGID_BODY else None,
            mass=p.mass,
            friction=p.friction,
            bounciness=p.bounciness,
            collision_shape=p.collision_shape.value
        )
        return {"status": "SUCCESS", "result": result}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

@register_tool(
    name="bake_physics_simulation",
    description="Bake physics simulation to keyframes",
    parameters=BakePhysicsParams.schema()
)
async def bake_physics_simulation_tool(params: Dict[str, Any]) -> JSONType:
    try:
        p = BakePhysicsParams(**params)
        result = await bake_physics_simulation(
            frame_start=p.frame_start,
            frame_end=p.frame_end,
            step=p.step,
            only_selected=p.only_selected
        )
        return {"status": "SUCCESS", "result": result}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# Register all tools
def register() -> None:
    # Tools are registered via decorators
    pass

# Auto-register tools when module is imported
register()

"""
Advanced Physics Tools for Blender-MCP.

This module provides tools for advanced physics simulations including cloth, fluids, and particles.
"""
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
from pydantic import BaseModel, Field, validator, conlist, conint, confloat
from fastmcp.types import JSONType

from blender_mcp.handlers.physics_advanced_handler import (
    setup_cloth_simulation,
    setup_fluid_simulation,
    setup_particle_system,
    bake_physics_simulation,
    setup_rigid_body_constraint,
    setup_dynamic_paint
)
from blender_mcp.tools import register_tool, validate_with
from blender_mcp.utils.error_handling import handle_errors
from blender_mcp.utils.validation import BaseValidator, ObjectValidator

# Enums for physics types
class ClothQualityPreset(str, Enum):
    """Cloth quality presets."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class FluidDomainType(str, Enum):
    """Fluid domain types."""
    GAS = "GAS"
    LIQUID = "LIQUID"

class ParticleSystemType(str, Enum):
    """Particle system types."""
    EMITTER = "EMITTER"
    HAIR = "HAIR"
    FLUID = "FLUID"

class ConstraintType(str, Enum):
    """Physics constraint types."""
    FIXED = "FIXED"
    POINT = "POINT"
    HINGE = "HINGE"
    SLIDER = "SLIDER"

# Parameter Models
class ClothSimulationParams(BaseValidator, ObjectValidator):
    """Parameters for cloth simulation."""
    quality_preset: ClothQualityPreset = Field(ClothQualityPreset.MEDIUM)
    mass: float = Field(0.3, gt=0.0)
    bending_stiffness: float = Field(0.5, ge=0.0, le=1.0)
    use_collision: bool = Field(True)
    use_self_collision: bool = Field(True)

class FluidSimulationParams(BaseValidator, ObjectValidator):
    """Parameters for fluid simulation."""
    domain_type: FluidDomainType = Field(FluidDomainType.LIQUID)
    resolution: int = Field(64, ge=16, le=512)
    time_scale: float = Field(1.0, gt=0.0)
    viscosity: float = Field(0.0, ge=0.0)
    surface_tension: float = Field(0.0, ge=0.0)

class ParticleSystemParams(BaseValidator, ObjectValidator):
    """Parameters for particle system."""
    system_type: ParticleSystemType = Field(ParticleSystemType.EMITTER)
    count: int = Field(1000, ge=1)
    frame_start: int = Field(1)
    frame_end: int = Field(200)
    lifetime: float = Field(50.0, gt=0.0)

class RigidBodyConstraintParams(BaseValidator, ObjectValidator):
    """Parameters for rigid body constraints."""
    constraint_type: ConstraintType = Field(ConstraintType.FIXED)
    target_object: str = Field("")
    use_breaking: bool = Field(False)
    breaking_threshold: float = Field(100.0, ge=0.0)

class DynamicPaintParams(BaseValidator, ObjectValidator):
    """Parameters for dynamic paint."""
    surface_type: str = Field("PAINT")
    use_antialiasing: bool = Field(True)
    image_resolution: int = Field(512, ge=16, le=8192)
    frame_start: int = Field(1)
    frame_end: int = Field(250)

# Tool Definitions
@register_tool(
    name="setup_cloth_simulation",
    description="Set up a cloth simulation on an object"
)
@handle_errors
@validate_with(ClothSimulationParams)
async def setup_cloth_simulation_tool(params: Dict[str, Any]) -> JSONType:
    """Set up a cloth simulation on an object."""
    result = await setup_cloth_simulation(
        object_name=params["object_name"],
        quality_preset=params["quality_preset"].value,
        mass=params["mass"],
        bending_stiffness=params["bending_stiffness"],
        use_collision=params["use_collision"],
        use_self_collision=params["use_self_collision"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="setup_fluid_simulation",
    description="Set up a fluid simulation on an object"
)
@handle_errors
@validate_with(FluidSimulationParams)
async def setup_fluid_simulation_tool(params: Dict[str, Any]) -> JSONType:
    """Set up a fluid simulation on an object."""
    result = await setup_fluid_simulation(
        object_name=params["object_name"],
        domain_type=params["domain_type"].value,
        resolution=params["resolution"],
        time_scale=params["time_scale"],
        viscosity=params["viscosity"],
        surface_tension=params["surface_tension"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="setup_particle_system",
    description="Set up a particle system on an object"
)
@handle_errors
@validate_with(ParticleSystemParams)
async def setup_particle_system_tool(params: Dict[str, Any]) -> JSONType:
    """Set up a particle system on an object."""
    result = await setup_particle_system(
        object_name=params["object_name"],
        system_type=params["system_type"].value,
        count=params["count"],
        frame_start=params["frame_start"],
        frame_end=params["frame_end"],
        lifetime=params["lifetime"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="setup_rigid_body_constraint",
    description="Set up a rigid body constraint between objects"
)
@handle_errors
@validate_with(RigidBodyConstraintParams)
async def setup_rigid_body_constraint_tool(params: Dict[str, Any]) -> JSONType:
    """Set up a rigid body constraint between objects."""
    result = await setup_rigid_body_constraint(
        object_name=params["object_name"],
        constraint_type=params["constraint_type"].value,
        target_object=params["target_object"] or None,
        use_breaking=params["use_breaking"],
        breaking_threshold=params["breaking_threshold"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="setup_dynamic_paint",
    description="Set up dynamic paint on an object"
)
@handle_errors
@validate_with(DynamicPaintParams)
async def setup_dynamic_paint_tool(params: Dict[str, Any]) -> JSONType:
    """Set up dynamic paint on an object."""
    result = await setup_dynamic_paint(
        object_name=params["object_name"],
        surface_type=params["surface_type"],
        use_antialiasing=params["use_antialiasing"],
        image_resolution=params["image_resolution"],
        frame_start=params["frame_start"],
        frame_end=params["frame_end"]
    )
    return {"status": "SUCCESS", "result": result}

@register_tool(
    name="bake_physics_simulation",
    description="Bake a physics simulation"
)
@handle_errors
@validate_with(BaseValidator)
async def bake_physics_simulation_tool(params: Dict[str, Any]) -> JSONType:
    """Bake a physics simulation."""
    result = await bake_physics_simulation()
    return {"status": "SUCCESS", "result": result}

def register() -> None:
    """Register all physics tools."""
    # Tools are registered via decorators
    pass

# Auto-register tools when module is imported
register()

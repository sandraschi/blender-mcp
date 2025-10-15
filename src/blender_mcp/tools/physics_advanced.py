"""
Advanced Physics Tools for Blender-MCP.

This module provides tools for advanced physics simulations including cloth, fluids, and particles.
The actual tool functions are defined in the handlers and registered with @app.tool decorators.
This module provides parameter models and enums for documentation and validation purposes.
"""

from enum import Enum
from pydantic import BaseModel, Field

# Note: The actual tool functions are defined in the handlers and registered with @app.tool decorators.
# This module provides parameter models and enums for documentation and validation purposes.
# We don't import from handlers to avoid circular imports.


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


class PhysicsType(str, Enum):
    """Physics simulation types."""

    RIGID_BODY = "RIGID_BODY"
    SOFT_BODY = "SOFT_BODY"
    CLOTH = "CLOTH"
    FLUID = "FLUID"
    PARTICLE = "PARTICLE"


class CollisionShape(str, Enum):
    """Collision shape types."""

    CONVEX_HULL = "CONVEX_HULL"
    MESH = "MESH"
    SPHERE = "SPHERE"
    BOX = "BOX"
    CAPSULE = "CAPSULE"
    CYLINDER = "CYLINDER"
    CONE = "CONE"


class ForceFieldType(str, Enum):
    """Force field types."""

    FORCE = "FORCE"
    WIND = "WIND"
    VORTEX = "VORTEX"
    MAGNET = "MAGNET"
    HARMONIC = "HARMONIC"
    CHARGE = "CHARGE"
    LENNARD_JONES = "LENNARD_JONES"
    TEXTURE = "TEXTURE"
    CURVE_GUIDE = "CURVE_GUIDE"
    BOID = "BOID"
    TURBULENCE = "TURBULENCE"
    DRAG = "DRAG"
    FLUID_FLOW = "FLUID_FLOW"


# Parameter Models for validation and documentation
class ClothSimulationParams(BaseModel):
    """Parameters for cloth simulation."""

    object_name: str = Field(..., description="Name of the object to apply cloth simulation to")
    quality_preset: ClothQualityPreset = Field(
        ClothQualityPreset.MEDIUM, description="Quality preset"
    )
    mass: float = Field(1.0, gt=0.0, description="Cloth mass")
    structural_stiffness: float = Field(1.0, ge=0.0, le=1.0, description="Structural stiffness")
    bending_stiffness: float = Field(0.1, ge=0.0, le=1.0, description="Bending stiffness")
    shear_stiffness: float = Field(1.0, ge=0.0, le=1.0, description="Shear stiffness")
    damping: float = Field(0.1, ge=0.0, le=1.0, description="Damping factor")
    air_damping: float = Field(0.1, ge=0.0, le=1.0, description="Air damping")
    use_pin_cloth: bool = Field(False, description="Use pin cloth")
    pin_strength: float = Field(1.0, ge=0.0, le=1.0, description="Pin strength")
    use_collision: bool = Field(True, description="Use collision")
    collision_quality: int = Field(3, ge=1, le=5, description="Collision quality")
    use_self_collision: bool = Field(False, description="Use self collision")
    self_collision_distance: float = Field(0.01, gt=0.0, description="Self collision distance")


class FluidSimulationParams(BaseModel):
    """Parameters for fluid simulation."""

    object_name: str = Field(..., description="Name of the object to apply fluid simulation to")
    domain_type: FluidDomainType = Field(FluidDomainType.LIQUID, description="Domain type")
    resolution: int = Field(64, ge=8, le=256, description="Simulation resolution")
    time_scale: float = Field(1.0, gt=0.0, description="Time scale")
    viscosity: float = Field(0.1, ge=0.0, description="Viscosity")
    density: float = Field(1.0, gt=0.0, description="Density")
    use_surface_tension: bool = Field(False, description="Use surface tension")
    surface_tension: float = Field(0.0, ge=0.0, description="Surface tension")
    use_dissolve: bool = Field(False, description="Use dissolve")
    dissolve_speed: float = Field(1.0, gt=0.0, description="Dissolve speed")


class ParticleSystemParams(BaseModel):
    """Parameters for particle system."""

    object_name: str = Field(..., description="Name of the object to apply particle system to")
    system_type: ParticleSystemType = Field(ParticleSystemType.EMITTER, description="System type")
    count: int = Field(1000, gt=0, description="Number of particles")
    lifetime: float = Field(50.0, gt=0.0, description="Particle lifetime")
    emit_from: str = Field("FACE", description="Emit from (FACE, VERT, VOLUME)")
    distribution: str = Field("RANDOM", description="Distribution (RANDOM, EVEN, JITTERED)")
    use_emit_random: bool = Field(True, description="Use random emission")
    use_rotation: bool = Field(False, description="Use rotation")
    use_dynamic_rotation: bool = Field(False, description="Use dynamic rotation")
    use_angular_velocity: bool = Field(False, description="Use angular velocity")
    use_size: bool = Field(True, description="Use size")
    use_velocity: bool = Field(True, description="Use velocity")
    use_gravity: bool = Field(True, description="Use gravity")
    gravity_strength: float = Field(1.0, description="Gravity strength")


class RigidBodyConstraintParams(BaseModel):
    """Parameters for rigid body constraint."""

    object_a: str = Field(..., description="First object name")
    object_b: str = Field(..., description="Second object name")
    constraint_type: ConstraintType = Field(ConstraintType.FIXED, description="Constraint type")
    use_limit_lin_x: bool = Field(False, description="Use linear X limit")
    limit_lin_x_lower: float = Field(-1.0, description="Linear X lower limit")
    limit_lin_x_upper: float = Field(1.0, description="Linear X upper limit")
    use_limit_lin_y: bool = Field(False, description="Use linear Y limit")
    limit_lin_y_lower: float = Field(-1.0, description="Linear Y lower limit")
    limit_lin_y_upper: float = Field(1.0, description="Linear Y upper limit")
    use_limit_lin_z: bool = Field(False, description="Use linear Z limit")
    limit_lin_z_lower: float = Field(-1.0, description="Linear Z lower limit")
    limit_lin_z_upper: float = Field(1.0, description="Linear Z upper limit")
    use_limit_ang_x: bool = Field(False, description="Use angular X limit")
    limit_ang_x_lower: float = Field(-3.14159, description="Angular X lower limit")
    limit_ang_x_upper: float = Field(3.14159, description="Angular X upper limit")
    use_limit_ang_y: bool = Field(False, description="Use angular Y limit")
    limit_ang_y_lower: float = Field(-3.14159, description="Angular Y lower limit")
    limit_ang_y_upper: float = Field(3.14159, description="Angular Y upper limit")
    use_limit_ang_z: bool = Field(False, description="Use angular Z limit")
    limit_ang_z_lower: float = Field(-3.14159, description="Angular Z lower limit")
    limit_ang_z_upper: float = Field(3.14159, description="Angular Z upper limit")


class DynamicPaintParams(BaseModel):
    """Parameters for dynamic paint."""

    object_name: str = Field(..., description="Name of the object to apply dynamic paint to")
    canvas_type: str = Field("PAINT", description="Canvas type (PAINT, WEIGHT)")
    brush_type: str = Field("PAINT", description="Brush type (PAINT, ERASE, WEIGHT)")
    use_wet_paint: bool = Field(False, description="Use wet paint")
    wet_paint_speed: float = Field(1.0, gt=0.0, description="Wet paint speed")
    use_dry_paint: bool = Field(True, description="Use dry paint")
    dry_paint_speed: float = Field(1.0, gt=0.0, description="Dry paint speed")
    use_dissolve: bool = Field(False, description="Use dissolve")
    dissolve_speed: float = Field(1.0, gt=0.0, description="Dissolve speed")
    use_smudge: bool = Field(False, description="Use smudge")
    smudge_strength: float = Field(1.0, gt=0.0, description="Smudge strength")


class PhysicsBakeParams(BaseModel):
    """Parameters for physics baking."""

    object_name: str = Field(..., description="Name of the object to bake physics for")
    start_frame: int = Field(1, description="Start frame")
    end_frame: int = Field(250, description="End frame")
    step: int = Field(1, ge=1, description="Bake step")
    use_cache: bool = Field(True, description="Use cache")
    cache_type: str = Field("MODULAR", description="Cache type (MODULAR, REPLACE)")
    use_disk_cache: bool = Field(False, description="Use disk cache")
    disk_cache_dir: str = Field("", description="Disk cache directory")


# Tool Definitions
# Note: The actual tool functions are defined in the handlers and registered with @app.tool decorators.
# This module provides parameter models and enums for documentation and validation purposes.

# The following tools are available (registered in handlers):
# - enable_physics: Enable physics simulation for an object
# - bake_physics_simulation: Bake physics simulation to keyframes
# - add_force_field: Add a force field to the scene
# - configure_cloth_simulation: Configure cloth simulation settings
# - bake_cloth_simulation: Bake cloth simulation
# - add_rigid_body_constraint: Add rigid body constraint
# - configure_rigid_body_world: Configure rigid body world settings
# - set_rigid_body_collision_shape: Set rigid body collision shape
# - create_particle_system: Create a particle system
# - control_particle_emission: Control particle emission settings


def register() -> None:
    """Register all physics tools."""
    # Tools are already registered via @app.tool decorators in handlers
    pass


# Auto-register tools when module is imported
register()

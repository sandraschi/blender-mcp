"""
MCP Tools for physics operations.

This module exposes physics functionality through MCP tools.
"""
from typing import Dict, Any, Optional, List, Union
from fastmcp.tools import MCPTool
from blender_mcp.handlers.physics_handler import (
    enable_physics_type,
    bake_physics_simulation,
    add_force_field,
    create_rigid_body_constraint,
    configure_rigid_body_world,
    set_rigid_body_collision_shape,
    create_particle_system,
    configure_particle_physics,
    control_particle_emission
)
from blender_mcp.tools import register_tool

# Tool for enabling physics types
enable_physics_tool = MCPTool(
    name="enable_physics_type",
    description="Enable physics simulation for an object",
    parameters={
        "type": "object",
        "properties": {
            "object_name": {"type": "string", "description": "Name of the object"},
            "physics_type": {
                "type": "string",
                "enum": ["RIGID_BODY", "CLOTH", "SOFT_BODY", "FLUID", "PARTICLE"],
                "description": "Type of physics to enable"
            },
            "mass": {"type": "number", "default": 1.0, "description": "Mass of the object"},
            "friction": {"type": "number", "default": 0.5, "description": "Friction coefficient"},
            "bounce": {"type": "number", "default": 0.3, "description": "Bounciness"},
            "collision_shape": {
                "type": "string",
                "enum": ["CONVEX_HULL", "MESH", "BOX", "SPHERE", "CAPSULE", "CYLINDER"],
                "default": "CONVEX_HULL",
                "description": "Collision shape type"
            },
            "use_margin": {"type": "boolean", "default": True, "description": "Use collision margin"},
            "collision_margin": {"type": "number", "default": 0.04, "description": "Collision margin"}
        },
        "required": ["object_name", "physics_type"]
    },
    execute=enable_physics_type
)

# Tool for baking physics simulations
bake_physics_tool = MCPTool(
    name="bake_physics_simulation",
    description="Bake physics simulation for objects",
    parameters={
        "type": "object",
        "properties": {
            "object_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of object names to bake"
            },
            "frame_start": {"type": "integer", "default": 1, "description": "Start frame"},
            "frame_end": {"type": "integer", "default": 250, "description": "End frame"},
            "step": {"type": "integer", "default": 1, "description": "Frame step"},
            "bake_to_keyframes": {"type": "boolean", "default": True, "description": "Bake to keyframes"},
            "clear_constraints": {"type": "boolean", "default": False, "description": "Clear constraints after baking"}
        },
        "required": ["object_names"]
    },
    execute=bake_physics_simulation
)

# Tool for adding force fields
add_force_field_tool = MCPTool(
    name="add_force_field",
    description="Add a force field to an object",
    parameters={
        "type": "object",
        "properties": {
            "object_name": {"type": "string", "description": "Name of the object"},
            "field_type": {
                "type": "string",
                "enum": ["FORCE", "WIND", "VORTEX", "MAGNETIC", "HARMONIC", 
                         "CHARGE", "LENNARDJ", "TEXTURE", "GUIDE", "BOID", 
                         "TURBULENCE", "DRAG", "SMOKE_FLOW"],
                "description": "Type of force field"
            },
            "strength": {"type": "number", "default": 1.0, "description": "Strength of the force field"},
            "flow": {"type": "number", "default": 1.0, "description": "Flow amount"},
            "falloff_type": {
                "type": "string",
                "enum": ["NONE", "CURVE", "TEXTURE"],
                "default": "NONE",
                "description": "Falloff type"
            },
            "use_max_distance": {"type": "boolean", "default": False, "description": "Use maximum distance"},
            "distance_max": {"type": "number", "default": 10.0, "description": "Maximum distance"}
        },
        "required": ["object_name", "field_type"]
    },
    execute=add_force_field
)

# Tool for creating rigid body constraints
create_constraint_tool = MCPTool(
    name="create_rigid_body_constraint",
    description="Create a rigid body constraint between two objects",
    parameters={
        "type": "object",
        "properties": {
            "object_a": {"type": "string", "description": "Name of the first object"},
            "object_b": {"type": "string", "description": "Name of the second object"},
            "constraint_type": {
                "type": "string",
                "enum": ["FIXED", "POINT", "HINGE", "SLIDER", "PISTON", "GENERIC", "GENERIC_SPRING"],
                "description": "Type of constraint"
            },
            "use_limit_lin_x": {"type": "boolean", "default": False},
            "limit_lin_x_lower": {"type": "number", "default": -1.0},
            "limit_lin_x_upper": {"type": "number", "default": 1.0},
            "use_limit_ang_z": {"type": "boolean", "default": False},
            "limit_ang_z_lower": {"type": "number", "default": -0.5},
            "limit_ang_z_upper": {"type": "number", "default": 0.5}
        },
        "required": ["object_a", "object_b", "constraint_type"]
    },
    execute=create_rigid_body_constraint
)

# Tool for configuring rigid body world
configure_rigid_body_world_tool = MCPTool(
    name="configure_rigid_body_world",
    description="Configure rigid body world settings",
    parameters={
        "type": "object",
        "properties": {
            "gravity": {
                "type": "array",
                "items": {"type": "number"},
                "minItems": 3,
                "maxItems": 3,
                "default": [0.0, 0.0, -9.81],
                "description": "Gravity vector (x, y, z)"
            },
            "time_scale": {"type": "number", "default": 1.0, "description": "Time scale"},
            "solver_iterations": {"type": "integer", "default": 10, "description": "Solver iterations"},
            "use_split_impulse": {"type": "boolean", "default": True, "description": "Use split impulse"},
            "split_impulse_threshold": {"type": "number", "default": 0.01, "description": "Split impulse threshold"},
            "deactivation_linear_threshold": {"type": "number", "default": 0.1, "description": "Linear velocity threshold for deactivation"},
            "deactivation_angular_threshold": {"type": "number", "default": 1.0, "description": "Angular velocity threshold for deactivation"},
            "deactivation_time": {"type": "number", "default": 2.0, "description": "Time before deactivation"}
        }
    },
    execute=configure_rigid_body_world
)

# Tool for creating particle systems
create_particle_system_tool = MCPTool(
    name="create_particle_system",
    description="Create a particle system on an object",
    parameters={
        "type": "object",
        "properties": {
            "object_name": {"type": "string", "description": "Name of the object"},
            "system_name": {"type": "string", "default": "ParticleSystem", "description": "Name of the particle system"},
            "particle_type": {
                "type": "string",
                "enum": ["EMITTER", "HAIR", "KEYED"],
                "default": "EMITTER",
                "description": "Type of particle system"
            },
            "count": {"type": "integer", "default": 1000, "description": "Number of particles"},
            "lifetime": {"type": "number", "default": 50.0, "description": "Particle lifetime"},
            "size": {"type": "number", "default": 0.1, "description": "Particle size"},
            "mass": {"type": "number", "default": 1.0, "description": "Particle mass"},
            "use_emit_random": {"type": "boolean", "default": True, "description": "Randomize emission"},
            "normal_factor": {"type": "number", "default": 0.0, "description": "Normal emission factor"},
            "random_factor": {"type": "number", "default": 1.0, "description": "Random emission factor"},
            "use_rotation": {"type": "boolean", "default": False, "description": "Enable particle rotation"},
            "phase_factor": {"type": "number", "default": 1.0, "description": "Initial rotation phase factor"},
            "use_rotations": {"type": "boolean", "default": False, "description": "Enable dynamic rotations"},
            "angular_velocity_factor": {"type": "number", "default": 0.0, "description": "Angular velocity factor"}
        },
        "required": ["object_name"]
    },
    execute=create_particle_system
)

def register() -> None:
    """Register all physics tools."""
    register_tool(enable_physics_tool)
    register_tool(bake_physics_tool)
    register_tool(add_force_field_tool)
    register_tool(create_constraint_tool)
    register_tool(configure_rigid_body_world_tool)
    register_tool(create_particle_system_tool)

# Auto-register tools when module is imported
register()

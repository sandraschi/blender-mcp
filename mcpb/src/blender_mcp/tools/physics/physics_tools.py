"""
Physics tools for Blender MCP.

Provides tools for rigid body, cloth, soft body, and fluid simulations.
"""

from blender_mcp.compat import *

from blender_mcp.app import get_app


def _register_physics_tools():
    """Register all physics-related tools."""
    app = get_app()

    @app.tool
    async def blender_physics(
        operation: str = "enable_rigid_body",
        object_name: str = "",
        physics_type: str = "RIGID_BODY",
        rigid_body_type: str = "ACTIVE",
        mass: float = 1.0,
        friction: float = 0.5,
        bounciness: float = 0.0,
        collision_shape: str = "MESH",
        damping_linear: float = 0.04,
        damping_angular: float = 0.1,
    ) -> str:
        """
        Enable and configure physics simulations for objects.

        Supports multiple operations through the operation parameter:
        - enable_rigid_body: Add rigid body physics to object
        - enable_cloth: Add cloth simulation to object
        - enable_soft_body: Add soft body simulation to object
        - enable_fluid: Add fluid simulation to object
        - bake_physics: Bake physics simulation to keyframes
        - add_force_field: Add force field to scene
        - set_rigid_body_constraint: Add constraints between objects
        - configure_world: Set up physics world settings

        Args:
            operation: Physics operation type
            object_name: Name of object to apply physics to
            physics_type: Type of physics (RIGID_BODY, CLOTH, SOFT_BODY, FLUID)
            rigid_body_type: Rigid body type (ACTIVE, PASSIVE)
            mass: Object mass in kg
            friction: Friction coefficient (0-1)
            bounciness: Bounciness/restitution (0-1)
            collision_shape: Collision shape type (MESH, BOX, SPHERE, etc.)
            damping_linear: Linear damping
            damping_angular: Angular damping

        Returns:
            Success message with physics setup details
        """
        from blender_mcp.handlers.physics_handler import (
            enable_physics,
            bake_physics_simulation,
            add_force_field,
            configure_rigid_body_world,
            set_rigid_body_collision_shape,
            configure_cloth_simulation,
        )

        try:
            if operation == "enable_rigid_body":
                if not object_name:
                    return "object_name parameter required"
                return await enable_physics(
                    object_name=object_name,
                    physics_type="RIGID_BODY",
                    rigid_body_type=rigid_body_type,
                    mass=mass,
                    friction=friction,
                    bounciness=bounciness,
                    collision_shape=collision_shape,
                    damping_linear=damping_linear,
                    damping_angular=damping_angular,
                )

            elif operation == "enable_cloth":
                if not object_name:
                    return "object_name parameter required"
                cloth_settings = {
                    "tension_stiffness": 15.0,
                    "compression_stiffness": 15.0,
                    "shear_stiffness": 15.0,
                    "bending_stiffness": 0.5,
                    "use_pressure": False,
                    "uniform_pressure_force": 1000.0,
                }
                return await configure_cloth_simulation(object_name=object_name, **cloth_settings)

            elif operation == "enable_soft_body":
                if not object_name:
                    return "object_name parameter required"
                return await enable_physics(object_name=object_name, physics_type="SOFT_BODY")

            elif operation == "enable_fluid":
                if not object_name:
                    return "object_name parameter required"
                return await enable_physics(object_name=object_name, physics_type="FLUID")

            elif operation == "bake_physics":
                if not object_name:
                    return "object_name parameter required"
                start_frame = 1
                end_frame = 250
                return await bake_physics_simulation(
                    object_name=object_name, start_frame=start_frame, end_frame=end_frame
                )

            elif operation == "add_force_field":
                field_type = "FORCE"
                strength = 10.0
                location = (0, 0, 0)
                return await add_force_field(
                    field_type=field_type, strength=strength, location=location
                )

            elif operation == "set_rigid_body_constraint":
                if not object_name:
                    return "object_name parameter required"
                # Constraint setup requires manual configuration
                return "Rigid body constraints require manual setup - use add_rigid_body_constraint directly"

            elif operation == "configure_world":
                gravity = (0, 0, -9.81)
                return await configure_rigid_body_world(gravity=gravity)

            elif operation == "set_collision_shape":
                if not object_name:
                    return "object_name parameter required"
                return await set_rigid_body_collision_shape(
                    object_name=object_name, collision_shape=collision_shape
                )

            else:
                return f"Unknown physics operation: {operation}. Available: enable_rigid_body, enable_cloth, enable_soft_body, enable_fluid, bake_physics, add_force_field, set_rigid_body_constraint, configure_world, set_collision_shape"

        except Exception as e:
            return f"Error in physics operation '{operation}': {str(e)}"


_register_physics_tools()

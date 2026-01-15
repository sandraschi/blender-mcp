"""
Particle tools for Blender MCP.

Provides tools for creating particle systems and effects.
"""

from blender_mcp.compat import *

from blender_mcp.app import get_app


def _register_particle_tools():
    """Register all particle-related tools."""
    app = get_app()

    @app.tool
    async def blender_particles(
        operation: str = "create_particle_system",
        object_name: str = "",
        particle_count: int = 1000,
        lifetime: float = 50.0,
        start_frame: int = 1,
        end_frame: int = 250,
        emission_rate: int = 100,
        particle_size: float = 0.05,
    ) -> str:
        """
        Create and manage particle systems and effects.

        Supports multiple operations through the operation parameter:
        - create_particle_system: Create basic particle system
        - create_hair_particles: Create hair/fur particles
        - create_fire_effect: Create fire/smoke particles
        - create_water_effect: Create water/splash particles
        - control_emission: Control particle emission settings
        - bake_particles: Bake particle simulation
        - set_particle_physics: Configure particle physics

        Args:
            operation: Particle operation type
            object_name: Name of object to add particles to
            particle_count: Total number of particles
            lifetime: Lifetime of each particle in frames
            start_frame: Frame when emission starts
            end_frame: Frame when emission ends
            emission_rate: Particles emitted per frame
            particle_size: Size of individual particles

        Returns:
            Success message with particle system details
        """
        from blender_mcp.handlers.particle_handler import create_particle_system, bake_particles

        try:
            if operation == "create_particle_system":
                if not object_name:
                    return "object_name parameter required"
                return await create_particle_system(
                    object_name=object_name,
                    particle_count=particle_count,
                    lifetime=lifetime,
                    start_frame=start_frame,
                    end_frame=end_frame,
                )

            elif operation == "bake_particles":
                if not object_name:
                    return "object_name parameter required"
                return await bake_particles(
                    object_name=object_name, start_frame=start_frame, end_frame=end_frame
                )

            elif operation == "create_hair_particles":
                if not object_name:
                    return "object_name parameter required"
                # Hair particles require specific setup
                script = f"""
import bpy

# Find object
obj = bpy.data.objects.get('{object_name}')
if not obj:
    logger.error(f"❌ Object '{object_name}' not found for particle system")
else:
    # Create particle system
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.particle_system_add()
    psys = obj.particle_systems[-1]
    psys.name = 'Hair'

    # Configure for hair
    settings = psys.settings
    settings.type = 'HAIR'
    settings.count = {particle_count}
    settings.hair_length = 1.0
    settings.emit_from = 'FACE'
    settings.use_emit_random = False

    logger.info(f"✨ Created hair particle system for '{object_name}'")
"""
                from ..utils.blender_executor import get_blender_executor

                executor = get_blender_executor()
                await executor.execute_script(script)
                return f"Created hair particle system on '{object_name}'"

            elif operation == "create_fire_effect":
                if not object_name:
                    return "object_name parameter required"
                # Create fire/smoke domain
                script = f"""
import bpy

# Create smoke domain
bpy.ops.object.empty_add(location=(0, 0, 0))
domain = bpy.context.active_object
domain.name = 'SmokeDomain'

# Add smoke modifier
bpy.ops.object.modifier_add(type='SMOKE')
smoke_mod = domain.modifiers[-1]
smoke_mod.smoke_type = 'DOMAIN'

# Set domain size
domain.scale = (2.0, 2.0, 2.0)

# Create fire emitter
bpy.ops.mesh.primitive_cube_add(location=(0, 0, -0.5))
emitter = bpy.context.active_object
emitter.name = 'FireEmitter'
emitter.scale = (0.2, 0.2, 0.1)

# Add smoke modifier to emitter
bpy.ops.object.modifier_add(type='SMOKE')
smoke_mod = emitter.modifiers[-1]
smoke_mod.smoke_type = 'FLOW'
smoke_mod.flow_settings.smoke_color = (0.8, 0.4, 0.1)  # Orange fire color
smoke_mod.flow_settings.temperature = 1.0  # Hot fire

logger.info(f"🔥 Created fire particle effect for '{object_name}'")
"""
                from ..utils.blender_executor import get_blender_executor

                executor = get_blender_executor()
                await executor.execute_script(script)
                return "Created fire effect system"

            else:
                return f"Unknown particle operation: {operation}. Available: create_particle_system, create_hair_particles, create_fire_effect, bake_particles"

        except Exception as e:
            return f"Error in particle operation '{operation}': {str(e)}"


_register_particle_tools()

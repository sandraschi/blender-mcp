"""
Modifier tools for Blender MCP.

Provides tools for adding, managing, and applying mesh modifiers.
"""

from blender_mcp.compat import *

from blender_mcp.app import get_app


def _register_modifier_tools():
    """Register all modifier-related tools."""
    app = get_app()

    @app.tool
    async def blender_modifiers(
        operation: str = "add_subsurf",
        object_name: str = "",
        modifier_name: str = "",
        modifier_type: str = "SUBSURF",
        levels: int = 2,
        render_levels: int = 3,
        segments: int = 8,
        angle_limit: float = 30.0,
        width: float = 0.1,
        offset: float = 0.0,
        count: int = 2,
        merge_threshold: float = 0.001,
    ) -> str:
        """
        Apply and manage mesh modifiers in Blender.

        Supports multiple operations through the operation parameter:
        - add_subsurf: Add subdivision surface modifier
        - add_bevel: Add bevel modifier
        - add_mirror: Add mirror modifier
        - add_solidify: Add solidify modifier
        - add_array: Add array modifier
        - add_boolean: Add boolean modifier
        - add_decimate: Add decimation modifier
        - add_displace: Add displacement modifier
        - add_wave: Add wave modifier
        - remove_modifier: Remove a modifier
        - apply_modifier: Apply modifier to mesh
        - get_modifiers: List all modifiers on object

        Args:
            operation: Modifier operation type
            object_name: Name of object to modify
            modifier_name: Name of modifier to operate on
            modifier_type: Type of modifier to add
            levels: Subdivision levels (for subsurf)
            render_levels: Render subdivision levels
            segments: Number of segments (for bevel, screw)
            angle_limit: Angle limit in degrees (for edge split)
            width: Width/thickness (for solidify, bevel)
            offset: Offset distance (for solidify)
            count: Count/repetitions (for array)
            merge_threshold: Merge threshold (for mirror)
            target_object: Target object name (for boolean, shrinkwrap)

        Returns:
            Success message with modifier operation details
        """
        from blender_mcp.handlers.modifier_handler import (
            add_modifier,
            remove_modifier,
            get_modifiers,
            apply_modifier,
        )

        try:
            if operation.startswith("add_"):
                # Extract modifier type from operation (e.g., "add_subsurf" -> "SUBSURF")
                mod_type = operation.replace("add_", "").upper()

                # Build modifier properties based on operation
                mod_props = {}

                if mod_type == "SUBSURF":
                    mod_props.update({"levels": levels, "render_levels": render_levels})
                elif mod_type == "BEVEL":
                    mod_props.update({"segments": segments, "width": width})
                elif mod_type == "SOLIDIFY":
                    mod_props.update({"thickness": width, "offset": offset})
                elif mod_type == "ARRAY":
                    mod_props.update({"count": count})
                elif mod_type == "MIRROR":
                    mod_props.update({"merge_threshold": merge_threshold})
                elif mod_type == "BOOLEAN":
                    # Boolean modifier requires manual setup
                    return "Boolean modifier requires manual setup - use add_modifier directly"
                elif mod_type == "DECIMATE":
                    mod_props.update(
                        {
                            "ratio": 0.5  # Default decimation ratio
                        }
                    )

                if not modifier_name:
                    modifier_name = f"{mod_type.lower()}_mod"

                return await add_modifier(
                    object_name=object_name, modifier_type=mod_type, name=modifier_name, **mod_props
                )

            elif operation == "remove_modifier":
                if not modifier_name:
                    return "modifier_name parameter required"
                return await remove_modifier(object_name=object_name, modifier_name=modifier_name)

            elif operation == "apply_modifier":
                if not modifier_name:
                    return "modifier_name parameter required"
                return await apply_modifier(object_name=object_name, modifier_name=modifier_name)

            elif operation == "get_modifiers":
                return await get_modifiers(object_name=object_name)

            else:
                return f"Unknown modifier operation: {operation}. Available: add_[type], remove_modifier, apply_modifier, get_modifiers"

        except Exception as e:
            return f"Error in modifier operation '{operation}': {str(e)}"


_register_modifier_tools()

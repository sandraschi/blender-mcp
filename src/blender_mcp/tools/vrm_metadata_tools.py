"""
VRM Metadata tools for Blender MCP.

Provides tools for managing VRM-specific metadata including first person offset,
blink/viseme mappings, spring bone parameters, and VRM avatar configuration.
"""

from typing import Any, Dict, Literal, Optional

from loguru import logger


def get_app():
    from blender_mcp.app import app
    return app


def _register_vrm_metadata_tools():
    """Register VRM metadata tools with the app."""
    app = get_app()

    @app.tool
    async def blender_vrm_metadata(
        operation: Literal[
            "set_first_person_offset", "setup_blink_viseme_mappings",
            "configure_spring_bones", "set_vrm_look_at", "export_vrm_metadata"
        ] = "set_first_person_offset",
        # First person offset params
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        offset_z: float = 0.1,
        # Facial mappings params
        viseme_mappings: Optional[Dict[str, str]] = None,
        blink_shape_key: str = "blink",
        # Spring bones params
        spring_bone_settings: Optional[Dict[str, Any]] = None,
        # Look at params
        look_at_settings: Optional[Dict[str, Any]] = None,
        # Export params
        output_path: str = "//vrm_metadata.json",
        include_spring_bones: bool = True,
        include_look_at: bool = True,
        # Common params
        target_armature: Optional[str] = None,
        target_mesh: Optional[str] = None
    ) -> str:
        """
        Comprehensive VRM metadata management for avatar configuration.

        Handles all VRM-specific settings required for proper avatar functionality
        in VRChat, VRoid Studio, and other VRM-compatible platforms.

        Args:
            operation: VRM metadata operation type
            offset_x: First person X offset from head bone
            offset_y: First person Y offset from head bone
            offset_z: First person Z offset from head bone (typically 0.1-0.2)
            viseme_mappings: Custom viseme to shape key mappings
            blink_shape_key: Shape key name for blink animation
            spring_bone_settings: Spring bone physics configuration
            look_at_settings: Eye tracking look-at configuration
            output_path: Path for metadata export
            include_spring_bones: Include spring bone data in export
            include_look_at: Include look-at data in export
            target_armature: Specific armature to modify
            target_mesh: Specific mesh for facial operations

        Returns:
            Operation result with VRM metadata configuration details

        Examples:
            - blender_vrm_metadata("set_first_person_offset", offset_z=0.15) - Set first person view
            - blender_vrm_metadata("setup_blink_viseme_mappings") - Configure facial animations
            - blender_vrm_metadata("configure_spring_bones") - Setup hair/cloth physics
            - blender_vrm_metadata("export_vrm_metadata") - Export VRM settings
        """
        logger.info(
            f"blender_vrm_metadata called with operation='{operation}'"
        )

        from blender_mcp.handlers.vrm_metadata_handler import (
            configure_spring_bones,
            export_vrm_metadata,
            set_first_person_offset,
            set_vrm_look_at,
            setup_blink_viseme_mappings,
        )

        try:
            if operation == "set_first_person_offset":
                result = await set_first_person_offset(
                    offset_x=offset_x,
                    offset_y=offset_y,
                    offset_z=offset_z,
                    target_armature=target_armature
                )

            elif operation == "setup_blink_viseme_mappings":
                result = await setup_blink_viseme_mappings(
                    viseme_mappings=viseme_mappings,
                    blink_shape_key=blink_shape_key,
                    target_mesh=target_mesh
                )

            elif operation == "configure_spring_bones":
                result = await configure_spring_bones(
                    spring_bone_settings=spring_bone_settings,
                    target_armature=target_armature
                )

            elif operation == "set_vrm_look_at":
                result = await set_vrm_look_at(
                    look_at_settings=look_at_settings,
                    target_armature=target_armature
                )

            elif operation == "export_vrm_metadata":
                result = await export_vrm_metadata(
                    output_path=output_path,
                    target_armature=target_armature,
                    include_spring_bones=include_spring_bones,
                    include_look_at=include_look_at
                )

            else:
                return f"Unknown VRM metadata operation: {operation}"

            # Format the result
            return _format_vrm_metadata_result(result)

        except Exception as e:
            logger.error(f"VRM metadata operation '{operation}' failed: {e}")
            return f"VRM metadata operation failed: {str(e)}"


def _format_vrm_metadata_result(result: dict) -> str:
    """Format VRM metadata operation results into a readable report."""
    status = result.get("status", "unknown")
    operation = result.get("operation", "vrm_metadata")

    # Status indicator
    status_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    status_icon = status_icons.get(status, "❓")

    report = f"{status_icon} **VRM Metadata Operation Result**\n"
    report += "=" * 40 + "\n\n"

    # Status and key info
    report += f"**Status:** {status.upper()}\n"

    if "armature_name" in result:
        report += f"**Armature:** {result['armature_name']}\n"

    if "mesh_name" in result:
        report += f"**Mesh:** {result['mesh_name']}\n"

    if "metadata_file" in result:
        report += f"**Metadata File:** {result['metadata_file']}\n"

    # First person offset
    if "first_person_offset" in result:
        offset = result["first_person_offset"]
        report += f"**First Person Offset:** ({offset[0]:.3f}, {offset[1]:.3f}, {offset[2]:.3f})\n"

    # Viseme mappings
    if "viseme_mappings" in result:
        mappings = result["viseme_mappings"]
        report += "**Viseme Mappings:**\n"
        for sound, shape in mappings.items():
            report += f"  • {sound}: {shape}\n"

    if "blink_shape_key" in result:
        report += f"**Blink Shape Key:** {result['blink_shape_key']}\n"

    # Shape key status
    if "found_visemes" in result and result["found_visemes"]:
        report += f"**Found Visemes:** {', '.join(result['found_visemes'])}\n"

    if "missing_visemes" in result and result["missing_visemes"]:
        report += f"**Missing Visemes:** {', '.join(result['missing_visemes'])}\n"

    if "blink_available" in result:
        report += f"**Blink Available:** {'Yes' if result['blink_available'] else 'No'}\n"

    # Spring bone settings
    if "spring_bone_settings" in result:
        settings = result["spring_bone_settings"]
        report += "**Spring Bone Settings:**\n"
        for key, value in settings.items():
            if isinstance(value, list):
                value_str = f"({', '.join(f'{v:.3f}' for v in value)})"
            else:
                value_str = str(value)
            report += f"  • {key}: {value_str}\n"

    # Look at settings
    if "look_at_settings" in result:
        settings = result["look_at_settings"]
        report += f"**Look At Type:** {settings.get('type', 'unknown')}\n"

    # Warnings
    if "warnings" in result and result["warnings"]:
        report += "\n**Warnings:**\n"
        for warning in result["warnings"]:
            report += f"  • {warning}\n"

    # Message
    if "message" in result:
        report += f"\n{result['message']}\n"

    # Recommendations
    if status == "success":
        if operation == "setup_blink_viseme_mappings":
            if "missing_visemes" in result and result["missing_visemes"]:
                report += "\n💡 **Next Steps:**\n"
                report += "  • Create missing viseme shape keys using blender_shapekeys\n"
                report += "  • Test facial animations in pose mode\n"
        elif operation == "set_first_person_offset":
            report += "\n💡 **Next Steps:**\n"
            report += "  • Test first person view in VR preview\n"
            report += "  • Adjust offset if camera feels too close/far\n"
        elif operation == "configure_spring_bones":
            report += "\n💡 **Next Steps:**\n"
            report += "  • Test spring bone physics in animation\n"
            report += "  • Adjust stiffness/damping for natural movement\n"

    return report


# Register the tools when this module is imported
_register_vrm_metadata_tools()

"""
Export presets tools for Blender MCP.

Provides platform-specific export configurations for VR platforms including
VRChat, Resonite, and Unity with appropriate scale, format, and settings.
"""

from typing import Any, Dict, List, Literal, Optional

from loguru import logger


def get_app():
    from blender_mcp.app import app
    return app


def _register_export_presets_tools():
    """Register export presets tools with the app."""
    app = get_app()

    @app.tool
    async def blender_export_presets(
        operation: Literal[
            "export_with_preset", "validate_export_preset", "get_platform_presets",
            "create_custom_preset"
        ] = "export_with_preset",
        # Common params
        target_objects: Optional[List[str]] = None,
        platform: str = "VRCHAT",
        # Export params
        output_path: str = "//export",
        include_materials: bool = True,
        include_textures: bool = True,
        apply_modifiers: bool = True,
        # Validation params
        check_bones: bool = True,
        check_materials: bool = True,
        check_scale: bool = True,
        # Custom preset params
        preset_name: str = "",
        base_platform: str = "VRCHAT",
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Platform-specific export presets for VR avatar deployment.

        Handles the critical differences between VR platforms (scale, format, bone limits)
        ensuring your avatars work correctly in VRChat, Resonite, and Unity environments.

        Args:
            operation: Export preset operation type
            target_objects: List of object names to export/validate
            platform: Target VR platform ("VRCHAT", "RESONITE", "UNITY", etc.)
            output_path: Export output path (without extension)
            include_materials: Include materials in export
            include_textures: Include textures in export
            apply_modifiers: Apply modifiers before export
            check_bones: Validate bone count and naming in validation
            check_materials: Validate material compatibility in validation
            check_scale: Validate scale settings in validation
            preset_name: Name for custom preset creation
            base_platform: Platform to base custom preset on
            custom_settings: Custom settings for preset creation

        Returns:
            Export/validation operation result with platform-specific details

        Examples:
            - blender_export_presets("export_with_preset", target_objects=["Avatar"], platform="VRCHAT") - Export for VRChat
            - blender_export_presets("validate_export_preset", target_objects=["Avatar"], platform="RESONITE") - Validate for Resonite
            - blender_export_presets("get_platform_presets") - List available platforms
            - blender_export_presets("create_custom_preset", preset_name="MyCustom", base_platform="VRCHAT") - Create custom preset
        """
        logger.info(
            f"blender_export_presets called with operation='{operation}', platform='{platform}'"
        )

        from blender_mcp.handlers.export_presets_handler import (
            create_custom_preset,
            export_with_preset,
            get_platform_presets,
            validate_export_preset,
        )

        try:
            if operation == "export_with_preset":
                if not target_objects:
                    target_objects = []
                result = await export_with_preset(
                    target_objects=target_objects,
                    platform=platform,
                    output_path=output_path,
                    include_materials=include_materials,
                    include_textures=include_textures,
                    apply_modifiers=apply_modifiers
                )

            elif operation == "validate_export_preset":
                if not target_objects:
                    target_objects = []
                result = await validate_export_preset(
                    target_objects=target_objects,
                    platform=platform,
                    check_bones=check_bones,
                    check_materials=check_materials,
                    check_scale=check_scale
                )

            elif operation == "get_platform_presets":
                result = await get_platform_presets()

            elif operation == "create_custom_preset":
                if not preset_name:
                    return "preset_name parameter required for create_custom_preset"
                result = await create_custom_preset(
                    preset_name=preset_name,
                    base_platform=base_platform,
                    custom_settings=custom_settings
                )

            else:
                return f"Unknown export preset operation: {operation}"

            # Format the result
            return _format_export_presets_result(result)

        except Exception as e:
            logger.error(f"Export presets operation '{operation}' failed: {e}")
            return f"Export presets operation failed: {str(e)}"


def _format_export_presets_result(result: dict) -> str:
    """Format export presets operation results into a readable report."""
    status = result.get("status", "unknown")
    operation = result.get("operation", "export_presets")

    # Status indicator
    status_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "fail": "❌",
        "pass": "✅",
        "unknown": "❓"
    }
    status_icon = status_icons.get(status.lower(), "❓")

    report = f"{status_icon} **Export Presets Operation Result**\n"
    report += "=" * 40 + "\n\n"

    # Status and key info
    report += f"**Status:** {status.upper()}\n"

    if "platform" in result:
        report += f"**Platform:** {result['platform']}\n"

    if "preset_name" in result:
        report += f"**Preset Name:** {result['preset_name']}\n"

    if "base_platform" in result:
        report += f"**Base Platform:** {result['base_platform']}\n"

    # Export results
    if "output_path" in result:
        report += f"**Output Path:** {result['output_path']}\n"

    if "format" in result:
        report += f"**Format:** {result['format']}\n"

    if "scale" in result:
        report += f"**Scale:** {result['scale']}\n"

    if "objects_exported" in result:
        report += f"**Objects Exported:** {result['objects_exported']}\n"

    # Validation results
    if "validation_results" in result:
        validation = result["validation_results"]
        val_status = validation.get("status", "unknown")

        status_emojis = {
            "PASS": "✅",
            "WARNING": "⚠️",
            "FAIL": "❌",
            "ERROR": "💥"
        }
        val_icon = status_emojis.get(val_status, "❓")

        report += f"**Validation Status:** {val_icon} {val_status}\n"

        issues = validation.get("issues", [])
        warnings = validation.get("warnings", [])
        recommendations = validation.get("recommendations", [])

        if issues:
            report += "\n**Issues Found:**\n"
            for issue in issues:
                report += f"  • ❌ {issue}\n"

        if warnings:
            report += "\n**Warnings:**\n"
            for warning in warnings:
                report += f"  • ⚠️ {warning}\n"

        if recommendations:
            report += "\n**Recommendations:**\n"
            for rec in recommendations:
                report += f"  • 💡 {rec}\n"

    # Platform presets list
    if "presets" in result:
        presets = result["presets"]
        report += f"**Available Platforms:** {len(presets)}\n\n"

        for platform_name, preset in presets.items():
            report += f"**{platform_name}:**\n"
            report += f"  • Format: {preset.get('format', 'Unknown')}\n"
            report += f"  • Scale: {preset.get('scale', 'Unknown')}\n"
            report += f"  • Max Bones: {preset.get('max_bones', 'Unlimited')}\n"
            report += f"  • Description: {preset.get('description', 'N/A')}\n\n"

    # Custom preset
    if "custom_preset" in result:
        preset = result["custom_preset"]
        report += "**Custom Preset Created:**\n"
        for key, value in preset.items():
            if key != "description":
                report += f"  • {key}: {value}\n"

    # Warnings from export
    if "warnings" in result and result["warnings"]:
        report += "\n**Export Warnings:**\n"
        for warning in result["warnings"]:
            report += f"  • ⚠️ {warning}\n"

    # Message
    if "message" in result:
        report += f"\n{result['message']}\n"

    # Recommendations
    if status.lower() == "success":
        if operation == "export_with_preset":
            report += "\n💡 **Next Steps:**\n"
            report += "  • Test the exported file in the target platform\n"
            if result.get("platform") == "VRCHAT":
                report += "  • Upload to VRChat and check for bone limit warnings\n"
            elif result.get("platform") == "RESONITE":
                report += "  • Import into Resonite and verify scale/materials\n"
            report += "  • Run validation if issues occur\n"

        elif operation == "validate_export_preset":
            validation = result.get("validation_results", {})
            if validation.get("status") == "PASS":
                report += "\n✅ **Ready for Export:**\n"
                report += "  • All validation checks passed\n"
                report += "  • Safe to proceed with export\n"
            else:
                report += "\n⚠️ **Address Issues Before Export:**\n"
                report += "  • Fix critical issues before exporting\n"
                report += "  • Consider warnings for optimal performance\n"

        elif operation == "get_platform_presets":
            report += "\n💡 **Usage Tips:**\n"
            report += "  • VRCHAT: Use for Unity-based VR experiences\n"
            report += "  • RESONITE: Use for Resonite-specific content\n"
            report += "  • LEGACY_VRCHAT: Only for old workflows requiring 0.01 scale\n"
            report += "  • Always validate before final export\n"

    return report


# Register the tools when this module is imported
_register_export_presets_tools()

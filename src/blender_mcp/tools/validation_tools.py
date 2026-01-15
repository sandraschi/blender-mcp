"""
Validation tools for Blender MCP.

Provides comprehensive pre-flight checks for avatars and models
to ensure compatibility with VR platforms like VRChat and Resonite.
"""

from typing import Literal, Optional

from loguru import logger


def get_app():
    from blender_mcp.app import app
    return app


def _register_validation_tools():
    """Register validation tools with the app."""
    app = get_app()

    @app.tool
    async def blender_validation(
        operation: Literal[
            "validate_avatar", "validate_model", "check_polycount",
            "check_materials", "check_rigging", "check_transforms", "check_textures"
        ] = "validate_avatar",
        target_platform: str = "vrchat",
        check_materials: bool = True,
        check_rigging: bool = True,
        check_transforms: bool = True,
        check_textures: bool = True,
        polycount_limit: Optional[int] = None,
        material_limit: Optional[int] = None,
        bone_limit: Optional[int] = None,
    ) -> str:
        """
        Comprehensive validation tools for avatars and 3D models.

        Performs pre-flight checks to ensure models meet platform requirements
        for VRChat, Resonite, Unity, and other 3D platforms.

        Args:
            operation: Validation operation type
            target_platform: Target platform ("vrchat", "resonite", "unity", "generic")
            check_materials: Whether to validate materials and draw calls
            check_rigging: Whether to validate bone structure and rigging
            check_transforms: Whether to check for unapplied transforms
            check_textures: Whether to validate texture requirements
            polycount_limit: Custom polycount limit override
            material_limit: Custom material count limit override
            bone_limit: Custom bone count limit override

        Returns:
            Formatted validation report with status, issues, and recommendations

        Examples:
            - blender_validation() - Full VRChat avatar validation
            - blender_validation("check_polycount") - Just polycount check
            - blender_validation(target_platform="resonite") - Resonite validation
            - blender_validation(check_materials=False) - Skip material checks
        """
        logger.info(
            f"blender_validation called with operation='{operation}', platform='{target_platform}', "
            f"checks: materials={check_materials}, rigging={check_rigging}, "
            f"transforms={check_transforms}, textures={check_textures}"
        )

        from blender_mcp.handlers.validation_handler import (
            _validate_materials,
            _validate_polycount,
            _validate_rigging,
            _validate_textures,
            _validate_transforms,
            validate_avatar,
        )

        try:
            if operation == "validate_avatar":
                # Full avatar validation
                result = await validate_avatar(
                    target_platform=target_platform,
                    check_materials=check_materials,
                    check_rigging=check_rigging,
                    check_transforms=check_transforms,
                    check_textures=check_textures
                )

            elif operation == "validate_model":
                # Generic model validation
                result = await validate_avatar(
                    target_platform="generic",
                    check_materials=check_materials,
                    check_rigging=check_rigging,
                    check_transforms=check_transforms,
                    check_textures=check_textures
                )

            elif operation == "check_polycount":
                # Individual checks with custom limits
                limit = polycount_limit or 70000  # Default to VRChat PC limit
                result = _validate_polycount(limit)

            elif operation == "check_materials":
                limit = material_limit or 8  # Default material limit
                result = _validate_materials(limit)

            elif operation == "check_rigging":
                limit = bone_limit or 256  # Default bone limit
                result = _validate_rigging(limit)

            elif operation == "check_transforms":
                result = _validate_transforms()

            elif operation == "check_textures":
                result = _validate_textures()

            else:
                return f"Unknown validation operation: {operation}"

            # Format the result as a readable report
            return _format_validation_report(result)

        except Exception as e:
            logger.error(f"Validation operation '{operation}' failed: {e}")
            return f"Validation failed: {str(e)}"


def _format_validation_report(result: dict) -> str:
    """Format validation results into a readable report."""
    platform = result.get("platform", "Unknown")
    status = result.get("status", "UNKNOWN")
    issues = result.get("issues", [])
    stats = result.get("stats", {})
    recommendations = result.get("recommendations", [])

    # Status indicator
    status_icons = {
        "PASS": "✅",
        "WARNING": "⚠️",
        "CRITICAL": "🚨",
        "FAIL": "❌",
        "ERROR": "💥"
    }
    status_icon = status_icons.get(status, "❓")

    report = f"{status_icon} **{platform} Validation Report**\n"
    report += "=" * 50 + "\n\n"

    # Overall status
    report += f"**Status:** {status}\n\n"

    # Statistics
    if stats:
        report += "**Statistics:**\n"
        for key, value in stats.items():
            # Format large numbers with commas
            if isinstance(value, int) and value > 1000:
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
            report += f"  • {key}: {formatted_value}\n"
        report += "\n"

    # Issues
    if issues:
        report += "**Issues Found:**\n"
        for issue in issues:
            report += f"  • {issue}\n"
        report += "\n"

    # Recommendations
    if recommendations:
        report += "**Recommendations:**\n"
        for rec in recommendations:
            report += f"  • {rec}\n"
        report += "\n"

    # Status-specific guidance
    if status == "PASS":
        report += "🎉 **Ready for deployment!**\n"
        report += "Your model meets all requirements for the target platform.\n"
    elif status == "WARNING":
        report += "⚠️ **Review recommended**\n"
        report += "Your model has some issues that may affect performance or compatibility.\n"
    elif status in ["CRITICAL", "FAIL"]:
        report += "🚫 **Action required**\n"
        report += "Your model has critical issues that must be fixed before deployment.\n"
    elif status == "ERROR":
        report += "💥 **Validation failed**\n"
        report += "Unable to complete validation. Check the model and try again.\n"

    return report


# Register the tools when this module is imported
_register_validation_tools()

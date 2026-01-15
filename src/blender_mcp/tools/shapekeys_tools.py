"""
Shape keys tools for Blender MCP.

Provides tools for managing shape keys, visemes, and facial animation
for VRM avatars and character models.
"""

from typing import Dict, List, Literal, Optional

from loguru import logger


def get_app():
    from blender_mcp.app import app
    return app


def _register_shapekeys_tools():
    """Register shape keys tools with the app."""
    app = get_app()

    @app.tool
    async def blender_shapekeys(
        operation: Literal[
            "create_viseme_shapekeys", "create_blink_shapekey", "set_viseme_weights",
            "create_facial_expression", "analyze_shapekeys"
        ] = "create_viseme_shapekeys",
        # Common params
        target_mesh: Optional[str] = None,
        # Viseme creation params
        viseme_type: str = "vrm",
        auto_generate: bool = True,
        base_expression: Optional[str] = None,
        # Blink creation params
        blink_intensity: float = 1.0,
        eyelid_vertices: Optional[List[int]] = None,
        # Viseme weights params
        viseme_weights: Optional[Dict[str, float]] = None,
        frame: int = 1,
        # Facial expression params
        expression_name: str = "expression",
        base_visemes: Optional[Dict[str, float]] = None,
        blink_weight: float = 0.0,
        additional_modifiers: Optional[Dict[str, float]] = None,
        # Analysis params
        include_statistics: bool = True
    ) -> str:
        """
        Comprehensive shape key management for facial animation and VRM avatars.

        Handles viseme creation for lip sync, blink animations, facial expressions,
        and VRM compliance checking for VR platforms.

        Args:
            operation: Shape key operation type
            target_mesh: Target mesh object (defaults to active)
            viseme_type: Type of viseme system ("vrm", "standard", "custom")
            auto_generate: Whether to auto-generate basic viseme shapes
            base_expression: Base expression shape key to start from
            blink_intensity: How closed the eyes should be (0.0-1.0)
            eyelid_vertices: Specific vertex indices for eyelid control
            viseme_weights: Dictionary of viseme names to weights (0.0-1.0)
            frame: Animation frame to set weights at
            expression_name: Name for the facial expression
            base_visemes: Base viseme weights for expression
            blink_weight: Blink component weight for expression
            additional_modifiers: Additional shape key modifiers
            include_statistics: Include deformation statistics in analysis

        Returns:
            Shape key operation result with facial animation details

        Examples:
            - blender_shapekeys("create_viseme_shapekeys") - Create VRM visemes (A, I, U, E, O)
            - blender_shapekeys("create_blink_shapekey") - Create blink animation
            - blender_shapekeys("set_viseme_weights", viseme_weights={"A": 1.0}) - Set mouth to A shape
            - blender_shapekeys("create_facial_expression", expression_name="happy") - Create happy expression
            - blender_shapekeys("analyze_shapekeys") - Check VRM compliance
        """
        logger.info(
            f"blender_shapekeys called with operation='{operation}'"
        )

        from blender_mcp.handlers.shapekeys_handler import (
            analyze_shapekeys,
            create_blink_shapekey,
            create_facial_expression,
            create_viseme_shapekeys,
            set_viseme_weights,
        )

        try:
            if operation == "create_viseme_shapekeys":
                result = await create_viseme_shapekeys(
                    target_mesh=target_mesh,
                    viseme_type=viseme_type,
                    auto_generate=auto_generate,
                    base_expression=base_expression
                )

            elif operation == "create_blink_shapekey":
                result = await create_blink_shapekey(
                    target_mesh=target_mesh,
                    blink_intensity=blink_intensity,
                    eyelid_vertices=eyelid_vertices
                )

            elif operation == "set_viseme_weights":
                result = await set_viseme_weights(
                    target_mesh=target_mesh,
                    viseme_weights=viseme_weights,
                    frame=frame
                )

            elif operation == "create_facial_expression":
                result = await create_facial_expression(
                    target_mesh=target_mesh,
                    expression_name=expression_name,
                    base_visemes=base_visemes,
                    blink_weight=blink_weight,
                    additional_modifiers=additional_modifiers
                )

            elif operation == "analyze_shapekeys":
                result = await analyze_shapekeys(
                    target_mesh=target_mesh,
                    include_statistics=include_statistics
                )

            else:
                return f"Unknown shape keys operation: {operation}"

            # Format the result
            return _format_shapekeys_result(result)

        except Exception as e:
            logger.error(f"Shape keys operation '{operation}' failed: {e}")
            return f"Shape keys operation failed: {str(e)}"


def _format_shapekeys_result(result: dict) -> str:
    """Format shape keys operation results into a readable report."""
    status = result.get("status", "unknown")
    operation = result.get("operation", "shapekeys")

    # Status indicator
    status_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    status_icon = status_icons.get(status, "❓")

    report = f"{status_icon} **Shape Keys Operation Result**\n"
    report += "=" * 35 + "\n\n"

    # Status and key info
    report += f"**Status:** {status.upper()}\n"

    if "mesh_name" in result:
        report += f"**Mesh:** {result['mesh_name']}\n"

    if "expression_name" in result:
        report += f"**Expression:** {result['expression_name']}\n"

    if "frame" in result:
        report += f"**Frame:** {result['frame']}\n"

    # Shape key counts
    if "total_shape_keys" in result:
        report += f"**Total Shape Keys:** {result['total_shape_keys']}\n"

    # VRM Compliance
    if "vrm_compliance" in result:
        compliance = result["vrm_compliance"]
        report += "**VRM Compliance:**\n"
        report += f"  • Visemes Present: {compliance['visemes_present']}/5\n"
        report += f"  • Has Blink: {'Yes' if compliance['has_blink'] else 'No'}\n"
        score_percent = int(compliance['total_score'] * 100)
        report += f"  • Compliance Score: {score_percent}%\n"

    # Viseme status
    if "existing_visemes" in result and result["existing_visemes"]:
        report += f"**Existing Visemes:** {', '.join(result['existing_visemes'])}\n"

    if "missing_visemes" in result and result["missing_visemes"]:
        report += f"**Missing Visemes:** {', '.join(result['missing_visemes'])}\n"

    if "created_visemes" in result and result["created_visemes"]:
        report += f"**Created Visemes:** {', '.join(result['created_visemes'])}\n"

    # Blink status
    if "blink_created" in result:
        report += f"**Blink Created:** {'Yes' if result['blink_created'] else 'No'}\n"

    if "blink_exists" in result and result["blink_exists"]:
        report += f"**Blink Shape Key:** {result['blink_exists']}\n"

    if "blink_intensity" in result:
        report += f"**Blink Intensity:** {result['blink_intensity']:.1f}\n"

    # Applied weights
    if "applied_weights" in result and result["applied_weights"]:
        report += "**Applied Weights:**\n"
        for viseme, weight in result["applied_weights"].items():
            report += f"  • {viseme}: {weight:.2f}\n"

    # Expression components
    if "base_visemes" in result and result["base_visemes"]:
        non_zero = {k: v for k, v in result["base_visemes"].items() if v > 0}
        if non_zero:
            report += "**Base Visemes:**\n"
            for viseme, weight in non_zero.items():
                report += f"  • {viseme}: {weight:.2f}\n"

    if "blink_weight" in result and result["blink_weight"] > 0:
        report += f"**Blink Weight:** {result['blink_weight']:.2f}\n"

    if "additional_modifiers" in result and result["additional_modifiers"]:
        non_zero = {k: v for k, v in result["additional_modifiers"].items() if v > 0}
        if non_zero:
            report += "**Additional Modifiers:**\n"
            for mod, weight in non_zero.items():
                report += f"  • {mod}: {weight:.2f}\n"

    # Shape key info summary
    if "shape_key_info" in result and result["shape_key_info"]:
        info = result["shape_key_info"]
        report += f"**Shape Key Details:** {len(info)} keys\n"
        # Show first few keys
        for i, (name, details) in enumerate(info.items()):
            if i >= 3:  # Limit to first 3
                report += f"  • ... and {len(info) - 3} more\n"
                break
            report += f"  • {name}: value={details.get('value', 0):.2f}\n"

    # Message
    if "message" in result:
        report += f"\n{result['message']}\n"

    # Recommendations
    if status == "success":
        if "missing_visemes" in result and result["missing_visemes"]:
            report += "\n💡 **Next Steps:**\n"
            report += "  • Create missing viseme shape keys\n"
            report += "  • Sculpt mouth shapes for each viseme\n"
            report += "  • Test lip sync animation\n"
        elif operation == "create_blink_shapekey":
            report += "\n💡 **Next Steps:**\n"
            report += "  • Sculpt closed eye positions\n"
            report += "  • Add blink animation to timeline\n"
            report += "  • Test eye animation smoothness\n"
        elif operation == "set_viseme_weights":
            report += "\n💡 **Next Steps:**\n"
            report += "  • Preview animation at current frame\n"
            report += "  • Adjust weights for natural lip sync\n"
            report += "  • Add transition keyframes\n"
        elif operation == "analyze_shapekeys":
            compliance = result.get("vrm_compliance", {})
            score = compliance.get("total_score", 0)
            if score < 1.0:
                report += "\n💡 **Next Steps:**\n"
                if result.get("missing_visemes"):
                    report += "  • Create missing VRM visemes\n"
                if not result.get("has_blink"):
                    report += "  • Add blink shape key\n"
                report += "  • Validate with VRChat or Resonite\n"

    return report


# Register the tools when this module is imported
_register_shapekeys_tools()

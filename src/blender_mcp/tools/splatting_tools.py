"""
Gaussian Splatting tools for Blender MCP.

Provides tools for importing, processing, and managing Gaussian Splats
for hybrid environments combining real-world captures with 3D models.
"""

from typing import Literal, Optional, Tuple

from loguru import logger

from ..app import get_app


def _register_splatting_tools():
    """Register splatting tools with the app."""
    app = get_app()

    @app.tool
    async def blender_splatting(
        operation: Literal[
            "import_gs", "crop_and_clean", "generate_collision_mesh",
            "export_for_resonite", "create_proxy", "optimize_for_vr"
        ] = "import_gs",
        file_path: str = "",
        target_format: str = "ply",
        crop_type: str = "sphere",
        radius: float = 5.0,
        center_point: Optional[Tuple[float, float, float]] = None,
        invert_crop: bool = False,
        density_threshold: float = 0.1,
        decimation_ratio: float = 0.1,
        smoothing_iterations: int = 2,
        sh_degree: int = 3,
        setup_proxy: bool = True,
        include_collision: bool = True,
        optimize_for_mobile: bool = False,
    ) -> str:
        """
        Advanced Gaussian Splatting (3DGS) management for hybrid environments.

        Supports importing real-world captures, cleaning them up, and preparing
        them for VR platforms like Resonite for immersive experiences.

        Args:
            operation: Splatting operation type
            file_path: Path to .ply or .spz splat file (for import_gs)
            target_format: Export format ("ply" or "spz")
            crop_type: Crop volume type ("sphere", "box", "cylinder")
            radius: Radius/size of crop volume
            center_point: Center point for cropping
            invert_crop: Whether to invert crop selection
            density_threshold: Minimum density for collision mesh generation
            decimation_ratio: Mesh simplification ratio (0.1 = 10% of faces)
            smoothing_iterations: Laplacian smoothing passes
            sh_degree: Spherical harmonics degree (0-3)
            setup_proxy: Create performance proxy for large splats
            include_collision: Export collision mesh with splat
            optimize_for_mobile: Apply mobile VR optimizations

        Returns:
            Operation result with status and details

        Examples:
            - blender_splatting("import_gs", file_path="street_scan.ply") - Import splat
            - blender_splatting("crop_and_clean", radius=10.0) - Clean up splat
            - blender_splatting("generate_collision_mesh") - Create collision geometry
            - blender_splatting("export_for_resonite") - Export for Resonite
        """
        logger.info(
            f"blender_splatting called with operation='{operation}', file_path='{file_path}', "
            f"crop_type='{crop_type}', radius={radius}"
        )

        from blender_mcp.handlers.splatting_handler import (
            crop_splat,
            export_splat_for_resonite,
            generate_collision_mesh,
            import_gaussian_splat,
        )

        try:
            if operation == "import_gs":
                if not file_path:
                    return "Error: file_path required for import_gs operation"
                result = await import_gaussian_splat(
                    file_path=file_path,
                    sh_degree=sh_degree,
                    setup_proxy=setup_proxy
                )

            elif operation == "crop_and_clean":
                result = await crop_splat(
                    crop_type=crop_type,
                    radius=radius,
                    center_point=center_point,
                    invert=invert_crop
                )

            elif operation == "generate_collision_mesh":
                result = await generate_collision_mesh(
                    density_threshold=density_threshold,
                    decimation_ratio=decimation_ratio,
                    smoothing_iterations=smoothing_iterations
                )

            elif operation == "export_for_resonite":
                result = await export_splat_for_resonite(
                    target_format=target_format,
                    include_collision=include_collision,
                    optimize_for_mobile=optimize_for_mobile
                )

            elif operation == "create_proxy":
                # Create proxy for active splat
                result = await import_gaussian_splat("", setup_proxy=True)  # Just proxy creation

            elif operation == "optimize_for_vr":
                # Comprehensive VR optimization
                result = {
                    "status": "info",
                    "message": "VR optimization would include: proxy setup, LOD generation, compression, and mobile optimizations"
                }

            else:
                return f"Unknown splatting operation: {operation}"

            # Format the result
            return _format_splatting_result(result)

        except Exception as e:
            logger.error(f"Splatting operation '{operation}' failed: {e}")
            return f"Splatting operation failed: {str(e)}"


def _format_splatting_result(result: dict) -> str:
    """Format splatting operation results into a readable report."""
    status = result.get("status", "unknown")

    # Status indicator
    status_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    status_icon = status_icons.get(status, "❓")

    report = f"{status_icon} **Splatting Operation Result**\n"
    report += "=" * 40 + "\n\n"

    # Status and key info
    report += f"**Status:** {status.upper()}\n"

    if "object_name" in result:
        report += f"**Object:** {result['object_name']}\n"

    if "point_count" in result:
        report += f"**Points:** {result['point_count']:,}\n"

    if "file_path" in result:
        report += f"**File:** {result['file_path']}\n"

    if "output_path" in result:
        report += f"**Output:** {result['output_path']}\n"

    if "proxy_name" in result:
        report += f"**Proxy:** {result['proxy_name']}\n"

    # Statistics
    if "stats" in result and result["stats"]:
        report += "\n**Statistics:**\n"
        for key, value in result["stats"].items():
            if isinstance(value, int) and value > 1000:
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
            report += f"  • {key}: {formatted_value}\n"

    # Issues or messages
    if "issues" in result and result["issues"]:
        report += "\n**Issues:**\n"
        for issue in result["issues"]:
            report += f"  • {issue}\n"

    if "message" in result:
        report += f"\n{result['message']}\n"

    # Recommendations
    if status == "success":
        if "object_name" in result:
            report += "\n💡 **Next Steps:**\n"
            report += "  • Use crop_and_clean to remove unwanted geometry\n"
            report += "  • Generate collision mesh for VR physics\n"
            report += "  • Export for Resonite when ready\n"

    return report


# Register the tools when this module is imported
_register_splatting_tools()

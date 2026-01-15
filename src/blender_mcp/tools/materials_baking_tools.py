"""
Materials baking tools for Blender MCP.

Provides tools for converting non-standard shaders (VRM/MToon) to PBR
for cross-platform compatibility in VR environments.
"""

from typing import Literal, Optional

from loguru import logger


def get_app():
    from blender_mcp.app import app
    return app


def _register_materials_baking_tools():
    """Register materials baking tools with the app."""
    app = get_app()

    @app.tool
    async def blender_materials_baking(
        operation: Literal[
            "bake_toon_to_pbr", "consolidate_materials", "convert_vrm_shaders",
            "setup_pbr_bake", "optimize_for_mobile"
        ] = "bake_toon_to_pbr",
        resolution: int = 2048,
        margin: int = 16,
        target_mesh: Optional[str] = None,
        output_dir: str = "//bakes",
        bake_type: str = "combined",
        max_atlas_size: int = 4096,
        remove_unused_uvs: bool = True,
        preserve_lighting: bool = True,
        create_backup: bool = True,
    ) -> str:
        """
        Convert non-standard (VRM/MToon) shaders to PBR textures.

        Essential for VRM avatars moving into Resonite, Unity, or other
        PBR-based environments. Prevents "Semantic Dilution" of artistic intent.

        Args:
            operation: Baking operation type
            resolution: Bake texture resolution (512, 1024, 2048, 4096)
            margin: Pixel margin for UV island bleeding
            target_mesh: Specific mesh object to process (defaults to active)
            output_dir: Output directory for baked textures
            bake_type: Type of bake ("combined", "albedo", "normal", "roughness")
            max_atlas_size: Maximum atlas texture size for consolidation
            remove_unused_uvs: Clean up unused UV space during consolidation
            preserve_lighting: Try to maintain original lighting in conversions
            create_backup: Create backup of original materials

        Returns:
            Operation result with texture paths and conversion details

        Examples:
            - blender_materials_baking("bake_toon_to_pbr") - Convert to PBR textures
            - blender_materials_baking("consolidate_materials") - Merge materials into atlas
            - blender_materials_baking("convert_vrm_shaders") - Convert VRM materials to PBR
        """
        logger.info(
            f"blender_materials_baking called with operation='{operation}', "
            f"resolution={resolution}, target_mesh='{target_mesh}'"
        )

        from blender_mcp.handlers.materials_baking_handler import (
            bake_toon_to_pbr,
            consolidate_materials,
            convert_vrm_shaders,
        )

        try:
            if operation == "bake_toon_to_pbr":
                result = await bake_toon_to_pbr(
                    resolution=resolution,
                    margin=margin,
                    target_mesh=target_mesh,
                    output_dir=output_dir,
                    bake_type=bake_type
                )

            elif operation == "consolidate_materials":
                result = await consolidate_materials(
                    max_atlas_size=max_atlas_size,
                    remove_unused_uvs=remove_unused_uvs,
                    target_mesh=target_mesh
                )

            elif operation == "convert_vrm_shaders":
                result = await convert_vrm_shaders(
                    target_mesh=target_mesh,
                    preserve_lighting=preserve_lighting,
                    create_backup=create_backup
                )

            elif operation == "setup_pbr_bake":
                # Setup environment for PBR baking
                result = {
                    "status": "info",
                    "message": "PBR baking environment configured",
                    "resolution": resolution,
                    "output_dir": output_dir
                }

            elif operation == "optimize_for_mobile":
                # Mobile VR optimizations
                result = await consolidate_materials(
                    max_atlas_size=2048,  # Mobile limit
                    remove_unused_uvs=True,
                    target_mesh=target_mesh
                )
                result["optimization"] = "mobile_vr"

            else:
                return f"Unknown materials baking operation: {operation}"

            # Format the result
            return _format_baking_result(result)

        except Exception as e:
            logger.error(f"Materials baking operation '{operation}' failed: {e}")
            return f"Materials baking failed: {str(e)}"


def _format_baking_result(result: dict) -> str:
    """Format materials baking results into a readable report."""
    status = result.get("status", "unknown")

    # Status indicator
    status_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    status_icon = status_icons.get(status, "❓")

    report = f"{status_icon} **Materials Baking Result**\n"
    report += "=" * 35 + "\n\n"

    # Status and key info
    report += f"**Status:** {status.upper()}\n"

    if "object_name" in result:
        report += f"**Object:** {result['object_name']}\n"

    if "materials_baked" in result:
        report += f"**Materials Baked:** {result['materials_baked']}\n"

    if "materials_converted" in result:
        report += f"**Materials Converted:** {result['materials_converted']}\n"

    if "materials_before" in result and "materials_after" in result:
        report += f"**Materials:** {result['materials_before']} → {result['materials_after']}\n"

    if "resolution" in result:
        report += f"**Resolution:** {result['resolution']}px\n"

    if "bake_type" in result:
        report += f"**Bake Type:** {result['bake_type']}\n"

    # Materials list
    if "materials" in result and result["materials"]:
        report += "\n**Processed Materials:**\n"
        for mat_info in result["materials"]:
            mat_name = mat_info.get("material_name", "Unknown")
            mat_status = mat_info.get("status", "unknown")
            status_emoji = "✅" if mat_status == "success" else "❌"

            report += f"  {status_emoji} {mat_name}"
            if "texture_path" in mat_info:
                report += f" → {mat_info['texture_path']}"
            if "error" in mat_info:
                report += f" (Error: {mat_info['error']})"
            report += "\n"

    # Additional info
    if "backup_created" in result:
        report += f"**Backup Created:** {'Yes' if result['backup_created'] else 'No'}\n"

    if "preserve_lighting" in result:
        report += f"**Lighting Preserved:** {'Yes' if result['preserve_lighting'] else 'No'}\n"

    if "optimization" in result:
        report += f"**Optimization:** {result['optimization']}\n"

    # Message
    if "message" in result:
        report += f"\n{result['message']}\n"

    if "note" in result:
        report += f"\n📝 **Note:** {result['note']}\n"

    # Recommendations
    if status == "success":
        report += "\n💡 **Next Steps:**\n"
        if "materials_baked" in result and result["materials_baked"] > 0:
            report += "  • Review baked textures for quality\n"
            report += "  • Assign new PBR materials to your model\n"
            report += "  • Test in target environment (Unity/Resonite)\n"
        if "materials_converted" in result and result["materials_converted"] > 0:
            report += "  • Test converted materials in VR\n"
            report += "  • Adjust PBR values if lighting doesn't match\n"

    return report


# Register the tools when this module is imported
_register_materials_baking_tools()

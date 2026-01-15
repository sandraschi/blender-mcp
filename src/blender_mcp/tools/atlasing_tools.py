"""
Atlasing tools for Blender MCP.

Provides tools for material and texture atlasing to reduce draw calls
and optimize performance for VR platforms.
"""

from typing import Any, Dict, List, Literal, Optional

from loguru import logger


def get_app():
    from blender_mcp.app import app
    return app


def _register_atlasing_tools():
    """Register atlasing tools with the app."""
    app = get_app()

    @app.tool
    async def blender_atlasing(
        operation: Literal[
            "create_material_atlas", "merge_texture_atlas", "optimize_draw_calls",
            "get_atlas_uv_layout"
        ] = "create_material_atlas",
        # Material atlas params
        target_mesh: Optional[str] = None,
        atlas_size: int = 2048,
        padding: int = 4,
        output_path: str = "//material_atlas.png",
        combine_similar: bool = True,
        # Texture atlas params
        texture_paths: Optional[List[str]] = None,
        # Draw call optimization params
        max_materials: int = 4,
        combine_by_color: bool = True,
        preserve_normals: bool = True,
        # UV layout params
        atlas_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Advanced material and texture atlasing for VR performance optimization.

        Reduces draw calls by intelligently merging materials and textures into
        atlas layouts, critical for mobile VR performance on Quest and similar devices.

        Args:
            operation: Atlasing operation type
            target_mesh: Target mesh object (defaults to active)
            atlas_size: Size of atlas texture (512, 1024, 2048, 4096)
            padding: Padding between atlas regions in pixels
            output_path: Path for atlas texture output
            combine_similar: Merge materials with similar properties
            texture_paths: List of texture files for texture atlas
            max_materials: Maximum materials for draw call optimization
            combine_by_color: Merge materials with similar base colors
            preserve_normals: Maintain normal map assignments during optimization
            atlas_info: Pre-calculated atlas information for UV layout

        Returns:
            Atlasing operation result with performance optimization details

        Examples:
            - blender_atlasing("create_material_atlas") - Create material atlas for active mesh
            - blender_atlasing("optimize_draw_calls", max_materials=2) - Reduce to 2 materials max
            - blender_atlasing("get_atlas_uv_layout") - Get UV coordinates for atlas usage
            - blender_atlasing("merge_texture_atlas", texture_paths=["tex1.png", "tex2.png"]) - Merge textures
        """
        logger.info(
            f"blender_atlasing called with operation='{operation}', atlas_size={atlas_size}"
        )

        from blender_mcp.handlers.atlasing_handler import (
            create_material_atlas,
            get_atlas_uv_layout,
            merge_texture_atlas,
            optimize_draw_calls,
        )

        try:
            if operation == "create_material_atlas":
                result = await create_material_atlas(
                    target_mesh=target_mesh,
                    atlas_size=atlas_size,
                    padding=padding,
                    output_path=output_path,
                    combine_similar=combine_similar
                )

            elif operation == "merge_texture_atlas":
                if not texture_paths:
                    texture_paths = []
                result = await merge_texture_atlas(
                    texture_paths=texture_paths,
                    output_path=output_path,
                    atlas_size=atlas_size,
                    padding=padding
                )

            elif operation == "optimize_draw_calls":
                result = await optimize_draw_calls(
                    target_mesh=target_mesh,
                    max_materials=max_materials,
                    combine_by_color=combine_by_color,
                    preserve_normals=preserve_normals
                )

            elif operation == "get_atlas_uv_layout":
                result = await get_atlas_uv_layout(
                    target_mesh=target_mesh,
                    atlas_info=atlas_info
                )

            else:
                return f"Unknown atlasing operation: {operation}"

            # Format the result
            return _format_atlasing_result(result)

        except Exception as e:
            logger.error(f"Atlasing operation '{operation}' failed: {e}")
            return f"Atlasing operation failed: {str(e)}"


def _format_atlasing_result(result: dict) -> str:
    """Format atlasing operation results into a readable report."""
    status = result.get("status", "unknown")

    # Status indicator
    status_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    status_icon = status_icons.get(status, "❓")

    report = f"{status_icon} **Atlasing Operation Result**\n"
    report += "=" * 35 + "\n\n"

    # Status and key info
    report += f"**Status:** {status.upper()}\n"

    if "mesh_name" in result:
        report += f"**Mesh:** {result['mesh_name']}\n"

    if "atlas_size" in result:
        report += f"**Atlas Size:** {result['atlas_size']}px\n"

    # Material/draw call optimization
    if "materials_before" in result and "materials_after" in result:
        before = result["materials_before"]
        after = result["materials_after"]
        reduction = before - after
        report += f"**Materials:** {before} → {after} ({reduction} reduction)\n"

    if "atlas_layout" in result:
        report += f"**Atlas Layout:** {result['atlas_layout']}\n"

    # Texture atlas info
    if "textures_merged" in result:
        report += f"**Textures Merged:** {result['textures_merged']}\n"

    if "atlas_grid" in result:
        report += f"**Atlas Grid:** {result['atlas_grid']}\n"

    # Performance metrics
    if "materials_reduced" in result:
        report += f"**Draw Calls Reduced:** ~{result['materials_reduced']}x improvement\n"

    # Output paths
    if "output_path" in result:
        report += f"**Output Path:** {result['output_path']}\n"

    # Texture lists
    if "loaded_textures" in result and result["loaded_textures"]:
        report += "**Loaded Textures:**\n"
        for tex in result["loaded_textures"]:
            report += f"  • {tex}\n"
        report += "\n"

    # UV mappings (summary)
    if "uv_mappings" in result and result["uv_mappings"]:
        mappings = result["uv_mappings"]
        report += f"**UV Regions:** {len(mappings)}\n"
        if len(mappings) <= 5:  # Show details for small atlases
            for i, mapping in enumerate(mappings):
                uv = mapping["uv_coords"]
                report += f"  Region {i}: ({uv['u_min']:.3f}, {uv['v_min']:.3f}) → ({uv['u_max']:.3f}, {uv['v_max']:.3f})\n"

    # Message
    if "message" in result:
        report += f"\n{result['message']}\n"

    # Recommendations
    if status == "success":
        if "materials_before" in result and "materials_after" in result:
            before = result["materials_before"]
            after = result["materials_after"]
            if before > after:
                report += "\n💡 **Next Steps:**\n"
                report += "  • Apply atlas UV mapping to materials\n"
                report += "  • Test performance in VR preview\n"
                report += "  • Verify visual quality matches original\n"
        elif "textures_merged" in result and result["textures_merged"] > 0:
            report += "\n💡 **Next Steps:**\n"
            report += "  • Update material nodes to use atlas texture\n"
            report += "  • Adjust UV coordinates for each region\n"
            report += "  • Test texture filtering and mipmaps\n"

    return report


# Register the tools when this module is imported
_register_atlasing_tools()

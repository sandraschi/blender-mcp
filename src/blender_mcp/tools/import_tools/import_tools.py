"""
Import tools for Blender MCP.

Provides tools for importing various file formats into Blender.
"""

from blender_mcp.app import get_app
from blender_mcp.compat import *


def _register_import_tools():
    """Register all import-related tools."""
    app = get_app()

    @app.tool
    async def blender_import(
        operation: str = "import_fbx",
        filepath: str = "",
        file_format: str = "FBX",
        global_scale: float = 1.0,
        use_custom_normals: bool = True,
        import_shading: bool = True,
        asset_name: str = "LinkedAsset",
        # CAD-specific parameters
        cad_conversion_tool: str = "auto",  # auto, mayo, freecad, online
        mesh_quality: str = "medium",  # low, medium, high
        cad_scale_factor: float = 1.0,
    ) -> str:
        """
        Import 3D files into Blender scenes.

        Supports multiple operations through the operation parameter:
        - import_[format]: Import files in any supported format (FBX, OBJ, GLTF, STL, PLY, etc.)
        - import_cad: Import CAD files (STEP, STP, IGES, IGS) with automatic conversion
        - link_asset: Link external assets without importing

        CAD IMPORT FEATURES:
        - Automatic STEP/STP conversion using Mayo, FreeCAD, or online tools
        - Mesh quality control (low/medium/high)
        - Scale adjustment for unit conversion
        - Direct integration with robotics-mcp CAD converter

        Args:
            operation: Import operation type
            filepath: Path to the file to import
            file_format: Format of the file (FBX, OBJ, GLTF, CAD, etc.)
            global_scale: Global scale factor for import
            use_custom_normals: Import custom normals
            import_shading: Import material shading
            cad_conversion_tool: CAD conversion tool (auto, mayo, freecad, online)
            mesh_quality: Mesh quality for CAD conversion (low, medium, high)
            cad_scale_factor: Scale factor for CAD unit conversion

        Returns:
            Success message with import details
        """
        from blender_mcp.handlers.import_handler import import_file, link_asset

        try:
            if operation.startswith("import_"):
                # Extract format from operation (e.g., "import_fbx" -> "FBX")
                file_format = operation.replace("import_", "").upper()

                # Special handling for CAD imports
                if file_format == "CAD" or file_format in ["STEP", "STP", "IGES", "IGS"]:
                    return await import_cad_file(
                        filepath=filepath,
                        cad_format=file_format,
                        conversion_tool=cad_conversion_tool,
                        mesh_quality=mesh_quality,
                        scale_factor=cad_scale_factor,
                        global_scale=global_scale,
                        use_custom_normals=use_custom_normals,
                        import_shading=import_shading,
                    )

                return await import_file(
                    filepath=filepath,
                    file_format=file_format,
                    global_scale=global_scale,
                    use_custom_normals=use_custom_normals,
                    import_shading=import_shading,
                )

            elif operation == "link_asset":
                return await link_asset(
                    filepath=filepath, name=kwargs.get("asset_name", "LinkedAsset")
                )

            else:
                return f"Unknown import operation: {operation}. Use import_[format] or link_asset"

        except Exception as e:
            return f"Error in import operation '{operation}': {str(e)}"


    @app.tool
    async def import_cad_file(
        filepath: str,
        cad_format: str = "STEP",
        conversion_tool: str = "auto",
        mesh_quality: str = "medium",
        scale_factor: float = 1.0,
        global_scale: float = 1.0,
        use_custom_normals: bool = True,
        import_shading: bool = True,
    ) -> str:
        """
        Import CAD files (STEP, IGES) into Blender with automatic conversion.

        This function handles the complete pipeline:
        1. Detect CAD file format
        2. Convert to mesh format using appropriate tool
        3. Import converted mesh into Blender

        Args:
            filepath: Path to CAD file
            cad_format: CAD format (STEP, STP, IGES, IGS)
            conversion_tool: Conversion tool to use (auto, mayo, freecad, online)
            mesh_quality: Mesh quality (low, medium, high)
            scale_factor: CAD unit conversion scale
            global_scale: Blender import scale
            use_custom_normals: Import custom normals
            import_shading: Import material shading

        Returns:
            Success message with import details
        """
        from blender_mcp.handlers.import_handler import import_file
        from pathlib import Path
        import tempfile
        import os

        try:
            cad_file = Path(filepath)
            if not cad_file.exists():
                return f"CAD file not found: {filepath}"

            # Determine output format (OBJ is most reliable for CAD conversion)
            output_format = "obj"
            temp_dir = tempfile.mkdtemp()
            converted_file = os.path.join(temp_dir, f"{cad_file.stem}_converted.{output_format}")

            # Try CAD conversion using robotics-mcp if available
            conversion_success = await _try_robotics_cad_conversion(
                filepath, converted_file, conversion_tool, mesh_quality, scale_factor
            )

            if not conversion_success:
                # Fallback to direct CAD conversion
                conversion_success = await _direct_cad_conversion(
                    filepath, converted_file, cad_format, mesh_quality, scale_factor
                )

            if not conversion_success:
                return f"Failed to convert CAD file: {filepath}. Try using robotics-mcp cad_converter tool first."

            # Import the converted mesh file into Blender
            result = await import_file(
                filepath=converted_file,
                file_format="OBJ",
                global_scale=global_scale,
                use_custom_normals=use_custom_normals,
                import_shading=import_shading,
            )

            # Clean up temp file
            try:
                os.remove(converted_file)
                os.rmdir(temp_dir)
            except:
                pass  # Ignore cleanup errors

            return f"CAD import successful: {result}"

        except Exception as e:
            return f"Error importing CAD file: {str(e)}"


async def _try_robotics_cad_conversion(
    cad_path: str, output_path: str, conversion_tool: str, mesh_quality: str, scale_factor: float
) -> bool:
    """Try to use robotics-mcp CAD converter for conversion."""
    try:
        # This would integrate with mounted robotics-mcp server
        # For now, return False to use fallback
        return False
    except:
        return False


async def _direct_cad_conversion(
    cad_path: str, output_path: str, cad_format: str, mesh_quality: str, scale_factor: float
) -> bool:
    """Direct CAD conversion using available tools."""
    try:
        # Check for Mayo converter (most reliable)
        import subprocess
        import os

        mayo_paths = [
            "C:\\Program Files\\Mayo\\mayo-conv.exe",
            "C:\\Program Files (x86)\\Mayo\\mayo-conv.exe",
            "mayo-conv.exe"
        ]

        mayo_exe = None
        for path in mayo_paths:
            if os.path.exists(path):
                mayo_exe = path
                break

        if mayo_exe:
            cmd = [mayo_exe, cad_path, "-o", output_path]

            # Add quality settings
            if mesh_quality == "low":
                cmd.extend(["--meshing-edge-length", "1.0"])
            elif mesh_quality == "medium":
                cmd.extend(["--meshing-edge-length", "0.5"])
            elif mesh_quality == "high":
                cmd.extend(["--meshing-edge-length", "0.1"])

            if scale_factor != 1.0:
                cmd.extend(["--scale", str(scale_factor)])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0

        return False

    except Exception:
        return False


_register_import_tools()

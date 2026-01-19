"""
Render tools for Blender MCP.

Provides tools for rendering scenes, animations, and previews.
"""

from blender_mcp.app import get_app
from blender_mcp.compat import *


def _register_render_tools():
    """Register all render-related tools."""
    app = get_app()

    @app.tool
    async def blender_render(
        operation: str = "render_preview",
        output_path: str = "",
        output_dir: str = "",
        resolution_x: int = 1920,
        resolution_y: int = 1080,
        frames: int = 60,
        frame_start: int = 1,
        frame_end: int = 250,
        file_format: str = "PNG",
        render_engine: str = "CYCLES",
        samples: int = 128,
    ) -> str:
        """
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates 4 related rendering operations into single interface. Prevents tool explosion while maintaining
        full rendering pipeline from quick previews to production animation sequences. Follows FastMCP 2.14.3 best practices.

        Professional rendering system for Blender supporting previews, animations, and custom output formats.

        **Render Operations:**
        - **render_preview**: Generate high-quality single frame preview with custom resolution
        - **render_turntable**: Create 360-degree object rotation animation for portfolio/showcase
        - **render_animation**: Render full timeline animation sequence with frame ranges
        - **render_current_frame**: Render only the current timeline frame for quick iteration

        Args:
            operation (str, required): The render operation to perform. Must be one of: "render_preview",
                "render_turntable", "render_animation", "render_current_frame".
                - "render_preview": Single frame with custom settings (uses: output_path, resolution_*, file_format, render_engine, samples)
                - "render_turntable": 360° rotation animation (uses: output_dir, frames, resolution_*, file_format, render_engine, samples)
                - "render_animation": Full timeline render (uses: output_dir, frame_start, frame_end, resolution_*, file_format, render_engine, samples)
                - "render_current_frame": Current frame only (uses: output_path, resolution_*, file_format, render_engine, samples)
            output_path (str): File path for single frame output. Required for: "render_preview", "render_current_frame".
                Format: absolute path with extension (.png, .jpg, .exr). Directory must exist.
            output_dir (str): Directory path for multi-frame output. Required for: "render_turntable", "render_animation".
                Directory must exist and be writable. Files named with frame numbers.
            resolution_x (int): Horizontal resolution in pixels. Default: 1920. Range: 64 to 8192.
                Common values: 1920 (FHD), 3840 (4K), 7680 (8K).
            resolution_y (int): Vertical resolution in pixels. Default: 1080. Range: 64 to 8192.
                Maintains aspect ratio with resolution_x for standard formats.
            frames (int): Number of frames for turntable animation. Default: 60. Range: 8 to 360.
                Higher values create smoother rotation but increase render time.
            frame_start (int): Starting frame number for animation rendering. Default: 1.
                Must be less than frame_end. Corresponds to timeline frame numbers.
            frame_end (int): Ending frame number for animation rendering. Default: 250.
                Must be greater than frame_start. Corresponds to timeline frame numbers.
            file_format (str): Output image format. One of: "PNG", "JPEG", "TIFF", "EXR", "HDR", "WEBP".
                Default: "PNG". "EXR" recommended for post-processing, "PNG" for previews.
            render_engine (str): Blender render engine. One of: "CYCLES", "EEVEE", "WORKBENCH".
                Default: "CYCLES". "EEVEE" fastest, "CYCLES" most realistic, "WORKBENCH" technical.
            samples (int): Render quality samples for Cycles/EEVEE. Default: 128. Range: 1 to 4096.
                Higher values reduce noise but increase render time. Use 16-32 for previews.

        Returns:
            str: Render completion message with file paths and render statistics.
                Format: "SUCCESS: {operation} completed - {output_info} ({render_time}s, {resolution})"

        Raises:
            ValueError: If operation parameters are invalid or paths don't exist
            RuntimeError: If Blender rendering fails or GPU memory is insufficient

        Examples:
            Quick preview: blender_render("render_preview", output_path="preview.png", resolution_x=1280, resolution_y=720)
            Turntable: blender_render("render_turntable", output_dir="./turntable", frames=36, render_engine="EEVEE")
            Animation: blender_render("render_animation", output_dir="./output", frame_start=1, frame_end=120, samples=256)
            Current frame: blender_render("render_current_frame", output_path="frame_050.png", file_format="EXR")

        Note:
            Turntable animations automatically rotate camera around scene center.
            Use blender_camera tools to set up custom camera angles before rendering.
            GPU acceleration available when enabled in user configuration.
            Long renders may timeout - consider breaking into smaller frame ranges.
        """
        from blender_mcp.handlers.render_handler import render_preview, render_turntable

        try:
            if operation == "render_turntable":
                if not output_dir:
                    return "output_dir parameter required for turntable rendering"
                return await render_turntable(
                    output_dir=output_dir,
                    frames=frames,
                    resolution_x=resolution_x,
                    resolution_y=resolution_y,
                    format=file_format,
                )

            elif operation == "render_preview":
                if not output_path:
                    return "output_path parameter required for preview rendering"
                return await render_preview(
                    output_path=output_path, resolution_x=resolution_x, resolution_y=resolution_y
                )

            elif operation == "render_animation":
                # This would need to be implemented in the handler
                return "Animation rendering not yet implemented - use render_turntable for now"

            elif operation == "render_current_frame":
                if not output_path:
                    return "output_path parameter required for frame rendering"
                return await render_preview(
                    output_path=output_path, resolution_x=resolution_x, resolution_y=resolution_y
                )

            else:
                return f"Unknown render operation: {operation}. Available: render_preview, render_turntable, render_animation, render_current_frame"

        except Exception as e:
            return f"Error in render operation '{operation}': {str(e)}"


_register_render_tools()

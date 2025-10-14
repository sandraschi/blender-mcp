"""
Render tools for Blender MCP.

Provides tools for rendering scenes, animations, and previews.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Union
from blender_mcp.app import get_app


def get_app():
    from blender_mcp.app import app
    return app


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
    samples: int = 128
    ) -> str:
        """
        Render Blender scenes and animations.

        Supports multiple operations through the operation parameter:
        - render_preview: Render a single frame preview
        - render_turntable: Render 360-degree turntable animation
        - render_animation: Render full animation sequence
        - render_current_frame: Render current frame only

        Args:
            operation: Render operation type
            output_path: Path for single frame output
            output_dir: Directory for animation/multi-frame output
            resolution_x: Horizontal resolution in pixels
            resolution_y: Vertical resolution in pixels
            frames: Number of frames for turntable animation
            frame_start: Start frame for animation
            frame_end: End frame for animation
            file_format: Output format (PNG, JPEG, EXR, etc.)
            render_engine: Render engine (CYCLES, EEVEE, WORKBENCH)
            samples: Render samples for Cycles

        Returns:
            Success message with render details
        """
        from blender_mcp.handlers.render_handler import (
            render_turntable, render_preview
        )

        try:
            if operation == "render_turntable":
                if not output_dir:
                    return "output_dir parameter required for turntable rendering"
                return await render_turntable(
                    output_dir=output_dir,
                    frames=frames,
                    resolution_x=resolution_x,
                    resolution_y=resolution_y,
                    format=file_format
                )

            elif operation == "render_preview":
                if not output_path:
                    return "output_path parameter required for preview rendering"
                return await render_preview(
                    output_path=output_path,
                    resolution_x=resolution_x,
                    resolution_y=resolution_y
                )

            elif operation == "render_animation":
                # This would need to be implemented in the handler
                return "Animation rendering not yet implemented - use render_turntable for now"

            elif operation == "render_current_frame":
                if not output_path:
                    return "output_path parameter required for frame rendering"
                return await render_preview(
                    output_path=output_path,
                    resolution_x=resolution_x,
                    resolution_y=resolution_y
                )

            else:
                return f"Unknown render operation: {operation}. Available: render_preview, render_turntable, render_animation, render_current_frame"

        except Exception as e:
            return f"Error in render operation '{operation}': {str(e)}"


_register_render_tools()

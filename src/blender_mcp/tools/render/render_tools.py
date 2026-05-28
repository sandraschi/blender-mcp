"""
Render tools for Blender MCP.

Provides tools for rendering scenes, animations, and previews.
"""

import json

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
        device: str = "GPU",
        use_denoising: bool = True,
        layer_name: str = "ViewLayer",
        use_bloom: bool = True,
        use_ssao: bool = True,
        use_motion_blur: bool = False,
        use_dof: bool = False,
        shading_mode: str = "SOLID",
        angles: int = 4,
        elevation_deg: float = 25.0,
        camera_radius: float = 5.0,
        prefer_session: bool = True,
    ) -> str:
        """
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates rendering operations into a single interface.

        **Render Operations:**
        - **render_preview**: Generate high-quality single frame preview
        - **render_turntable**: Create 360-degree object rotation animation
        - **render_animation**: Render full timeline animation sequence
        - **render_current_frame**: Render only the current timeline frame
        - **screenshot_viewport**: Capture viewport for agent vision (prefers live GUI session)
        - **render_multi_angle**: Render N stills from orbit angles for review loops
        - **set_engine**: Configure Cycles/EEVEE engine, samples, device
        - **configure_layers**: Enable render passes on a view layer
        - **setup_post_processing**: EEVEE bloom, SSAO, motion blur, DOF
        """
        from blender_mcp.handlers.render_handler import (
            render_multi_angle,
            render_preview,
            render_turntable,
            screenshot_viewport,
        )
        from blender_mcp.handlers.rendering_handler import (
            configure_render_layers,
            set_render_engine,
            setup_post_processing,
        )

        try:
            if operation == "screenshot_viewport":
                if not output_path:
                    return json.dumps({"success": False, "error": "output_path is required"})
                result = await screenshot_viewport(
                    output_path=output_path,
                    resolution_x=resolution_x,
                    resolution_y=resolution_y,
                    shading_mode=shading_mode,
                    prefer_session=prefer_session,
                )
                return json.dumps(result, indent=2)

            if operation == "set_engine":
                result = await set_render_engine(
                    engine=render_engine,
                    device=device,
                    use_denoising=use_denoising,
                    samples=samples,
                    resolution_x=resolution_x,
                    resolution_y=resolution_y,
                )
                return json.dumps(result, indent=2)

            if operation == "configure_layers":
                result = await configure_render_layers(layer_name=layer_name)
                return json.dumps(result, indent=2)

            if operation == "setup_post_processing":
                result = await setup_post_processing(
                    use_bloom=use_bloom,
                    use_ssao=use_ssao,
                    use_motion_blur=use_motion_blur,
                    use_dof=use_dof,
                )
                return json.dumps(result, indent=2)

            if operation == "render_multi_angle":
                if not output_dir:
                    return json.dumps({"success": False, "error": "output_dir is required"})
                result = await render_multi_angle(
                    output_dir=output_dir,
                    angles=angles,
                    elevation_deg=elevation_deg,
                    radius=camera_radius,
                    resolution_x=resolution_x,
                    resolution_y=resolution_y,
                    prefer_session=prefer_session,
                )
                return json.dumps(result, indent=2)

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
                return "Animation rendering not yet implemented - use render_turntable for now"

            elif operation == "render_current_frame":
                if not output_path:
                    return "output_path parameter required for frame rendering"
                return await render_preview(
                    output_path=output_path, resolution_x=resolution_x, resolution_y=resolution_y
                )

            else:
                return (
                    f"Unknown render operation: {operation}. Available: render_preview, "
                    "render_turntable, render_animation, render_current_frame, "
                    "screenshot_viewport, render_multi_angle, set_engine, configure_layers, setup_post_processing"
                )

        except Exception as e:
            return f"Error in render operation '{operation}': {e!s}"


_register_render_tools()

"""
Video Sequence Editor tools for Blender MCP.

Provides tools for Blender's built-in VSE: strip management, timeline editing,
transitions/effects, and video rendering.
"""

import logging
from typing import Literal

from blender_mcp.app import get_app
from blender_mcp.compat import *

logger = logging.getLogger(__name__)


def _register_vse_tools():
    app = get_app()

    @app.tool
    async def blender_vse(
        operation: Literal[
            "add_movie",
            "add_sound",
            "add_image_sequence",
            "add_scene",
            "add_color",
            "add_text",
            "add_effect",
            "delete_strip",
            "cut_strip",
            "trim_strip",
            "move_strip",
            "mute_strip",
            "lock_strip",
            "set_speed",
            "set_blend",
            "set_transform",
            "list_strips",
            "render_video",
            "clear_vse",
            "get_timeline_info",
        ] = "list_strips",
        filepath: str = "",
        directory: str = "",
        strip_name: str = "",
        strip1_name: str = "",
        strip2_name: str = "",
        channel: int = 1,
        frame: int = 1,
        length: int = 120,
        frame_start: int = 1,
        frame_end: int = 250,
        text: str = "",
        font_size: int = 48,
        color_r: float = 0.0,
        color_g: float = 0.0,
        color_b: float = 0.0,
        effect_type: str = "CROSS",
        cut_type: str = "SOFT",
        mute: bool = True,
        lock: bool = True,
        speed_factor: float = 1.0,
        blend_type: str = "ALPHA_OVER",
        blend_alpha: float = 1.0,
        position_x: float | None = None,
        position_y: float | None = None,
        scale_x: float | None = None,
        scale_y: float | None = None,
        rotation: float | None = None,
        scene_name: str = "",
        fit_method: str = "FIT",
        include_audio: bool = True,
        resolution_x: int = 1920,
        resolution_y: int = 1080,
        output_path: str = "",
        container: str = "MPEG4",
        codec: str = "H264",
        quality: str = "MEDIUM",
        fps: int = 30,
        audio_codec: str = "AAC",
        audio_bitrate: int = 192,
    ) -> str:
        """
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates 20 VSE operations into a single interface. Prevents tool explosion while
        providing full video editing: strip management, timeline editing, effects, and rendering.
        Follows FastMCP 3.x best practices.

        Blender's built-in Video Sequence Editor (VSE) exposed as MCP tools.
        Add video/audio/image strips, apply transitions, trim, cut, move, and render to video.

        **Strip Creation (7 operations):**
        - **add_movie**: Add a video/MP4 file as a movie strip
        - **add_sound**: Add an audio file (WAV, MP3, etc.) as a sound strip
        - **add_image_sequence**: Add a folder of images as an image sequence strip
        - **add_scene**: Add a 3D scene as a strip (compositing)
        - **add_color**: Add a solid color matte strip
        - **add_text**: Add a text overlay strip
        - **add_effect**: Add a transition/filter effect between strips

        **Strip Editing (6 operations):**
        - **delete_strip**: Remove a strip by name
        - **cut_strip**: Cut a strip at a specific frame
        - **trim_strip**: Set strip start/end frames (trim handles)
        - **move_strip**: Move a strip to a different channel or frame
        - **mute_strip**: Mute or unmute a strip
        - **lock_strip**: Lock or unlock a strip

        **Properties (3 operations):**
        - **set_speed**: Change playback speed (creates speed effect strip)
        - **set_blend**: Set blend mode and opacity (ALPHA_OVER, CROSS, ADD, etc.)
        - **set_transform**: Set position, scale, rotation of a strip

        **Information (2 operations):**
        - **list_strips**: List all strips in the timeline with properties
        - **get_timeline_info**: Get timeline frame range, FPS, strip count, channels

        **Rendering (1 operation):**
        - **render_video**: Render the VSE timeline to a video file (H264/MPEG4)

        **Cleanup (1 operation):**
        - **clear_vse**: Remove all strips from the timeline

        Args:
            operation (Literal, required): The VSE operation to perform.
            filepath (str): Path to video or audio file. Required for: add_movie, add_sound.
            directory (str): Directory path for image sequences. Required for: add_image_sequence.
            strip_name (str): Target strip name for editing operations. Required for most edit ops.
            strip1_name (str): First strip name for effect creation. Required for: add_effect.
            strip2_name (str): Second strip name for effect creation. Required for: add_effect.
            channel (int): VSE channel number (higher = on top). Default: 1.
            frame (int): Frame number for placement/cutting. Default: 1.
            length (int): Strip duration in frames. Default: 120. Used for: add_color, add_text, add_effect.
            frame_start (int): Start frame for trim or render range. Default: 1.
            frame_end (int): End frame for render range. Default: 250.
            text (str): Text content. Required for: add_text.
            font_size (int): Font size in points. Default: 48. Used for: add_text.
            color_r/g/b (float): RGB color values 0.0-1.0. Default: (0,0,0). Used for: add_color.
            effect_type (str): Effect type. Options: CROSS, WIPE, GLOW, TRANSFORM, SPEED,
                ADJUSTMENT, GAUSSIAN_BLUR, TEXT, COLOR, MULTICAM. Default: CROSS.
            cut_type (str): Cut type. SOFT (preserves handles) or HARD (snaps). Default: SOFT.
            mute (bool): True to mute, False to unmute. Default: True. Used for: mute_strip.
            lock (bool): True to lock, False to unlock. Default: True. Used for: lock_strip.
            speed_factor (float): Playback speed multiplier. 2.0 = double speed, 0.5 = half speed. Default: 1.0.
            blend_type (str): Blend mode. Options: ALPHA_OVER, CROSS, ADD, SUBTRACT, MULTIPLY,
                SCREEN, OVERLAY, DARKEN, LIGHTEN, etc. Default: ALPHA_OVER.
            blend_alpha (float): Opacity 0.0-1.0. Default: 1.0.
            position_x/y (float): Strip position offset. Used for: set_transform.
            scale_x/y (float): Strip scale factor. Used for: set_transform.
            rotation (float): Strip rotation in degrees. Used for: set_transform.
            scene_name (str): Source 3D scene name. Required for: add_scene.
            fit_method (str): How to fit media. FIT (maintains aspect), FILL (crops), STRETCH. Default: FIT.
            include_audio (bool): Include audio track from video. Default: True. Used for: add_movie.
            resolution_x/y (int): Output resolution. Default: 1920x1080. Used for: render_video.
            output_path (str): Output file path (.mp4 recommended). Required for: render_video.
            container (str): Video container format. Options: MPEG4, AVI, QUICKTIME, OGG, MKV. Default: MPEG4.
            codec (str): Video codec. Options: H264, H265, THEORA, AV1. Default: H264.
            quality (str): Encoding quality. Options: BEST, GOOD, MEDIUM. Default: MEDIUM. Used for: render_video.
            fps (int): Frames per second. Default: 30. Used for: render_video.
            audio_codec (str): Audio codec. Options: AAC, MP3, PCM, VORBIS, FLAC. Default: AAC. Used for: render_video.
            audio_bitrate (int): Audio bitrate in kbps. Default: 192. Used for: render_video.

        Returns:
            str: Operation result message with success/failure status and details.

        Raises:
            ValueError: If required parameters are missing or invalid
            BlenderVSEError: If Blender VSE operations fail

        Examples:
            Add video: blender_vse("add_movie", filepath="C:/video/clip.mp4", channel=1, frame=1)
            Add transition: blender_vse("add_effect", effect_type="CROSS", strip1_name="clip1", strip2_name="clip2")
            Trim strip: blender_vse("trim_strip", strip_name="clip1", frame_start=10, frame_end=100)
            Cut strip: blender_vse("cut_strip", strip_name="clip1", frame=50)
            Set speed: blender_vse("set_speed", strip_name="clip1", speed_factor=2.0)
            List timeline: blender_vse("list_strips")
            Render output: blender_vse("render_video", output_path="C:/output/final.mp4", frame_start=1, frame_end=300)

        Note:
            Strips stack vertically by channel (higher channel = rendered on top).
            Effects require two selected strips (above/below the effect channel).
            Use add_movie first, then add_effect between strips for transitions.
            VSE rendering respects scene frame range unless overridden.
        """
        from blender_mcp.handlers.vse_handler import (
            add_color,
            add_effect,
            add_image_sequence,
            add_movie,
            add_scene,
            add_sound,
            add_text,
            clear_vse,
            cut_strip,
            delete_strip,
            get_timeline_info,
            list_strips,
            lock_strip,
            move_strip,
            mute_strip,
            render_video,
            set_blend,
            set_speed,
            trim_strip,
        )
        from blender_mcp.handlers.vse_handler import (
            set_transform as set_strip_transform,
        )

        logger.info(f"VSE operation: {operation}")

        try:
            if operation == "add_movie":
                if not filepath:
                    return "filepath required for add_movie"
                return await add_movie(
                    filepath=filepath,
                    channel=channel,
                    frame=frame,
                    fit_method=fit_method,
                    include_audio=include_audio,
                    strip_name=strip_name,
                )

            elif operation == "add_sound":
                if not filepath:
                    return "filepath required for add_sound"
                return await add_sound(
                    filepath=filepath,
                    channel=channel,
                    frame=frame,
                    strip_name=strip_name,
                )

            elif operation == "add_image_sequence":
                if not directory:
                    return "directory required for add_image_sequence"
                return await add_image_sequence(
                    directory=directory,
                    channel=channel,
                    frame=frame,
                    frame_start=frame_start,
                    frame_end=frame_end,
                    strip_name=strip_name,
                )

            elif operation == "add_scene":
                return await add_scene(
                    scene_name=scene_name,
                    channel=channel,
                    frame=frame,
                    strip_name=strip_name,
                )

            elif operation == "add_color":
                return await add_color(
                    channel=channel,
                    frame=frame,
                    length=length,
                    color=(color_r, color_g, color_b),
                    strip_name=strip_name,
                )

            elif operation == "add_text":
                return await add_text(
                    text=text,
                    channel=channel,
                    frame=frame,
                    length=length,
                    font_size=font_size,
                    strip_name=strip_name,
                )

            elif operation == "add_effect":
                if not strip1_name:
                    return "strip1_name required for add_effect"
                return await add_effect(
                    effect_type=effect_type,
                    strip1_name=strip1_name,
                    strip2_name=strip2_name,
                    channel=channel,
                    frame=frame,
                    length=length,
                    strip_name=strip_name,
                )

            elif operation == "delete_strip":
                if not strip_name:
                    return "strip_name required for delete_strip"
                return await delete_strip(strip_name=strip_name)

            elif operation == "cut_strip":
                if not strip_name:
                    return "strip_name required for cut_strip"
                return await cut_strip(strip_name=strip_name, frame=frame, cut_type=cut_type)

            elif operation == "trim_strip":
                if not strip_name:
                    return "strip_name required for trim_strip"
                return await trim_strip(
                    strip_name=strip_name,
                    frame_start=frame_start if frame_start != 1 else None,
                    frame_end=frame_end if frame_end != 250 else None,
                )

            elif operation == "move_strip":
                if not strip_name:
                    return "strip_name required for move_strip"
                return await move_strip(
                    strip_name=strip_name,
                    channel=channel if channel != 1 else None,
                    frame_start=frame if frame != 1 else None,
                )

            elif operation == "mute_strip":
                if not strip_name:
                    return "strip_name required for mute_strip"
                return await mute_strip(strip_name=strip_name, mute=mute)

            elif operation == "lock_strip":
                if not strip_name:
                    return "strip_name required for lock_strip"
                return await lock_strip(strip_name=strip_name, lock=lock)

            elif operation == "set_speed":
                if not strip_name:
                    return "strip_name required for set_speed"
                return await set_speed(strip_name=strip_name, speed_factor=speed_factor)

            elif operation == "set_blend":
                if not strip_name:
                    return "strip_name required for set_blend"
                return await set_blend(strip_name=strip_name, blend_type=blend_type, blend_alpha=blend_alpha)

            elif operation == "set_transform":
                if not strip_name:
                    return "strip_name required for set_transform"
                return await set_strip_transform(
                    strip_name=strip_name,
                    position_x=position_x,
                    position_y=position_y,
                    scale_x=scale_x,
                    scale_y=scale_y,
                    rotation=rotation,
                )

            elif operation == "list_strips":
                return await list_strips()

            elif operation == "render_video":
                if not output_path:
                    return "output_path required for render_video"
                return await render_video(
                    output_path=output_path,
                    resolution_x=resolution_x,
                    resolution_y=resolution_y,
                    frame_start=frame_start,
                    frame_end=frame_end,
                    container=container,
                    codec=codec,
                    quality=quality,
                    fps=fps,
                    audio_codec=audio_codec,
                    audio_bitrate=audio_bitrate,
                )

            elif operation == "clear_vse":
                return await clear_vse()

            elif operation == "get_timeline_info":
                return await get_timeline_info()

            else:
                return f"Unknown operation: {operation}"

        except Exception as e:
            logger.error(f"VSE error ({operation}): {e!s}")
            return f"Error in {operation}: {e!s}"


_register_vse_tools()

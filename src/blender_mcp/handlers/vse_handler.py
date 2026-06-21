"""Video Sequence Editor handler for Blender MCP server.

Provides VSE strip management, timeline editing, and video rendering via bpy script generation.
"""

import os
from pathlib import Path

from ..compat import *
from ..decorators import blender_operation
from ..exceptions import BlenderVSEError
from ..utils.blender_executor import get_blender_executor

_executor = get_blender_executor()


def _ensure_vse_exists() -> str:
    return """
if not bpy.context.scene.sequence_editor:
    bpy.context.scene.sequence_editor_create()
seq = bpy.context.scene.sequence_editor
"""


@blender_operation("vse_add_movie", log_args=True)
async def add_movie(
    filepath: str,
    channel: int = 1,
    frame: int = 1,
    fit_method: str = "FIT",
    include_audio: bool = True,
    strip_name: str = "",
) -> str:
    try:
        filepath = str(Path(filepath).absolute())
        if not os.path.exists(filepath):
            return f"ERROR: File not found: {filepath}"

        script = f"""
import bpy
import os

try:
{_ensure_vse_exists()}
    scene = bpy.context.scene
    scene.frame_current = {frame}

    bpy.ops.sequencer.movie_strip_add(
        filepath=r"{filepath}",
        frame_start={frame},
        channel={channel},
        fit_method='{fit_method}',
        sound={str(include_audio).lower()}
    )
    strip = seq.active_strip
    if "{strip_name}":
        strip.name = "{strip_name}"
    print(
        f"SUCCESS: Added movie strip '{{strip.name}}' "
        f"at frame {{strip.frame_start}} channel {{strip.channel}}"
    )
except Exception as e:
    print(f"ERROR: Failed to add movie strip: {{e}}")
    raise e
"""
        await _executor.execute_script(script, script_name="vse_add_movie")
        name = strip_name or os.path.basename(filepath)
        return f"Added movie strip '{name}' at frame {frame} channel {channel}"

    except Exception as e:
        raise BlenderVSEError("add_movie", str(e)) from e


@blender_operation("vse_add_sound", log_args=True)
async def add_sound(
    filepath: str,
    channel: int = 2,
    frame: int = 1,
    strip_name: str = "",
) -> str:
    try:
        filepath = str(Path(filepath).absolute())
        if not os.path.exists(filepath):
            return f"ERROR: File not found: {filepath}"

        script = f"""
import bpy
import os

try:
{_ensure_vse_exists()}
    scene = bpy.context.scene
    scene.frame_current = {frame}

    bpy.ops.sequencer.sound_strip_add(
        filepath=r"{filepath}",
        frame_start={frame},
        channel={channel}
    )
    strip = seq.active_strip
    if "{strip_name}":
        strip.name = "{strip_name}"
    print(
        f"SUCCESS: Added sound strip '{{strip.name}}' "
        f"at frame {{strip.frame_start}} channel {{strip.channel}}"
    )
except Exception as e:
    print(f"ERROR: Failed to add sound strip: {{e}}")
    raise e
"""
        await _executor.execute_script(script, script_name="vse_add_sound")
        name = strip_name or os.path.basename(filepath)
        return f"Added sound strip '{name}' at frame {frame} channel {channel}"

    except Exception as e:
        raise BlenderVSEError("add_sound", str(e)) from e


@blender_operation("vse_add_image_sequence", log_args=True)
async def add_image_sequence(
    directory: str,
    channel: int = 1,
    frame: int = 1,
    frame_start: int = 1,
    frame_end: int = 60,
    strip_name: str = "",
) -> str:
    try:
        directory = str(Path(directory).absolute())
        if not os.path.isdir(directory):
            return f"ERROR: Directory not found: {directory}"

        script = f"""
import bpy
import os

try:
{_ensure_vse_exists()}

    files = []
    image_exts = ('.png', '.jpg', '.jpeg', '.tiff', '.tif',
                  '.exr', '.bmp', '.webp')
    for f in sorted(os.listdir(r"{directory}")):
        if f.lower().endswith(image_exts):
            files.append({{"name": f}})

    if not files:
        raise Exception("No image files found in directory")

    scene = bpy.context.scene
    scene.frame_current = {frame}

    bpy.ops.sequencer.image_strip_add(
        directory=r"{directory}",
        files=files,
        frame_start={frame},
        channel={channel},
        fit_method='FIT'
    )
    strip = seq.active_strip
    if "{strip_name}":
        strip.name = "{strip_name}"
    strip.frame_final_start = {frame_start}
    strip.frame_final_end = {frame_end}
    print(
        f"SUCCESS: Added image sequence strip '{{strip.name}}' "
        f"frames {{strip.frame_final_start}}-{{strip.frame_final_end}}"
    )
except Exception as e:
    print(f"ERROR: Failed to add image sequence: {{{{e}}}}")
    raise e
"""
        await _executor.execute_script(script, script_name="vse_add_image_sequence")
        name = strip_name or os.path.basename(directory)
        return f"Added image sequence strip '{name}' at frame {frame} channel {channel}"

    except Exception as e:
        raise BlenderVSEError("add_image_sequence", str(e)) from e


@blender_operation("vse_add_scene", log_args=True)
async def add_scene(
    scene_name: str = "",
    channel: int = 1,
    frame: int = 1,
    strip_name: str = "",
) -> str:
    try:
        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    scene = bpy.context.scene
    scene.frame_current = {frame}

    src_scene = bpy.data.scenes.get("{scene_name}") or scene

    bpy.ops.sequencer.scene_strip_add(
        frame_start={frame},
        channel={channel},
        scene=src_scene.name
    )
    strip = seq.active_strip
    if "{strip_name}":
        strip.name = "{strip_name}"
    print(
        f"SUCCESS: Added scene strip '{{strip.name}}' "
        f"from scene '{{src_scene.name}}'"
    )
except Exception as e:
    print(f"ERROR: Failed to add scene strip: {{e}}")
    raise e
"""
        await _executor.execute_script(script, script_name="vse_add_scene")
        name = strip_name or scene_name or "Scene"
        return f"Added scene strip '{name}' at frame {frame} channel {channel}"

    except Exception as e:
        raise BlenderVSEError("add_scene", str(e)) from e


@blender_operation("vse_add_color", log_args=True)
async def add_color(
    channel: int = 1,
    frame: int = 1,
    length: int = 120,
    color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    strip_name: str = "",
) -> str:
    try:
        r, g, b = color
        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    scene = bpy.context.scene
    scene.frame_current = {frame}

    bpy.ops.sequencer.effect_strip_add(
        frame_start={frame},
        frame_end={frame + length},
        channel={channel},
        type='COLOR'
    )
    strip = seq.active_strip
    if "{strip_name}":
        strip.name = "{strip_name}"
    strip.color = ({r}, {g}, {b})
    print(
        f"SUCCESS: Added color strip '{{strip.name}}' "
        f"RGB({{strip.color[0]}},{{strip.color[1]}},{{strip.color[2]}})"
    )
except Exception as e:
    print(f"ERROR: Failed to add color strip: {{e}}")
    raise e
"""
        await _executor.execute_script(script, script_name="vse_add_color")
        name = strip_name or f"Color({r:.1f},{g:.1f},{b:.1f})"
        return f"Added color strip '{name}' frames {frame}-{frame + length} channel {channel}"

    except Exception as e:
        raise BlenderVSEError("add_color", str(e)) from e


@blender_operation("vse_add_text", log_args=True)
async def add_text(
    text: str = "Text",
    channel: int = 1,
    frame: int = 1,
    length: int = 120,
    font_size: int = 48,
    location_x: float = 0.5,
    location_y: float = 0.5,
    strip_name: str = "",
) -> str:
    try:
        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    scene = bpy.context.scene
    scene.frame_current = {frame}

    bpy.ops.sequencer.effect_strip_add(
        frame_start={frame},
        frame_end={frame + length},
        channel={channel},
        type='TEXT'
    )
    strip = seq.active_strip
    if "{strip_name}":
        strip.name = "{strip_name}"
    strip.text = r"{text}"
    strip.font_size = {font_size}
    strip.location[0] = {location_x}
    strip.location[1] = {location_y}
    print(f"SUCCESS: Added text strip '{{strip.name}}'")
except Exception as e:
    print(f"ERROR: Failed to add text strip: {{e}}")
    raise e
"""
        await _executor.execute_script(script, script_name="vse_add_text")
        return f"Added text strip '{strip_name or text[:20]}' frames {frame}-{frame + length} channel {channel}"

    except Exception as e:
        raise BlenderVSEError("add_text", str(e)) from e


@blender_operation("vse_add_effect", log_args=True)
async def add_effect(
    effect_type: str = "CROSS",
    strip1_name: str = "",
    strip2_name: str = "",
    channel: int = 1,
    frame: int = 1,
    length: int = 30,
    strip_name: str = "",
) -> str:
    try:
        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    scene = bpy.context.scene

    if not seq.sequences:
        raise Exception("No strips in timeline")

    for s in seq.sequences:
        s.select = False

    s1 = seq.sequences.get("{strip1_name}") if "{strip1_name}" else None
    s2 = seq.sequences.get("{strip2_name}") if "{strip2_name}" else None

    if "{strip1_name}" and not s1:
        raise Exception(f"Strip not found: {{{{strip1_name}}}}")
    if "{strip2_name}" and not s2:
        raise Exception(f"Strip not found: {{{{strip2_name}}}}")

    if s1:
        s1.select = True
    if s2:
        s2.select = True

    scene.frame_current = {frame}

    bpy.ops.sequencer.effect_strip_add(
        frame_start={frame},
        frame_end={frame + length},
        channel={channel},
        type='{effect_type}'
    )
    strip = seq.active_strip
    if "{strip_name}":
        strip.name = "{strip_name}"
    print(
        f"SUCCESS: Added {{'{effect_type}'}} "
        f"effect strip '{{strip.name}}'"
    )
except Exception as e:
    print(f"ERROR: Failed to add effect strip: {{{{e}}}}")
    raise e
"""
        await _executor.execute_script(script, script_name="vse_add_effect")
        return f"Added {effect_type} effect strip '{strip_name or effect_type}' frames {frame}-{frame + length}"

    except Exception as e:
        raise BlenderVSEError("add_effect", str(e)) from e


@blender_operation("vse_delete_strip", log_args=True)
async def delete_strip(strip_name: str) -> str:
    try:
        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    strip = seq.sequences.get("{strip_name}")
    if not strip:
        print(f"STRIP_NOT_FOUND: {strip_name}")
    else:
        for s in seq.sequences:
            s.select = False
        strip.select = True
        bpy.ops.sequencer.delete()
        print(f"SUCCESS: Deleted strip '{strip_name}'")
except Exception as e:
    print(f"ERROR: Failed to delete strip: {{e}}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_delete_strip")
        if "STRIP_NOT_FOUND" in result:
            return f"Strip '{strip_name}' not found in timeline"
        return f"Deleted strip '{strip_name}'"

    except Exception as e:
        raise BlenderVSEError("delete_strip", str(e)) from e


@blender_operation("vse_cut_strip", log_args=True)
async def cut_strip(strip_name: str, frame: int, cut_type: str = "SOFT") -> str:
    try:
        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    strip = seq.sequences.get("{strip_name}")
    if not strip:
        print(f"STRIP_NOT_FOUND: {strip_name}")
    else:
        for s in seq.sequences:
            s.select = False
        strip.select = True
        scene = bpy.context.scene
        scene.frame_current = {frame}
        bpy.ops.sequencer.cut(frame={frame}, type='{cut_type}')
        print(f"SUCCESS: Cut strip '{strip_name}' at frame {frame}")
except Exception as e:
    print(f"ERROR: Failed to cut strip: {{e}}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_cut_strip")
        if "STRIP_NOT_FOUND" in result:
            return f"Strip '{strip_name}' not found in timeline"
        return f"Cut strip '{strip_name}' at frame {frame}"

    except Exception as e:
        raise BlenderVSEError("cut_strip", str(e)) from e


@blender_operation("vse_trim_strip", log_args=True)
async def trim_strip(
    strip_name: str,
    frame_start: int | None = None,
    frame_end: int | None = None,
    frame_offset_start: int | None = None,
    frame_offset_end: int | None = None,
) -> str:
    try:
        ops = []
        if frame_start is not None:
            ops.append(f"strip.frame_start = {frame_start}")
        if frame_end is not None:
            ops.append(f"strip.frame_final_end = {frame_end}")
        if frame_offset_start is not None:
            ops.append(f"strip.frame_offset_start = {frame_offset_start}")
        if frame_offset_end is not None:
            ops.append(f"strip.frame_offset_end = {frame_offset_end}")

        if not ops:
            return "No trim parameters provided"

        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    strip = seq.sequences.get("{strip_name}")
    if not strip:
        print(f"STRIP_NOT_FOUND: {strip_name}")
    else:
        {chr(10).join("        " + op for op in ops)}
        print(
            f"SUCCESS: Trimmed strip '{{strip.name}}' "
            f"start={{strip.frame_start}} end={{strip.frame_final_end}} "
            f"offs_s={{strip.frame_offset_start}} offs_e={{strip.frame_offset_end}}"
        )
except Exception as e:
    print(f"ERROR: Failed to trim strip: {{{{e}}}}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_trim_strip")
        if "STRIP_NOT_FOUND" in result:
            return f"Strip '{strip_name}' not found in timeline"
        return f"Trimmed strip '{strip_name}'"

    except Exception as e:
        raise BlenderVSEError("trim_strip", str(e)) from e


@blender_operation("vse_move_strip", log_args=True)
async def move_strip(
    strip_name: str,
    channel: int | None = None,
    frame_start: int | None = None,
) -> str:
    try:
        ops = []
        if channel is not None:
            ops.append(f"strip.channel = {channel}")
        if frame_start is not None:
            ops.append(f"strip.frame_start = {frame_start}")

        if not ops:
            return "No move parameters provided"

        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    strip = seq.sequences.get("{strip_name}")
    if not strip:
        print(f"STRIP_NOT_FOUND: {strip_name}")
    else:
        {chr(10).join("        " + op for op in ops)}
        print(
            f"SUCCESS: Moved strip '{{strip.name}}' "
            f"to channel {{strip.channel}} frame {{strip.frame_start}}"
        )
except Exception as e:
    print(f"ERROR: Failed to move strip: {{{{e}}}}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_move_strip")
        if "STRIP_NOT_FOUND" in result:
            return f"Strip '{strip_name}' not found in timeline"
        return f"Moved strip '{strip_name}'"

    except Exception as e:
        raise BlenderVSEError("move_strip", str(e)) from e


@blender_operation("vse_mute_strip", log_args=True)
async def mute_strip(strip_name: str, mute: bool = True) -> str:
    try:
        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    strip = seq.sequences.get("{strip_name}")
    if not strip:
        print(f"STRIP_NOT_FOUND: {strip_name}")
    else:
        strip.mute = {str(mute).lower()}
        state = 'Muted' if {str(mute).lower()} else 'Unmuted'
        print(f"SUCCESS: {{state}} strip '{{strip.name}}'")
except Exception as e:
    print(f"ERROR: Failed to mute strip: {{e}}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_mute_strip")
        if "STRIP_NOT_FOUND" in result:
            return f"Strip '{strip_name}' not found in timeline"
        return f"{'Muted' if mute else 'Unmuted'} strip '{strip_name}'"

    except Exception as e:
        raise BlenderVSEError("mute_strip", str(e)) from e


@blender_operation("vse_lock_strip", log_args=True)
async def lock_strip(strip_name: str, lock: bool = True) -> str:
    try:
        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    strip = seq.sequences.get("{strip_name}")
    if not strip:
        print(f"STRIP_NOT_FOUND: {strip_name}")
    else:
        strip.lock = {str(lock).lower()}
        state = 'Locked' if {str(lock).lower()} else 'Unlocked'
        print(f"SUCCESS: {{state}} strip '{{strip.name}}'")
except Exception as e:
    print(f"ERROR: Failed to lock strip: {{e}}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_lock_strip")
        if "STRIP_NOT_FOUND" in result:
            return f"Strip '{strip_name}' not found in timeline"
        return f"{'Locked' if lock else 'Unlocked'} strip '{strip_name}'"

    except Exception as e:
        raise BlenderVSEError("lock_strip", str(e)) from e


@blender_operation("vse_set_speed", log_args=True)
async def set_speed(strip_name: str, speed_factor: float = 1.0) -> str:
    try:
        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    strip = seq.sequences.get("{strip_name}")
    if not strip:
        print(f"STRIP_NOT_FOUND: {strip_name}")
    else:
        for s in seq.sequences:
            s.select = False
        strip.select = True
        bpy.context.scene.frame_current = strip.frame_start
        bpy.ops.sequencer.effect_strip_add(type='SPEED')
        speed_strip = seq.active_strip
        speed_strip.speed_factor = {speed_factor}
        speed_strip.name = strip.name + "_speed"
        print(
            f"SUCCESS: Set speed {speed_factor}x "
            f"on strip '{{strip.name}}' via speed effect"
        )
except Exception as e:
    print(f"ERROR: Failed to set speed: {{{{e}}}}")
    raise e
"""
        await _executor.execute_script(script, script_name="vse_set_speed")
        return f"Set speed {speed_factor}x on strip '{strip_name}'"

    except Exception as e:
        raise BlenderVSEError("set_speed", str(e)) from e


@blender_operation("vse_set_blend", log_args=True)
async def set_blend(
    strip_name: str,
    blend_type: str = "ALPHA_OVER",
    blend_alpha: float = 1.0,
) -> str:
    try:
        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    strip = seq.sequences.get("{strip_name}")
    if not strip:
        print(f"STRIP_NOT_FOUND: {strip_name}")
    else:
        strip.blend_type = '{blend_type}'
        strip.blend_alpha = {blend_alpha}
        print(
            f"SUCCESS: Set blend '{{strip.blend_type}}' "
            f"alpha={{strip.blend_alpha}} on strip '{{strip.name}}'"
        )
except Exception as e:
    print(f"ERROR: Failed to set blend: {{e}}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_set_blend")
        if "STRIP_NOT_FOUND" in result:
            return f"Strip '{strip_name}' not found in timeline"
        return f"Set blend {blend_type} alpha={blend_alpha} on strip '{strip_name}'"

    except Exception as e:
        raise BlenderVSEError("set_blend", str(e)) from e


@blender_operation("vse_set_transform", log_args=True)
async def set_transform(
    strip_name: str,
    position_x: float | None = None,
    position_y: float | None = None,
    scale_x: float | None = None,
    scale_y: float | None = None,
    rotation: float | None = None,
) -> str:
    try:
        ops = []
        if position_x is not None:
            ops.append(f"strip.transform.offset_x = {position_x}")
        if position_y is not None:
            ops.append(f"strip.transform.offset_y = {position_y}")
        if scale_x is not None:
            ops.append(f"strip.transform.scale_x = {scale_x}")
        if scale_y is not None:
            ops.append(f"strip.transform.scale_y = {scale_y}")
        if rotation is not None:
            ops.append(f"strip.transform.rotation = {rotation}")

        if not ops:
            return "No transform parameters provided"

        script = f"""
import bpy

try:
{_ensure_vse_exists()}
    strip = seq.sequences.get("{strip_name}")
    if not strip:
        print(f"STRIP_NOT_FOUND: {strip_name}")
    else:
        if not hasattr(strip, 'transform'):
            raise Exception(
                "Strip does not support transforms "
                "(use movie/image/scene strips)"
            )
{chr(10).join("        " + op for op in ops)}
        print(
            f"SUCCESS: Transformed strip '{{strip.name}}' "
            f"off=({{strip.transform.offset_x}},"
            f"{{strip.transform.offset_y}}) "
            f"scale=({{strip.transform.scale_x}},"
            f"{{strip.transform.scale_y}}) "
            f"rot={{strip.transform.rotation}}"
        )
except Exception as e:
    print(f"ERROR: Failed to transform strip: {{{{e}}}}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_set_transform")
        if "STRIP_NOT_FOUND" in result:
            return f"Strip '{strip_name}' not found in timeline"
        return f"Transformed strip '{strip_name}'"

    except Exception as e:
        raise BlenderVSEError("set_transform", str(e)) from e


@blender_operation("vse_list_strips", log_args=False)
async def list_strips() -> str:
    try:
        script = """
import bpy
import json

try:
    if not bpy.context.scene.sequence_editor:
        print("VSE_EMPTY: No sequence editor. Add strips first.")
    else:
        seq = bpy.context.scene.sequence_editor
        strips = []
        for s in seq.sequences_all:
            strips.append({
                "name": s.name,
                "type": s.type,
                "channel": s.channel,
                "frame_start": s.frame_start,
                "frame_final_start": s.frame_final_start,
                "frame_final_end": s.frame_final_end,
                "mute": s.mute,
                "lock": s.lock,
                "blend_type":
                    s.blend_type if hasattr(s, 'blend_type') else 'N/A',
            })
        print(f"VSE_STRIPS: {json.dumps(strips, indent=2)}")
except Exception as e:
    print(f"ERROR: Failed to list strips: {e}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_list_strips")
        if "VSE_EMPTY" in result:
            return "No strips in Video Sequence Editor"
        return result

    except Exception as e:
        raise BlenderVSEError("list_strips", str(e)) from e


@blender_operation("vse_render_video", log_args=True)
async def render_video(
    output_path: str,
    resolution_x: int = 1920,
    resolution_y: int = 1080,
    frame_start: int = 1,
    frame_end: int = 250,
    file_format: str = "FFMPEG",
    container: str = "MPEG4",
    codec: str = "H264",
    quality: str = "MEDIUM",
    fps: int = 30,
    audio_codec: str = "AAC",
    audio_bitrate: int = 192,
) -> str:
    try:
        output_path = str(Path(output_path).absolute())
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        script = f"""
import bpy
import os

try:
{_ensure_vse_exists()}
    scene = bpy.context.scene

    if not seq.sequences:
        raise Exception("No strips in timeline to render")

    scene.frame_start = {frame_start}
    scene.frame_end = {frame_end}
    scene.frame_current = {frame_start}

    scene.render.resolution_x = {resolution_x}
    scene.render.resolution_y = {resolution_y}
    scene.render.resolution_percentage = 100
    scene.render.fps = {fps}
    scene.render.image_settings.file_format = '{file_format}'
    scene.render.ffmpeg.format = '{container}'
    scene.render.ffmpeg.codec = '{codec}'
    scene.render.ffmpeg.constant_rate_factor = '{quality}'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.ffmpeg.audio_codec = '{audio_codec}'
    scene.render.ffmpeg.audio_bitrate = {audio_bitrate}

    scene.render.use_sequencer = True

    os.makedirs(r"{output_dir}", exist_ok=True)
    scene.render.filepath = r"{output_path}"

    print(
        f"Rendering video to {{r'{output_path}'}} "
        f"frames {{scene.frame_start}}-{{scene.frame_end}}"
    )
    bpy.ops.render.render(animation=True)

    print("SUCCESS: Video render complete!")
except Exception as e:
    print(f"ERROR: Failed to render video: {{{{e}}}}")
    raise e
"""
        await _executor.execute_script(script, script_name="vse_render_video")
        n_frames = frame_end - frame_start + 1
        return f"Rendered video to {output_path} ({resolution_x}x{resolution_y}, {codec}, {n_frames} frames)"

    except Exception as e:
        raise BlenderVSEError("render_video", str(e)) from e


@blender_operation("vse_clear", log_args=True)
async def clear_vse() -> str:
    try:
        script = """
import bpy

try:
    scene = bpy.context.scene
    if scene.sequence_editor:
        seq = scene.sequence_editor
        count = len(seq.sequences_all)
        seq.clear()
        print(f"SUCCESS: Cleared {count} strips from VSE")
    else:
        print("VSE_EMPTY: Nothing to clear")
except Exception as e:
    print(f"ERROR: Failed to clear VSE: {e}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_clear")
        if "VSE_EMPTY" in result:
            return "VSE is already empty"
        return "Cleared all strips from Video Sequence Editor"

    except Exception as e:
        raise BlenderVSEError("clear", str(e)) from e


@blender_operation("vse_timeline_info", log_args=False)
async def get_timeline_info() -> str:
    try:
        script = """
import bpy
import json

try:
    scene = bpy.context.scene
    info = {
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "fps": scene.render.fps,
        "has_sequencer": scene.sequence_editor is not None,
        "strip_count": 0,
        "output_format": scene.render.image_settings.file_format,
        "sequencer_enabled": scene.render.use_sequencer,
    }
    if scene.sequence_editor:
        seq = scene.sequence_editor
        info["strip_count"] = len(seq.sequences_all)
        channels_used = sorted(
            set(s.channel for s in seq.sequences_all)
        )
        info["channels_used"] = channels_used
        info["max_channel"] = max(channels_used) if channels_used else 0
        info["min_frame"] = (
            min(s.frame_start for s in seq.sequences_all)
            if seq.sequences_all else 0
        )
        info["max_frame"] = (
            max(s.frame_final_end for s in seq.sequences_all)
            if seq.sequences_all else 0
        )
    print(f"VSE_TIMELINE: {json.dumps(info)}")
except Exception as e:
    print(f"ERROR: {{e}}")
    raise e
"""
        result = await _executor.execute_script(script, script_name="vse_timeline_info")
        return result

    except Exception as e:
        raise BlenderVSEError("timeline_info", str(e)) from e

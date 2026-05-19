# Blender MCP — Video Sequence Editor (VSE) Guide

Blender ships with a built-in, lightweight video editor called the **Video Sequence Editor (VSE)**.
The `blender_vse` MCP tool exposes 20 operations for fully automated video editing without ever opening Blender's GUI.

## Quick Start

```python
# 1. Add a video clip
blender_vse(operation="add_movie", filepath="C:/footage/clip.mp4", channel=1, frame=1)

# 2. Check what's on the timeline
blender_vse(operation="list_strips")

# 3. Render to video
blender_vse(operation="render_video", output_path="C:/output/final.mp4",
            frame_start=1, frame_end=300, resolution_x=1920, resolution_y=1080)
```

## Concepts

### Channels (Layers)
Strips stack vertically by channel number. Higher channels render on top (like layers in Photoshop).
- Channel 1: bottom (background)
- Channel 2+: progressively on top
- Audio strips typically use channels 5+

### Frames & Timing
- Frame 1 = start of timeline
- Default FPS: 30 (set via `render_video` or scene settings)
- Duration is in frames, not seconds

### Blender runs headless
All VSE operations execute via the Blender executor in `--background` mode. No GUI required.

## Operations Reference

### Strip Creation

| Operation | Key Params | Notes |
|-----------|-----------|-------|
| `add_movie` | `filepath`, `channel`, `frame`, `fit_method` | Adds video/MP4. `include_audio=True` imports audio track. |
| `add_sound` | `filepath`, `channel`, `frame` | Audio only. WAV, MP3, FLAC, OGG. |
| `add_image_sequence` | `directory`, `channel`, `frame` | All images in a folder become one strip. |
| `add_scene` | `scene_name`, `channel`, `frame` | Inserts a 3D scene as a strip. |
| `add_color` | `color_r`, `color_g`, `color_b`, `length` | Solid color matte. RGB values 0.0-1.0. |
| `add_text` | `text`, `font_size`, `length` | Text overlay with position control. |
| `add_effect` | `effect_type`, `strip1_name`, `strip2_name`, `length` | Transition/filter. Requires 1-2 input strips. |

#### Effect Types
- `CROSS` — crossfade (needs 2 strips)
- `WIPE` — wipe transition (needs 2 strips)
- `GLOW` — bloom/glow filter (needs 1 strip)
- `TRANSFORM` — 2D transform (needs 1 strip)
- `SPEED` — speed ramp (needs 1 strip)
- `ADJUSTMENT` — adjustment layer (needs 1 strip)
- `GAUSSIAN_BLUR` — blur filter (needs 0-1 strips)
- `COLOR` — color matte (needs 0 strips)
- `TEXT` — text overlay (needs 0 strips)
- `MULTICAM` — multi-camera selector (needs 2+ strips)

### Strip Editing

| Operation | Key Params | Notes |
|-----------|-----------|-------|
| `delete_strip` | `strip_name` | Removes a strip permanently. |
| `cut_strip` | `strip_name`, `frame`, `cut_type` | Splits strip at frame. SOFT preserves handles. |
| `trim_strip` | `strip_name`, `frame_start`, `frame_end` | Sets strip boundaries. |
| `move_strip` | `strip_name`, `channel`, `frame` | Rechannel or reposition. |
| `mute_strip` | `strip_name`, `mute` | Toggle mute. `True`=mute, `False`=unmute. |
| `lock_strip` | `strip_name`, `lock` | Toggle lock. `True`=lock, `False`=unlock. |

### Properties

| Operation | Key Params | Notes |
|-----------|-----------|-------|
| `set_speed` | `strip_name`, `speed_factor` | 2.0 = double speed, 0.5 = half speed. Creates speed effect strip. |
| `set_blend` | `strip_name`, `blend_type`, `blend_alpha` | Blend mode: ALPHA_OVER, CROSS, ADD, MULTIPLY, SCREEN, OVERLAY, etc. |
| `set_transform` | `strip_name`, `position_x`, `position_y`, `scale_x`, `scale_y`, `rotation` | 2D transform of strip. |

### Rendering

| Operation | Key Params | Notes |
|-----------|-----------|-------|
| `render_video` | `output_path`, `resolution_x`, `resolution_y`, `frame_start`, `frame_end`, `codec`, `container`, `fps`, `audio_codec` | Renders VSE timeline to video file. |

#### Render Codecs
- `H264` — standard, widely compatible
- `H265` — better compression, larger files
- `THEORA` — open source
- `AV1` — modern, best compression

#### Containers
- `MPEG4` — .mp4 files
- `AVI` — .avi files
- `QUICKTIME` — .mov files
- `MKV` — .mkv files
- `OGG` — .ogv files

#### Audio Codecs
- `AAC` — standard (default)
- `MP3` — widely compatible
- `PCM` — uncompressed
- `VORBIS` — open source
- `FLAC` — lossless

## Complete Workflow Example

```python
# === BUILD A SIMPLE VIDEO EDIT ===

# Step 1: Add clips
blender_vse(operation="add_movie", filepath="C:/footage/intro.mp4",
            channel=1, frame=1, strip_name="intro")
blender_vse(operation="add_movie", filepath="C:/footage/main.mp4",
            channel=1, frame=61, strip_name="main")
blender_vse(operation="add_movie", filepath="C:/footage/outro.mp4",
            channel=1, frame=181, strip_name="outro")

# Step 2: Add transitions between clips
blender_vse(operation="add_effect", effect_type="CROSS",
            strip1_name="intro", strip2_name="main",
            frame=55, length=10, channel=2, strip_name="xfade1")
blender_vse(operation="add_effect", effect_type="CROSS",
            strip1_name="main", strip2_name="outro",
            frame=175, length=10, channel=2, strip_name="xfade2")

# Step 3: Add background music
blender_vse(operation="add_sound", filepath="C:/audio/bgm.mp3",
            channel=10, frame=1, strip_name="bgm")

# Step 4: Add title text
blender_vse(operation="add_text", text="My Video Title",
            channel=3, frame=1, length=60, font_size=64,
            strip_name="title")

# Step 5: Review timeline
blender_vse(operation="list_strips")
blender_vse(operation="get_timeline_info")

# Step 6: Render final video
blender_vse(operation="render_video",
            output_path="C:/output/final.mp4",
            frame_start=1, frame_end=300,
            resolution_x=1920, resolution_y=1080,
            codec="H264", container="MPEG4",
            fps=30, quality="GOOD",
            audio_codec="AAC", audio_bitrate=192)
```

## Limitations

- **Headless only**: Blender `--background` mode. No real-time preview available.
- **No GPU preview**: In background mode, all processing is CPU-based.
- **Strip naming**: You must track strip names yourself — there's no auto-naming.
- **No audio waveform**: Audio visualization not available headless.
- **No keyframe animation of properties**: Strip transforms are static at creation time.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No strips in timeline" | Add at least one strip before rendering. |
| Strip not found | Use `list_strips` to verify exact strip names. |
| Render produces blank video | Check `scene.render.use_sequencer = True` (set automatically by `render_video`). |
| Blender not found | Configure `BLENDER_EXECUTABLE` in `config.py` or check your installation path. |
| Effect strip has no visible effect | Ensure the effect channel is above the input strips (higher channel number). |

## Cross-MCP Integration

The VSE tool works with fleet servers for end-to-end pipelines:

```
qcad-mcp (DXF) → blender_vse (title card) → blender_vse (render_video)
                                                    ↓
                                          filesystem-mcp (copy to output dir)
                                                    ↓
                                          plex-mcp (add to library)
```

Combine with `blender_render` for 3D scene turntables, then edit in VSE:
```python
blender_render(operation="render_turntable", output_dir="C:/turntable", frames=60)
blender_vse(operation="add_image_sequence", directory="C:/turntable", channel=1)
blender_vse(operation="add_text", text="Product Showcase", channel=2, length=60)
blender_vse(operation="render_video", output_path="C:/output/showcase.mp4")
```

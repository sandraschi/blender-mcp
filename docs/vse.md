# Video Sequence Editor (VSE) in blender-mcp

The `blender_vse` portmanteau tool provides Blender's built-in Video Sequence Editor
capabilities from any MCP client: strip management, effects, transitions, and rendering.

## Quick Start

```
blender_vse(operation="list_strips")
blender_vse(operation="add_movie", filepath="C:/clip.mp4", channel=1)
blender_vse(operation="add_text", text="Title", channel=3, length=120)
blender_vse(operation="render_video", output_path="C:/output.mp4", fps=30)
```

## Operations (30+)

| Operation | Params | Description |
|-----------|--------|-------------|
| `list_strips` | — | List all strips in the VSE timeline |
| `get_timeline_info` | — | Timeline metadata (resolution, fps, frame range) |
| `add_movie` | filepath, channel, start_frame | Import video clip |
| `add_sound` | filepath, channel | Import audio strip |
| `add_image` | filepath, channel, length | Import image as strip |
| `add_text` | text, channel, length, font_size | Add text overlay |
| `add_color` | color, channel, length | Add solid color strip |
| `add_effect` | effect_type, channel | Apply effect (cross, gamma, speed, etc.) |
| `add_transition` | strip_a, strip_b, transition_type | Crossfade, wipe between strips |
| `mute_strip` | strip_name, mute | Toggle strip mute |
| `delete_strip` | strip_name | Remove strip from timeline |
| `cut_strip` | strip_name, frame | Split strip at frame |
| `set_speed` | strip_name, speed_factor | Change strip playback speed |
| `set_strip_property` | strip_name, property, value | Set any strip property |
| `clear_vse` | — | Remove all strips from timeline |
| `render_video` | output_path, resolution, fps, codec | Render timeline to video file |

## Effect Types

| Effect | Description |
|--------|-------------|
| `CROSS` | Cross fade |
| `GAMMA_CROSS` | Gamma-corrected cross fade |
| `ADD` | Additive blend |
| `SUBTRACT` | Subtractive blend |
| `MULTIPLY` | Multiply blend |
| `ALPHA_OVER` | Alpha-over composite |
| `SPEED` | Speed control |
| `GLOW` | Glow effect |
| `GAUSSIAN_BLUR` | Blur effect |
| `COLOR_BALANCE` | Color correction |

## Render Formats

| Codec | Container | Quality Options |
|-------|-----------|----------------|
| H264 | MP4, MKV | GOOD, HIGH, LOSSLESS |
| H265 | MP4, MKV | GOOD, HIGH, LOSSLESS |
| DNxHD | MOV | Good, High |
| ProRes | MOV | Proxy, LT, Standard, HQ |
| PNG | Sequence | Lossless |
| JPEG | Sequence | Quality 1-100 |

## Webapp Page

Route `/video` — Strip list, add movie/sound/text controls, render settings, live output.

## Fleet Integration

```
tahoma2d-mcp (2D animation) → render frames
        │
        ▼
   blender-mcp VSE (edit, composite, render video)
        │
        ▼
   resolveops (final color grade)
```

## See Also

- `src/blender_mcp/tools/vse/vse_tools.py` — MCP tool registration
- `src/blender_mcp/handlers/vse_handler.py` — Blender Python scripts
- `webapp/frontend/src/pages/video-editor.tsx` — Webapp UI

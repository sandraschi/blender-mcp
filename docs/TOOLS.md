# blender-mcp Tool Reference (Index)

Full capability catalog: [docs/FEATURES.md](FEATURES.md). Generated API detail:
[docs/API.md](API.md). Agent-oriented reference: `llms-full.txt` at repo root.

Live inventory (always current): `GET /api/capabilities` on the backend
(`http://127.0.0.1:10849/api/capabilities`) returns every registered tool name
plus `tool_count` — prefer it over any static list.

## Tool families (portmanteau tools with `operation=` discriminators)

| Family | Examples of operations | Notes |
|--------|------------------------|-------|
| `blender_status` | `status` | Scene state, includes `blender_shutdown` (confirm-gated, DESTRUCTIVE) |
| `blender_session` | `start` | Live GUI session (needs bridge addon); batch jobs use headless |
| `blender_mesh` | mesh edit ops | Also `create_cube`, `create_cylinder`, `create_cone`, … primitives |
| `blender_materials` | `set_material`, `assign_material` | PBR, baking via pipeline tools |
| `blender_render` | `screenshot_viewport`, `render_preview`, `render_multi_angle`, `render_turntable` | Headless unless live session |
| `blender_export` | `export_scene_format`, `batch_export_objects`, `export_for_unity/unreal/vrchat` | GLB/GLTF/FBX/OBJ/USD/VRM |
| `blender_script_execute` | inline `bpy` | Headless executor with timeout |
| `blender_ai_generate` | `ai_generate_mesh`, Rodin/Tripo/Hunyuan hooks | Needs LLM/API keys |
| `agentic_blender_workflow` | `workflow_prompt` | Multi-step natural-language builds (ctx.sample + Ollama fallback) |
| `intelligent_3d_processing` | batch pipelines | Decimation, cleanup, batch ops |
| `manage_object_repo` | `save`, `load`, `search`, `list_objects` | Local asset repository |
| `manage_blender_addons` | `search`, `install_known`, `install_url` | Incl. bridge addon management |
| `blender_api_docs` | `bpy` reference lookup | Offline-capable docs |
| `blender_vse` | `vse_render_video` | Video sequence editor, headless MP4 |

## Conventions

- Every tool returns `{success, message, ...}` (dialogic shape) unless it streams.
- Mutating tools carry `annotations=` hints (READ_ONLY / MUTATING / DESTRUCTIVE).
- Headless is the default; pass `prefer_session=False` to force headless batch mode.
- Set `BLENDER_EXECUTABLE` when Blender is not on PATH (see CONFIGURATION.md).

# Improvement Roadmap

Phased plan derived from [COMPETITIVE_ANALYSIS.md](COMPETITIVE_ANALYSIS.md).

## Phase 1 — Agent vision and surface wiring (0.8.0)

**Status: complete**

| Item | Tool / module |
|------|----------------|
| Live-session-first execution | `utils/blender_runtime.py` |
| Viewport screenshot + base64 | `blender_render` → `screenshot_viewport` |
| Multi-angle stills | `blender_render` → `render_multi_angle` |
| Shader node graph | `blender_shaders` |
| Compositor graph | `blender_compositor` |
| Export formats | `blender_export` → GLTF, GLB, FBX, OBJ, STL, USD, VRM, Unreal |
| Blender API docs | `blender_api_docs`, resource `blender://api/{identifier}` |
| Fix shader node properties bug | `handlers/shader_handler.py` |

### Live GUI workflow

```powershell
# Terminal: HTTP MCP server (webapp does this via start.ps1)
uv run python -m blender_mcp.cli --http --port 10849

# Agent or user:
# blender_session operation=start
# Enable docs/blender_bridge_addon.py in Blender → Start Bridge
# blender_render operation=screenshot_viewport output_path=...
```

## Phase 2 — Jobs and modeling depth (0.8.1)

**Status: complete**

| Item | Tool / module |
|------|----------------|
| Async job queue | `blender_jobs` (`submit`, `status`, `list`, `cancel`) |
| Mesh edit portmanteau | `blender_mesh` → extrude, inset, bevel_modifier, subdivide, merge_vertices, delete_faces, join, separate_loose, triangulate |

## Phase 3 — Generative and procedural (0.9.0)

**Status: complete**

| Item | Tool / module |
|------|----------------|
| AI mesh backends (Rodin/Hunyuan/Tripo) | `blender_ai_generate` |
| Vision refinement loop | `blender_vision_refine` |
| Geometry nodes | `blender_geonodes` |
| Optional socket-only addon mode | deferred — HTTP + bridge addon cover live GUI |

### AI mesh API keys

| Backend | Environment variable |
|---------|---------------------|
| Tripo | `TRIPO_API_KEY` |
| Rodin (Hyper3D) | `RODIN_API_KEY` or `HYPER3D_API_KEY` |
| Hunyuan3D | `HUNYUAN3D_API_KEY` (+ optional `HUNYUAN3D_API_URL`) |

## Phase 4 — Measurement and polish (0.9.1)

**Status: complete**

| Item | Tool / module |
|------|----------------|
| Mesh validation audit | `blender_validation` → `validate_geometry`, `check_manifold` |
| Wire `rendering_handler` | `blender_render` → `set_engine`, `configure_layers`, `setup_post_processing` |
| Dedupe addon tools | `blender_addons` canonical; `manage_blender_addons` alias |
| `blender_batch` | resize, convert, export |

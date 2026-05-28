# Competitive Analysis — Blender MCP Ecosystem

Last updated: 2026-05-28

This document compares **sandraschi/blender-mcp** (this repo) with other Blender MCP
projects on GitHub and records what we adopt, what we skip, and our differentiation.

## Summary

| Repo | Scale | Architecture | Standout |
|------|-------|--------------|----------|
| [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) | ~22k stars | Socket addon + `uvx` MCP | Viewport screenshots, Rodin/Hunyuan3D, Poly Haven, Sketchfab |
| [RFingAdam/mcp-blender](https://github.com/RFingAdam/mcp-blender) | 218 atomic tools | Addon + MCP server | Mesh editing (24), GeoNodes, AI gen, vision refinement loop |
| [zorak1103/blender-mcp](https://github.com/zorak1103/blender-mcp) | Newer | HTTP MCP inside Blender | Shader node graph, batch modifiers, bearer auth |
| [djeada/blender-mcp-server](https://github.com/djeada/blender-mcp-server) | 27 tools | Socket addon | Async job queue for long scripts |
| [bpype/blender_mcp](https://github.com/bpype/blender_mcp) | Blender Lab adjacent | Addon + MCP | `get_python_api_docs`, blend-file introspection |
| **sandraschi/blender-mcp** | ~58 portmanteau tools | HTTP FastMCP + headless + **live bridge** | VRM/VR, VSE, splats, AI construction, fleet webapp |

## Where we lead

- **VRM / VR platforms** — validation, metadata, VRChat/Resonite/Unity/Unreal export paths
- **VSE** — 20 video-editing operations (rare in MCP repos)
- **Gaussian splats** — import, crop, collision proxy, Resonite export
- **AI construction** — `construct_object`, agentic workflows, object repository
- **Fleet ops** — webapp dashboard, MCPB, Tauri native app, `just` recipes
- **Portmanteau design** — fewer MCP tools, richer `operation` enums (better for LLM context)
- **Dual execution** — headless subprocess **and** live GUI via `blender_session` + bridge addon

## Gaps we are closing (roadmap)

See [ROADMAP.md](ROADMAP.md) for phase tracking.

| Gap (competitors have) | Our response | Phase |
|------------------------|--------------|-------|
| Viewport screenshot / vision loop | `blender_render` → `screenshot_viewport`, `render_multi_angle` | 1 (done) |
| Shader / compositor node tools | `blender_shaders`, `blender_compositor` | 1 (done) |
| Export glTF/FBX/OBJ/STL/USD/VRM/Unreal | `blender_export` format ops | 1 (done) |
| `get_python_api_docs` | `blender_api_docs` + `blender://api/{id}` resource | 1 (done) |
| Async long-running jobs | `blender_jobs` | 2 (done) |
| Mesh editing (extrude, bevel, …) | `blender_mesh` edit operations | 2 (done) |
| AI mesh generation (Rodin/Hunyuan) | `blender_ai_generate` | 3 |
| Vision refine loop | `blender_vision_refine` | 3 |
| Geometry nodes portmanteau | `blender_geonodes` | 3 |

## What we deliberately skip

- **218 separate atomic tools** — context explosion; we use portmanteau + CodeMode discovery
- **MSFS livery pipeline** (RFingAdam) — niche unless user demand
- **PyPI-only `uvx blender-mcp`** as sole install — our stack includes webapp/fleet/MCPB
- **Nonexistent Docker image** — removed from install docs (no `ghcr.io/sandraschi/blender-mcp`)

## Architecture comparison

```
ahujasid / djeada:  MCP client → stdio MCP → socket addon → Blender GUI

sandraschi:         MCP client → stdio OR HTTP (/mcp on :10849)
                              → headless Blender subprocess (default)
                              → OR live bridge addon (polls /api/v1/blender/pending)
```

HTTP Streamable transport is **already implemented** in `src/blender_mcp/transport.py`
(`--http`, `MCP_TRANSPORT=http`, default port 10849). The webapp and bridge addon use
this HTTP surface — not a separate transport stack.

## Live GUI vs headless

| Mode | Best for | How |
|------|----------|-----|
| **Live GUI** | User watches agent build; viewport screenshots | `blender_session` start + bridge addon |
| **Headless** | Fleet batch, CI, no display | `BlenderExecutor` subprocess (default) |

Phase 1 added `blender_runtime.execute_bpy_script()` — tries live session first when
`prefer_session=True`, falls back to headless.

## References

- [INSTALL.md](../INSTALL.md) — setup including bridge addon
- [ROADMAP.md](ROADMAP.md) — phased improvement plan
- [CHANGELOG.md](../CHANGELOG.md) — release history

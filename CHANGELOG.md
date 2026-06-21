
## [Unreleased] — 2026-06-14

### Fixed
- Tauri build: resolved Rust crate conflict (brotli/alloc-no-stdlib)
- Tauri build: fixed PyInstaller path mismatch (hyphen to underscore in src dirs)
- Tauri build: fixed TypeScript errors (unused imports, useRef arg, import.meta.env)
- Tauri CORS: allow_origins includes tauri://localhost for WebView access

### Added
- CUA-NSIS: just cua-nsis-test recipe, smoke script, config
- CUA-NSIS: build.ps1 now copies NSIS installer to dist/
- CUA-NSIS: 11-phase smoke test (install, launch, WebView OCR, diagnostics, uninstall)
- CUA-NSIS: local certification — all 11 phases pass locally (2026-06-14)

# Changelog

All notable changes to **Blender MCP** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.10.0] - 2026-05-28

### Added
- **Phase 5 — Sculpting, telemetry, Docker** (see [docs/ROADMAP.md](docs/ROADMAP.md))
  - **`blender_sculpt`**: enter/exit sculpt, set_brush, dynotopo, symmetrize, mask_clear, remesh_voxel, list_brushes
  - **Prometheus telemetry**: tool call counters/histograms, job gauge, `/metrics` + optional `PROMETHEUS_PORT`
  - **JSON logging** for Loki: `BLENDER_MCP_LOG_FORMAT=json`
  - **Docker**: streamlined `Dockerfile`, `docker-compose.yml` with optional monitoring profile
  - **Docs**: [docs/MONITORING.md](docs/MONITORING.md), [docs/DOCKER.md](docs/DOCKER.md)
  - **Optional dep**: `uv sync --extra monitoring` (`prometheus-client`)
- **Tests**: `tests/test_phase5_tools.py`

### Changed
- **Dockerfile**: HTTP MCP default, Blender 4.2 Linux, GHCR-ready production target
- **CI**: existing `build-docker` job publishes to `ghcr.io/sandraschi/blender-mcp`

## [0.9.1] - 2026-05-28

### Added
- **Phase 4 — Measurement & polish** (see [docs/ROADMAP.md](docs/ROADMAP.md))
  - **`blender_validation`**: `validate_geometry`, `check_manifold` mesh audits (polycount, non-manifold, loose geometry)
  - **`blender_render`**: `set_engine`, `configure_layers`, `setup_post_processing` wired from `rendering_handler`
  - **`blender_batch`**: resize, convert, export batch ops
  - **`blender_addons`**: consolidated enable/disable/install_known/info (canonical addon tool)
  - **`manage_blender_addons`**: compatibility alias delegating to `blender_addons`
  - **`scripts/smoke_test.py`**: headless registration + bpy smoke test
- **Tests**: `tests/test_phase4_tools.py`

### Fixed
- **`blender_geonodes`**: script indentation (textwrap.dedent) for headless execution
- **`set_render_engine`**: invalid f-string referencing undefined `scene` at template build time

## [0.9.0] - 2026-05-28

### Added
- **Phase 3 — Generative & procedural** (see [docs/ROADMAP.md](docs/ROADMAP.md))
  - **`blender_ai_generate`**: Rodin (Hyper3D), Tripo, Hunyuan backends; generate + import into Blender
  - **`blender_geonodes`**: create_group, add_node, connect_nodes, assign_modifier, add_input, list_node_types
  - **`blender_vision_refine`**: capture, review_bundle (multi-angle + scene summary), apply_script refinement loop
  - **`utils/ai_mesh_backends.py`**: async submit/poll/download for external AI mesh APIs
- **Tests**: `tests/test_phase3_tools.py`

## [0.8.1] - 2026-05-28

### Added
- **Phase 2 — Async jobs & mesh editing** (see [docs/ROADMAP.md](docs/ROADMAP.md))
  - **`blender_jobs`**: submit, status, list, cancel for long-running bpy scripts
  - **`blender_mesh` edit ops**: extrude, inset, bevel_modifier, subdivide, merge_vertices, delete_faces, join, separate_loose, triangulate
  - **`handlers/mesh_edit_handler.py`**: edit-mode ops via live session when bridge connected
- **Tests**: `tests/test_phase2_tools.py`

## [0.8.0] - 2026-05-28

### Added
- **Phase 1 — Agent vision & tool surface** (see [docs/ROADMAP.md](docs/ROADMAP.md), [docs/COMPETITIVE_ANALYSIS.md](docs/COMPETITIVE_ANALYSIS.md))
  - **`blender_runtime`**: live Blender session preferred over headless subprocess when bridge is connected
  - **`blender_render`**: `screenshot_viewport` (PNG path + base64), `render_multi_angle` for review loops
  - **`blender_shaders`**: create_material, create_node, connect_nodes, list_node_types
  - **`blender_compositor`**: enable, add_node, connect_nodes, glow
  - **`blender_export`**: export_gltf, export_glb, export_fbx, export_obj, export_stl, export_usd, export_vrm, export_unreal
  - **`blender_api_docs`** tool and **`blender://api/{identifier}`** MCP resource
- **Documentation**: aligned [INSTALL.md](INSTALL.md) + [docs/installation.md](docs/installation.md); competitive analysis and roadmap docs
- **Tests**: `tests/test_phase1_tools.py`

### Fixed
- **`create_shader_node`**: undefined `properties` parameter in generated script (now `node_properties`)

### Changed
- Install docs: corrected `just`/`uv sync` flow; MCPB install options; removed nonexistent Docker image reference

## [0.7.0] - 2026-05-19

### Added
- **Video Sequence Editor (VSE)**: Full Blender built-in video editor exposed as a `blender_vse` portmanteau tool with 20 operations.
  - **Strip Creation**: `add_movie`, `add_sound`, `add_image_sequence`, `add_scene`, `add_color`, `add_text`, `add_effect`
  - **Strip Editing**: `delete_strip`, `cut_strip`, `trim_strip`, `move_strip`, `mute_strip`, `lock_strip`
  - **Properties**: `set_speed`, `set_blend`, `set_transform`
  - **Information**: `list_strips`, `get_timeline_info`
  - **Output**: `render_video` — render VSE timeline to H264/MPEG4 with configurable resolution, FPS, codec, quality
  - **Cleanup**: `clear_vse`
- **VSE Handler** (`handlers/vse_handler.py`): 20 bpy script generators for headless Blender VSE operations
- **VSE Exception** (`BlenderVSEError`): dedicated error type for video editing failures
- **VSE Help**: new "Video Editing" category in the help system
- **VSE Documentation**: `docs/blender/VSE_GUIDE.md` — complete usage guide
- **Webapp — Video Editor Page** (`/video`): new sidebar tab for VSE strip management and rendering

## [0.6.1] - 2026-04-27

### Added
- **Industrial Startup Script**: New root `start.ps1` with `-Headless`, `-BackendOnly`, and `-NoBrowser` support.
- **Port Management**: Automatic port clearing and backend polling for robust dev starts.

## [0.6.0] - 2026-04-24

### Added
- **FastMCP 3.2.0 Parity**: Full integration of native **Prompts** and formalized **Skills**.
- **Native Prompts**: Introduced `optimize-3d-scene` and `agentic-robot-creation` templates for standard 3D workflows.
- **Formalized Skills**: Migrated agentic workflows to the industry-standard **Claude Skills (`SKILL.md`)** format.
- **Enhanced Sampling Logic**: Refined autonomous creation loops within `agentic.py` for more robust multi-step reasoning.

## [0.5.0] - 2026-04-14

### Added
- **Industrial Quality Stack**: Integrated **Biome** (frontend) and **Ruff** (core) for high-performance, Rust-native linting and formatting.
- **Protocol Hardening**: Purged all protocol-breaking `print` and `console.log` statements from main processes to ensury strict JSON-RPC compliance for stdio transport.
- **FastMCP 3.2.0**: Official support and alignment with the latest fleet-wide SOTA standards.
- **Unified Justfile**: Refactored root recipes for single-pass linting and fixing across the entire Python + TypeScript repository.

### Changed
- `pyproject.toml`: Hardened Ruff `T201` checks with surgical `per-file-ignores` for CLI and test runners.
- `webapp/frontend`: Set Biome `noConsoleLog` to `"error"` for automated compliance monitoring.

## [0.4.3] - 2026-04-10

### Added

### Fixed
- `compat.py`: removed `Tool = None` pre-assignment footgun; FastMCP 3.x imports are now direct eager imports that fail loudly with a clear `pip install 'fastmcp>=3.1.1'` message
- `app.py`: version reads from `__version__` dynamically; instructions bumped to FastMCP 3.1.1 with CodeMode noted; health endpoint no longer hardcodes stale date
- `config.py`: fixed mangled docstring; default Blender path now probes a candidate list (4.2/4.3/4.4 Windows, common Linux paths) rather than one hardcoded string
- `decorators.py`: fixed mangled `from ..compat import *` comment leaked into docstring
- `transport.py`: `FastMCP 2.14.4+` references updated to `3.1.1`
- `agentic.py`: `@app.tool()` with parens → `@app.tool` for all three tools (FastMCP 3.x style)
- `construct_tools.py`: added `_model_dump()` pydantic v1/v2 shim; `validation.dict()` → `_model_dump(validation)`; `_gather_construction_context` rewritten using executor (removes broken `get_scene_info` import); `_analyze_reference_object` stub replaced with real executor call; dangling discarded f-string prompt wired properly to `ctx.sample()`
- `repository_tools.py`: imported and used `_model_dump`; `_save_object` documents session-context limitation with `session_required` flag and glTF fallback; `construct_and_save` compound operation added
- `addon_tools.py`: `list_installed` boolean filter logic fixed; deferred `import json` in enable/disable lifted to local aliases

### Removed
- `server_fixed.py`, `server_fixed.bak` — broken old alternate entrypoints
- `server_new.py` — obsolete FastMCP 2.10 stub
- `update_imports.py` — one-shot migration script, no longer needed

### Added
- `tests/conftest.py` — shared fixtures: session event loop, autouse env vars, mock executor factory, mock ctx, temp repo dir with auto-patching
- `__init__.py` version: `0.4.1`

## [0.4.3] - 2026-03-29

### Added

- **`blender_session` MCP tool** (`session_tools.py`): start/stop/status/run_script/demo
  - `start`: launches Blender GUI (`subprocess.Popen`, no `--background`) with optional `.blend` file; prints setup instructions for bridge addon
  - `stop`: terminates the managed process cleanly
  - `status`: checks PID and running state; hints on bridge setup
  - `run_script`: executes Python in running Blender via bridge (`_exec_in_blender_session`)
  - `demo`: runs a named built-in demo through the bridge (4 demos available)
- **Demo scripts** (`data/scripts/demos.json`): 4 complete scene demos
  - `living_room_with_car`: interior living room + sports car + 3-keyframe camera flythrough
  - `driver_training`: bird's-eye overhead track with car at start line
  - `garden`: garden with fence scene + sun/fill lighting + camera
  - `house_interior`: open-front house shell + sofa + bookshelf + lighting
- **Additional scripts**:
  - `data/scripts/houses.json`: `basic_house` — four-wall house with pitched roof, chimney, door, windows, brick + tile materials
  - `data/scripts/nature.json`: `driver_training_layout` — 50×40 tarmac range with kerbs, lane markings, roundabout, cones; `garden_with_fence` — lawn, picket fence with gate, flower beds, path slabs, bench
- **Fixed `status_tools.py`**: rewritten with correct control flow — the original had `if operation == "status": status_parts = []` followed by body code that ran regardless of branch (classic Python fall-through in if/elif chains without returns). All four operations now properly isolated.
- **Tests**: `tests/test_session_tools.py` (15 tests: status/start/stop/run_script/demo/unknown), `tests/test_status_tools.py` (10 tests: json format, text format, no fall-through, system_info, health_check, monitor, unknown)

### Changed

- `data/scripts/` now has 7 categories: `robots`, `furniture`, `rooms`, `vehicles`, `houses`, `nature`, `demos`



### Added

- **Real construction scripts** (`data/scripts/`): JSON files replacing all mock script stubs
  - `robots.json`: `classic_robot` (bipedal, jointed arms/legs, gunmetal + amber eyes), `industrial_robot_arm` (6-axis, yellow paint)
  - `furniture.json`: `modern_chair` (Scandinavian, tapered legs, teal fabric + oak), `coffee_table` (glass top + walnut), `bookshelf` (5-shelf oak)
  - `rooms.json`: `living_room` (floor, walls, sofa, coffee table, floor lamp, area rug, full materials)
  - `vehicles.json`: `sports_car` (body, cabin, spoiler, torus wheels + hubcaps, gloss red + rubber + chrome)
- **Blender Bridge Addon** (`docs/blender_bridge_addon.py`): installable Blender addon that solves the session context limitation
  - Starts background poll thread hitting `GET /api/v1/blender/pending`
  - Executes queued scripts in the live Blender session via `bpy.app.timers` (thread-safe)
  - POSTs results back to `/api/v1/blender/result`
  - Properties panel in Properties > Scene > Blender MCP Bridge
- **Session bridge HTTP endpoints** on the MCP server:
  - `POST /api/v1/blender/exec` — queue a script for the bridge
  - `GET /api/v1/blender/pending` — bridge polls this
  - `POST /api/v1/blender/result` — bridge posts execution result here
- **`_exec_in_blender_session()`** async helper in `app.py`: queues a task, waits up to 30 s for result
- **`_session_tasks`** in-process task queue (no external dependencies)
- **`data/scripts/` path resolution** in `_load_script_collection`: reads from `data/scripts/{category}.json` relative to `app.py`; falls back to empty list — no mock data remains
- **`/tool` endpoint docstring** documents the Script Editor one-liner for calling MCP tools from Blender without the addon

### Fixed

- **`manage_object_construction` — `modify` operation unreachable**: stray `return construct_result` before `elif operation == "modify":` made the entire modify branch dead code
- **`_save_object` session bridge integration**: now tries `_exec_in_blender_session()` first; only falls back to executor + placeholder if bridge not connected; `session_required` flag set correctly based on actual execution path
- **`data/secrets/jwt_secret.txt` exposed**: deleted plaintext secret; `data/secrets/` and `*.bak` added to `.gitignore`

### Changed

- `_load_script_collection` now reads from `data/scripts/{category}.json`; mock inline dict removed entirely
- `_load_specific_script` simplified (no longer needs a separate impl)



### Added

- **Addon Management Tool** (`manage_blender_addons`): Full MCP-exposed addon lifecycle
  - `search` / `info` / `install_known` / `install_url` / `list_installed` / `enable` / `disable`
  - Known-addon registry includes `gaussian_splat`, `3dgs_blender`, `openscatter`, `asset_bridge`, `blender_gis`, `blender_tools_collection`
  - Auto-discovers Blender addons directory on Windows and Linux without environment variable
- **WorldLabs Gaussian Splat import** (`blender_splatting` operation `worldlabs`):
  - Probes running Blender for a 3DGS operator; auto-installs `gaussian_splat` addon from GitHub if missing
  - Falls back through three import operators: `import_scene.gaussian_splat` → `import_mesh.fastgs` → `import_mesh.ply`
  - Returns actionable error with exact fix command if all operators missing
- **Real object repository** (`manage_object_repo`):
  - `save`: exports active Blender object as `.blend` via executor, writes `metadata.json`, updates `~/.blender-mcp/repository/repository_index.json`
  - `load`: appends stored `.blend` into current scene via `bpy.data.libraries.load`, applies position/scale
  - `search`: real index query with query/category/tags/quality filters
  - `list_objects`: returns full index from disk
- **Real object info query** (`_get_object_info`): Blender executor call returning type, vertex count, materials, bone count, dimensions
- **Real construction script execution** (`_execute_construction_script`): fixed broken `execute_blender_script(timeout_seconds=...)` call to correct `execute_script(timeout=...)` signature; appends post-execution object detection
- **Real object backup** (`_create_object_backup`): duplicates object in Blender, hides from viewport/render
- **Real modification script execution** (`_execute_modification_script`): runs via executor, returns actual Blender output
- **Real cross-MCP export** (`export_for_mcp_handoff`):
  - VRChat: opens `.blend`, optionally decimates over 70k poly limit, exports FBX via `bpy.ops.export_scene.fbx`
  - Resonite: opens `.blend`, exports GLB via `bpy.ops.export_scene.gltf`
  - Both write actual files to a temp directory and return real paths
- **Real `_get_asset_from_repository`**: reads `metadata.json` from disk; returns actual polygon count and material list from stored `obj_info`
- **Real `_find_construction_script`**: searches repository index JSON for stored construction script; returns `None` honestly if absent
- **Webapp — Repository page** (`/repository`): browse, search, save, load objects from the repository
- **Webapp — Addon Manager page** (`/addons`): search, install, enable/disable Blender addons; WorldLabs splat workflow guide
- **Updated `mcp.ts`**: added `repositoryList`, `repositorySave`, `repositoryLoad`, `repositorySearch`, `addonManage`, `splatWorldlabs` API helpers

### Fixed

- **`download_tools.py`**: replaced blocking synchronous `requests.get()` with async `httpx.AsyncClient` + streaming — no more event loop blocking on downloads
- **`splatting_handler.py`**: removed top-level `import bpy` that crashed the MCP server process on startup; all handlers now use executor subprocess pattern
- **`construct_tools.py`**: fixed `_execute_construction_script` calling nonexistent `execute_blender_script(timeout_seconds=..., max_memory_mb=...)` — corrected to `get_blender_executor().execute_script(timeout=120)`
- **`repository_tools.py`**: replaced all 9 stub/mock helpers with real implementations
- **`pyproject.toml`**: removed `black`, `flake8`, `isort`, `mypy`, `pytest`, `pytest-cov`, `ruff`, `pre-commit` from runtime dependencies (were incorrectly in `[project.dependencies]`)
- **`pyproject.toml`**: bumped `fastmcp>=3.1.1` (fixes CodeMode BM25 tool discovery broken by `pydantic-monty` 0.0.8)
- **`pyproject.toml`**: removed `[tool.black]` section; ruff `target-version` and mypy `python_version` corrected from `py38` to `py312`; classifiers fixed to match `requires-python = ">=3.12"`
- **`pyproject.toml`**: removed duplicate `ruff>=0.1.6` dev dependency; consolidated to `ruff>=0.14.0`

### Changed

- `blender_splatting` tool now exposes `worldlabs` operation in addition to existing operations
- `splatting_handler.py` rewritten; all operations now return structured dicts via executor rather than calling bpy directly
- Repository engine now writes to `~/.blender-mcp/repository/` with a flat JSON index

---

## [0.3.0] - 2026-01-19

### Added
- **AI Construction System**: `manage_object_construction`, `manage_object_repo`
- FastMCP 2.14.3 sampling integration for conversational 3D creation
- Multi-layer security validation (syntax, security scoring, sandbox execution)
- MCP Resource System: URI-based script collections (`blender://scripts/...`)
- Enhanced CLI with `--list-tools` and `--show-config`
- Portmanteau tool consolidation

### Fixed
- Critical import issues for `Context` and `ScriptValidationResult`
- Logger standardisation (print → logging)
- Cross-platform compatibility (Windows/PowerShell)

---

## [0.2.0] - 2026-01-15

### Added
- 8 Advanced VR tools: `blender_validation`, `blender_splatting`, `blender_materials_baking`,
  `blender_vrm_metadata`, `blender_atlasing`, `blender_shapekeys`, `blender_export_presets`
- Gaussian Splatting support with proxy objects and collision meshes
- VRChat / Resonite / Unity / VRM export pipeline
- PBR conversion and texture atlasing

---

## [0.1.0] - 2025-12-24

### Added
- Initial alpha release
- Basic Blender connectivity and core MCP server implementation
- Development infrastructure (CI/CD, testing, documentation)

---

## Release Process

1. Update version in `src/blender_mcp/__init__.py`
2. Update `CHANGELOG.md`
3. Create pull request — CI/CD handles the rest

### Version Types
- **PATCH** (`0.0.X`): Bug fixes, small improvements
- **MINOR** (`0.X.0`): New features, backwards compatible
- **MAJOR** (`X.0.0`): Breaking changes

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).*



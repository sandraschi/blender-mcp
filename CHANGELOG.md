# Changelog

All notable changes to **Blender MCP** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2026-03-29

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

# Blender MCP — Project Assessment

**Assessment Date**: 2026-03-29
**Version**: 0.4.2
**Status**: Active Development — Production-Grade Core, Continued Feature Work

---

## Executive Summary

Blender MCP is a FastMCP 3.1.1 server exposing Blender 3D operations as MCP tools,
enabling AI-driven 3D creation workflows from natural language through to VR-ready
exports. The codebase has CI/CD, mcpb packaging, Glama.ai publication, and a React
webapp frontend.

Versions 0.4.0 and 0.4.1 represent a substantial quality pass: 9 stub/mock
implementations replaced with real Blender executor calls, 7 distinct bugs fixed
across the core package (broken function signatures, top-level `import bpy`,
blocking async I/O, pydantic compat, dead f-string prompt, `compat.py` footgun),
and housekeeping across version strings, docstrings, orphan files, and the test
scaffold.

---

## Capability Matrix

| Area | Status | Notes |
|------|--------|-------|
| Core MCP server (stdio + HTTP) | Production | FastMCP 3.1.1, transport layer clean |
| Blender executor (subprocess) | Production | Async, timeout, process kill, TBBmalloc tolerance |
| Mesh / scene / transform tools | Production | 40+ tools across handlers |
| Material / texture tools | Production | PBR, procedural, UV |
| Animation / rigging | Production | Keyframes, shape keys, IK, NLA |
| Render tools | Production | Cycles, EEVEE, all output formats |
| Import / export | Production | FBX, OBJ, glTF, VRM, PLY, USD, Alembic |
| VR pipeline (VRChat, Resonite) | Production | Validation, atlasing, export presets |
| Object repository | Fixed 0.4.0 | Real .blend save/load/search; session-required flag documented |
| Cross-MCP export (VRChat/Resonite) | Fixed 0.4.0 | Real FBX/GLB export via executor |
| AI construction (sampling) | Functional* | Requires sampling-capable client; prompt was previously discarded |
| Addon management | New 0.4.0 | Install, enable, disable, known-addon registry |
| Gaussian Splat / WorldLabs import | Fixed 0.4.0 | Auto-install addon, 3-operator fallback chain |
| Asset library (PolyHaven) | Production | Real API, real async download |
| Download tool | Fixed 0.4.0 | Async httpx; was blocking event loop |
| Webapp frontend | Active | React/Tailwind; Repository + Addon Manager pages added |
| Test coverage | Improved | 6 test files, ~80 tests; integration tests still need live Blender |
| Version hygiene | Fixed 0.4.1 | All version strings, docstrings, orphan files cleaned |

*AI construction requires Claude Desktop or Antigravity as MCP client (sampling support).

---

## What Was Fixed in 0.4.0

### Critical Bugs
- `splatting_handler.py`: top-level `import bpy` crashed MCP server on startup —
  rewritten to executor subprocess pattern
- `construct_tools.py`: called nonexistent `execute_blender_script(timeout_seconds=...,
  max_memory_mb=...)` — fixed to `executor.execute_script(timeout=120)`
- `download_tools.py`: synchronous `requests.get()` in async tool blocked the event
  loop — replaced with async `httpx.AsyncClient` streaming

### Stubs Replaced (all previously returned mock data or unconditional `True`)
- `_get_object_info` — real Blender executor call
- `_find_construction_script` — searches repository index JSON
- `_save_object` — exports glTF/blend via executor; writes metadata; updates index;
  documents session_required limitation
- `_load_object` — appends .blend via `bpy.data.libraries.load`
- `_list_objects` / `_search_objects` — real index reads with filter support
- `_create_object_backup` — duplicates object in Blender, hides from viewport/render
- `_execute_modification_script` — runs via executor, returns real output
- `_get_asset_from_repository` — reads metadata.json from disk
- `VRChatExportEngine.export_blend_file` — real FBX via executor
- `ResoniteExportEngine.export_blend_file` — real GLB via executor

### New Capabilities
- `manage_blender_addons` MCP tool: search, install_known, install_url,
  list_installed, enable, disable
- `blender_splatting` operation `worldlabs`: probes for 3DGS operator, auto-installs
  `gaussian_splat` addon, falls back across three operators
- `construct_and_save` compound operation: construct → validate → execute → save
- Webapp: Repository page (`/repository`), Addon Manager page (`/addons`)
- `mcp.ts`: `repositoryList/Save/Load/Search`, `addonManage`, `splatWorldlabs`

---

## What Was Fixed in 0.4.1

### Logic Bugs
- `construct_tools._generate_construction_script`: full prompt was built into a
  discarded f-string expression (never sent to LLM); now assigned and passed as
  `content=` to `ctx.sample()` with all context fields
- `construct_tools._gather_construction_context`: broken `from
  blender_mcp.handlers.scene_handler import get_scene_info` (function doesn't exist);
  replaced with real executor call returning scene object/material counts
- `construct_tools._analyze_reference_object`: was a stub returning hardcoded
  `{"type": "mesh", "vertex_count": 0}`; replaced with real executor call
- `addon_tools.list_installed`: `not {enabled_only} or mod_name` was always True;
  fixed to correct logic iterating `preferences.addons.keys()`
- `addon_tools` enable/disable: deferred `import json` inside branch caused scope
  issues; lifted to local alias at point of use

### Pydantic Compat
- `_model_dump()` shim added to `construct_tools` and imported into
  `repository_tools`; all `validation.dict()` and `validation.model_dump()` calls
  replaced with `_model_dump(validation)` — works on both pydantic v1 and v2

### Repository Save Session Context
- `_save_object` now documents that `--factory-startup` executor starts a fresh empty
  scene; attempts glTF export first, falls back to placeholder blend, records
  `session_required: True` in metadata and return value with a clear note

### Version / Housekeeping
- `__init__.py`: bumped `0.2.0` → `0.4.1`
- `app.py`: version now reads from `__version__` dynamically; instructions and health
  endpoint no longer hardcode stale version strings
- `config.py`: junk `from ..compat import *` comment removed from docstring; default
  Blender path now uses `_find_default_blender()` probing 4.2/4.3/4.4 on Windows and
  common Linux paths
- `decorators.py`: same junk comment removed from docstring
- `transport.py`: all `FastMCP 2.14.4+` references updated to `3.1.1`
- `compat.py`: replaced `Tool = None` / `FunctionTool = None` pre-assignment footgun
  with direct eager imports that fail loudly with a clear install message
- Orphan files removed: `server_fixed.py`, `server_new.py`, `server_fixed.bak`,
  `update_imports.py` — all pre-refactor artefacts
- All `.bak` files from the editing session deleted

### Test Scaffold
- `tests/conftest.py` created: session-scoped event loop, autouse env/repo path
  patching, `make_mock_executor`, `mock_ctx`, `repo_dir` fixtures, marker registration
- `tests/test_construct_tools.py`: 25 tests — `_model_dump`, validation, extraction,
  context gathering, reference object analysis, script generation (with prompt content
  verification), execution, summary
- `tests/test_fixes_0_4_1.py`: session_required path, construct_and_save short-circuit,
  search edge cases, JSON-serialisable output
- `tests/test_repository.py`: 15 tests — object info, save, list, search, find script,
  get asset
- `tests/test_addon_handler.py`: 8 tests — search, addons dir, install from URL,
  tool registration
- `tests/test_splatting.py`: 9 tests — import (file not found/bad format/no
  operator/success/crash), collision mesh, Resonite export

---

## Known Remaining Issues

| Issue | Priority | Notes |
|-------|----------|-------|
| `_save_object` requires active Blender session | Medium | Documented; `session_required` flag returned; fix = HTTP bridge or addon-side call |
| Resource scripts in `app.py` are mock data | **Fixed 0.4.2** | Real scripts in `data/scripts/*.json`; 7 working bpy scripts across robots/furniture/rooms/vehicles |
| Session context limitation for `_save_object` | **Fixed 0.4.2** | Bridge addon + `/api/v1/blender/exec|pending|result` endpoints; `_exec_in_blender_session()` helper |
| `modify` operation unreachable in `manage_object_construction` | **Fixed 0.4.2** | Dead `return` statement removed |
| Plaintext JWT secret in `data/secrets/jwt_secret.txt` | **Fixed 0.4.2** | File deleted; `data/secrets/` and `*.bak` added to `.gitignore` |

---

## Architecture Notes

### Repository Layout (`~/.blender-mcp/repository/`)
```
repository/
  repository_index.json          # flat index, updated on every save
  {obj_id}/
    metadata.json                # full metadata including obj_info, blend_file, session_required
    model_{version}.glb          # glTF export (preferred, works headless)
    model_{version}.blend        # blend export (requires active session or placeholder)
```

### Executor Pattern
All Blender operations run via `BlenderExecutor.execute_script(script, timeout=N)`:
1. Write script to temp file
2. Launch `blender --background --factory-startup --enable-autoexec --python {script}`
3. Capture stdout/stderr
4. Parse structured output via sentinel prefixes (`GS_RESULT:`, `OBJ_INFO:`,
   `EXPORT_OK:`, `SCENE_CTX:`, `REF_OBJ:`, etc.)

**Session limitation**: The executor always starts fresh — objects from the user's
running Blender are not present. Operations that need the active session (save, backup)
work correctly when called from the MCP HTTP bridge with a running Blender instance,
or from a Blender addon.

### Tool Discovery
`discover_tools()` in `tools/__init__.py` imports all `*.py` modules in `tools/`,
triggering `_register_*_tools()` calls which register `@app.tool` decorators.

### Pydantic Compat
`_model_dump(model)` in `construct_tools.py` handles v1 (`.dict()`) and v2
(`.model_dump()`) transparently. Import it wherever pydantic models are serialised.

---

## Standards Compliance

- FastMCP 3.1.1 portmanteau pattern
- mcpb packaging via Anthropic mcpb CLI (validate + pack)
- Glama.ai: https://glama.ai/mcp/servers?query=sandraschi
- CI/CD: GitHub Actions with ruff, mypy, pytest
- All new tools documented with full operation descriptions in docstrings

---

## Next Steps

### Before Next Release (0.5.0)
1. Integration test scaffold with Blender Docker image in CI
2. Fix `construct_and_save` quality_rating passthrough (currently hardcoded 5)
3. Test bridge addon end-to-end with a live Blender 4.4 instance
4. Test WorldLabs end-to-end with a real `.ply` file

### Short Term
1. FastMCP 3.1.1 CodeMode transform on tool set (BM25 discovery for 40+ tools)
2. Repository thumbnail preview (render active object via executor, store PNG)
3. Extend `KNOWN_ADDONS` with animation addons (Auto-Rig Pro, Rigify extensions)
4. Webapp Repository page: tag editing, thumbnail display
5. Add `nature` category scripts (trees, terrain)

### Medium Term
1. Multi-user repository isolation
2. `blender://scripts/` MCP resource backed by the new JSON files (already wired)
3. Bridge addon auto-start on Blender launch via startup script

---

**Last updated**: 2026-03-29
**Next review**: 2026-04-30

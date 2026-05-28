# Blender MCP — AI-Powered Blender Automation

Control Blender with natural language through MCP. Tell Claude "create a steampunk robot
with glowing red eyes" and watch it build your vision in Blender automatically.

<p align="center">
  <a href="https://github.com/sandraschi/blender-mcp"><img src="https://img.shields.io/github/stars/sandraschi/blender-mcp?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/sandraschi/blender-mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://tauri.app"><img src="https://img.shields.io/badge/Tauri-2.0-FFC107?style=flat-square&logo=tauri&logoColor=white" alt="Tauri"></a>
  <a href=""><img src="https://img.shields.io/badge/fleet-SOTA-6366f1?style=flat-square" alt="Fleet SOTA"></a>
</p>

## Contents

- [Quick Start](#quick-start)
- [Webapp Dashboard](#webapp-dashboard)
- [Native Desktop App (Tauri 2.0)](#native-desktop-app-tauri-20)
- [Available Tools](#available-tools-41-tools-170-operations)
- [Documentation](#documentation)
  - [Installation Guide](INSTALL.md)
  - [Competitive Analysis](docs/COMPETITIVE_ANALYSIS.md)
  - [Roadmap](docs/ROADMAP.md)
  - [Addons, Mesh, Splat](docs/ADDONS_MESH_SPLAT.md)
  - [Video Editing (VSE)](docs/blender/VSE_GUIDE.md)
  - [Usage Examples](docs/USAGE.md)
  - [Features Overview](docs/FEATURES.md)
  - [Architecture](docs/ARCHITECTURE.md)
  - [Development](docs/DEVELOPMENT.md)
  - [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Quality Stack](#industrial-quality-stack)
- [Packaging](#packaging--distribution)
- [Architecture](#architecture)
- [Development](#development)
- [License](#license)

## Quick Start

```powershell
git clone https://github.com/sandraschi/blender-mcp
cd blender-mcp
uv sync --all-extras
just
```

This opens an interactive dashboard showing all available commands. Run `just serve`
for stdio MCP testing, or `.\start.ps1` for the webapp dashboard.

See **[INSTALL.md](INSTALL.md)** for Claude Desktop, Cursor, and troubleshooting.

### Live Blender GUI (watch the agent build)

Headless is fine for batch work; for interactive sessions use the **session bridge**:

1. Start HTTP MCP: `.\start.ps1` or `uv run python -m blender_mcp.cli --http --port 10849`
2. `blender_session` → `start` (opens Blender GUI)
3. Install **docs/blender_bridge_addon.py** → enable → **Start Bridge**
4. Agent tools run in the live scene; use `blender_render` → `screenshot_viewport` for vision feedback

Details: [INSTALL.md — Live Blender session](INSTALL.md#live-blender-session-bridge)

### Manual Setup (without `just`)

```powershell
uv sync --all-extras
uv run python -m blender_mcp.cli --stdio
```

### Claude Desktop Integration

Drag-and-drop the `.mcpb` from [releases](https://github.com/sandraschi/blender-mcp/releases),
or add a manual config — full options in **[INSTALL.md](INSTALL.md#claude-desktop-integration)**.

## Webapp Dashboard

A premium web interface for monitoring and control runs on port **10848**
(backed by API on **10849**).

```powershell
.\start.ps1
```

Startup flags: `-Headless` (background), `-BackendOnly` (API only), `-NoBrowser` (no auto-open).

Access the dashboard at **http://localhost:10848**.

## Available Tools (45+ tools, 180+ operations)

| Category | Tools |
|----------|-------|
| **Scene Management** | create/clear/list scenes, collections, view layers |
| **Mesh & Geometry** | primitives, duplicate/delete; **Phase 2:** extrude, bevel, inset, subdivide |
| **Materials & Shaders** | presets + **`blender_shaders`** node graph (create/connect) |
| **Compositor** | **`blender_compositor`** enable, nodes, glow |
| **Furniture** | chair, table, bed, sofa, room, building |
| **Lighting** | sun, point, spot, area lights, HDRI environments, lighting rigs |
| **Camera & Viewport** | camera rigs; **`screenshot_viewport`**, **`render_multi_angle`** |
| **Animation & Rigging** | armatures, character rigging, keyframes, walk cycles |
| **Rendering & Output** | Cycles/EEVEE, turntable, viewport capture for agent vision |
| **Import & Export** | import broad formats; **export** GLTF, GLB, FBX, OBJ, STL, USD, VRM, Unity, VRChat, Unreal |
| **Physics & Simulation** | rigid/soft body, cloth, fluid, particle systems |
| **Modifiers & Effects** | subdivision, bevel, array, boolean, lattice |
| **Textures & UVs** | procedural textures, image textures, UV unwrap, texture baking |
| **Video Editing (VSE)** | 20 operations: add clips, transitions, text, audio, render to MP4 |
| **Agent utilities** | **`blender_api_docs`**, **`blender_session`** live GUI bridge |

**Key capabilities:**
- **Live GUI bridge**: user sees construction in Blender while agents call MCP tools
- **HTTP MCP** on port **10849** (FastMCP Streamable) — powers webapp + bridge addon
- **Conversational 3D Creation**: Natural language to professional 3D objects
- **FastMCP 3.2 Integration**: Advanced AI sampling and security validation
- **Object Repository**: Versioned asset management with intelligent search
- **Cross-Platform Export**: Handoff to VR platforms (VRChat, Resonite, Unity, Unreal)
- **VRM Avatars**: Avatar pipeline for VR/AR applications
- **3D Gaussian Splatting**: Import and render splats
- **Grease Pencil**: 2D drawing in 3D space

See [docs/COMPETITIVE_ANALYSIS.md](docs/COMPETITIVE_ANALYSIS.md) for how we compare to other Blender MCP repos.

## Documentation

- **[Installation Guide](INSTALL.md)** — full setup and troubleshooting
- **[Competitive Analysis](docs/COMPETITIVE_ANALYSIS.md)** — vs ahujasid, RFingAdam, zorak1103, others
- **[Roadmap](docs/ROADMAP.md)** — phased improvements (vision, jobs, mesh edit, AI gen)
- **[Addons, Mesh, Splat](docs/ADDONS_MESH_SPLAT.md)** — install addons from URL, search packs, download/import meshes, Gaussian splat import; webapp `/mesh` page
- **[Video Editing (VSE)](docs/blender/VSE_GUIDE.md)** — Blender's built-in video editor: add clips, transitions, text, audio; render to MP4
- **[Development](docs/DEVELOPMENT.md)** — Ruff (lint/format), code quality, server entry points
- **[Usage Examples](docs/USAGE.md)** — AI construction examples, VR avatar pipeline, batch processing
- **[Features Overview](docs/FEATURES.md)** — complete tool catalog, AI construction details, VR platform integration
- **[Architecture](docs/ARCHITECTURE.md)** — system design, security, performance, scalability
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** — common issues, debug info, platform-specific problems

## Native Desktop App (Tauri 2.0)

A ~15 MB installer bundles the full app — no Python, no Node.js, no git clone needed.

```powershell
just build-native        # Full pipeline: webapp → PyInstaller → Tauri installer
just build-native-debug  # Debug build (skips PyInstaller)
```

The installer lands at `native/target/release/bundle/nsis/Blender MCP_0.1.0_x64-setup.exe`.

## Industrial Quality Stack

Adheres to **SOTA 14.1** industrial standards:

- **Python**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` in core handlers (`T201`).
- **Webapp**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened stdout/stderr isolation for crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

## Packaging & Distribution

SOTA 2026 compliant via `@anthropic-ai/mcpb`:

```bash
mcpb pack . dist/blender-mcp.mcpb
```

## Architecture

- `src/blender_mcp/server.py` — Core FastMCP 3.2 server definition
- `src/blender_mcp/handlers/` — Context-specific tool handlers (scene, object, render, etc.)
- `src/blender_mcp/tools/` — MCP tool definitions organized by category
- `src/blender_mcp/utils/` — Path resolution and Blender integration utilities
- `webapp/` — React dashboard for fleet visibility

## Development

```bash
uv run pytest                    # Run tests
uv run ruff check .              # Lint
uv run ruff format .             # Format
uv run mypy src                  # Type check
```

## License

MIT — By [FlowEngineer sandraschi](https://github.com/sandraschi). Free for personal and commercial use.

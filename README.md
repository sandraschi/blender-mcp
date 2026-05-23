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
- [Available Tools](#available-tools-41-tools-170-operations)
- [Documentation](#documentation)
  - [Installation Guide](INSTALL.md)
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
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap`
to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup (without `just`)

```powershell
uv sync
.venv\Scripts\activate
python run_server.py
```

### Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "blender-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/blender-mcp", "run", "blender-mcp"]
  }
}
```

## Webapp Dashboard

A premium web interface for monitoring and control runs on port **10848**
(backed by API on **10849**).

```powershell
.\start.ps1
```

Startup flags: `-Headless` (background), `-BackendOnly` (API only), `-NoBrowser` (no auto-open).

Access the dashboard at **http://localhost:10848**.

## Available Tools (41+ tools, 170+ operations)

| Category | Tools |
|----------|-------|
| **Scene Management** | create/clear/list scenes, collections, view layers |
| **Mesh & Geometry** | cube, sphere, cylinder, plane, torus, monkey, text, curves, NURBS |
| **Materials & Shaders** | metal, wood, glass, fabric, ceramic, plastic, emissive, presets |
| **Furniture** | chair, table, bed, sofa, room, building |
| **Lighting** | sun, point, spot, area lights, HDRI environments, lighting rigs |
| **Camera & Viewport** | camera creation, positioning, rigs, viewport config |
| **Animation & Rigging** | armatures, character rigging, keyframes, walk cycles |
| **Rendering & Output** | Cycles/EEVEE, render settings, animation rendering, render passes |
| **Import & Export** | FBX, OBJ, glTF, STL, batch export |
| **Physics & Simulation** | rigid/soft body, cloth, fluid, particle systems |
| **Modifiers & Effects** | subdivision, bevel, array, boolean, lattice |
| **Textures & UVs** | procedural textures, image textures, UV unwrap, texture baking |
| **Video Editing (VSE)** | 20 operations: add clips, transitions, text, audio, render to MP4 |

**Key capabilities:**
- **Conversational 3D Creation**: Natural language to professional 3D objects
- **FastMCP 3.2 Integration**: Advanced AI sampling and security validation
- **Object Repository**: Versioned asset management with intelligent search
- **Cross-Platform Export**: Handoff to VR platforms (VRChat, Resonite, Unity)
- **VRM Avatars**: Avatar pipeline for VR/AR applications
- **3D Gaussian Splatting**: Import and render splats
- **Grease Pencil**: 2D drawing in 3D space

## Documentation

- **[Installation Guide](INSTALL.md)** — full setup and troubleshooting
- **[Addons, Mesh, Splat](docs/ADDONS_MESH_SPLAT.md)** — install addons from URL, search packs, download/import meshes, Gaussian splat import; webapp `/mesh` page
- **[Video Editing (VSE)](docs/blender/VSE_GUIDE.md)** — Blender's built-in video editor: add clips, transitions, text, audio; render to MP4
- **[Development](docs/DEVELOPMENT.md)** — Ruff (lint/format), code quality, server entry points
- **[Usage Examples](docs/USAGE.md)** — AI construction examples, VR avatar pipeline, batch processing
- **[Features Overview](docs/FEATURES.md)** — complete tool catalog, AI construction details, VR platform integration
- **[Architecture](docs/ARCHITECTURE.md)** — system design, security, performance, scalability
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** — common issues, debug info, platform-specific problems

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

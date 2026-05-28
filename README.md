# Blender MCP — AI-Powered Blender Automation

Control Blender with natural language through MCP. Tell Claude to create a steampunk robot
with glowing eyes and watch it build in Blender.

<p align="center">
  <a href="https://github.com/sandraschi/blender-mcp"><img src="https://img.shields.io/github/stars/sandraschi/blender-mcp?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/sandraschi/blender-mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

## Features

- **Natural-language 3D creation** — scenes, meshes, materials, lighting, animation
- **Live GUI bridge** — watch the agent build in Blender while you chat
- **48+ MCP tools** — mesh edit, sculpt, geonodes, compositor, VSE, export (GLB, VRM, VRChat, Unity)
- **Generative AI hooks** — Rodin/Tripo/Hunyuan mesh generation and vision refine
- **Webapp dashboard** — scene explorer, agent lab, materials, mesh/splat pipeline
- **Fleet-ready** — FastMCP 3.2, `.mcpb` packaging, Prometheus metrics, optional Docker

## Quick Install

1. Download **`blender-mcp-*.mcpb`** from [Releases](https://github.com/sandraschi/blender-mcp/releases/latest)
2. Drag it into **Claude Desktop**

Done. Install [Blender](https://www.blender.org/download/) separately if you have not already.

Other methods (npx mcpb, manual config, developer setup): **[INSTALL.md](INSTALL.md)**

## What You Can Do

Try these in Claude Desktop after install:

> Create a red cube on a gray floor with a sun lamp and render a viewport screenshot.

> Build a simple chair with wood material and export as GLB.

> Start a live Blender session and add a sphere with a metallic blue shader.

## Documentation

| Doc | Contents |
|-----|----------|
| [Installation](INSTALL.md) | All install methods, prerequisites, bridge setup |
| [Configuration](docs/CONFIGURATION.md) | Env vars, Claude Desktop `env` block |
| [Tool Reference](docs/FEATURES.md) | Capabilities and tool catalog |
| [Development](docs/DEVELOPMENT.md) | Contributing, `just`, lint, build |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common errors and fixes |
| [Architecture](docs/ARCHITECTURE.md) | System design |
| [Roadmap](docs/ROADMAP.md) | Planned improvements |
| [Monitoring](docs/MONITORING.md) | Prometheus / Grafana / Loki |
| [Docker](docs/DOCKER.md) | Optional container deploy |

Extended guides: [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)

## Webapp and Native App

**Dashboard** (optional): `.\start.ps1` → http://localhost:10848 — see [INSTALL.md](INSTALL.md#webapp-dashboard-optional).

**Tauri desktop installer** (~15 MB, no Python required): `just build-native` — see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Requirements

- **Claude Desktop** (or any MCP client for manual config)
- **Blender 3.0+** — auto-detected; override with `BLENDER_EXECUTABLE`
- **OS:** Windows, macOS, Linux
- **Python 3.12+** — only for Options C/D (clone-from-source)

## License

MIT — [FlowEngineer sandraschi](https://github.com/sandraschi). Free for personal and commercial use.

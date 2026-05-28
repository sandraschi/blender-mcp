# Installation

Complete setup for blender-mcp: fleet `just` workflow, editable install, Claude Desktop,
webapp dashboard, and troubleshooting.

## Quick Start (recommended)

```powershell
# Install just if you don't have it
winget install Casey.Just    # Windows
# scoop install just          # Windows (alternative)
# brew install just           # macOS
# sudo apt install just       # Debian/Ubuntu
# cargo install just          # Linux (Rust)

git clone https://github.com/sandraschi/blender-mcp
cd blender-mcp
uv sync --all-extras
just
```

The interactive recipe dashboard opens in your browser. Common next steps:

```powershell
just serve      # stdio server (local MCP testing)
.\start.ps1     # webapp dashboard (ports 10848/10849)
```

> **Why not `pip install blender-mcp` from PyPI?** MCP servers bundle webapps, configs,
> project scaffolding, and tooling that a flat Python package cannot deliver. PyPI offers
> no safety advantage — it does not audit packages either. Clone + `uv sync` gives you
> the complete, ready-to-run stack.

---

## Editable Install (without `just`)

Clone and install locally with `uv`:

```powershell
git clone https://github.com/sandraschi/blender-mcp.git
cd blender-mcp
uv pip install -e .
```

Or with plain pip:

```powershell
pip install -e .
```

**Verify:**

```powershell
python -m blender_mcp.cli --help
```

> **Windows note:** The `blender-mcp` CLI script is installed to
> `%APPDATA%\Python\Python3XX\Scripts\` which is often not in PATH.
> Use `python -m blender_mcp.cli` instead — it always works.

---

## Traditional Setup (`uv sync`)

If you prefer the repo venv workflow without editable pip install:

1. Install [Python 3.12+](https://python.org) (3.13+ recommended) and [uv](https://docs.astral.sh/uv/)
2. Clone and enter the repo:
   ```powershell
   git clone https://github.com/sandraschi/blender-mcp
   cd blender-mcp
   ```
3. Install dependencies:
   ```powershell
   uv sync --all-extras
   ```
4. Start the server:
   ```powershell
   # stdio mode (for MCP clients like Claude Desktop)
   uv run python -m blender_mcp.cli --stdio

   # Alternative stdio entry point
   uv run blender-mcp-server

   # Legacy dev entry point
   uv run python run_server.py

   # HTTP mode (for web dashboard API)
   uv run uvicorn blender_mcp.server:app --port 10849
   ```
5. (optional) Start the frontend:
   ```powershell
   cd webapp
   npm install
   npm run dev
   ```
6. Open `http://localhost:10849` or the frontend URL.

---

## Webapp Dashboard

A premium web interface for monitoring and control runs on port **10848**
(backed by API on **10849**).

```powershell
.\start.ps1
```

Startup flags: `-Headless` (background), `-BackendOnly` (API only), `-NoBrowser` (no auto-open).

Access the dashboard at **http://localhost:10848**.

---

## Live Blender session (bridge)

For **interactive GUI** work (user watches the agent build):

1. Start the MCP HTTP server (`.\start.ps1` or `uv run python -m blender_mcp.cli --http --port 10849`)
2. Use MCP tool **`blender_session`** with `operation=start` to launch Blender GUI
3. In Blender: **Edit → Preferences → Add-ons → Install** → select **`docs/blender_bridge_addon.py`**
4. Enable **Blender MCP Session Bridge** → **Properties → Scene → Blender MCP Bridge → Start Bridge**
5. Agent tools execute in the live scene; **`blender_render`** `screenshot_viewport` returns PNG + base64 for vision loops

Without the bridge, tools fall back to **headless** Blender subprocess execution.

---

## Claude Desktop Integration

### Option A — Drag and drop (easiest)

1. Download **[blender-mcp-v0.5.0.mcpb](https://github.com/sandraschi/blender-mcp/releases/download/v0.5.0/blender-mcp-v0.5.0.mcpb)** from the [releases page](https://github.com/sandraschi/blender-mcp/releases)
2. Drag the `.mcpb` file into Claude Desktop

Done — Claude Desktop registers the server automatically.

### Option B — mcpb CLI

Requires the [mcpb CLI](https://github.com/anthropics/mcpb) to be installed first.
`mcpb` is **not** on PyPI — `uvx mcpb` will not work. Install it per the mcpb docs, then:

```bash
mcpb install sandraschi/blender-mcp
```

Build a local bundle with `just mcpb-pack` (output: `dist/blender-mcp-v0.6.0.mcpb`).

### Option C — Manual config

Clone the repo first (see [Quick Start](#quick-start-recommended) or [Editable Install](#editable-install-without-just)), then add this to your
`claude_desktop_config.json`
(`%APPDATA%\Claude\claude_desktop_config.json` on Windows,
`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "python",
      "args": ["-m", "blender_mcp.cli", "--stdio"]
    }
  }
}
```

If you use `uv` and want a self-contained install without activating a venv:

```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "uv",
      "args": [
        "--directory", "C:/path/to/blender-mcp",
        "run", "python", "-m", "blender_mcp.cli", "--stdio"
      ]
    }
  }
}
```

Restart Claude Desktop after editing the config.

---

## Other MCP Clients (Cursor, VS Code, etc.)

Use the same `python -m blender_mcp.cli --stdio` invocation in your MCP client settings.

With `uv`:

```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "uv",
      "args": [
        "--directory", "C:/path/to/blender-mcp",
        "run", "python", "-m", "blender_mcp.cli", "--stdio"
      ]
    }
  }
}
```

---

## HTTP Server Mode

```bash
python -m blender_mcp.cli --http --host 0.0.0.0 --port 8001
```

Or via uvicorn (webapp API on port 10849):

```powershell
uv run uvicorn blender_mcp.server:app --port 10849
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `BLENDER_EXECUTABLE` | Path to Blender binary | auto-detected |
| `MCP_DEBUG` | Enable debug logging | `false` |

**Windows example:**
```powershell
$env:BLENDER_EXECUTABLE = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
```

**Linux/macOS example:**
```bash
export BLENDER_EXECUTABLE=/usr/bin/blender
```

---

## Requirements

- **Python:** 3.12+ (3.13+ recommended)
- **Blender:** 3.0+ (auto-detected or set via `BLENDER_EXECUTABLE`)
- **Platform:** Windows, macOS, Linux

---

## Development Install

```bash
git clone https://github.com/sandraschi/blender-mcp.git
cd blender-mcp
pip install -e .[dev]
```

Or with uv:

```powershell
uv sync --all-extras
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `just` not found | Install via `winget install Casey.Just`, `scoop install just`, or `brew install just` |
| Port conflict (10848/10849) | Re-run `.\start.ps1` (clears stale ports) or stop the conflicting process |
| Dependencies out of sync | `uv sync --all-extras` |
| `blender-mcp` command not found (Windows) | Use `python -m blender_mcp.cli` instead (see below) |
| Blender not found | Set `BLENDER_EXECUTABLE` (see [Configuration](#configuration)) |
| Permission errors | Use a venv: `python -m venv venv` then `venv\Scripts\activate` and `pip install -e .` |
| Something else | [Open a GitHub issue](https://github.com/sandraschi/blender-mcp/issues) |

### `blender-mcp` command not found (Windows)

The entry-point script lands in `%APPDATA%\Python\Python3XX\Scripts\` — often not in PATH.
Use the module form instead:

```bash
python -m blender_mcp.cli --help
```

Or add the Scripts folder to your PATH permanently:

```powershell
$scripts = [System.IO.Path]::Combine($env:APPDATA, "Python", "Python313", "Scripts")
[System.Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";" + $scripts, "User")
```

### Blender not found

```bash
# Windows
set BLENDER_EXECUTABLE=C:\Program Files\Blender Foundation\Blender 5.1\blender.exe

# Linux/macOS
export BLENDER_EXECUTABLE=/usr/bin/blender
```

---

## Health Checks

```bash
# Test Python import
python -c "import blender_mcp; print('OK')"

# Test CLI
python -m blender_mcp.cli --check-blender

# Test server startup (stdio mode, exits cleanly)
python -m blender_mcp.cli --stdio --debug
```

---

*See the main [README](README.md) for feature overview and documentation.*

# Installation Guide

## Quick Start (Recommended)

Clone the repo and install locally with `uv`:

```bash
git clone https://github.com/sandraschi/blender-mcp.git
cd blender-mcp
uv pip install -e .
```

Or with plain pip:

```bash
pip install -e .
```

**Verify:**

```bash
python -m blender_mcp.cli --help
```

> **Windows note:** The `blender-mcp` CLI script is installed to
> `%APPDATA%\Python\Python3XX\Scripts\` which is often not in PATH.
> Use `python -m blender_mcp.cli` instead — it always works.

---

## Claude Desktop Integration

### Option A — mcpb (one-command install, recommended)

Requires the [mcpb CLI](https://github.com/anthropics/mcpb) to be installed first.
`mcpb` is **not** on PyPI — `uvx mcpb` will not work. Install it per the mcpb docs, then:

```bash
mcpb install sandraschi/blender-mcp
```

This registers the server in your Claude Desktop config automatically.

### Option B — Manual config

Clone the repo first (see Quick Start above), then add this to your
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

---

## HTTP Server Mode

```bash
python -m blender_mcp.cli --http --host 0.0.0.0 --port 8001
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

- **Python:** 3.12+
- **Blender:** 3.0+ (auto-detected or set via `BLENDER_EXECUTABLE`)
- **Platform:** Windows, macOS, Linux

---

## Development Install

```bash
git clone https://github.com/sandraschi/blender-mcp.git
cd blender-mcp
pip install -e .[dev]
```

---

## Troubleshooting

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

### Permission errors / conflicting packages

Use a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS
pip install -e .
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

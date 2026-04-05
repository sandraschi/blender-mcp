# Installation Guide

## Quick Start (Recommended)

**Install from PyPI:**
```bash
# With uv (recommended)
uv pip install blender-mcp

# Or with pip
pip install blender-mcp

# For development
pip install blender-mcp[dev]
```

**Verify installation:**
```bash
blender-mcp --help
```

## Installation Methods

### PyPI/Pip (Universal)
```bash
pip install blender-mcp
```
- ✅ Works on Windows, Mac, Linux
- ✅ Auto-discovers in MCP clients
- ✅ Clean dependencies

### Docker (Containerized)
```bash
# Quick start
docker run -p 8000:8000 ghcr.io/sandraschi/blender-mcp:latest

# With Docker Compose
docker-compose up blender-mcp

# Development mode
docker-compose --profile dev up
```
- ✅ Isolated environment
- ✅ Includes Blender
- ✅ Consistent across platforms

### MCPB (Claude Desktop)
```bash
uvx mcpb install sandraschi/blender-mcp
```
- ✅ One-command install
- ✅ Claude Desktop integration
- ✅ Auto-updates

### Manual Setup (Development)
```bash
git clone https://github.com/sandraschi/blender-mcp.git
cd blender-mcp
pip install -e .[dev]
blender-mcp --install-config
```

## Platform-Specific Setup

### Claude Desktop
```bash
uvx mcpb install sandraschi/blender-mcp
```

### Cursor/VS Code
```bash
pip install blender-mcp
# Configure in MCP client settings
```

### HTTP Server Mode
```bash
blender-mcp --http --host 0.0.0.0 --port 8001
```

## Configuration

### Environment Variables
```bash
export BLENDER_EXECUTABLE=/path/to/blender
export MCP_DEBUG=true
```

### Claude Desktop Config
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

## Requirements

- **Python**: 3.10+
- **Blender**: 3.0+ (auto-detected or via `BLENDER_EXECUTABLE`)
- **Platform**: Windows, macOS, Linux

## Troubleshooting

### Common Issues

**"blender-mcp command not found"**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
# Or use python module
python -m blender_mcp.cli
```

**"Blender not found"**
```bash
export BLENDER_EXECUTABLE=/path/to/blender
```

**Permission errors**
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows
pip install blender-mcp
```

## Health Checks

```bash
# Test Python import
python -c "import blender_mcp; print('OK')"

# Test CLI
blender-mcp --check-blender

# Test server startup
blender-mcp --stdio --debug
```

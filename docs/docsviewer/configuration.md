# ⚙️ Configuration Guide

Complete configuration reference for Blender MCP server, including environment variables, MCP settings, and performance tuning.

## MCP Server Configuration

### Claude Desktop Setup

#### Basic Configuration
```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "python",
      "args": ["-m", "blender_mcp"],
      "env": {
        "BLENDER_EXECUTABLE": "/path/to/blender"
      }
    }
  }
}
```

#### Windows Path Example
```json
{
  "BLENDER_EXECUTABLE": "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe"
}
```

#### macOS Path Example
```json
{
  "BLENDER_EXECUTABLE": "/Applications/Blender.app/Contents/MacOS/Blender"
}
```

#### Linux Path Example
```json
{
  "BLENDER_EXECUTABLE": "/home/user/blender/blender"
}
```

## Environment Variables

### Required Settings

#### `BLENDER_EXECUTABLE`
Path to Blender executable
```bash
# Windows
export BLENDER_EXECUTABLE="C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"

# macOS
export BLENDER_EXECUTABLE="/Applications/Blender.app/Contents/MacOS/Blender"

# Linux
export BLENDER_EXECUTABLE="/usr/bin/blender"
```

### Performance Settings

#### `OPERATION_TIMEOUT`
Maximum seconds for single operations (default: 30)
```bash
export OPERATION_TIMEOUT=60  # Longer for complex operations
export OPERATION_TIMEOUT=10  # Faster for simple operations
```

#### `MAX_PARALLEL_OPERATIONS`
Concurrent Blender operations (default: 3)
```bash
export MAX_PARALLEL_OPERATIONS=1   # Conservative (less resource usage)
export MAX_PARALLEL_OPERATIONS=5   # Aggressive (faster but more RAM)
```

#### `PROCESS_TIMEOUT`
Blender subprocess timeout (default: 300)
```bash
export PROCESS_TIMEOUT=600  # 10 minutes for complex renders
```

### Rendering Settings

#### `ENABLE_GPU_RENDERING`
Use GPU acceleration (default: false)
```bash
export ENABLE_GPU_RENDERING=true   # Enable GPU rendering
export ENABLE_GPU_RENDERING=false  # CPU only
```

#### `RENDER_SAMPLES`
Default render samples (default: 128)
```bash
export RENDER_SAMPLES=64    # Faster previews
export RENDER_SAMPLES=512   # Higher quality
```

#### `RENDER_ENGINE`
Default render engine (default: CYCLES)
```bash
export RENDER_ENGINE=CYCLES     # Physically based
export RENDER_ENGINE=BLENDER_EEVEE  # Real-time
export RENDER_ENGINE=WORKBENCH     # Fast previews
```

### Logging Configuration

#### `LOG_LEVEL`
Logging verbosity (default: INFO)
```bash
export LOG_LEVEL=DEBUG     # Maximum verbosity
export LOG_LEVEL=INFO      # Normal operation
export LOG_LEVEL=WARNING   # Only warnings/errors
export LOG_LEVEL=ERROR     # Errors only
```

#### `LOG_FILE`
Optional log file path
```bash
export LOG_FILE="/path/to/blender_mcp.log"
export LOG_FILE="./logs/blender_mcp.log"
```

### Directory Settings

#### `TEMP_DIRECTORY`
Custom temporary directory
```bash
export TEMP_DIRECTORY="/tmp/blender_mcp"
export TEMP_DIRECTORY="./temp"
```

#### `ASSET_CACHE_DIR`
Downloaded asset cache location
```bash
export ASSET_CACHE_DIR="./assets/cache"
export ASSET_CACHE_DIR="/home/user/blender_assets"
```

### Auto-Detection Settings

#### `BLENDER_AUTO_DETECT`
Auto-find Blender if path fails (default: true)
```bash
export BLENDER_AUTO_DETECT=true   # Try to find Blender automatically
export BLENDER_AUTO_DETECT=false  # Require explicit path
```

#### `AUTO_UPDATE_ASSETS`
Auto-update asset libraries (default: false)
```bash
export AUTO_UPDATE_ASSETS=true    # Check for asset updates
export AUTO_UPDATE_ASSETS=false   # Manual updates only
```

## Advanced Configuration

### Custom Blender Arguments
```python
# In your MCP server configuration
{
  "args": [
    "-m", "blender_mcp",
    "--blender-args", "--factory-startup,--disable-autoexec"
  ]
}
```

### Multiple Blender Versions
```json
{
  "mcpServers": {
    "blender-mcp-4.4": {
      "command": "python",
      "args": ["-m", "blender_mcp"],
      "env": {
        "BLENDER_EXECUTABLE": "/path/to/blender-4.4"
      }
    },
    "blender-mcp-4.2": {
      "command": "python",
      "args": ["-m", "blender_mcp"],
      "env": {
        "BLENDER_EXECUTABLE": "/path/to/blender-4.2"
      }
    }
  }
}
```

### Development Configuration
```json
{
  "mcpServers": {
    "blender-mcp-dev": {
      "command": "python",
      "args": ["-m", "blender_mcp", "--debug", "--http"],
      "env": {
        "BLENDER_EXECUTABLE": "/path/to/blender",
        "LOG_LEVEL": "DEBUG",
        "OPERATION_TIMEOUT": "60",
        "MAX_PARALLEL_OPERATIONS": "1"
      }
    }
  }
}
```

## Platform-Specific Configuration

### Windows Configuration

#### Path Handling
```json
{
  "env": {
    "BLENDER_EXECUTABLE": "C:\\\\Program Files\\\\Blender Foundation\\\\Blender 4.4\\\\blender.exe",
    "TEMP_DIRECTORY": "C:\\\\Temp\\\\blender_mcp",
    "LOG_FILE": "C:\\\\Logs\\\\blender_mcp.log"
  }
}
```

#### Antivirus Considerations
```json
{
  "env": {
    "EXCLUDE_FROM_DEFENDER": "true",
    "DISABLE_WINDOWS_DEFENDER_REALTIME": "false"
  }
}
```

### macOS Configuration

#### Permission Settings
```json
{
  "env": {
    "BLENDER_EXECUTABLE": "/Applications/Blender.app/Contents/MacOS/Blender",
    "GRANT_ACCESSIBILITY": "true",
    "ALLOW_CAMERA_ACCESS": "false"
  }
}
```

#### Gatekeeper Bypass
```bash
# Allow Blender to run without warnings
xattr -rd com.apple.quarantine /Applications/Blender.app
```

### Linux Configuration

#### Display Settings (Headless)
```json
{
  "env": {
    "DISPLAY": ":0",
    "WAYLAND_DISPLAY": "wayland-0",
    "XDG_RUNTIME_DIR": "/run/user/1000"
  }
}
```

#### Library Paths
```bash
export LD_LIBRARY_PATH="/usr/lib/blender:$LD_LIBRARY_PATH"
export PYTHONPATH="/usr/share/blender/scripts:$PYTHONPATH"
```

### WSL2 Configuration

#### Windows Path Mapping
```json
{
  "env": {
    "BLENDER_EXECUTABLE": "/mnt/c/Program\\ Files/Blender\\ Foundation/Blender\\ 4.4/blender.exe",
    "TEMP_DIRECTORY": "/mnt/c/Temp/blender_mcp",
    "LOG_FILE": "/mnt/c/Logs/blender_mcp.log"
  }
}
```

#### Interoperability Settings
```bash
export WSL_INTEROP=/run/WSL/1_interop
export WSL_DISTRO_NAME=Ubuntu-20.04
```

## Performance Tuning

### Memory Management
```json
{
  "env": {
    "BLENDER_MEMORY_LIMIT": "4096",  # MB
    "ENABLE_MEMORY_MONITORING": "true",
    "AUTO_SAVE_INTERVAL": "300"      # seconds
  }
}
```

### CPU Optimization
```json
{
  "env": {
    "BLENDER_THREADS": "auto",      # Auto-detect CPU cores
    "ENABLE_MULTITHREADING": "true",
    "TILE_SIZE": "256"              # Render tile size
  }
}
```

### Network Settings
```json
{
  "env": {
    "DOWNLOAD_TIMEOUT": "30",       # Asset download timeout
    "CONNECTION_POOL_SIZE": "10",   # HTTP connection pool
    "ENABLE_COMPRESSION": "true"    # Compress network traffic
  }
}
```

## Security Configuration

### File Access Control
```json
{
  "env": {
    "ALLOWED_DIRECTORIES": "/home/user/projects,/tmp",
    "BLOCKED_EXTENSIONS": ".exe,.bat,.cmd,.scr",
    "SANDBOX_MODE": "true"
  }
}
```

### Network Security
```json
{
  "env": {
    "ALLOWED_DOMAINS": "polyhaven.com,ambientcg.com,free3d.com",
    "SSL_VERIFY": "true",
    "PROXY_URL": "http://proxy.company.com:8080"
  }
}
```

## Monitoring and Debugging

### Health Check Configuration
```json
{
  "env": {
    "ENABLE_HEALTH_CHECKS": "true",
    "HEALTH_CHECK_INTERVAL": "60",   # seconds
    "LOG_SYSTEM_STATS": "true"
  }
}
```

### Debug Settings
```json
{
  "env": {
    "DEBUG_MODE": "true",
    "LOG_BLENDER_OUTPUT": "true",
    "TRACE_EXECUTION": "false",
    "PROFILE_PERFORMANCE": "true"
  }
}
```

## Custom Scripts and Extensions

### User Scripts Directory
```json
{
  "env": {
    "USER_SCRIPTS_DIR": "/home/user/blender/scripts",
    "CUSTOM_MODULES": "my_tools,my_utils",
    "AUTO_LOAD_ADDONS": "true"
  }
}
```

### Plugin Configuration
```json
{
  "env": {
    "ENABLE_PLUGINS": "true",
    "PLUGIN_DIR": "/home/user/blender_mcp/plugins",
    "AUTO_DISCOVER_PLUGINS": "true"
  }
}
```

## Configuration Validation

### Test Configuration
```bash
# Validate MCP server starts
python -m blender_mcp --validate-config

# Test Blender integration
python -c "
from blender_mcp.app import get_app
from blender_mcp.server import setup_logging
import os

setup_logging('INFO')
app = get_app()
tools = app.get_tools()
print(f'✅ Configuration valid: {len(tools)} tools loaded')
print(f'✅ Blender path: {os.environ.get(\"BLENDER_EXECUTABLE\", \"Not set\")}')
"
```

### Configuration File
```python
# config.py - Example configuration file
import os

BLENDER_MCP_CONFIG = {
    'blender_executable': '/usr/bin/blender',
    'operation_timeout': 30,
    'max_parallel_operations': 3,
    'log_level': 'INFO',
    'temp_directory': '/tmp/blender_mcp',
    'enable_gpu_rendering': True,
    'render_samples': 128
}

# Load configuration
for key, value in BLENDER_MCP_CONFIG.items():
    os.environ[key.upper()] = str(value)
```

## Troubleshooting Configuration

### Configuration Issues

#### "Blender executable not found"
```bash
# Check path exists
ls -la "$BLENDER_EXECUTABLE"

# Test Blender runs
"$BLENDER_EXECUTABLE" --version

# Update configuration with correct path
```

#### "Permission denied"
```bash
# Fix executable permissions
chmod +x "$BLENDER_EXECUTABLE"

# Check directory permissions
ls -ld "$(dirname "$BLENDER_EXECUTABLE")"
```

#### "Invalid environment variable"
```bash
# Validate numeric values
echo "$OPERATION_TIMEOUT" | grep -E '^[0-9]+$'

# Check boolean values
case "$ENABLE_GPU_RENDERING" in
    true|false) echo "Valid";;
    *) echo "Invalid";;
esac
```

#### "Configuration not loaded"
```bash
# Check MCP server restart
# Verify JSON syntax in Claude Desktop
# Check environment variable names (case-sensitive)
```

### Performance Issues

#### High Memory Usage
```json
{
  "env": {
    "MAX_PARALLEL_OPERATIONS": "1",
    "BLENDER_MEMORY_LIMIT": "2048",
    "ENABLE_MEMORY_MONITORING": "true"
  }
}
```

#### Slow Operations
```json
{
  "env": {
    "OPERATION_TIMEOUT": "120",
    "ENABLE_MULTITHREADING": "true",
    "RENDER_SAMPLES": "64"
  }
}
```

---

**Configuration complete! Your Blender MCP server is optimized for your workflow.** ⚙️🚀

*For advanced users: Check the [development documentation](../development/README.md) for custom configuration options.*

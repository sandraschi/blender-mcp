# 🛠️ Installation Guide

Complete installation instructions for Blender MCP across different platforms and environments.

## Prerequisites

### System Requirements
- **Python**: 3.10 or higher (3.11+ recommended)
- **Blender**: 4.0+ (4.4+ recommended for full compatibility)
- **RAM**: 8GB minimum, 16GB+ recommended
- **Storage**: 2GB free space for installation + assets

### Operating System Support
- ✅ **Windows 10/11** - Fully supported
- ✅ **macOS 12+** - Fully supported
- ✅ **Linux (Ubuntu 20.04+)** - Fully supported
- ✅ **WSL2** - Windows Subsystem for Linux

## Quick Install (Recommended)

### Option 1: PyPI Package
```bash
# Install from PyPI
pip install blender-mcp

# Verify installation
python -c "import blender_mcp; print('✅ Blender MCP installed successfully')"
```

### Option 2: MCPB Package (One-Click Install)
```bash
# Install MCPB CLI if not already installed
pip install mcpb

# Download and install Blender MCP
mcpb install https://github.com/sandraschi/blender-mcp/releases/latest/download/blender-mcp.mcpb
```

## Advanced Installation

### From Source Code
```bash
# Clone the repository
git clone https://github.com/sandraschi/blender-mcp.git
cd blender-mcp

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Verify installation
python -m blender_mcp --help
```

### Development Setup
```bash
# Install additional development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests to verify everything works
pytest tests/unit/ -v
```

## Blender Setup

### Download and Install Blender

#### Windows
```bash
# Download from https://blender.org/download/
# Run the installer
# Note the installation path (usually: C:\Program Files\Blender Foundation\Blender 4.4\)
```

#### macOS
```bash
# Download from https://blender.org/download/
# Drag to Applications folder
# Note the path: /Applications/Blender.app/Contents/MacOS/Blender
```

#### Linux
```bash
# Download from https://blender.org/download/
# Extract to ~/blender/
# Make executable: chmod +x ~/blender/blender
# Note the path: ~/blender/blender
```

### Verify Blender Installation
```bash
# Run Blender to verify it works
/path/to/blender --version

# Expected output:
# Blender 4.4.0
# ...
```

## MCP Server Configuration

### Claude Desktop Setup

#### Windows/macOS/Linux
1. **Open Claude Desktop**
2. **Go to Settings → MCP Servers**
3. **Add new MCP server:**

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

#### Blender Path Examples

**Windows:**
```json
"BLENDER_EXECUTABLE": "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe"
```

**macOS:**
```json
"BLENDER_EXECUTABLE": "/Applications/Blender.app/Contents/MacOS/Blender"
```

**Linux:**
```json
"BLENDER_EXECUTABLE": "/home/user/blender/blender"
```

### Environment Variables

#### Optional Performance Tuning
```json
{
  "env": {
    "BLENDER_EXECUTABLE": "/path/to/blender",
    "OPERATION_TIMEOUT": "30",
    "MAX_PARALLEL_OPERATIONS": "3",
    "ENABLE_GPU_RENDERING": "true",
    "LOG_LEVEL": "INFO"
  }
}
```

#### Available Environment Variables
- `BLENDER_EXECUTABLE` - Path to Blender executable (required)
- `OPERATION_TIMEOUT` - Seconds before operation timeout (default: 30)
- `MAX_PARALLEL_OPERATIONS` - Concurrent operations limit (default: 3)
- `ENABLE_GPU_RENDERING` - Use GPU for rendering (default: false)
- `LOG_LEVEL` - Logging verbosity: DEBUG, INFO, WARNING, ERROR (default: INFO)
- `TEMP_DIRECTORY` - Custom temp directory for operations
- `BLENDER_AUTO_DETECT` - Auto-detect Blender if path not found (default: true)

## Testing Installation

### Basic Functionality Test
```bash
# Test Blender MCP server
python -m blender_mcp --help

# Test with debug logging
python -m blender_mcp --debug --version

# Test Blender integration
python -c "
from blender_mcp.app import get_app
app = get_app()
print(f'✅ Server initialized with {len(app.get_tools())} tools')
"
```

### Claude Desktop Integration Test
1. **Restart Claude Desktop** after configuration
2. **Ask Claude**: "What Blender tools are available?"
3. **Expected response**: Lists available tools and categories

### Comprehensive Test
```bash
# Run unit tests (no Blender required)
pytest tests/unit/ -v

# Run integration tests (Blender required)
pytest tests/integration/ -v --tb=short
```

## Troubleshooting Installation

### Common Issues

#### "blender_mcp module not found"
```bash
# Ensure you're in the right environment
which python
pip list | grep blender-mcp

# Try reinstalling
pip uninstall blender-mcp
pip install blender-mcp
```

#### "Blender executable not found"
```bash
# Verify Blender path
/path/to/blender --version

# Update MCP configuration with correct path
# Restart Claude Desktop
```

#### "Permission denied" errors
```bash
# On macOS/Linux, ensure execute permissions
chmod +x /path/to/blender

# On Windows, run as administrator or check antivirus
```

#### Import errors in Blender
```bash
# Test Blender can run Python scripts
/path/to/blender --background --python "print('Python works')"

# Check Blender version compatibility
/path/to/blender --version
```

### Debug Mode
```bash
# Run with maximum logging
LOG_LEVEL=DEBUG python -m blender_mcp

# Check Blender subprocess logs
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from blender_mcp.utils.blender_executor import get_blender_executor
exec = get_blender_executor()
print('Blender executor initialized')
"
```

## Platform-Specific Notes

### Windows
- **Antivirus**: May flag subprocess execution - add exceptions
- **Paths**: Use double backslashes or forward slashes in JSON
- **Permissions**: Run as administrator if needed

### macOS
- **Gatekeeper**: May block unsigned applications
- **PATH**: Blender may not be in system PATH
- **Permissions**: Grant accessibility permissions if needed

### Linux
- **Dependencies**: Ensure required system libraries installed
- **Display**: May need virtual display for headless operation
- **Permissions**: Ensure user can execute Blender

### WSL2 (Windows Subsystem for Linux)
```bash
# Install Blender in WSL2
wget https://download.blender.org/release/Blender4.4/blender-4.4.0-linux-x64.tar.xz
tar -xf blender-4.4.0-linux-x64.tar.xz
export PATH=$PATH:~/blender-4.4.0-linux-x64

# Configure MCP with WSL path
"BLENDER_EXECUTABLE": "/home/user/blender-4.4.0-linux-x64/blender"
```

## Asset Libraries (Optional)

### BlenderKit Setup (Recommended)
```bash
# In Blender:
# 1. Install BlenderKit add-on
# 2. Login with account
# 3. Configure download preferences

# Test integration
python -c "
from blender_mcp.tools.download_tools import blender_download_info
import asyncio
asyncio.run(blender_download_info())
"
```

### Free Asset Sources
- **Poly Haven**: https://polyhaven.com/
- **AmbientCG**: https://ambientcg.com/
- **Kenney Assets**: https://kenney.nl/assets

## Updating Blender MCP

### From PyPI
```bash
pip install --upgrade blender-mcp
```

### From Source
```bash
cd blender-mcp
git pull
pip install -r requirements.txt
pip install -e .
```

### MCPB Updates
```bash
# Check for updates
mcpb info blender-mcp

# Update package
mcpb update blender-mcp
```

## Support and Community

### Getting Help
- **Documentation**: https://blender-mcp.readthedocs.io/
- **Issues**: https://github.com/sandraschi/blender-mcp/issues
- **Discussions**: https://github.com/sandraschi/blender-mcp/discussions
- **Discord**: Community support channel

### Reporting Problems
When reporting installation issues, include:
- Operating system and version
- Python version (`python --version`)
- Blender version (`blender --version`)
- Installation method used
- Full error messages and logs
- MCP configuration used

---

**Installation complete! You're ready to create 3D content with AI-powered Blender automation.** 🎉🚀

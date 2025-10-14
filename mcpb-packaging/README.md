# Blender MCP - MCPB Packaging

**Version:** 1.0.0
**Status:** Production Ready

## Overview

This directory contains the complete MCPB (Model Context Protocol Bundle) packaging system for the Blender MCP server. MCPB provides one-click installation for Claude Desktop and other MCP-compatible applications.

## 🎯 What's Included

- **37 working Blender automation tools** across 19 categories
- **Complete FastMCP 2.12 implementation** with proper tool registration
- **Comprehensive user configuration** system
- **Extensive prompt templates** for different workflows
- **Automated build and validation** scripts
- **Production-ready packaging** for distribution

## 📦 Package Structure

```
mcpb-packaging/
├── manifests/              # MCPB manifest files
│   └── mcpb_manifest.json  # Main package configuration
├── scripts/                # Build and test scripts
│   ├── build-mcpb-package.ps1     # Package builder
│   ├── validate-mcpb-package.ps1  # Package validator
│   └── test-mcpb-installation.ps1 # Installation tester
├── prompts/                # Workflow templates
│   ├── quick_start_templates.md   # Basic usage templates
│   └── advanced_workflow_templates.md # Production pipelines
├── templates/              # Configuration templates
├── build/                  # Build artifacts (generated)
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Node.js** (for MCPB CLI): `npm install -g @anthropic-ai/mcpb`
2. **Python 3.10+**: Download from python.org
3. **Blender 4.0+**: Download from blender.org

### Build Package

```powershell
# Navigate to project root
cd D:\Dev\repos\blender-mcp

# Build MCPB package
.\mcpb-packaging\scripts\build-mcpb-package.ps1
```

### Validate Package

```powershell
# Validate built package
.\mcpb-packaging\scripts\validate-mcpb-package.ps1 -PackagePath dist\blender-mcp.mcpb -Detailed
```

### Test Installation

```powershell
# Test installation process
.\mcpb-packaging\scripts\test-mcpb-installation.ps1 -PackagePath dist\blender-mcp.mcpb
```

## 🛠️ Available Tools

### Core Categories (37 Tools Total)

#### 🎨 Object Creation & Mesh (9 operations)
- `blender_mesh` - Create primitives, duplicate, delete objects

#### 🎭 Animation & Motion (7 operations)
- `blender_animation` - Keyframes, motion paths, playback control

#### 💡 Lighting & Rendering (7 operations)
- `blender_lighting` - Sun, point, spot, area lights, HDRI, three-point setup

#### 📤 Export Systems (2 operations)
- `blender_export` - Unity and VRChat export pipelines

#### 📥 Import Systems (2 operations)
- `blender_import` - FBX, OBJ, glTF, VRM import support

#### 🪑 Furniture Creation (8 operations)
- `blender_furniture` - Complete furniture modeling system

#### 🎨 Textures & Materials (3 operations)
- `blender_textures` - Procedural and image-based textures

#### 📷 Camera Control (3 operations)
- `blender_camera` - Camera creation and positioning

#### 🔧 Mesh Modifiers (8 operations)
- `blender_modifiers` - Subdivision, bevel, mirror, array, etc.

#### 🎬 Rendering Pipeline (5 operations)
- `blender_render` - Preview, turntable, animation rendering

#### 📐 Transform Tools (7 operations)
- `blender_transform` - Position, rotation, scale operations

#### 🎯 Selection Tools (6 operations)
- `blender_selection` - Object selection and filtering

#### 🦴 Rigging System (4 operations)
- `blender_rigging` - Armature creation and bone manipulation

#### ⚡ Physics Simulation (9 operations)
- `blender_physics` - Rigid body, cloth, soft body, fluid simulation

#### 🎆 Particle Effects (4 operations)
- `blender_particles` - Particle systems and effects

#### 🧵 UV Mapping (4 operations)
- `blender_uv` - UV unwrapping and mapping tools

## ⚙️ Configuration Options

### User Configuration

The package supports comprehensive user configuration:

- **Blender Executable Path**: Auto-detection or manual specification
- **Performance Settings**: Timeout, parallel operations, GPU rendering
- **Render Quality**: Samples, resolution, output format
- **Directories**: Temp files, logs, backups
- **Debug Options**: Logging levels, performance monitoring

### Build Configuration

Customize the build process:

```powershell
# Build with custom version
.\build-mcpb-package.ps1 -Version "1.1.0"

# Skip signing
.\build-mcpb-package.ps1 -NoSign

# Clean build
.\build-mcpb-package.ps1 -Clean

# Verbose output
.\build-mcpb-package.ps1 -Verbose
```

## 📋 Workflow Templates

### Quick Start Templates

Located in `prompts/quick_start_templates.md`:

- **Basic Scene Creation**: Cube, sphere, lighting, rendering
- **Game Asset Pipeline**: Character creation, export to Unity
- **Product Visualization**: Clean lighting, turntable animation
- **Animation Workflow**: Keyframes, motion, playback

### Advanced Workflow Templates

Located in `prompts/advanced_workflow_templates.md`:

- **Character Creation Pipeline**: Modeling → UV → Rigging → Animation
- **Environment Creation**: Terrain, architecture, vegetation, lighting
- **VFX Pipeline**: Particles, fluids, compositing
- **Procedural Generation**: Cities, materials, textures

## 🔧 Development Scripts

### Build Script (`build-mcpb-package.ps1`)

**Parameters:**
- `-NoSign`: Skip package signing
- `-Clean`: Clean previous builds
- `-OutputDir`: Custom output directory
- `-Version`: Set package version
- `-Verbose`: Detailed output

**Example:**
```powershell
.\build-mcpb-package.ps1 -Version "2.0.0" -Verbose
```

### Validation Script (`validate-mcpb-package.ps1`)

**Parameters:**
- `-PackagePath`: Path to MCPB package (required)
- `-Verbose`: Detailed output
- `-Detailed`: Extract and validate contents

**Example:**
```powershell
.\validate-mcpb-package.ps1 -PackagePath dist\blender-mcp.mcpb -Detailed
```

### Installation Test Script (`test-mcpb-installation.ps1`)

**Parameters:**
- `-PackagePath`: Path to MCPB package (required)
- `-TempDir`: Custom temp directory
- `-KeepTemp`: Don't clean up test files
- `-Verbose`: Detailed output
- `-SkipCleanup`: Skip cleanup

**Example:**
```powershell
.\test-mcpb-installation.ps1 -PackagePath dist\blender-mcp.mcpb -KeepTemp
```

## 🎯 Quality Assurance

### Automated Testing

The packaging system includes comprehensive testing:

1. **Package Validation**: Structure, manifest, contents
2. **Installation Testing**: Simulated install, functionality tests
3. **Blender Integration**: Script execution, tool registration
4. **Configuration Testing**: User settings, defaults

### CI/CD Integration

For automated builds in GitHub Actions:

```yaml
- name: Build MCPB Package
  run: .\mcpb-packaging\scripts\build-mcpb-package.ps1

- name: Validate Package
  run: .\mcpb-packaging\scripts\validate-mcpb-package.ps1 -PackagePath dist\blender-mcp.mcpb

- name: Test Installation
  run: .\mcpb-packaging\scripts\test-mcpb-installation.ps1 -PackagePath dist\blender-mcp.mcpb
```

## 📚 Documentation

### Included Documentation

- **Tool Reference**: Complete API documentation for all 37 tools
- **Workflow Guides**: Step-by-step tutorials for common tasks
- **Troubleshooting**: Common issues and solutions
- **Best Practices**: Performance optimization, file organization

### External Resources

- [FastMCP 2.12 Documentation](https://fastmcp.com/)
- [Blender Python API](https://docs.blender.org/api/current/)
- [MCP Specification](https://modelcontextprotocol.io/)

## 🚀 Distribution

### One-Click Installation

Users can install by:
1. Downloading the `.mcpb` file
2. Dragging it into Claude Desktop
3. Configuring Blender path in settings

### Manual Installation

For custom installations:

```powershell
# Extract package
mcpb extract blender-mcp.mcpb --output install-dir

# Configure environment
cd install-dir
python -m pip install -r requirements.txt

# Run server
python -m blender_mcp
```

## 🔒 Security & Sandboxing

- **Trusted Execution**: All Blender scripts run in controlled environment
- **File Access**: Limited to specified directories
- **Network Access**: Disabled by default
- **Subprocess Control**: Restricted to Blender execution only

## 🐛 Troubleshooting

### Common Issues

**Build Fails:**
- Ensure Node.js and MCPB CLI are installed
- Check Python dependencies
- Verify file paths in manifest

**Validation Errors:**
- Check manifest JSON syntax
- Verify all required files exist
- Ensure tool registrations are correct

**Installation Issues:**
- Confirm Blender executable path
- Check Python environment
- Verify MCPB CLI version

### Debug Mode

Enable verbose logging:

```powershell
$env:BLENDER_MCP_LOG_LEVEL = "DEBUG"
.\scripts\build-mcpb-package.ps1 -Verbose
```

## 📈 Performance Optimization

### Build Optimization

- **Parallel Processing**: Multiple operations can run simultaneously
- **GPU Acceleration**: Enable for rendering operations
- **Caching**: Reuse computed results where possible

### Runtime Optimization

- **LOD Systems**: Automatic level-of-detail for complex scenes
- **Texture Streaming**: Load textures on demand
- **Memory Management**: Automatic cleanup of unused resources

## 🤝 Contributing

### Development Setup

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install MCPB CLI: `npm install -g @anthropic-ai/mcpb`
4. Run tests: `python -m pytest tests/`

### Adding New Tools

1. Create tool in appropriate category folder
2. Register in `src/blender_mcp/app.py`
3. Add to manifest configuration
4. Update documentation
5. Test installation and functionality

## 📄 License

This MCPB package is licensed under the MIT License. See the main project LICENSE file for details.

## 🆘 Support

- **Documentation**: Check `docs/` directory for detailed guides
- **Issues**: Report bugs on GitHub Issues
- **Templates**: Use included workflow templates for common tasks
- **Community**: Join Blender MCP discussions

---

**Blender MCP MCPB Packaging v1.0.0** - Professional 3D automation for Claude Desktop

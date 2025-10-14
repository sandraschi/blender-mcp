# 🎨 Blender MCP Documentation

**Complete Blender automation and asset management platform with AI-powered workflows.**

Blender MCP is a FastMCP 2.12 compliant server that provides programmatic control over Blender's 3D creation, manipulation, and rendering capabilities through AI assistants like Claude Desktop.

## 🚀 Quick Start

### For Users
1. **Install** the MCP server package
2. **Configure** your Blender executable path
3. **Connect** to Claude Desktop
4. **Start creating** 3D content with natural language

### For Developers
1. **Clone** the repository
2. **Install** dependencies with `pip install -r requirements.txt`
3. **Run** `python -m blender_mcp --debug`
4. **Start developing** custom tools and integrations

## 🎯 Key Features

### Core Capabilities
- **50+ Specialized Tools** across 19 categories
- **Real Blender Integration** - All tools tested with Blender 4.4
- **Full 3D Pipeline** - From modeling to rendering with physics
- **Asset Management** - Download and import from popular repositories
- **GUI Mode Support** - Interactive Blender workflows

### AI Integration
- **Natural Language Control** - Describe what you want in plain English
- **Intelligent Tool Selection** - Claude automatically chooses the right tools
- **Context Awareness** - Maintains scene state across operations
- **Error Recovery** - Graceful handling of operation failures

### Asset Ecosystem
- **BlenderKit Integration** - Official Blender asset platform
- **Free Asset Libraries** - Poly Haven, AmbientCG, and more
- **Automated Downloads** - Direct URL import with format detection
- **Material Management** - PBR materials and texture workflows

## 📖 Documentation Sections

### 🎨 Blender MCP
- **[Tool Reference](blender/TOOL_REFERENCE.md)** - Complete API documentation
- **[Functionality Plan](blender/BLENDER_MCP_FUNCTIONALITY_PLAN.md)** - Tool inventory and status
- **[GUI Mode](blender/GUI_MODE.md)** - Interactive Blender integration

### 📦 Assets & Downloads
- **[BlenderKit Guide](blender/BLENDERKIT_GUIDE.md)** - Official asset platform
- **[Free Assets Guide](blender/FREE_ASSETS_GUIDE.md)** - Legal free asset sources
- **[Asset Repositories](blender/ASSET_REPOSITORIES.md)** - Automated repository integration

### 🔧 Development
- **[Standards](.cursor/rules.md)** - Coding and documentation standards
- **[AI Development](development/AI_DEVELOPMENT_RULES.md)** - AI-assisted development guide
- **[Logging Guide](development/LOGURU_LOGGING_GUIDE.md)** - Comprehensive logging documentation

## 🛠️ Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install blender-mcp
```

### Option 2: Install from Source
```bash
git clone https://github.com/sandraschi/blender-mcp.git
cd blender-mcp
pip install -r requirements.txt
pip install -e .
```

### Option 3: MCPB Package
```bash
# Download from releases
mcpb install blender-mcp.mcpb
```

## ⚙️ Configuration

### Basic Setup
```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "python",
      "args": ["-m", "blender_mcp"],
      "env": {
        "BLENDER_EXECUTABLE": "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe"
      }
    }
  }
}
```

### Advanced Configuration
- **Custom Blender Path** - Specify exact Blender executable location
- **Performance Settings** - Adjust operation timeouts and parallel processing
- **Asset Directories** - Configure download and cache locations
- **Logging Levels** - Control verbosity and log destinations

## 🎮 Usage Examples

### Basic Scene Creation
```
"Create a red cube at position [0, 0, 0] with size 2"
→ blender_mesh(operation="create_cube", location=[0,0,0], scale=[2,2,2])
→ blender_materials(operation="create_basic_material", name="RedMaterial", base_color=[1,0,0])
→ blender_materials(operation="assign_material", object_name="Cube", material_name="RedMaterial")
```

### Asset Download & Import
```
"Download a katana model from polyhaven and import it"
→ Search Poly Haven for katana assets
→ Download selected model
→ blender_download(url="https://dl.polyhaven.org/file/.../katana.obj")
```

### Complex Animation
```
"Create a bouncing ball animation with physics"
→ blender_mesh(operation="create_sphere", name="Ball")
→ blender_physics(operation="add_rigid_body", object_name="Ball")
→ blender_physics(operation="enable_gravity")
→ blender_animation(operation="bake_physics", start_frame=1, end_frame=120)
```

## 🏗️ Architecture

### FastMCP 2.12 Framework
- **Tool Registration** - Automatic discovery and registration
- **Parameter Validation** - Pydantic-based type checking
- **Async Operations** - Non-blocking Blender execution
- **Error Handling** - Comprehensive exception management

### Blender Integration
- **Subprocess Execution** - Isolated Blender processes
- **Script Generation** - Dynamic Python script creation
- **Result Parsing** - Structured output processing
- **Resource Management** - Automatic cleanup and optimization

### Asset Pipeline
- **Multi-Format Support** - OBJ, FBX, glTF, STL, and more
- **Automatic Import** - Format detection and appropriate import methods
- **Material Preservation** - Maintain PBR properties and textures
- **Batch Processing** - Handle multiple assets efficiently

## 📊 Tool Categories

| Category | Tools | Description |
|----------|-------|-------------|
| **Scene Management** | 12 | Object hierarchy, selections, transformations |
| **Mesh Creation** | 7 | Primitives, modifiers, mesh operations |
| **Materials** | 7 | PBR materials, textures, shaders |
| **Lighting** | 1 | HDRI, lights, rendering setup |
| **Animation** | 1 | Keyframes, physics, character animation |
| **Assets** | 3 | Download, import, asset management |
| **Export/Import** | 2 | File format conversion |
| **Utilities** | 9 | Help, logging, status, debugging |

## 🔧 Development

### Contributing
- **Fork** the repository
- **Create** a feature branch
- **Add** comprehensive tests
- **Submit** a pull request

### Testing
```bash
# Unit tests (no Blender required)
pytest tests/unit/ -v

# Integration tests (Blender required)
pytest tests/integration/ -v

# All tests
pytest tests/ -v
```

### Building Documentation
```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

## 📈 Roadmap

### Current Status
- ✅ **50 Working Tools** - Complete Blender automation
- ✅ **Asset Integration** - BlenderKit and free repositories
- ✅ **Documentation** - Comprehensive guides and references
- ✅ **Testing** - Full test coverage and CI/CD

### Upcoming Features
- 🔄 **Enhanced AI Integration** - Better tool selection and chaining
- 🔄 **Performance Optimization** - Faster operations and caching
- 🔄 **Extended Asset Support** - More formats and repositories
- 🔄 **Plugin Architecture** - Custom tool development
- 🔄 **Cloud Rendering** - Distributed rendering capabilities

## 🤝 Community

### Support
- **Issues** - [GitHub Issues](https://github.com/sandraschi/blender-mcp/issues)
- **Discussions** - [GitHub Discussions](https://github.com/sandraschi/blender-mcp/discussions)
- **Discord** - Community chat and support

### Contributing
- **Code** - Submit pull requests
- **Documentation** - Improve guides and examples
- **Testing** - Add test cases and report bugs
- **Feedback** - Share your experience and suggestions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Transform your Blender workflow with AI-powered 3D automation!** 🚀🎨✨

*Built with ❤️ for the Blender community*

# Blender MCP Server 

A comprehensive Model-Controller-Presenter (MCP) server for Blender, designed to automate 3D content creation, manipulation, and optimization through a clean, programmatic interface. Perfect for automating Blender workflows, batch processing, and integrating with other applications.

## Features

- **Automated 3D Content Creation**: Programmatically generate and manipulate 3D objects, materials, and scenes
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Extensive Toolset**:
  - Advanced animation and rigging tools
  - Material and shader management
  - Scene composition and lighting controls
  - Physics and simulation configuration
  - High-quality rendering pipeline
  - Export to multiple formats (FBX, glTF, OBJ, etc.)
- **Developer Friendly**:
  - Type-annotated Python code
  - Comprehensive documentation
  - Example scripts for common workflows
  - Modular architecture for easy extension

## Quick Start

### Basic Usage Example

```python
# Scene setup
await create_scene("VictorianBoudoir")

# Add elegant furniture
await create_chaiselongue(
    name="ElegantChaise",
    x=0.0, y=0.0, z=0.0,
    style="victorian"
)

# Apply materials
await create_fabric_material(
    name="VelvetUpholstery",
    fabric_type="velvet",
    base_r=0.5, base_g=0.2, base_b=0.3,
    roughness=0.8
)

# Export for Unity
await export_for_unity(
    output_path="boudoir_scene.fbx",
    scale=1.0,
    apply_modifiers=True,
    optimize_materials=True,
    bake_textures=False,
    lod_levels=2
)
```

### VRChat Optimization Example

```python
await export_for_vrchat(
    output_path="vrchat_avatar.vrm",
    polygon_limit=20000,
    material_limit=8,
    texture_size_limit=1024,
    performance_rank="Good"
)
```

## Installation

### Prerequisites

- Python 3.8+
- Blender 3.0+
- pip

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-org/blender-mcp.git
   cd blender-mcp
   ```

2. Install the package in development mode:

   ```bash
   pip install -e .
   ```

3. Set the Blender executable path (or ensure it's in your PATH):

   ```bash
   # Linux/macOS
   export BLENDER_EXECUTABLE=/path/to/blender
   
   # Windows
   set BLENDER_EXECUTABLE=C:\\path\\to\\blender.exe
   ```

## Usage

### Starting the Server

#### Standard Input/Output Mode

```bash
python -m blender_mcp.server
```

#### HTTP Server Mode

```bash
python -m blender_mcp.server --http --host 0.0.0.0 --port 8000
```

### Example: Creating a Scene with Furniture

```python
# Scene setup
await create_scene("VictorianBoudoir")

# Add elegant furniture
await create_chaiselongue(
    name="ElegantChaise",
    x=0.0, y=0.0, z=0.0,
    style="victorian"
)

# Apply materials
await create_fabric_material(
    name="VelvetUpholstery",
    fabric_type="velvet",
    base_r=0.5, base_g=0.2, base_b=0.3,
    roughness=0.8
)

# Export for Unity
await export_for_unity(
    output_path="boudoir_scene.fbx",
    scale=1.0,
    apply_modifiers=True,
    optimize_materials=True,
    bake_textures=False,
    lod_levels=2
)
```

### Example: VRChat Optimization

```python
await export_for_vrchat(
    output_path="vrchat_avatar.vrm",
    polygon_limit=20000,
    material_limit=8,
    texture_size_limit=1024,
    performance_rank="Good"
)
```

## Project Structure

```text
blender-mcp/
├── dxt/                    # DXT packaging files
│   ├── dxt.json           # Package manifest
│   └── install.py         # Installation script
├── src/
│   └── blender_mcp/       # Main package
│       ├── handlers/      # MCP tool handlers
│       │   ├── __init__.py
│       │   ├── scene_handler.py
│       │   ├── mesh_handler.py
│       │   ├── material_handler.py
│       │   ├── export_handler.py
│       │   └── render_handler.py
│       ├── decorators.py  # Custom decorators
│       ├── exceptions.py  # Custom exceptions
│       ├── server.py      # MCP server entry point
│       └── utils/         # Utility modules
│           └── blender_executor.py
├── tests/                 # Test suite
├── README.md              # This file
└── pyproject.toml         # Project configuration
```

## API Reference

### Scene Management

- `create_scene(name: str) -> str`: Create a new Blender scene
- `list_scenes() -> str`: List all available scenes
- `clear_scene() -> str`: Remove all objects from the current scene

### Mesh Creation

- `create_chaiselongue(name: str, x: float, y: float, z: float, style: str) -> str`: Create a chaiselongue
- `create_vanity_table(name: str, x: float, y: float, z: float, style: str) -> str`: Create a vanity table

### Material Creation

- `create_fabric_material(name: str, fabric_type: str, base_r: float, base_g: float, base_b: float, roughness: float) -> str`: Create a fabric material
- `create_metal_material(name: str, metal_type: str, roughness: float) -> str`: Create a metal material
- `create_wood_material(name: str, wood_type: str, grain_scale: float) -> str`: Create a wood material

### Export & Rendering

- `export_for_unity(output_path: str, scale: float, apply_modifiers: bool, optimize_materials: bool, bake_textures: bool, lod_levels: int) -> str`: Export scene for Unity
- `export_for_vrchat(output_path: str, polygon_limit: int, material_limit: int, texture_size_limit: int, performance_rank: str) -> str`: Export scene for VRChat
- `render_turntable(output_dir: str, frames: int, resolution_x: int, resolution_y: int, format: str) -> str`: Render a turntable animation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Blender Foundation for the amazing 3D creation suite
- FastMCP team for the MCP server framework
- All contributors who helped improve this project

# Blender MCP Server

A comprehensive FastMCP 2.12 compliant MCP server for Blender automation, designed to provide programmatic control over Blender's extensive 3D creation, manipulation, and rendering capabilities. Connects via stdio to Claude Desktop and via HTTP transport to other MCP-compatible tools.

## What is This?

This is a **FastMCP 2.12 server** that exposes Blender's powerful 3D creation and manipulation capabilities as standardized MCP tools. It allows AI assistants like Claude to:

- **Create 3D scenes, objects, and materials programmatically**
- **Automate complex Blender workflows**
- **Generate content for games, visualization, and media production**
- **Batch process 3D assets and exports**

## Architecture

**FastMCP 2.12 Standard Compliance:**
- ✅ Proper `@app.tool` decorators
- ✅ Multiline self-documenting docstrings (no """ inside)
- ✅ Pydantic parameter validation
- ✅ Async/await pattern
- ✅ Stdio and HTTP transport support

**Connection Methods:**
- **Stdio**: Connect to Claude Desktop for interactive 3D creation
- **HTTP**: REST API for integration with other applications
- **Local Development**: Direct Python API access

## Available Tools by Category

### 🎨 Scene Management
- `create_scene` - Create new Blender scenes
- `list_scenes` - List all scenes in the project
- `clear_scene` - Remove all objects from active scene
- `set_active_scene` - Switch between scenes
- `link_object_to_scene` - Share objects between scenes
- `create_collection` - Organize objects in collections
- `add_to_collection` - Add objects to collections
- `set_active_collection` - Set working collection
- `set_view_layer` - Control render layers

### 🏗️ Mesh & Geometry
- `create_cube` - Create cube primitives
- `create_sphere` - Create sphere primitives
- `create_cylinder` - Create cylinder primitives
- `create_plane` - Create plane primitives
- `create_torus` - Create torus primitives
- `create_monkey` - Create Blender's Suzanne primitive
- `create_text` - Create 3D text objects
- `create_curve` - Create bezier curves
- `create_surface` - Create NURBS surfaces

### 🎨 Materials & Shaders
- `create_fabric_material` - Realistic fabric materials (velvet, silk, cotton, etc.)
- `create_metal_material` - Metal materials (gold, silver, brass, etc.)
- `create_wood_material` - Wood materials with grain textures
- `create_glass_material` - Glass materials with refraction
- `create_ceramic_material` - Ceramic materials
- `create_plastic_material` - Plastic materials
- `create_emissive_material` - Self-illuminating materials
- `assign_material_to_object` - Apply materials to objects
- `create_material_from_preset` - Use predefined material configurations

### 🪑 Furniture Creation
- `create_chair` - Create chair objects with various styles
- `create_table` - Create table objects with dimensions
- `create_bed` - Create bed objects
- `create_sofa` - Create sofa objects with seat configurations
- `create_room` - Generate complete room environments
- `create_building` - Create multi-floor building structures

### 💡 Lighting
- `create_sun_light` - Create directional sunlight
- `create_point_light` - Create omnidirectional point lights
- `create_spot_light` - Create focused spotlights
- `create_area_light` - Create area lighting panels
- `set_light_properties` - Control light intensity, color, shadows
- `create_hdri_environment` - Set up HDR environment lighting
- `configure_lighting_setup` - Automated lighting rigs

### 📷 Camera & Viewport
- `create_camera` - Add cameras to scenes
- `set_camera_properties` - Control focal length, aperture, focus
- `position_camera` - Set camera location and rotation
- `create_camera_rig` - Multi-camera setups
- `set_active_camera` - Switch between cameras
- `configure_viewport` - Set viewport display options

### 🎬 Animation & Rigging
- `create_armature` - Create bone structures
- `rig_character` - Automated character rigging
- `create_animation` - Keyframe animation tools
- `animate_object` - Animate object properties
- `create_walk_cycle` - Procedural walk animations
- `export_animation` - Export animation data

### 🎯 Rendering & Output
- `set_render_engine` - Switch between Cycles/EEVEE
- `configure_render_settings` - Resolution, samples, quality
- `set_output_format` - Configure export formats
- `render_scene` - Generate final renders
- `render_animation` - Create animation sequences
- `create_render_passes` - Multi-layer rendering

### 📦 Import & Export
- `import_fbx` - Import FBX files
- `import_obj` - Import OBJ files
- `import_gltf` - Import glTF files
- `export_fbx` - Export to FBX format
- `export_gltf` - Export to glTF format
- `export_obj` - Export to OBJ format
- `export_stl` - Export to STL format
- `batch_export` - Process multiple files

### ⚡ Physics & Simulation
- `enable_physics` - Add physics properties
- `create_rigid_body` - Rigid body dynamics
- `create_soft_body` - Soft body simulation
- `create_cloth` - Cloth simulation
- `create_fluid` - Fluid simulation
- `bake_physics` - Bake physics animations

### 🎛️ Modifiers & Effects
- `add_subdivision` - Subdivision surface modifier
- `add_bevel` - Bevel modifier
- `add_array` - Array modifier
- `add_boolean` - Boolean operations
- `add_lattice` - Lattice deformation
- `apply_modifiers` - Apply all modifiers

### 🎨 Textures & UVs
- `create_texture` - Generate procedural textures
- `load_image_texture` - Import image textures
- `unwrap_uv` - UV unwrapping tools
- `pack_uv_islands` - Optimize UV layouts
- `bake_textures` - Bake lighting to textures

### 🎭 Particles & Effects
- `create_particle_system` - Hair, grass, fire effects
- `configure_emitter` - Particle emission settings
- `create_smoke` - Smoke simulation
- `create_fire` - Fire effects
- `create_explosion` - Explosion effects

### 🏗️ Advanced Features
- `create_asset` - Asset management tools
- `batch_process` - Process multiple files
- `create_procedural` - Procedural generation
- `optimize_scene` - Performance optimization
- `validate_geometry` - Mesh validation tools

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Stdio Connection (Claude Desktop)
```bash
python -m blender_mcp.server
```

### HTTP Server Mode
```bash
python -m blender_mcp.server --http --port 8000
```

### Direct Python API
```python
from blender_mcp.app import get_app

app = get_app()

# Use tools programmatically
result = await app.run_tool("create_scene", {"scene_name": "MyScene"})
```

## Configuration

- **Blender Path**: Auto-detected or set via `BLENDER_EXECUTABLE` environment variable
- **Tool Categories**: Organized by functionality for easy discovery
- **Parameter Validation**: All tools use Pydantic schemas for type safety
- **Error Handling**: Comprehensive error reporting and recovery

## Development

- **Handler Layer**: Business logic in `src/blender_mcp/handlers/`
- **Tool Layer**: MCP interface in `src/blender_mcp/tools/` (organized by category)
- **Standards**: FastMCP 2.12 compliance with proper decorators and documentation
- **Testing**: Comprehensive test suite with real Blender integration

## Contributing

1. Add handlers in `src/blender_mcp/handlers/`
2. Create tool definitions in `src/blender_mcp/tools/{category}/`
3. Follow FastMCP 2.12 patterns with `@app.tool` decorators
4. Use multiline docstrings for self-documentation
5. Add tests in `tests/` directory

## License

MIT License - see LICENSE file

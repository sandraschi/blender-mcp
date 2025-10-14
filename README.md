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

## Available Tools

This server provides **50 working tools** for comprehensive Blender automation:

### 🎨 Object Creation & Mesh (1 tool - 7 operations)
- **`blender_mesh`** - Create and manipulate 3D objects ✅ **TESTED & WORKING**
  - `create_cube` - Create cube primitives
  - `create_sphere` - Create sphere primitives
  - `create_cylinder` - Create cylinder primitives
  - `create_cone` - Create cone primitives
  - `create_plane` - Create plane primitives
  - `create_torus` - Create torus primitives
  - `create_monkey` - Create Suzanne (monkey) primitives
  - `duplicate_object` - Duplicate existing objects
  - `delete_object` - Delete objects by name

### 🎬 Animation & Motion (1 tool - 6 operations)
- **`blender_animation`** - Create animations and keyframes ✅ **FRAMEWORK WORKING**
  - `set_keyframe` - Set keyframes for object properties
  - `animate_location` - Animate object movement over time
  - `animate_rotation` - Animate object rotation over time
  - `animate_scale` - Animate object scaling over time
  - `play_animation` - Start animation playback
  - `set_frame_range` - Set animation frame range
  - `clear_animation` - Clear all keyframes from objects

### 💡 Lighting & Rendering (2 tools - 7 operations)
- **`blender_lighting`** - Create and manage lights ✅ **TESTED & WORKING**
  - `create_sun` - Create directional sun lights
  - `create_point` - Create omnidirectional point lights
  - `create_spot` - Create focused spot lights
  - `create_area` - Create area lights for soft shadows
  - `setup_three_point` - Create three-point lighting rigs
  - `setup_hdri` - Set up HDRI environment lighting
  - `adjust_light` - Modify existing light properties
- **`setup_lighting`** - Legacy lighting setup tool

### 🎨 Scene Management (12 tools)
- `create_scene` - Create new Blender scenes
- `list_scenes` - List all scenes in the project ✅ **TESTED & WORKING**
- `clear_scene` - Remove all objects from active scene
- `set_active_scene` - Switch between scenes
- `link_object_to_scene` - Share objects between scenes
- `create_collection` - Organize objects in collections
- `add_to_collection` - Add objects to collections
- `set_active_collection` - Set working collection
- `set_view_layer` - Control render layers
- `setup_lighting` - Automated lighting rigs
- `setup_camera` - Camera positioning
- `set_render_settings` - Basic render configuration

### 📤 Export & Import (2 tools - 5+ operations)
- **`blender_export`** - Export scenes for Unity and VRChat ✅ **WORKING**
  - `export_unity` - Export to Unity-compatible formats
  - `export_vrchat` - Export to VRChat-compatible formats
- **`blender_import`** - Import various 3D file formats ✅ **WORKING**
  - `import_[format]` - Import FBX, OBJ, GLTF, STL, PLY, etc.
  - `link_asset` - Link external assets

### 🪑 Complex Objects & Furniture (1 tool - 9 operations)
- **`blender_furniture`** - Create furniture and complex objects ✅ **WORKING**
  - `create_chair` - Create dining/office/arm chairs
  - `create_table` - Create dining/coffee/desks
  - `create_bed` - Create single/double/bunk beds
  - `create_sofa` - Create sofas and couches
  - `create_cabinet` - Create storage cabinets
  - `create_desk` - Create office workstations
  - `create_shelf` - Create bookshelves
  - `create_stool` - Create stools and bar stools

### 🎨 Textures & Materials (2 tools - 10+ operations)
- **`blender_textures`** - Create and manage textures ✅ **WORKING**
  - `create_[type]` - Create noise/voronoi/musgrave/wave textures
  - `assign_texture` - Assign textures to materials
  - `bake_texture` - Bake textures from objects
- **`blender_materials`** - Material creation and management
  - `create_fabric_material` - Realistic fabric materials (velvet, silk, cotton, etc.)
  - `create_metal_material` - Metal materials (gold, silver, brass, etc.)
  - `create_wood_material` - Wood materials with grain textures
  - `create_glass_material` - Glass materials with refraction
  - `create_ceramic_material` - Ceramic materials
  - `assign_material_to_object` - Apply materials to objects
  - `create_material_from_preset` - Use predefined material configurations

### 📷 Camera Control (1 tool - 3 operations)
- **`blender_camera`** - Camera creation and control ✅ **WORKING**
  - `create_camera` - Create new cameras with custom settings
  - `set_active_camera` - Switch between cameras
  - `set_camera_lens` - Adjust lens, sensor, and clipping

### 🔌 Addon Management (1 tool - 3 operations)
- **`blender_addons`** - Manage Blender addons ✅ **WORKING**
  - `list_addons` - List all available addons
  - `install_addon` - Install addon from file
  - `uninstall_addon` - Remove addons

### 🔧 Modifiers (1 tool - 10+ operations)
- **`blender_modifiers`** - Apply mesh modifiers ✅ **WORKING**
  - `add_subsurf` - Add subdivision surface modifier
  - `add_bevel` - Add bevel modifier
  - `add_mirror` - Add mirror modifier
  - `add_solidify` - Add solidify modifier
  - `add_array` - Add array modifier
  - `remove_modifier` - Remove modifiers
  - `apply_modifier` - Apply modifier to mesh

### 🎨 Render (1 tool - 4 operations)
- **`blender_render`** - Render scenes and animations ✅ **WORKING**
  - `render_preview` - Render single frame preview
  - `render_turntable` - Render 360-degree turntable animation
  - `render_animation` - Render full animation sequence

### 📐 Transform (1 tool - 8 operations)
- **`blender_transform`** - Transform objects in 3D space ✅ **WORKING**
  - `set_location` - Set object position
  - `set_rotation` - Set object rotation
  - `set_scale` - Set object scale
  - `translate` - Move object by offset
  - `rotate` - Rotate object by angle
  - `apply_transform` - Apply transforms to mesh
  - `reset_transform` - Reset transforms to identity

### 🎯 Selection (1 tool - 6 operations)
- **`blender_selection`** - Select objects and elements ✅ **WORKING**
  - `select_objects` - Select specific objects by name
  - `select_by_type` - Select all objects of a type
  - `select_by_material` - Select objects by material
  - `select_all` - Select all objects in scene
  - `select_none` - Deselect all objects
  - `invert_selection` - Invert current selection

### 🦴 Rigging (1 tool - 4 operations)
- **`blender_rigging`** - Create armatures and character rigging ✅ **WORKING**
  - `create_armature` - Create new armature object
  - `add_bone` - Add bones to armature
  - `create_bone_ik` - Create inverse kinematics constraints
  - `create_basic_rig` - Create basic biped rig

### ⚡ Physics (1 tool - 9 operations)
- **`blender_physics`** - Enable physics simulations ✅ **WORKING**
  - `enable_rigid_body` - Add rigid body physics
  - `enable_cloth` - Add cloth simulation
  - `enable_soft_body` - Add soft body simulation
  - `enable_fluid` - Add fluid simulation
  - `bake_physics` - Bake physics to keyframes
  - `add_force_field` - Add force fields to scene
  - `configure_world` - Set physics world settings

### ✨ Particles (1 tool - 3 operations)
- **`blender_particles`** - Create particle systems ✅ **WORKING**
  - `create_particle_system` - Create basic particle system
  - `create_hair_particles` - Create hair/fur particles
  - `create_fire_effect` - Create fire/smoke effects
  - `bake_particles` - Bake particle simulation

### 🗺️ UV Mapping (1 tool - 7 operations)
- **`blender_uv`** - Manage UV mapping and unwrapping ✅ **WORKING**
  - `unwrap` - Unwrap UV coordinates
  - `smart_project` - Smart UV projection
  - `cube_project` - Cube projection
  - `cylinder_project` - Cylindrical projection
  - `sphere_project` - Spherical projection
  - `reset_uvs` - Reset UV coordinates
  - `get_uv_info` - Get UV mapping information

📚 **Complete tool documentation**: See [`docs/BLENDER_MCP_FUNCTIONALITY_PLAN.md`](docs/BLENDER_MCP_FUNCTIONALITY_PLAN.md) for detailed information about all implemented tools.

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

# Blender MCP Server

A comprehensive FastMCP 2.12+ MCP server for Blender automation, designed to provide programmatic control over Blender's extensive 3D creation, manipulation, and rendering capabilities. **Full VRM avatar workflow support** for character animation.

## What is This?

This is a **FastMCP 2.12+ server** that exposes Blender's powerful 3D creation and manipulation capabilities as standardized MCP tools. It allows AI assistants like Claude to:

- **Create 3D scenes, objects, and materials programmatically**
- **Animate VRM avatars** with bone posing and facial expressions
- **Automate complex Blender workflows**
- **Generate content for games, VRChat, and media production**
- **Batch process 3D assets and exports**

## Architecture

**FastMCP 2.12+ Standard Compliance:**
- ✅ Proper `@app.tool` decorators with Literal types
- ✅ Portmanteau pattern (32 tools, 100+ operations)
- ✅ Multiline self-documenting docstrings
- ✅ Pydantic parameter validation
- ✅ Async/await pattern
- ✅ Stdio and HTTP transport support

**Connection Methods:**
- **Stdio**: Connect to Claude Desktop for interactive 3D creation
- **HTTP**: REST API for integration with other applications
- **Local Development**: Direct Python API access

## Available Tools

This server provides **32 portmanteau tools** with **100+ operations**:

### 🎨 Object Creation & Mesh
- **`blender_mesh`** (9 ops) - Create and manipulate 3D primitives
  - `create_cube`, `create_sphere`, `create_cylinder`, `create_cone`
  - `create_plane`, `create_torus`, `create_monkey`
  - `duplicate_object`, `delete_object`

### 🎬 Animation & Motion (21 operations) ⭐ NEW
- **`blender_animation`** - Complete animation system
  - **Basic**: `set_keyframe`, `animate_location/rotation/scale`, `play_animation`, `set_frame_range`, `clear_animation`
  - **Shape Keys (VRM)**: `list_shape_keys`, `set_shape_key`, `keyframe_shape_key`, `create_shape_key`
  - **Actions**: `list_actions`, `create_action`, `set_active_action`, `push_to_nla`
  - **Interpolation**: `set_interpolation`, `set_easing`
  - **Constraints**: `add_constraint`, `add_bone_constraint`
  - **Baking**: `bake_action`, `bake_all_actions`

### 🦴 Rigging & Bones (8 operations) ⭐ NEW
- **`blender_rigging`** - Armature and bone control
  - `create_armature`, `add_bone`, `create_bone_ik`, `create_basic_rig`
  - **VRM Support**: `list_bones`, `pose_bone`, `set_bone_keyframe`, `reset_pose`

### 🎨 Scene Management
- **`blender_scene`** (12 ops) - Scene, collection, view layer control
  - `create_scene`, `list_scenes`, `clear_scene`, `set_active_scene`
  - `create_collection`, `add_to_collection`, `set_active_collection`
  - `link_object_to_scene`, `set_view_layer`
  - `setup_lighting`, `setup_camera`, `set_render_settings`

### 🎨 Materials
- **`blender_materials`** (7 ops) - PBR material creation
  - `create_fabric`, `create_metal`, `create_wood`, `create_glass`, `create_ceramic`
  - `assign_to_object`, `create_from_preset`

### 💡 Lighting & Rendering
- **`blender_lighting`** (7 ops) - Light management
- **`blender_render`** (4 ops) - Preview, turntable, animation render
- **`blender_camera`** (3 ops) - Camera creation and settings

### 📤 Import & Export
- **`blender_import`** (2 ops) - FBX, OBJ, glTF, VRM import
- **`blender_export`** (2 ops) - Unity/VRChat export

### 🔧 Additional Tools
- `blender_physics`, `blender_particles`, `blender_modifiers`
- `blender_transform`, `blender_selection`, `blender_textures`, `blender_uv`
- `blender_furniture`, `blender_addons`
- `blender_help`, `blender_status`, `blender_download`, `blender_view_logs`

## VRM Avatar Workflow ⭐

Complete workflow for VRM character animation:

```python
# 1. Import VRM model
blender_import(operation="import_gltf", filepath="avatar.vrm")

# 2. Discover bone structure
blender_rigging(operation="list_bones", armature_name="Armature")
# Returns: hips, spine, chest, leftUpperArm, leftLowerArm, ...

# 3. Find facial expressions
blender_animation(operation="list_shape_keys", object_name="Face")
# Returns: happy, sad, angry, blink, ...

# 4. Pose bones (raise left arm)
blender_rigging(operation="pose_bone", armature_name="Armature", 
                bone_name="leftUpperArm", rotation=[0, 0, 90])

# 5. Set facial expression
blender_animation(operation="set_shape_key", object_name="Face", 
                  shape_key_name="happy", value=1.0)

# 6. Keyframe at frame 1
blender_rigging(operation="set_bone_keyframe", armature_name="Armature", 
                bone_name="leftUpperArm", frame=1)
blender_animation(operation="keyframe_shape_key", object_name="Face", 
                  shape_key_name="happy", frame=1)

# 7. Bake for clean export
blender_animation(operation="bake_action", object_name="Armature", 
                  start_frame=1, end_frame=120)
```
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

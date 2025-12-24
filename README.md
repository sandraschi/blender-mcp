# Blender MCP Server

**By FlowEngineer sandraschi**

A comprehensive FastMCP 2.13+ MCP server for Blender automation, providing programmatic control over Blender's 3D creation, manipulation, and rendering capabilities. **Full VRM avatar workflow support** for character animation.

## What is This?

This is a **FastMCP 2.13+ server** that exposes Blender's powerful 3D capabilities as standardized MCP tools. It allows AI assistants like Claude to:

- **Create 3D scenes, objects, and materials programmatically**
- **Animate VRM avatars** with bone posing and facial expressions
- **Execute batch workflows** via the macro tool
- **Generate content for games, VRChat, and media production**
- **Batch process 3D assets and exports**

## Architecture

**FastMCP 2.13+ Standard Compliance:**
- ✅ Proper `@app.tool` decorators with Literal types
- ✅ Portmanteau pattern (33 tools, 100+ operations)
- ✅ Multiline self-documenting docstrings
- ✅ Pydantic parameter validation
- ✅ Async/await pattern
- ✅ Stdio and HTTP transport support

**Connection Methods:**
- **Stdio**: Connect to Claude Desktop for interactive 3D creation
- **HTTP**: REST API for integration with other applications
- **Local Development**: Direct Python API access

## Available Tools (33 tools, 100+ operations)

### 🎨 Object Creation & Mesh
| Tool | Ops | Description |
|------|-----|-------------|
| `blender_mesh` | 9 | Create primitives (cube, sphere, cylinder, cone, plane, torus, monkey), duplicate, delete |
| `blender_furniture` | 9 | Create furniture (sofa, chair, table, bed, cabinet, desk, shelf, stool) with full geometry |

### 🎬 Animation & Motion ⭐ VRM-Ready
| Tool | Ops | Description |
|------|-----|-------------|
| `blender_animation` | 21 | Complete animation: keyframes, shape keys, actions, NLA, interpolation, constraints, baking |
| `blender_rigging` | 8 | Armature control: create, add bones, IK, list/pose/keyframe bones, reset pose |

### 🎨 Scene & Materials
| Tool | Ops | Description |
|------|-----|-------------|
| `blender_scene` | 12 | Scene/collection/view layer management, lighting setup, camera setup, render settings |
| `blender_materials` | 7 | PBR materials: fabric, metal, wood, glass, ceramic, assign, presets |

### 💡 Lighting & Camera
| Tool | Ops | Description |
|------|-----|-------------|
| `blender_lighting` | 7 | Sun, point, spot, area lights, three-point setup, HDRI, adjust |
| `blender_camera` | 3 | Create camera, set active, configure lens |
| `blender_render` | 4 | Preview, turntable, animation, current frame |

### 🔧 Modifiers & Transform
| Tool | Ops | Description |
|------|-----|-------------|
| `blender_modifiers` | 12 | Subsurf, bevel, mirror, solidify, array, boolean, decimate, displace, wave, apply |
| `blender_transform` | 8 | Location, rotation, scale (set/offset), apply, reset |
| `blender_selection` | 6 | Select by name/type/material, all, none, invert |

### ⚡ Physics & Particles
| Tool | Ops | Description |
|------|-----|-------------|
| `blender_physics` | 8 | Rigid body, cloth, soft body, fluid, bake, force fields, constraints |
| `blender_particles` | 7 | Particle systems, hair, fire, water, emission control, bake |

### 🗺️ Textures & UV
| Tool | Ops | Description |
|------|-----|-------------|
| `blender_textures` | 7 | Procedural: noise, voronoi, musgrave, wave, checker, brick, gradient |
| `blender_uv` | 5 | Unwrap, smart/cube/cylinder project, reset |

### 📤 Import & Export
| Tool | Ops | Description |
|------|-----|-------------|
| `blender_import` | 2 | FBX, OBJ, glTF, VRM import |
| `blender_export` | 2 | Unity/VRChat export |
| `blender_download` | 2 | Download assets from URLs |

### 🔄 Workflow & Batch ⭐ NEW
| Tool | Ops | Description |
|------|-----|-------------|
| `blender_workflow` | 3 | Execute multiple operations in single call, templates, variable passing |

### 🔧 Utility
| Tool | Ops | Description |
|------|-----|-------------|
| `blender_addons` | 3 | List, install, uninstall addons |
| `blender_help` | 5 | Documentation and help system |
| `blender_status` | 4 | System status and health |
| `blender_view_logs` | 2 | Log viewing and stats |

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

# 8. Export for VRChat
blender_export(operation="export_vrchat", output_path="avatar_animated.fbx")
```

## Batch Workflow (Macro) Tool ⭐ NEW

Execute multiple operations in a single call:

```python
# Create a furnished room in one call
blender_workflow(operation="execute", steps=[
    {"tool": "blender_scene", "operation": "clear_scene"},
    {"tool": "blender_furniture", "operation": "create_sofa", "name": "LivingSofa"},
    {"tool": "blender_furniture", "operation": "create_table", "name": "CoffeeTable", "table_type": "coffee"},
    {"tool": "blender_lighting", "operation": "setup_three_point"},
    {"tool": "blender_scene", "operation": "setup_camera", "location": [5, -5, 2]}
])

# Or use predefined templates
blender_workflow(operation="execute", template="product_shot")
blender_workflow(operation="execute", template="simple_scene")
```

**Features:**
- Batch execution (no round-trips)
- Predefined templates
- Variable references (`$varname`)
- Conditional execution (`if_result`)

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
result = await app.run_tool("blender_mesh", {"operation": "create_cube", "name": "MyCube"})
```

## Configuration

- **Blender Path**: Auto-detected or set via `BLENDER_EXECUTABLE` environment variable
- **Tool Categories**: Organized by functionality for easy discovery
- **Parameter Validation**: All tools use Pydantic schemas for type safety
- **Error Handling**: Comprehensive error reporting and recovery

## Development

- **Handler Layer**: Business logic in `src/blender_mcp/handlers/`
- **Tool Layer**: MCP interface in `src/blender_mcp/tools/` (organized by category)
- **Standards**: FastMCP 2.13 compliance with proper decorators and documentation
- **Testing**: Comprehensive test suite with real Blender integration

## Documentation

- [`docs/blender/TOOL_REFERENCE.md`](docs/blender/TOOL_REFERENCE.md) - Complete tool reference
- [`docs/blender/README.md`](docs/blender/README.md) - Blender-specific documentation
- [`docs/EXAMPLES.md`](docs/EXAMPLES.md) - Usage examples

## License

MIT License - see LICENSE file

# API Reference

## Overview

Blender MCP provides comprehensive APIs for 3D content creation through multiple interfaces: MCP protocol, HTTP REST API, and direct Python API.

## MCP Protocol Interface

### Tool Categories

#### AI Construction Tools

##### `construct_object`
Create 3D objects using natural language descriptions.

**Parameters:**
- `description` (str, required): Natural language object description
- `name` (str): Object name in scene (default: "ConstructedObject")
- `complexity` (str): "simple", "standard", "complex" (default: "standard")
- `style_preset` (str): "realistic", "stylized", "lowpoly", "scifi"
- `reference_objects` (List[str]): Objects to use as style reference
- `allow_modifications` (bool): Allow scene modifications (default: True)
- `max_iterations` (int): Maximum refinement iterations (default: 3)

**Returns:**
```json
{
  "success": true,
  "object_name": "ConstructedObject",
  "script_generated": true,
  "iterations_used": 1,
  "validation_results": {
    "security_score": 95,
    "complexity_score": 75
  },
  "scene_objects_created": ["Object1", "Object2"],
  "estimated_complexity": "standard",
  "next_steps": ["Apply materials", "Setup lighting"]
}
```

##### `manage_object_construction`
Advanced object construction and modification operations.

**Operations:**
- `construct`: Create new object (same as construct_object)
- `modify`: Improve existing object with LLM guidance

**Parameters:**
- `operation` (str, required): "construct" or "modify"
- `object_name` (str): Target object for modify operations
- `modification_description` (str): Description of desired changes
- Additional parameters same as construct_object

#### Repository Management Tools

##### `manage_object_repo`
Object repository operations with versioning and search.

**Operations:**
- `save`: Save object to repository
- `load`: Load object from repository
- `search`: Search repository by natural language
- `list_objects`: List all repository objects

**Save Parameters:**
- `object_name` (str, required): Blender object to save
- `object_name_display` (str, required): Display name
- `description` (str): Object description
- `tags` (List[str]): Search tags
- `category` (str): Organization category
- `quality_rating` (int): 1-10 quality score

**Load Parameters:**
- `object_id` (str, required): Repository object ID
- `target_name` (str): Name in current scene
- `position` (List[float]): [x, y, z] position
- `scale` (List[float]): [x, y, z] scale
- `version` (str): Specific version to load

**Search Parameters:**
- `query` (str, required): Natural language search query
- `category` (str): Filter by category
- `tags` (List[str]): Filter by tags
- `author` (str): Filter by author
- `min_quality` (int): Minimum quality rating
- `complexity` (str): Filter by complexity

#### Export and Integration Tools

##### `export_for_mcp_handoff`
Export objects for cross-MCP server integration.

**Parameters:**
- `asset_id` (str, required): Repository asset ID
- `target_mcp` (str, required): Target MCP ("vrchat", "resonite", "unity")
- `optimization_preset` (str): "automatic", "conservative", "aggressive"
- `quality_level` (str): "draft", "standard", "high", "ultra"
- `include_metadata` (bool): Include integration metadata

**Returns:**
```json
{
  "success": true,
  "asset_id": "asset_001",
  "target_mcp": "vrchat",
  "primary_files": ["asset.fbx"],
  "supporting_files": ["textures/*.png", "materials.json"],
  "integration_commands": [
    "vrchat_import_fbx --file asset.fbx --auto-setup"
  ],
  "metadata": {
    "platform_requirements": {
      "vrchat": {
        "polygon_limit": 70000,
        "material_limit": 8
      }
    }
  }
}
```

## Professional Tool Suite

### Mesh and Geometry (40+ operations)

#### `blender_mesh`
Basic mesh creation and manipulation.

**Operations:**
- `create_cube`, `create_sphere`, `create_cylinder`, `create_cone`, `create_plane`, `create_torus`, `create_monkey`
- `duplicate`, `delete`, `combine`, `separate`

**Common Parameters:**
- `name` (str): Object name
- `location` (List[float]): [x, y, z] position
- `rotation` (List[float]): [x, y, z] rotation in degrees
- `scale` (List[float]): [x, y, z] scale

#### `blender_furniture`
Pre-built furniture objects.

**Operations:**
- `create_sofa`, `create_chair`, `create_table`, `create_bed`, `create_cabinet`
- `create_desk`, `create_shelf`, `create_stool`

**Parameters:**
- `name` (str, required): Object name
- `position` (List[float]): Placement position
- `rotation` (float): Rotation in degrees
- `scale` (float): Size multiplier

### Materials and Texturing

#### `blender_materials`
PBR material creation and application.

**Operations:**
- `apply_pbr`: Apply physically-based rendering material
- `create_basic`: Create basic colored material
- `apply_texture`: Apply image texture
- `mix_materials`: Combine multiple materials

**PBR Parameters:**
- `object_name` (str, required): Target object
- `base_color` (List[float]): [R, G, B, A] 0-1 range
- `metallic` (float): 0-1 metallic value
- `roughness` (float): 0-1 roughness value
- `emission` (List[float]): Emission color and strength

#### `blender_textures`
Procedural and image textures.

**Operations:**
- `create_noise`, `create_voronoi`, `create_musgrave`, `create_wave`
- `load_image`, `apply_image`, `resize_texture`

### Animation and Rigging

#### `blender_animation`
Keyframe and timeline animation.

**Operations:**
- `set_frame_range`: Set animation start/end frames
- `add_keyframe`: Add position/rotation/scale keyframes
- `create_action`: Create named animation action
- `set_interpolation`: Set keyframe interpolation mode

**Keyframe Parameters:**
- `object_name` (str, required): Animated object
- `frame` (int, required): Frame number
- `location` (List[float]): Position at frame
- `rotation` (List[float]): Rotation at frame (degrees)
- `scale` (List[float]): Scale at frame

#### `blender_rigging`
Character rigging and bone animation.

**Operations:**
- `create_armature`: Create bone structure
- `add_bone`: Add individual bones
- `set_bone_pose`: Pose bones for animation
- `humanoid_mapping`: Setup for biped characters

### Rendering and Visualization

#### `blender_render`
Render settings and output.

**Operations:**
- `setup_camera`: Position and configure camera
- `set_resolution`: Set render resolution
- `render_image`: Render single frame
- `render_animation`: Render animation sequence

#### `blender_lighting`
Lighting setup and control.

**Operations:**
- `create_sun`, `create_point`, `create_spot`, `create_area`
- `setup_three_point`: Professional lighting setup
- `set_hdri`: Environment lighting

### VR and Game Development

#### Avatar Pipeline Tools

##### `blender_validation`
Pre-flight checks for VR platforms.

**Operations:**
- `validate_vrchat`: VRChat compatibility check
- `validate_resonite`: Resonite compatibility check
- `check_polygons`: Polygon count validation
- `check_materials`: Material limit verification

##### `blender_rigging` (VR Extensions)
- `humanoid_mapping`: Unity/VRChat bone structure
- `setup_physbones`: Dynamic bone physics
- `add_ik_constraints`: Inverse kinematics setup

##### `blender_materials_baking`
VR-optimized material processing.

**Operations:**
- `convert_to_pbr`: Shader conversion for mobile VR
- `bake_textures`: Combine textures for performance
- `optimize_transparency`: Handle transparent materials

### Import/Export and File Operations

#### `blender_import`
Import external 3D formats.

**Supported Formats:**
- FBX, OBJ, glTF/GLB, VRM, STL, PLY, X3D

**Parameters:**
- `filepath` (str, required): Source file path
- `import_settings` (Dict): Format-specific options

#### `blender_export`
Export to various formats.

**Supported Formats:**
- FBX, OBJ, glTF/GLB, VRM, STL, PLY, COLLADA

**Parameters:**
- `object_names` (List[str], required): Objects to export
- `filepath` (str, required): Output file path
- `export_settings` (Dict): Format-specific options

## HTTP REST API

### Base URL
```
http://localhost:8000
```

### Authentication
```bash
# Include API key in headers
curl -H "X-API-Key: your-api-key" http://localhost:8000/tools/construct_object
```

### Endpoint Structure

#### Tool Execution
```http
POST /tools/{tool_name}
Content-Type: application/json

{
  "operation": "create_cube",
  "name": "MyCube",
  "location": [0, 0, 0]
}
```

#### Response Format
```json
{
  "success": true,
  "result": {
    "object_created": "MyCube",
    "vertices": 8,
    "faces": 6
  },
  "execution_time": 0.234
}
```

### Error Responses
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid parameter: name must be string",
  "details": {
    "parameter": "name",
    "expected": "string",
    "received": "integer"
  }
}
```

## Python Direct API

### Basic Usage

```python
from blender_mcp.app import get_app

# Get application instance
app = get_app()

# Execute tools directly
result = await app.run_tool("blender_mesh", {
    "operation": "create_cube",
    "name": "MyCube"
})

print(f"Created: {result['object_created']}")
```

### Advanced Usage with Context

```python
from blender_mcp.app import get_app
from fastmcp import Context

app = get_app()
ctx = Context()

# AI construction with context
result = await app.run_tool("construct_object", {
    "description": "a red racing car",
    "complexity": "complex",
    "style_preset": "realistic"
}, ctx=ctx)

# Context preserves conversation state
refinement = await app.run_tool("manage_object_construction", {
    "operation": "modify",
    "object_name": result["object_name"],
    "modification_description": "add racing stripes"
}, ctx=ctx)
```

### Batch Operations

```python
# Execute multiple operations
operations = [
    ("blender_mesh", {"operation": "create_cube", "name": "Cube1"}),
    ("blender_mesh", {"operation": "create_sphere", "name": "Sphere1"}),
    ("blender_materials", {"operation": "apply_color", "object_name": "Cube1", "color": [1, 0, 0]})
]

results = []
for tool_name, params in operations:
    result = await app.run_tool(tool_name, params)
    results.append(result)
```

## Error Handling

### MCP Protocol Errors

#### Parameter Validation
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid complexity level",
  "valid_options": ["simple", "standard", "complex"]
}
```

#### Blender Execution Errors
```json
{
  "success": false,
  "error": "BlenderExecutionError",
  "message": "Failed to create object: insufficient memory",
  "blender_error": "MemoryError: out of memory"
}
```

#### Security Violations
```json
{
  "success": false,
  "error": "SecurityError",
  "message": "Script validation failed",
  "security_score": 25,
  "issues": ["dangerous_import", "unapproved_operation"]
}
```

### HTTP API Error Codes

- `400 Bad Request`: Invalid parameters
- `403 Forbidden`: Security violation
- `500 Internal Server Error`: Blender execution failure
- `503 Service Unavailable`: System overload

## Rate Limiting

### MCP Protocol
- No explicit rate limiting (client-controlled)
- Server may queue requests during high load

### HTTP API
- 100 requests per minute per IP
- Burst allowance: 20 requests
- Rate limit headers included in responses

## Webhooks and Callbacks

### Result Notifications
```json
{
  "event": "tool_completed",
  "tool_name": "construct_object",
  "execution_id": "exec_12345",
  "success": true,
  "result": {...},
  "timestamp": "2026-01-19T10:30:00Z"
}
```

### Progress Updates
```json
{
  "event": "progress_update",
  "execution_id": "exec_12345",
  "stage": "validation",
  "progress": 75,
  "message": "Validating generated script..."
}
```

## Versioning

### API Versioning
- Current version: v1
- URL format: `/v1/tools/{tool_name}`
- Backward compatibility maintained within major versions

### Breaking Changes
- Major version increments for breaking changes
- Deprecation warnings for 3 months before removal
- Migration guides provided for version upgrades

This comprehensive API provides multiple access methods for different integration needs, from simple MCP tool calls to complex web service integrations.

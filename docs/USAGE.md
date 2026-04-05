# Usage Guide

## Getting Started

After installation, start creating 3D objects with natural language:

```
You: "Create a steampunk robot with glowing red eyes"
Blender MCP: Analyzes request → Generates Blender script → Executes in Blender → Returns result
Result: 3D robot appears in Blender ready for use
```

## Basic Usage

### CLI Commands

```bash
# Start MCP server (for Claude Desktop)
blender-mcp --stdio

# Start HTTP server
blender-mcp --http --port 8000

# Check Blender installation
blender-mcp --check-blender

# List available tools
blender-mcp --list-tools

# Show configuration
blender-mcp --show-config
```

### Claude Desktop Integration

1. Install Blender MCP
2. Restart Claude Desktop
3. Start creating: *"Create a red cube with rounded edges"*

## AI Construction Examples

### Simple Objects
```python
# Basic primitives
construct_object("a blue sphere")
construct_object("a wooden table")

# With parameters
construct_object(
    description="a medieval castle",
    complexity="complex",
    style_preset="realistic"
)
```

### Complex Scenes
```python
# Environment with multiple objects
construct_object(
    description="a cozy living room with sofa, coffee table, and lamp",
    complexity="complex",
    allow_modifications=True
)

# Character with rigging
construct_object(
    description="a robot with articulated arms and legs",
    complexity="complex",
    style_preset="scifi"
)
```

### Architectural Visualization
```python
construct_object(
    description="modern office building with glass facade and green roof",
    complexity="complex",
    style_preset="realistic"
)
```

## Advanced Workflows

### Object Repository Management

```python
# Save created object
manage_object_repo("save", object_name="MyRobot", category="robots", quality_rating=8)

# Load from repository
manage_object_repo("load", object_id="robot_001", target_name="RobotCopy")

# Search repository
manage_object_repo("search", query="steampunk robot", min_quality=7)
```

### Batch Processing

```python
# Process multiple objects
blender_batch("resize", pattern="*.png", width=1024, height=1024)
blender_batch("convert", source_format="jpg", target_format="webp", quality=85)
```

### Material and Texturing

```python
# Apply materials
blender_materials("apply_pbr", object_name="Robot", metallic=0.8, roughness=0.2)

# Create procedural textures
blender_textures("create_noise", type="perlin", scale=4.0)
```

## Cross-MCP Export (Coming Soon)

Export Blender assets for use in other MCP servers:

```python
# Export for VRChat
export_for_mcp_handoff("robot_001", "vrchat", quality_level="high")

# Export for Unity
export_for_mcp_handoff("building_001", "unity", optimization_preset="game_asset")

# Export for Resonite
export_for_mcp_handoff("environment_001", "resonite", quality_level="ultra")
```

## VR Avatar Pipeline

### Complete Character Workflow

1. **Create Base Character**
```python
construct_object(
    description="humanoid character with detailed face and clothing",
    complexity="complex",
    style_preset="realistic"
)
```

2. **Apply Rigging**
```python
blender_rigging("humanoid_mapping", armature_name="CharacterRig")
blender_rigging("add_ik", bone_groups=["left_arm", "right_arm"])
```

3. **Setup Materials**
```python
blender_materials_baking("convert_to_pbr", target_mesh="Body")
blender_atlasing("create_atlas", max_size=2048)
```

4. **Add Facial Animation**
```python
blender_shapekeys("create_visemes", target_mesh="Face")
blender_shapekeys("add_blink", intensity=1.0)
```

5. **Export for VR Platform**
```python
blender_export_presets("export_vrchat", include_animations=True)
# Result: VRChat-ready avatar package
```

## API Usage

### Direct Python API

```python
from blender_mcp.app import get_app

app = get_app()

# Create object
result = await app.run_tool("construct_object", {
    "description": "a red cube",
    "complexity": "simple"
})

# Apply material
await app.run_tool("blender_materials", {
    "operation": "apply_color",
    "object_name": "Cube",
    "color": [1.0, 0.0, 0.0]
})
```

### HTTP API

```bash
# Start HTTP server
blender-mcp --http --port 8000

# API calls
curl -X POST http://localhost:8000/tools/construct_object \
  -H "Content-Type: application/json" \
  -d '{"description": "blue sphere", "complexity": "simple"}'
```

## Best Practices

### Performance Optimization

1. **Use Appropriate Complexity Levels**
   - `simple`: Quick iterations, basic shapes
   - `standard`: Most use cases, balanced quality/speed
   - `complex`: Maximum detail, slower generation

2. **Batch Similar Operations**
   - Group related object creation
   - Use repository for reusable assets
   - Leverage batch processing tools

3. **Memory Management**
   - Clear scene between large operations
   - Use appropriate texture sizes
   - Monitor Blender memory usage

### Quality Assurance

1. **Validate Outputs**
   - Use `blender_analysis` tools for quality checks
   - Check polygon counts and texture sizes
   - Validate material assignments

2. **Iterative Refinement**
   - Start simple, add complexity gradually
   - Use reference objects for style consistency
   - Leverage modification tools for adjustments

3. **Version Control**
   - Save important objects to repository
   - Use descriptive names and categories
   - Maintain quality ratings

## Integration Examples

### Game Development Pipeline

```python
# 1. Create modular assets
construct_object("stone wall section for castle", style_preset="medieval")
construct_object("wooden door with iron hardware", complexity="standard")

# 2. Setup materials
blender_materials("apply_pbr", object_name="Wall", roughness=1.0)
blender_materials("apply_pbr", object_name="Door", metallic=0.9)

# 3. Batch export
blender_batch("export_fbx", pattern="castle_*", output_dir="./assets")
```

### Architectural Visualization

```python
# Create building
construct_object("modern office building, 10 stories, glass facade", complexity="complex")

# Add details
construct_object("landscaping with trees and paths", reference_objects=["Building"])

# Setup lighting
blender_lighting("setup_three_point")
blender_render("setup_camera", location=[50, -50, 20])

# Export for client presentation
blender_export("render_turntable", frames=36, output_path="building_presentation.mp4")
```

### Character Creation

```python
# Base character
construct_object("humanoid character, athletic build", style_preset="realistic")

# Add clothing
construct_object("casual clothes: t-shirt, jeans, sneakers", reference_objects=["Character"])

# Setup rigging and animation
blender_rigging("humanoid_mapping")
blender_animation("create_walk_cycle", reference_bones=["Hips", "Spine"])

# Export for game engine
blender_export("export_unity_prefab", include_animations=True)
```

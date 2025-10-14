# 🚀 Quick Start Guide

Get up and running with Blender MCP in 5 minutes. Create your first 3D scene with AI assistance.

## Prerequisites

- ✅ Blender MCP installed ([Installation Guide](installation.md))
- ✅ Blender 4.0+ installed and configured
- ✅ Claude Desktop configured with MCP server

## Verify Setup

### Test Blender MCP
```bash
# Check server starts
python -m blender_mcp --version

# Test with debug logging
python -m blender_mcp --debug --help
```

### Test Claude Integration
1. **Open Claude Desktop**
2. **Ask**: "What Blender tools are available?"
3. **Expected**: Claude lists 50+ tools across categories

## Your First 3D Scene

### Step 1: Create a Basic Object
**Tell Claude:**
```
Create a red cube at position [2, 0, 0] with size 2
```

**What happens:**
- Claude analyzes your request
- Selects appropriate tools (`blender_mesh`, `blender_materials`)
- Executes Blender operations
- Returns confirmation with results

### Step 2: Add Lighting
**Tell Claude:**
```
Set up professional three-point lighting for the scene
```

**What happens:**
- Creates key, fill, and rim lights
- Positions lights optimally
- Configures light properties

### Step 3: Add Camera and Render
**Tell Claude:**
```
Add a camera looking at the cube and render a preview image
```

**What happens:**
- Creates and positions camera
- Sets up render settings
- Generates preview image

## Advanced Examples

### Character Creation Workflow
```
Create a simple character: body (cylinder), head (sphere), arms (cylinders), legs (cylinders)
Apply skin material to all parts
Add a ground plane
Position character and set up lighting
```

### Animation Sequence
```
Create a bouncing ball: sphere with physics
Add a ground plane
Enable gravity and physics simulation
Bake the animation for 120 frames
```

### Asset Download and Import
```
Download a katana model from polyhaven and import it
Apply a metallic material to the blade
Add Japanese pattern texture to handle
Position it on a display stand
```

## Understanding Claude's Responses

### Tool Selection
Claude automatically chooses the right tools:
```
User: "Create a blue sphere"
Claude: Uses blender_mesh.create_sphere + blender_materials for coloring
```

### Parameter Handling
Claude converts natural language to tool parameters:
```
User: "big red cube at [1,2,3]"
Claude: location=[1,2,3], scale=[2,2,2], color=[1,0,0]
```

### Error Handling
If something goes wrong, Claude explains and suggests fixes:
```
"Operation failed: Object 'Cube' not found. Try creating it first with create_cube."
```

## Common Patterns

### Object Creation
```
"Create a [shape] [color] [size] at [position]"
"Add a [material] [object] with [properties]"
"Make a [complex object] using [primitives]"
```

### Scene Setup
```
"Set up [lighting type] lighting"
"Add [camera type] camera at [position]"
"Create [environment] background"
```

### Materials and Textures
```
"Apply [material type] material to [object]"
"Download [texture type] from [source]"
"Create PBR material with [properties]"
```

### Animation and Physics
```
"Make [object] [animation type]"
"Add physics to [object]"
"Bake simulation for [frames] frames"
```

## Troubleshooting

### "No tools available"
- Check MCP server configuration in Claude Desktop
- Restart Claude Desktop
- Verify Blender MCP is installed and running

### "Blender operation failed"
- Check Blender is properly installed and accessible
- Verify BLENDER_EXECUTABLE path in MCP config
- Look at logs: `blender_view_logs(level_filter="ERROR")`

### "Asset download failed"
- Check internet connection
- Verify URL is accessible
- Try different asset source

### Slow Performance
- Reduce operation complexity
- Close other Blender instances
- Check system resources (RAM, CPU)

## Next Steps

### Explore Documentation
- **[Tool Reference](blender/TOOL_REFERENCE.md)** - Complete API guide
- **[BlenderKit Guide](blender/BLENDERKIT_GUIDE.md)** - Asset management
- **[Free Assets Guide](blender/FREE_ASSETS_GUIDE.md)** - Download resources

### Advanced Topics
- **Workflow Automation** - Chain multiple operations
- **Custom Materials** - Create complex shaders
- **Animation Rigs** - Character setup and animation
- **Render Farms** - Batch rendering and optimization

### Development
- **Custom Tools** - Extend Blender MCP capabilities
- **Integration** - Connect with other pipelines
- **Performance** - Optimize for large scenes

## Example Workflows

### Product Visualization
```
1. Download product model or create primitives
2. Apply realistic materials (metal, plastic, fabric)
3. Set up professional lighting (HDRI + rim lights)
4. Position camera for best angles
5. Render multiple views with different settings
```

### Game Asset Creation
```
1. Create low-poly base mesh
2. UV unwrap for texturing
3. Create optimized materials
4. Add LOD variants
5. Export in game formats (FBX, glTF)
```

### Architectural Visualization
```
1. Import architectural model
2. Apply realistic materials (concrete, glass, wood)
3. Set up interior/exterior lighting
4. Add vegetation and context
5. Render high-quality stills or animations
```

---

**Ready to create amazing 3D content? Start with simple objects and build up to complex scenes!** 🎨✨

*Need help? Check the [troubleshooting section](troubleshooting.md) or ask in our [community discussions](https://github.com/sandraschi/blender-mcp/discussions).* 🚀

# Features Overview

## AI Construction System

### Conversational 3D Creation
Transform natural language into professional 3D objects through an intelligent pipeline:

- **Natural Language Processing**: Understand design intent, style preferences, and technical requirements
- **LLM Script Generation**: AI-generated production-ready Blender Python code
- **Security Validation**: Multi-layer validation with sandboxed execution
- **Iterative Refinement**: Conversational improvement cycles with user feedback

### Complexity Levels
- **Simple**: Basic primitives, transforms, simple materials
- **Standard**: Complex meshes, modifiers, materials, basic animation
- **Complex**: Advanced geometry, rigging, physics, complex materials/textures

### Style Presets
- **Realistic**: Physically accurate materials and proportions
- **Stylized**: Artistic interpretation with exaggerated features
- **Lowpoly**: Optimized geometry for performance
- **Scifi**: Futuristic design with metallic effects and glow

## Professional Tool Suite

### Object Creation & Modeling (40+ tools)

#### Mesh & Geometry
- **Primitives**: Cube, sphere, cylinder, cone, plane, torus, monkey
- **Furniture**: Sofa, chair, table, bed, cabinet, desk, shelf, stool
- **Operations**: Duplicate, delete, combine, separate, clean geometry

#### Materials & Texturing
- **PBR Materials**: Metallic, roughness, normal, emission maps
- **Procedural Textures**: Noise, voronoi, musgrave, wave patterns
- **UV Operations**: Unwrap, smart project, cube project, reset

#### Animation & Motion
- **Keyframe Animation**: Location, rotation, scale animation
- **Shape Keys**: Facial animation, morphing, blend shapes
- **NLA Editor**: Non-linear animation, track management
- **Interpolation**: Constant, linear, bezier, elastic easing

### Rigging & Character Animation

#### Humanoid Setup
- **Automatic Rigging**: Humanoid bone structure creation
- **Bone Management**: Create, delete, rename, parent bones
- **Weight Painting**: Automatic and manual weight assignment
- **IK Setup**: Inverse kinematics for natural joint movement

#### Facial Animation
- **Viseme Creation**: A, I, U, E, O mouth shapes for lip sync
- **Blend Shapes**: Eye blinks, facial expressions, emotion morphs
- **Bone-Based Animation**: Jaw, eyelid, eyebrow controls

### Rendering & Visualization

#### Camera & Lighting
- **Camera Setup**: Perspective, orthographic, lens settings
- **Lighting**: Sun, point, spot, area lights with HDRI support
- **Three-Point Lighting**: Professional lighting setup automation

#### Render Settings
- **Output Formats**: PNG, JPEG, WebP, TIFF, EXR
- **Turntable Animation**: 360° object rotation renders
- **Preview Rendering**: Quick viewport renders with custom settings

### VR & Game Development

#### Avatar Pipeline
- **VRChat Compatibility**: Polygon limits, material constraints, PhysBones
- **Resonite Support**: ProtoFlux components, dynamic bones, collision
- **Unity Integration**: Prefab generation, script components, navigation
- **Unreal Engine**: Blueprint generation, material conversion

#### Platform Optimization
- **LOD Generation**: Automatic level-of-detail mesh creation
- **Texture Atlasing**: Combine materials to reduce draw calls
- **Bone Limits**: Automatic bone count optimization
- **Performance Profiling**: Real-time performance analysis

### Import & Export Systems

#### File Format Support
- **Import**: FBX, OBJ, glTF, VRM, STL, PLY, X3D
- **Export**: FBX, OBJ, glTF, VRM, STL, PLY, COLLADA, X3D
- **CAD Integration**: DXF export for CAD software
- **Batch Processing**: Convert multiple files automatically

#### Cross-Platform Handoff
- **VRChat Export**: FBX with avatar optimizations and PhysBone setup
- **Resonite Export**: GLTF with ProtoFlux components and collision
- **Unity Export**: FBX with prefab generation and script components
- **Unreal Export**: FBX with material conversion and blueprint setup

## Addon Management

### `manage_blender_addons`
Full addon lifecycle via MCP — no manual Blender GUI required.

- **search**: keyword search across known-addon registry
- **info**: list all known addons with URLs and addons directory location
- **install_known**: install a pre-registered addon by name (downloads ZIP from GitHub)
- **install_url**: install from any arbitrary URL (ZIP or single `.py`)
- **list_installed**: query addons currently enabled in running Blender instance
- **enable / disable**: toggle addon state and persist to user preferences

Known addons: `gaussian_splat`, `3dgs_blender`, `openscatter`, `asset_bridge`, `blender_gis`, `blender_tools_collection`

## Gaussian Splat / WorldLabs Import

### `blender_splatting` — `worldlabs` operation
One-call workflow for importing WorldLabs `.ply` exports:

1. Probes running Blender for a 3DGS import operator
2. Auto-installs `gaussian_splat` addon from GitHub if no operator found
3. Tries import operators in order: `import_scene.gaussian_splat` → `import_mesh.fastgs` → `import_mesh.ply`
4. Creates performance proxy object (bounding box, hidden by default)
5. Returns structured result with point count, object name, and any warnings

For manual control use `operation='import_gs'` with the addon already installed.

## Object Repository

### `manage_object_repo`
File-based versioned object store at `~/.blender-mcp/repository/`.

- **save**: exports active Blender object as `.blend` via executor; writes `metadata.json`; updates flat index
- **load**: appends `.blend` from repository into current scene; applies position and scale
- **search**: filters index by free-text query, category, tags, minimum quality rating
- **list_objects**: returns full repository index

### Batch Processing Engine
Process multiple images or objects with consistent settings:

```python
# Resize all images in directory
blender_batch("resize", pattern="*.png", width=1024, height=1024)

# Convert format with quality settings
blender_batch("convert", source_format="jpg", target_format="webp", quality=85)

# Apply watermark to multiple files
blender_batch("watermark", pattern="*.png", watermark="logo.png", position="bottom-right")
```

### Macro System
Execute complex multi-step workflows in single operations:

```python
# Create furnished room in one call
blender_workflow("execute", steps=[
    {"tool": "blender_scene", "operation": "clear_scene"},
    {"tool": "blender_furniture", "operation": "create_sofa", "name": "LivingSofa"},
    {"tool": "blender_furniture", "operation": "create_table", "name": "CoffeeTable"},
    {"tool": "blender_lighting", "operation": "setup_three_point"},
    {"tool": "blender_camera", "operation": "setup_camera"}
])
```

### Object Repository
Version-controlled asset management with intelligent search:

```python
# Save with metadata
manage_object_repo("save", object_name="Robot", category="scifi", quality_rating=9)

# Smart search
manage_object_repo("search", query="red robot with glowing eyes", min_quality=7)

# Load with transformations
manage_object_repo("load", object_id="robot_001", scale=[2, 2, 2], position=[0, 0, 5])
```

## Technical Specifications

### Performance Metrics
- **Generation Speed**: <30 seconds for standard complexity objects
- **Memory Usage**: <2GB per active session
- **Concurrent Users**: Support for 100+ simultaneous sessions
- **File Size**: Optimized output for target platforms

### Quality Standards
- **Visual Fidelity**: Professional-grade output quality
- **Standards Compliance**: Valid geometry, proper UV mapping, optimized topology
- **Cross-Platform**: Consistent results across Windows, Mac, Linux
- **Error Recovery**: Graceful handling of edge cases and user errors

### Integration Capabilities
- **MCP Protocol**: Full FastMCP 2.14.3 compliance
- **HTTP API**: RESTful web service interface
- **CLI Tools**: Command-line interface with comprehensive options
- **Python API**: Direct programmatic access for custom integrations

## Safety & Security

### Script Validation Pipeline
- **Syntax Checking**: AST parsing and Python validation
- **Security Scoring**: Risk assessment for generated operations (0-100 scale)
- **Sandbox Execution**: Isolated Blender environment with resource limits
- **Operation Whitelisting**: Approved Blender API calls only

### Content Safety
- **Input Sanitization**: All user inputs validated and cleaned
- **Resource Limits**: Memory, CPU, and execution time constraints
- **Error Containment**: Graceful failure handling without system impact
- **Audit Logging**: Comprehensive operation logging for security review

## Extensibility

### Custom Tool Development
- **Modular Architecture**: Easy addition of new tools and operations
- **Standardized Interfaces**: Consistent parameter and return formats
- **Documentation Generation**: Automatic help system updates
- **Testing Framework**: Comprehensive test coverage for new features

### Plugin System
- **Custom Operations**: User-defined Blender operations
- **Material Libraries**: Custom material and texture collections
- **Export Presets**: Platform-specific export configurations
- **Workflow Templates**: Reusable automation sequences

## Future Capabilities

### AI-Enhanced Features
- **Multi-Modal Input**: Image and voice-based creation
- **Style Transfer**: Apply artistic styles between objects
- **Collaborative Creation**: Real-time multi-user editing
- **Context Awareness**: Scene-aware object placement and scaling

### Advanced Rendering
- **Real-Time Ray Tracing**: GPU-accelerated rendering
- **Neural Rendering**: AI-enhanced image quality
- **HDR Pipeline**: High dynamic range rendering workflows
- **Compositing**: Multi-layer image composition and effects

### Industry Integration
- **Game Engines**: Direct export to Unity, Unreal, Godot
- **CAD Software**: Integration with FreeCAD, OpenSCAD
- **Web Platforms**: Three.js and WebGL export
- **AR/VR Platforms**: Comprehensive XR content creation

This feature set makes Blender MCP a comprehensive 3D creation platform suitable for professional workflows across gaming, architecture, VFX, education, and creative industries.

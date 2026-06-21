# Blender MCP: Comprehensive User Guide and Workflow Manual

Welcome to the Blender MCP Industrial Ecosystem. This guide is designed to transform complex 3D modeling and animation tasks into streamlined agentic workflows. Whether you are a solo developer building game assets or a technical artist orchestrating large-scale renders this manual provides the blueprints for success.

## 1. Getting Started: The Agentic Paradigm

Blender MCP is not just a collection of tools; it is a Command and Control Center for Blender. Instead of clicking through menus you describe your objective and the agentic layer handles the Python API orchestration.

### 1.1 Prerequisites
- Blender 4.2+ required for the latest Geometry Nodes and Eevee Next features
- FastMCP 3.2 ensures clean tool registration and sampling
- Python 3.10+ is the core execution runtime
- The BLENDER_EXECUTABLE environment variable must point to your Blender binary
- Default operation timeout is 300 seconds (adjust via BLENDER_TIMEOUT)

### 1.2 The First Scene
To verify your installation try this simple command: "Create a 2m cube at the center add a red procedural material set up a camera 5m away and render a preview." The server will: 1) Initialize the blender_mesh tool (create_cube), 2) Use blender_materials to generate a Principled BSDF shader, 3) Position the camera using blender_camera, 4) Render a PNG using blender_render.

### 1.3 Transport Modes
The server supports stdio mode (default for Claude Desktop) where it communicates via stdin/stdout JSON-RPC, and HTTP mode (for web integration) where it runs as a uvicorn server. Set MCP_TRANSPORT=http and MCP_PORT=8000 for HTTP mode. CLI flags --stdio --http and --sse override environment variables.

## 2. Advanced Modeling Tutorials

### 2.1 Hard Surface Workflow (Industrial Furniture)
For architectural visualization the blender_furniture tool is your best friend.

Example - Modern Living Room: 1) Floor: Create a large plane 10m x 10m using create_plane. 2) Sofa: blender_furniture operation=create_sofa style=modern. 3) Table: blender_furniture operation=create_table style=industrial dimensions=[2,1,0.75]. 4) Detail: Add a Bevel modifier using blender_modifiers to the table edges for realistic specular highlights. 5) Lighting: Use setup_three_point for even room illumination. 6) Camera: Place at [8,-8,6] looking at origin for a standard isometric view.

### 2.2 Procedural Assets with Geometry Nodes
While most tools use standard mesh ops you can orchestrate Geometry Nodes by using the blender_modifiers tool to add a Geometry Nodes modifier and then using the workflow tool to link the node tree. For complex procedural generation (terrain, scatter, building generators) use the run_workflow operation with a geometry_nodes preset. This approach creates fully parametric assets that can be adjusted after generation.

### 2.3 Character Base Mesh Workflow
1) Create a humanoid base using primitives (box for torso cylinder for limbs). 2) Apply Mirror modifier for symmetry along X axis. 3) Use create_sphere with ico topology for the head (set subdivisions=2 for game topology). 4) Add Subdivision Surface modifier at level 1 for viewport smooth preview. 5) Apply transforms before adding armature for rigging (always apply scale to avoid bone deformation distortion). 6) Create armature with spine neck and head bones using blender_rigging. 7) Parent mesh to armature with automatic weights.

### 2.4 Room Box Fill: Environment Prototyping
Use blender_furniture operations to rapidly fill architectural spaces: 1) Create the room shell using create_cube (inverted normals) or planes for walls. 2) Add furniture: create_bed style=modern dimensions=[2,1.5,0.4] for a bed, create_desk style=industrial at position [1,0.5,0], create_chair at [1,0.5,0.45], create_shelf on wall at [2,0,1.2] with rustic style. 3) Lighting: Use setup_hdri for ambient environment light then add area lights above windows for interior realism. 4) Camera: Set a wide-angle lens (24mm) for interior shots to capture the full room.

## 3. The Animation Pipeline

Animation in Blender MCP is frame-discrete and highly precise.

### 3.1 Keyframing Basics
To animate a bouncing ball: 1) Create a UV Sphere with location [0,0,5]. 2) blender_animation operation=set_keyframe object_name=Sphere frame=1. 3) Set Z location to 0. 4) blender_animation operation=set_keyframe object_name=Sphere frame=12. 5) Set Z back to 5. 6) blender_animation operation=set_keyframe object_name=Sphere frame=24. 7) Set the range to 1-24 using set_frame_range. 8) play_animation to preview. For smoother bounce use bezier interpolation: set interpolation=BEZIER on the keyframes and adjust handle positions via the animation tool.

### 3.2 Physics-Driven Motion
For complex motion use blender_physics: 1) enable_rigid_body on objects for falling or collisions. 2) enable_cloth on meshes for flags capes or bedding (set quality_steps=10 for production cloth). 3) enable_fluid on liquid or smoke domains. 4) Always call bake_physics before rendering animation involving simulations. 5) Use add_force_field to add wind turbulence or vortex effects. Physics baking can take significant time; the server returns progress updates via stderr logging.

### 3.3 Camera Animation
Create cinematic shots by animating camera movement: 1) Create a camera at starting position. 2) Set keyframe at frame 1. 3) Move camera to ending position over the timeline. 4) Set keyframe at the last frame. 5) Optionally animate focal length for Hitchcock zoom effect (dolly zoom). 6) Use camera_target_lock with an empty object as the target for orbit-style shots.

### 3.4 Full Scene Turntable Render
Use the turntable workflow for product visualization: 1) Place object at origin. 2) Set up three-point lighting. 3) Create camera at [5,-5,3] targeting origin. 4) Add empty at origin. 5) Parent camera to empty. 6) Animate empty rotation 0 to 360 over frame range. 7) Use blender_render operation=render_turntable with output_dir set. 8) The render produces 360 frames that can be composited into a video.

## 4. Lighting and Cinematic Rendering

### 4.1 Three-Point Lighting Standard
Professional character renders require contrast. Use blender_lighting with setup_three_point operation: Key Light is primary illumination (brightest at energy=2.0), Fill Light softens shadows (half intensity at energy=1.0), Back Light separates the subject from the background (at energy=1.5 with rim angle). Adjust light positions relative to the subject: Key at 45 degrees left and 30 degrees up, Fill at 45 degrees right and slightly below, Back behind the subject pointing at the back of the head.

### 4.2 HDRIs for Realism
For outdoor or complex indoor lighting use setup_hdri. This tool automatically sets up the World shader node tree and links the requested .exr or .hdr file. HDRIs provide 360-degree environmental lighting with realistic reflections on metallic surfaces. Recommended HDRI resolution is 4K for viewport and 8K for final renders. The tool accepts an hdri_path parameter pointing to the .hdr file location.

### 4.3 Render Settings
Use blender_render for final output: Parameters include resolution_x and resolution_y (up to 8K), output_path, file_format (PNG, JPEG, EXR, TIFF), samples (128-256 for final, 32-64 for preview), engine (CYCLES or EEVEE), use_denoising (true for Cycles final renders), and color_depth (8, 12, or 16 bit). For animations set frame_start, frame_end, and output_pattern for the frame sequence.

### 4.4 Eevee Next vs Cycles
Eevee Next: Real-time engine ideal for viewport preview and stylized renders. Fast but less physically accurate. Use for previsualization and animations with tight deadlines. Cycles: Path-traced production renderer. Use for final quality architectural visualization, product shots, and cinematic sequences. Cycles benefits from GPU acceleration (CUDA/OptiX). The server auto-detects available GPU compute devices.

## 5. Exporting for Game Engines

### 5.1 Unity Pipeline
Unity and VRChat have strict requirements for scale and rotation. 1) Selection: Select all objects intended for export. 2) Transform: Use blender_transform apply_transform to freeze scales and rotations. 3) Export: Use blender_export operation=export_unity. This tool automatically applies the -90 degree X-rotation required to translate Blender Z-up to Unity Y-up without messing up your model orientation. Unity export uses 0.01 scale factor (1 Blender unit = 0.01 Unity units) which is the standard Unity importer setting.

### 5.2 VRChat Avatar Export
For VRChat avatars: 1) Ensure armature is named Armature. 2) All meshes use the same armature. 3) Material names must be unique and descriptive. 4) Apply all transforms (location=0, rotation=0, scale=1). 5) Use export_vrchat which sets FBX Avatar mode, includes animation if present, and embeds textures. 6) Maximum recommended triangle count is 20,000 for optimized Quest avatars and 70,000 for PC.

### 5.3 GLTF for Web
Use blender_export operation=export_gltf for web applications. Key considerations: Include texture files via copy mode (texture_copy=true), use Draco mesh compression (use_draco=true) for smaller files, embed images (export_format=GLB) for single-file delivery, set export_image_format=JPEG for smaller textures. GLTF is the standard for three.js, React Three Fiber, and web AR/VR experiences.

### 5.4 FBX vs GLB
Use FBX for Unity/Unreal if you need complex rigging and bone hierarchies. Use GLB/GLTF for web applications or lightweight AR experiences. FBX supports embedded animation, blend shapes, and custom properties. GLTF supports PBR materials, Draco compression, and is natively supported by modern browsers. OBJ is a legacy format best used only when required by specific tools.

## 6. Optimization and Troubleshooting

### 6.1 Performance Hits
Boolean Modifiers: High-poly booleans can be computationally expensive. Use them sparingly or apply once the shape is finalized. Cycles Samples: For internal iteration keep samples at 32-64. For final delivery 128-256 with Denoising is standard. Particle Systems: Keep particle counts manageable (under 100,000 for viewport, under 1,000,000 for final bake). Subdivision Surface: Use level 1 for viewport and level 2 for render; higher levels increase memory exponentially.

### 6.2 Common Errors
Object not found: Ensure you use the exact case-sensitive name returned by the selection tool. Timeout: Simulations or high-resolution renders might exceed the 300s default timeout. Increase BLENDER_TIMEOUT environment variable if needed. Blender executable not found: Set BLENDER_EXECUTABLE to the full path of your Blender binary. Permission denied: Ensure Blender has filesystem access to the output directory.

### 6.3 Debugging
Use the blender_logs tool to retrieve recent server logs: get_logs operation with level_filter=ERROR for error-only view, or with specific module_filter to narrow down. Logs include timestamps, log levels, module names, and function names. The memory buffer retains the last 1000 log entries. If Blender crashes the server logs the crash and continues running (process isolation).

## 7. Industrial Quality Standards

As an industrial-grade server we follow SOTA 14.1. Zero Pollution: The system never prints to stdout. Structured Logs: All feedback is provided via standard logger structures. Atomic Operations: Each tool call is designed to be atomic and reversible (where possible). All communication adheres to strict protocol standards. The FastMCP 3.2 framework ensures clean tool registration and sampling capabilities.

## 8. Tool Reference Quick-Map

New Geometry: blender_mesh (basic primitives). Move/Rotate: blender_transform (use degrees for rotation). Smoothing: blender_modifiers (add Subsurf). Pictures: blender_render (set output path). Movies: blender_animation (bake first if using physics). Unity Export: blender_export (use Unity preset). Lighting: blender_lighting (three-point or HDRI). Materials: blender_textures (procedural shaders). Character Rig: blender_rigging (armature and IK). Physics: blender_physics (bake before render). Import: blender_import (FBX, GLTF, OBJ, STL). Particles: blender_particles (emitter or hair). UV Mapping: blender_uv (smart project). Selection: blender_selection (by name or type).

## 9. Final Thoughts

The power of Blender is now at your fingertips in plain language. Experiment with physics play with light and build worlds that were previously locked behind a complex UI. Welcome to the future of 3D creation. For advanced use cases like crowd simulation, cloth dynamics, or VFX compositing the toolset can be combined in novel ways by chaining multiple tool calls. The server is designed to be a creative partner not just a remote control.

## 10. Advanced Modeling Techniques

### 10.1 Boolean Workflow for Hard Surface Modeling
Boolean operations are essential for hard-surface mechanical design. The blender_modifiers tool with add_boolean operation supports three modes: DIFFERENCE (subtract shape A from B), UNION (combine shapes into one), and INTERSECT (keep only overlapping volume). For clean booleans: 1) Ensure both objects have applied transforms (apply_transform before boolean). 2) Use relatively simple geometry for the boolean tool (under 1000 faces). 3) Apply the boolean modifier after the result is finalized to prevent performance degradation. 4) Add a Bevel modifier after boolean to smooth the resulting edges (0.5mm to 2mm width depending on scale). 5) Check for non-manifold geometry after boolean and clean with the blender_mesh cleanup operations.

### 10.2 Procedural Texture Blending
Combine multiple procedural textures for realistic surfaces: 1) Create a base noise texture for surface variation. 2) Create a Voronoi texture for wear-and-tear patterns (dirt accumulation in crevices). 3) Create a Musgrave texture for macro-level detail. 4) Use blender_textures assign_texture operation to combine them into a single material using MixRGB nodes. 5) The material system supports up to 10 texture layers for complex surfaces like aged concrete, weathered metal, or organic skin. 6) Bake the combined procedural material to a single texture map for game engine export using bake_texture at 2048x2048 or 4096x4096 resolution.

### 10.3 Camera Animation for Cinematic Shots
Professional camera movement techniques: 1) Dolly shot: Animate camera location along a straight path while maintaining focus on a target. Set keyframes at start and end positions with linear interpolation. 2) Orbit shot: Create an empty at the subject location, parent the camera to the empty, animate empty rotation 0-360 degrees. 3) Crane shot: Animate camera location on Z axis while simultaneously adjusting the target lock for a sweeping reveal. 4) Handheld effect: Add slight random noise to camera location and rotation keyframes (2-5cm translation, 0.5-2 degree rotation). 5) Focus pull: Animate the camera focus_distance parameter while keeping aperture constant. Use set_keyframe for focus distance at the start and end of the pull.

## 11. Materials and Shading Reference

### 11.1 PBR Material Quick Reference
Realistic PBR materials require correct Roughness and Metallic values: Metal (iron): Roughness 0.3-0.6, Metallic 1.0. Metal (chrome): Roughness 0.1, Metallic 1.0. Metal (brushed aluminum): Roughness 0.4, Metallic 1.0. Plastic (glossy): Roughness 0.1-0.3, Metallic 0.0. Plastic (matte): Roughness 0.7-0.9, Metallic 0.0. Rubber: Roughness 0.9, Metallic 0.0. Glass: Roughness 0.0, Metallic 0.0, Transmission 1.0, IOR 1.45. Skin: Roughness 0.4-0.5, Metallic 0.0, Subsurface 0.1. Wood: Roughness 0.6-0.8, Metallic 0.0. Concrete: Roughness 0.9, Metallic 0.0. Dielectric materials (plastic, wood, concrete, stone) always have Metallic=0.0. Conductive materials (iron, copper, gold, aluminum) always have Metallic=1.0 with Roughness controlling the finish.

### 11.2 Texture Baking Pipeline
Baking converts procedural materials into image textures for export: 1) UV unwrap the target object using smart_project with default settings. 2) Set up image textures at the target resolution (e.g. 2048x2048). 3) Assign the procedural material to the object. 4) Call bake_texture with the target image name and bake type (DIFFUSE, GLOSSY, TRANSMISSION, NORMAL, DISPLACEMENT, COMBINED). 5) Baking uses Cycles render engine and can take several minutes for high-resolution bakes. 6) The baked textures are saved to the output directory and can be exported with the model. 7) For game engine export, bake at minimum: DIFFUSE (albedo color), ROUGHNESS (roughness map), METALLIC (metal mask), NORMAL (normal map), and optionally DISPLACEMENT (height map).

## 12. Command Line Interface Reference

The blender-mcp server supports CLI arguments for configuration: --host (bind address, default 127.0.0.1), --port (HTTP port, default 8000), --http (run in HTTP mode instead of stdio), --debug (enable debug logging). Transport modes: stdio mode communicates via stdin/stdout JSON-RPC (default, for Claude Desktop). HTTP mode runs a uvicorn server for web integration. The server respects these environment variables: BLENDER_EXECUTABLE (path to Blender binary), BLENDER_TIMEOUT (operation timeout in seconds), BLENDER_OUTPUT_DIR (output directory for renders and exports), BLENDER_PORT (TCP bridge port for Blender communication), MCP_TRANSPORT (transport override), MCP_HOST (bind address), MCP_PORT (port), MCP_PATH (HTTP endpoint path).

## 13. Scene Data Reference

The tool responses include structured data about scenes, objects, and materials. Object data includes name, type (MESH, CURVE, ARMATURE, LIGHT, CAMERA, EMPTY), location (x,y,z in Blender units), rotation (Euler in degrees), scale (x,y,z), dimensions (bounding box), and material slots. Material data includes name, shader type (Principled BSDF, Emission, Glass), and key parameters (Roughness, Metallic, Alpha, IOR, Emission Strength). Scene data includes scene name, frame range, resolution, render engine (Cycles or Eevee), and samples. This data is returned in structured JSON format for programmatic consumption.

## 14. Complete Project Example: Sci-Fi Corridor Scene

Building a complete scene end-to-end: 1) Create the corridor shell: a 4m x 20m x 3m box with wall, floor, and ceiling materials applied. 2) Add wall panel details using array modifiers on small panel objects. 3) Create ceiling lights using area lights recessed into the ceiling with emission materials. 4) Add wall-mounted pipes and cables using cylinder primitives with array and curve modifiers. 5) Create doorways using boolean modifiers on the walls at regular intervals. 6) Place furniture (control panels, chairs, storage units) using blender_furniture operations. 7) Apply PBR materials: metallic floor (roughness 0.3, metallic 0.8), matte walls (roughness 0.8), emissive panels (emission strength 10). 8) Set up volumetric lighting with a volume scatter shader on the world. 9) Place cameras at corridor intersections for dramatic perspective shots. 10) Render a turntable animation for portfolio presentation.

## 15. Best Practices for AI-Assisted 3D Workflows

When working with blender-mcp through an AI agent, follow these guidelines for best results: 1) Be specific about measurements and units (always specify dimensions in meters or use the scale parameter explicitly). 2) Name objects clearly with descriptive names that follow a convention (e.g. Wall_Left_01, Pipe_03, Light_Ceiling_04) for easier selection and modification later. 3) For complex multi-step operations, break down the request into logical phases (modeling first, then materials, then lighting, then rendering) rather than asking for everything at once. 4) Use apply_transform before any modifier operations to prevent distortion artifacts. 5) Check intermediate results using render_preview at low resolution (640x360) before committing to a full-resolution render. 6) When exporting, specify the target platform explicitly (Unity, VRChat, Web) so the export tool applies the correct scale and orientation settings. 7) For scenes with many objects, work in layers by using blender_selection to target specific object groups. 8) Use physics and particle systems sparingly in viewport-heavy workflows as they consume significant resources. 9) The server handles Blender crashes gracefully through process isolation but complex scenes with multiple simulations should be baked gradually rather than all at once.

## 16. Extending the Toolset

blender-mcp can be extended with custom scripts through the blender_workflow tool which accepts custom ECMAScript or Python snippets for execution in the Blender context. Advanced users can register custom tool modules by adding files in the blender_mcp/tools/ directory following the decorator pattern established by existing modules. The server's modular architecture means new tools are automatically discovered on import. Custom tools must follow the return format conventions (success bool, structured data dict) and use the register_tool decorator or the @app.tool decorator from FastMCP. When building extensions, reference the existing tool implementations for correct error handling patterns, parameter validation approaches, and logging conventions.

## 17. Modifier Stack Management Reference

The modifier stack is a critical concept in non-destructive modeling. Each object has an ordered list of modifiers applied sequentially. The order affects the final result dramatically: modifiers at the bottom of the stack are evaluated first, and modifiers at the top are evaluated last. Standard modifier ordering: Mirror (first, creates symmetry before any other operation), Subdivision Surface (before modifiers that need high-poly input like Bevel), Bevel (after subdivision for clean bevelled edges), Boolean (in the middle of the stack, after base shape is established), Armature (near the top, deforms the final high-poly mesh), Solidify (before armature but after subdivision for proper thickness). When applying modifiers, they are applied in stack order from bottom to top. The apply_modifier operation collapses a single modifier, converting its effect into real geometry. The remove_modifier operation deletes a modifier without applying it. The modifier_update operation changes parameters of an existing modifier without applying or removing it. Use blender_modifiers operation=modifier_update to adjust subdivision levels, bevel widths, array counts, or boolean operations dynamically during modeling without losing the modifier stack.

## 18. Geometry Nodes Integration

Geometry Nodes provide a node-based procedural modeling system within Blender. The server supports creating and manipulating Geometry Nodes modifiers through the blender_modifiers tool. To set up a Geometry Nodes workflow: 1) Create a Geometry Nodes modifier on the target object using add_geonodes operation (available through modifier tools). 2) The modifier creates an empty node group that can be populated via custom scripts. 3) Common procedural operations achievable through Geometry Nodes include: point scattering (distribute instances on mesh surface), curve generation (create procedural roads, pipes, cables), mesh boolean operations, attribute transfer between meshes, L-system growth simulation, and fractal terrain generation. 4) The server does not provide individual Geometry Nodes operations for every possible node type due to the vast number of nodes, but the custom script tool allows executing any Geometry Nodes Python API code. 5) For complex procedural setups, use the custom Python execution through the blender_workflow tool with a script that creates and connects the Geometry Nodes node tree programmatically.

## 19. Blender File (.blend) Structure and Management

Blender .blend files contain all scene data in a single archive format with internal data blocks. The file structure includes: scenes (can contain multiple scenes within one file sharing data blocks), objects with their transform and link information, mesh data (geometry vertices, edges, faces), materials and textures, armatures and actions, world and lighting settings, render settings (resolution, samples, output format), and animation data (keyframes, F-curves, drivers). The .blend format supports incremental saving where only changed data blocks are written, making saves fast on large files. The blender_scene tool manages multiple scenes within a file: new_scene creates an empty scene, delete_scene removes a scene, set_active_scene switches the working scene, list_scenes enumerates all scenes, and clear_scene removes all objects from the current scene. When working with large files, use clear_scene rather than delete_object operations to efficiently reset the scene state. Each scene maintains its own world, camera, lighting, and render settings while sharing mesh, material, and other data blocks across scenes for memory efficiency.

## 20. Creating Custom Materials with the Principled BSDF

The Principled BSDF is Blender's universal PBR shader supporting the full range of real-world materials through a single node. Key parameters: Base Color (RGB, the diffuse/albedo color of the material), Subsurface (0.0-1.0, simulates light scattering beneath the surface for skin, wax, milk, marble), Subsurface Radius (RGB, scatter distance per channel), Subsurface Color (tint of scattered light), Metallic (0.0-1.0, 0 for dielectrics, 1 for conductors), Specular (0.0-1.0, dielectric specular reflection intensity, default 0.5), Specular Tint (tint of specular reflection), Roughness (0.0-1.0, surface micro-roughness, 0 for mirror, 1 for matte), Anisotropic (0.0-1.0, directionality of specular highlights for brushed metal), Anisotropic Rotation (rotation of anisotropic effect), Sheen (0.0-1.0, soft velvet-like reflection for fabrics), Sheen Tint (tint of sheen), Clearcoat (0.0-1.0, additional clear coat layer for car paint), Clearcoat Roughness (roughness of clear coat), IOR (index of refraction for transmissive materials, 1.45 for glass, 1.33 for water, 2.42 for diamond), Transmission (0.0-1.0, how much light passes through, glass=1.0), Transmission Roughness (roughness of transmission), Emission (RGB color emitted), Emission Strength (intensity of emission), Alpha (0.0-1.0, transparency with 0=fully transparent), Normal (tangent space normal map input), Clearcoat Normal (separate normal for clear coat), Tangent (custom tangent direction for anisotropic). The blender_materials tool provides create_principled operation that accepts these parameters and creates a fully configured material node tree.

## 21. Lattice and Simple Deform Modifiers

The Simple Deform modifier provides four deformation types: Bend (curves the mesh along a specified axis, angle parameter in degrees), Taper (scales one end of the mesh, factor parameter 0.0-1.0), Stretch (stretches the mesh along the axis, factor can be positive or negative), Twist (rotates the mesh around the axis, angle parameter in degrees). Each deformation works on a vertex group if specified, otherwise the entire mesh. The modifier has an origin point that determines the deformation center. For bending, the origin placement determines the bend direction and radius. The Lattice modifier uses a Lattice object to deform the mesh using free-form deformation (FFD). The lattice grid resolution (U, V, W divisions) determines deformation detail. Lattice deformation is commonly used for: organic shape sculpting, character squash and stretch animation, non-destructive mesh reshaping for different poses. Both modifiers should be placed after the Mirror modifier but before Subdivision Surface in the stack for best results.

## 22. Keyframe Interpolation Reference

Blender supports three keyframe interpolation modes: BEZIER (default, smooth acceleration and deceleration with adjustable handle positions for natural motion), LINEAR (constant velocity between keyframes, useful for mechanical motion and camera cuts), and CONSTANT (instant value change at the keyframe, used for visibility toggles and instantaneous state changes). Each keyframe also has left and right handle types: AUTO (automatic smooth tangents), VECTOR (linear segments between keyframes), ALIGNED (handles maintain a straight line but can be adjusted), FREE (independent left and right handles for full control). The set_keyframe and animate_location/rotation/scale operations accept the interpolation parameter. For bouncing ball animation use BEZIER with modified handle positions on the ground contact keyframes to create squash and stretch. For robotic arm motion use LINEAR interpolation. For light toggles and visibility switches use CONSTANT interpolation. The animation tools return the number of keyframes set and the interpolation type used.

## 23. UV Unwrapping Strategies

UV unwrapping determines how 2D textures map onto 3D geometry. The blender_uv tool provides four projection methods: smart_project (automatically creates UV islands based on face angle, best for organic shapes and mechanical parts with 90-degree angles, parameters: angle_limit in degrees default 66, island_margin default 0.0), cube_project (projects from six cube directions, best for blocky architecture and rectangular objects), cylinder_project (wraps UVs around an axis, best for cylindrical objects like bottles, pipes, columns), sphere_project (maps latitude/longitude, best for spherical objects like planets, domes, balls). General UV unwrapping best practices: use smart_project for most objects with angle_limit=66 and island_margin=0.02, ensure proper seam placement for organic shapes (hidden in natural creases like armpits, crotch, behind ears), maintain consistent texel density across all objects in a scene (uniform pixel-per-unit ratio), and verify UVs visually by applying a checker texture. The get_uv_info operation returns UV island count, total area, and overlapping UV count.

## 24. Command Line Examples Quick Reference

Useful command patterns: python -m blender_mcp.server starts the server in stdio mode for Claude Desktop. python -m blender_mcp.server --http --port 8000 starts in HTTP mode on port 8000. python -m blender_mcp.server --debug enables verbose logging. Set BLENDER_EXECUTABLE=C:/Program Files/Blender Foundation/Blender 4.2/blender.exe for non-standard Blender installations. The server reads MCP_TRANSPORT, MCP_PORT, MCP_HOST from environment. Default timeout is 300 seconds. All tools accept standard FastMCP parameters and return structured dicts.

## 25. Motion Blur and Depth of Field

Motion blur simulates the streaking effect of fast-moving objects during a camera exposure. Render settings: motion_blur=true in Cycles or Eevee, shutter_type (CURVED for realistic, or LINEAR for simple), shutter_time (exposure time factor, 0.5 default), and samples for motion blur quality (higher = smoother). Depth of field creates a realistic focal plane effect: enable_dof=true on the camera, fstop (aperture size, lower = more blur, typical range 1.4-22), focus_distance (distance to the focal plane in Blender units). The camera tools accept these parameters for cinematic effects.

## 26. Color Management and Output

Blender uses a color management pipeline based on OpenColorIO (OCIO). The default configuration uses the AgX view transform (introduced in Blender 4.0) which provides improved color rendition compared to the legacy Filmic transform. When rendering, the color management settings affect the final output: the View Transform determines how scene-referred linear values map to display-referred sRGB values. For final render output use AgX (default) or Filmic for filmic contrast curves. For technical/VFX work use Standard (raw linear output). For game engine textures use Raw (no transform) and apply the appropriate color space in the target engine. The Display Device should match the target output (sRGB for web, Rec.709 for broadcast, DCI-P3 for cinema). The Look can add additional stylization (None for neutral, Photographic for contrast, High Contrast for punchy colors). These settings are managed through the scene configuration in the render tools and affect the blender_render output.
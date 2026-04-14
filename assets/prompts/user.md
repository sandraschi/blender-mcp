# 🎨 Blender MCP: Comprehensive User Guide & Workflow Manual

Welcome to the **Blender MCP Industrial Ecosystem**. This guide is designed to transform complex 3D modeling and animation tasks into streamlined, agentic workflows. Whether you are a solo developer building game assets or a technical artist orchestrating large-scale renders, this manual provides the blueprints for success.

---

## 🚀 1. Getting Started: The Agentic Paradigm

Blender MCP is not just a collection of tools; it is a **Command and Control Center** for Blender. Instead of clicking through menus, you describe your objective, and the agentic layer handles the Python API orchestration.

### 1.1. Prerequisites
- **Blender 4.2+**: Required for the latest Geometry Nodes and Eevee Next features.
- **FastMCP 3.2**: Ensures clean tool registration and sampling.
- **Python 3.10+**: The core execution runtime.

### 1.2. The First Scene
To verify your installation, try this simple command:
> "Create a 2m cube at the center, add a red procedural material, set up a camera 5m away, and render a preview."

The server will:
1. Initialize the `blender_mesh` tool (`create_cube`).
2. Use `blender_materials` to generate a Principled BSDF shader.
3. Position the camera using `blender_camera`.
4. Render a PNG using `blender_render`.

---

## 🏗️ 2. Advanced Modeling Tutorials

### 2.1. Hard Surface Workflow (Industrial Furniture)
For architectural visualization, the `blender_furniture` tool is your best friend.

**Example: Modern Living Room**
1. **Floor**: Create a large plane (10m x 10m).
2. **Sofa**: `blender_furniture` (operation: `create_sofa`, style: `modern`).
3. **Table**: `blender_furniture` (operation: `create_table`, style: `industrial`).
4. **Detail**: Add a `blender_modifiers` (Bevel) to the table edges for realistic specular highlights.

### 2.2. Procedural Assets with Geometry Nodes
While most tools use standard mesh ops, you can orchestrate Geometry Nodes by using the `blender_modifiers` tool to add a "Geometry Nodes" modifier and then using the custom script tool to link the node tree.

---

## 🎬 3. The Animation Pipeline

Animation in Blender MCP is frame-discrete and highly precise.

### 3.1. Keyframing Basics
To animate a bouncing ball:
1. Create a `UV Sphere`.
2. Move it to Z=5.
3. `blender_animation` (set_keyframe at Frame 1).
4. Move to Z=0.
5. `blender_animation` (set_keyframe at Frame 12).
6. Move back to Z=5.
7. `blender_animation` (set_keyframe at Frame 24).
8. Set the range to 1-24 and `play_animation`.

### 3.2. Physics-Driven Motion
For more complex motion, use `blender_physics`.
- **Rigid Body**: Use this for falling objects or collisions.
- **Cloth**: Use for flags, capes, or bedding.
- **Baking**: Always remember to call `bake_physics` before rendering an animation involving simulations.

---

## 💡 4. Lighting & Cinematic Rendering

### 4.1. The Three-Point Lighting Standard
Professional character renders require contrast. Use `blender_lighting` with the `setup_three_point` operation.
- **Key Light**: Primary illumination (brightest).
- **Fill Light**: Softens shadows (half intensity).
- **Back Light**: Separates the subject from the background (high contrast).

### 4.2. HDRIs for Realism
For outdoor or complex indoor lighting, use `setup_hdri`. This tool will automatically set up the World shader node tree and link the requested `.exr` or `.hdr` file.

---

## 📤 5. Exporting for Game Engines

### 5.1. The Unity/VRChat Pipeline
Unity and VRChat have strict requirements for scale and rotation.
1. **Selection**: Select all objects intended for export.
2. **Transform**: Use `blender_transform` (apply_transform) to freeze scales.
3. **Export**: Use `blender_export` (operation: `export_unity`). This tool automatically applies the -90 degree X-rotation required to translate Blender's Z-up to Unity's Y-up without messing up your model's orientation.

### 5.2. FBX vs. GLB
- Use **FBX** for Unity/Unreal if you need complex rigging and bone hierarchies.
- Use **GLB/GLTF** for web applications or lightweight AR experiences.

---

## 🔧 6. Optimization & Troubleshooting

### 6.1. Performance Hits
- **Boolean Modifiers**: High-poly booleans can crawl your system. Use them sparingly or apply them once the shape is finalized.
- **Cycles Samples**: For internal iteration, keep samples at 32-64. For final delivery, 128-256 with Denoising is standard.

### 6.2. Common Errors
- **"Object not found"**: Ensure you use the exact case-sensitive name returned by the selection tool.
- **"Timeout"**: Simulations or high-res renders might exceed the 300s default timeout. Increase the `OPERATION_TIMEOUT` in your environment config if needed.

---

## 🏆 7. Industrial Quality Standards

As an industrial-grade server, we follow **SOTA 14.1**.
- **Zero Pollution**: The system never prints to stdout.
- **Structured Logs**: All feedback is provided via standard logger structures.
- **Atomic Operations**: Each tool call is designed to be atomic and reversible (where possible).

---

## 📚 8. Tool Reference Quick-Map

| Need | Primary Tool | Note |
|------|--------------|------|
| New Geometry | `blender_mesh` | Basic primitives |
| Move/Rotate | `blender_transform` | Use degrees for rotation |
| Smoothing | `blender_modifiers` | Add Subsurf |
| Pictures | `blender_render` | Set output path |
| Movies | `blender_animation` | Bake first if using physics |
| Unity Export | `blender_export` | Use Unity preset |

---

## 🏁 9. Final Thoughts
The power of Blender is now at your fingertips in plain language. Experiment with physics, play with light, and build worlds that were previously locked behind a complex UI. **Welcome to the future of 3D creation.**

# Blender MCP Quick Start Templates

**Version:** 1.0.0
**Last Updated:** October 14, 2025

## 🎯 Quick Start Templates

### 1. Basic Scene Creation

**Template: Create Simple Scene**
```
I want to create a basic 3D scene. Help me:
1. Create a cube at position [0, 0, 0] with scale [2, 2, 2]
2. Create a sphere at position [3, 0, 0] with radius 1.5
3. Add a basic material to both objects
4. Set up simple lighting
5. Position the camera for a good view
6. Render a preview image
```

**Template: Game Asset Creation**
```
Help me create a game-ready asset:
1. Create a low-poly character base (cylinder for body, sphere for head)
2. Add basic armature rig for the character
3. Create simple walk cycle animation (4 keyframes)
4. Add basic materials (skin, clothing colors)
5. UV unwrap the model
6. Export as FBX for Unity
```

### 2. Lighting & Rendering

**Template: Professional Lighting Setup**
```
Set up professional lighting for my scene:
1. Create a three-point lighting rig (key, fill, rim lights)
2. Add an HDRI environment for realistic reflections
3. Set up camera with proper depth of field
4. Configure render settings for high quality (256 samples, 4K resolution)
5. Render turntable animation (36 frames, 360 degrees)
6. Output as PNG sequence for review
```

**Template: Product Visualization**
```
Create a product visualization setup:
1. Import my OBJ model (ask for file path)
2. Create clean white background
3. Set up soft, even lighting from all sides
4. Add subtle shadows and reflections
5. Position camera for isometric view
6. Render high-quality image with transparency
```

### 3. Animation Workflows

**Template: Character Animation**
```
Help me animate a character:
1. Create a simple biped rig (head, torso, arms, legs)
2. Set keyframes for a walk cycle:
   - Frame 1: Neutral pose
   - Frame 8: Right foot forward, left arm forward
   - Frame 16: Left foot forward, right arm forward
   - Frame 24: Back to neutral
3. Add smooth interpolation
4. Test playback in viewport
5. Export animation as FBX
```

**Template: Mechanical Animation**
```
Animate a mechanical device:
1. Create simple robot arm (cubes and cylinders)
2. Set up pivot points for joints
3. Create keyframes for arm movement:
   - Base rotation: 0° to 90°
   - Elbow bend: 180° to 90°
   - Wrist rotation: continuous 360°
4. Add smooth curves for realistic motion
5. Bake animation and test
```

### 4. Materials & Textures

**Template: PBR Material Creation**
```
Create realistic PBR materials:
1. Create fabric material (cotton, roughness 0.8, subsurface scattering 0.2)
2. Create metal material (brass, high reflectivity, anisotropic)
3. Create wood material with procedural grain texture
4. Create glass material with proper refraction
5. Assign materials to appropriate objects in scene
6. Set up proper lighting to showcase materials
```

**Template: Texture Baking**
```
Set up texture baking workflow:
1. Create high-poly detail mesh
2. Create low-poly version for baking
3. UV unwrap low-poly mesh
4. Set up baking settings (normal, AO, diffuse)
5. Bake textures at 2048x2048 resolution
6. Save baked textures as PNG
7. Apply baked textures to low-poly mesh
```

### 5. Physics Simulations

**Template: Rigid Body Destruction**
```
Create a destruction simulation:
1. Create a tower of cubes (5x5x10 stack)
2. Enable rigid body physics on all cubes
3. Create a sphere projectile
4. Set up collision detection
5. Animate sphere hitting the tower
6. Bake physics simulation
7. Render slow-motion destruction
```

**Template: Cloth Simulation**
```
Set up cloth simulation:
1. Create a plane as cloth (grid of 20x20 vertices)
2. Create collision objects (sphere, cube)
3. Configure cloth material properties (stiffness, damping)
4. Set up wind force field
5. Animate cloth falling and interacting with objects
6. Bake cloth simulation
7. Render final animation
```

### 6. Advanced Modeling

**Template: Architectural Modeling**
```
Create an architectural scene:
1. Create building base (cube scaled to building dimensions)
2. Add windows using boolean operations
3. Create roof structure
4. Add architectural details (cornices, columns)
5. Create surrounding environment (ground plane, trees)
6. Set up realistic materials
7. Position cameras for architectural shots
```

**Template: Organic Modeling**
```
Model organic shapes:
1. Start with basic primitives (spheres, cylinders)
2. Use modifiers (subdivision surface, displace)
3. Create procedural textures for displacement
4. Sculpt details using proportional editing
5. Create UV maps for texturing
6. Set up proper materials for organic look
7. Render with subsurface scattering
```

### 7. Batch Processing

**Template: Asset Batch Processing**
```
Set up batch processing pipeline:
1. Import multiple OBJ files from directory
2. Apply common material to all objects
3. Set up standard lighting rig
4. Create turntable camera animation for each
5. Batch render previews (512x512, fast settings)
6. Export all as optimized FBX files
7. Generate contact sheet of all assets
```

**Template: Texture Optimization**
```
Optimize texture workflow:
1. Import high-resolution textures
2. Create multiple LOD versions (4K, 2K, 1K, 512)
3. Apply different compression settings per LOD
4. Generate normal maps from height maps
5. Create roughness/metallic/ambient occlusion maps
6. Package textures for different platforms (PC, mobile, console)
7. Generate texture atlas for efficient rendering
```

### 8. Game Development Pipeline

**Template: Unity Asset Pipeline**
```
Prepare assets for Unity:
1. Import character model (FBX)
2. Set up armature and bone naming (Unity standard)
3. Create LOD meshes (high, medium, low detail)
4. Generate lightmaps UVs
5. Create collision meshes (simplified versions)
6. Set up ragdoll physics bones
7. Export with proper transform orientation
8. Create Unity prefab setup script
```

**Template: VRChat Avatar Setup**
```
Prepare VRChat avatar:
1. Import avatar model (FBX or VRM)
2. Set up armature (VRChat bone naming standard)
3. Create blendshapes for facial expressions
4. Set up eye tracking bones
5. Create physics bones for hair/clothes
6. Set up viseme shapes for lip sync
7. Create Unity package with shaders
8. Test avatar in VRChat SDK
```

### 9. Visual Effects

**Template: Particle Effects**
```
Create advanced particle effects:
1. Set up multiple particle systems (fire, smoke, sparks)
2. Create particle materials with emission/glow
3. Set up force fields for realistic movement
4. Add collision with scene objects
5. Create particle sub-emitters
6. Set up texture animation for particles
7. Render with motion blur and depth of field
```

**Template: Fluid Simulation**
```
Set up fluid simulation:
1. Create fluid domain (large cube)
2. Add fluid inflow object (small cube)
3. Set up fluid material properties
4. Add collision objects in fluid path
5. Configure fluid simulation settings (resolution, timesteps)
6. Bake fluid simulation (can take hours)
7. Set up fluid mesh and materials
8. Render final fluid animation
```

### 10. Troubleshooting Templates

**Template: Performance Optimization**
```
Optimize scene performance:
1. Analyze current scene (vertex count, texture memory)
2. Identify performance bottlenecks
3. Reduce polygon count where possible
4. Optimize texture sizes and compression
5. Simplify materials and shaders
6. Set up LOD system
7. Test render times at different quality settings
8. Create performance comparison report
```

**Template: Export Issues**
```
Debug export problems:
1. Check export settings compatibility
2. Verify object hierarchies are clean
3. Ensure proper UV mapping
4. Check material assignments
5. Validate animation data
6. Test export with minimal scene first
7. Check target application import logs
8. Create simplified test case for issue reproduction
```

---

## 🎯 Template Usage Guide

### How to Use Templates

1. **Copy the template text** into Claude/ChatGPT
2. **Customize file paths and parameters** as needed
3. **Run the commands step by step**
4. **Check results** after each step
5. **Iterate and refine** based on results

### Template Categories

- **🎨 Basic**: Simple operations for beginners
- **⚡ Advanced**: Complex workflows for professionals
- **🎮 Game Dev**: Game-specific pipelines
- **🏗️ Architecture**: Building and environment creation
- **🎭 VFX**: Visual effects and simulations
- **🔧 Technical**: Optimization and troubleshooting

### Customization Tips

- **File Paths**: Always update paths to your actual files
- **Parameters**: Adjust numbers based on your needs
- **Quality Settings**: Balance quality vs. speed for your use case
- **Output Formats**: Choose formats appropriate for your pipeline

### Best Practices

- **Start Small**: Test with simple scenes first
- **Save Iterations**: Save versions as you progress
- **Check Logs**: Monitor console output for errors
- **Performance**: Balance quality and speed requirements
- **Documentation**: Keep notes on what works for future reference

---

*Blender MCP Quick Start Templates v1.0.0 - Comprehensive workflow guides for 3D content creation*

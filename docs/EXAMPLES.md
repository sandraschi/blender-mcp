# Blender-MCP Examples

This document provides practical examples of how to use Blender-MCP tools for common tasks.

## Table of Contents
- [Basic Scene Setup](#basic-scene-setup)
- [Material Creation](#material-creation)
- [Animation](#animation)
- [Physics Simulation](#physics-simulation)
- [Rendering](#rendering)
- [Exporting](#exporting)

## Basic Scene Setup

### Create a New Scene with Basic Lighting

```python
# Create a new scene
await create_scene(name="MyScene")

# Add a camera
await create_camera(
    name="MainCamera",
    location=(5, -5, 3),
    rotation=(1.0, 0.0, 0.8)
)

# Add a sun light
await create_light(
    name="Sun",
    light_type='SUN',
    location=(0, 0, 10),
    energy=2.0,
    rotation=(0.6, 0, 0.8)
)

# Add a ground plane
await create_plane(
    name="Ground",
    size=10.0,
    location=(0, 0, 0)
)
```

## Material Creation

### Create and Assign a Metallic Material

```python
# Create a metallic material
await create_material(
    name="Chrome",
    material_type='PRINCIPLED',
    color=(0.8, 0.8, 0.8),
    metallic=1.0,
    roughness=0.1
)

# Create a sphere
await create_sphere(
    name="MetalSphere",
    location=(0, 0, 1),
    radius=1.0
)

# Assign the material
await assign_material(
    object_name="MetalSphere",
    material_name="Chrome"
)
```

## Animation

### Create a Simple Bouncing Ball Animation

```python
# Create a sphere
await create_sphere(
    name="Ball",
    location=(0, 0, 5),
    radius=0.5
)

# Add a ground plane
await create_plane(
    name="Ground",
    size=10.0,
    location=(0, 0, 0)
)

# Add rigid body physics to the ball
await setup_rigid_body(
    object_name="Ball",
    type='ACTIVE',
    mass=1.0,
    friction=0.5,
    bounce=0.8
)

# Add rigid body to ground
await setup_rigid_body(
    object_name="Ground",
    type='PASSIVE',
    friction=0.5,
    bounce=0.5
)

# Bake physics simulation
await bake_physics_simulation(
    frame_start=1,
    frame_end=100,
    step=1
)
```

## Physics Simulation

### Create a Cloth Simulation

```python
# Create a plane for cloth
await create_plane(
    name="Cloth",
    size=2.0,
    location=(0, 0, 3),
    rotation=(0, 0, 0)
)

# Add cloth simulation
await setup_cloth_simulation(
    object_name="Cloth",
    quality_preset='MEDIUM',
    mass=0.3,
    bending_stiffness=0.5,
    use_collision=True,
    use_self_collision=True
)

# Create a sphere as a collision object
await create_sphere(
    name="CollisionSphere",
    location=(0, 0, 1),
    radius=0.8
)

# Add collision to the sphere
await setup_collision(
    object_name="CollisionSphere",
    type='PASSIVE',
    friction=0.5
)

# Bake the simulation
await bake_physics_simulation(
    frame_start=1,
    frame_end=100,
    step=1
)
```

## Rendering

### Set Up and Render a Scene

```python
# Set up render engine (Cycles)
await set_render_engine(engine='CYCLES')

# Set render resolution
await set_render_resolution(
    resolution_x=1920,
    resolution_y=1080,
    resolution_percentage=100
)

# Set up samples
await set_render_samples(
    render_samples=256,
    preview_samples=32,
    use_adaptive_sampling=True,
    adaptive_threshold=0.01
)

# Set up denoising
await set_render_denoising(
    use_denoising=True,
    denoiser='OPENIMAGEDENOISE'
)

# Set up output
await setup_render_output(
    filepath="//renders/render_"
    file_format='PNG',
    color_mode='RGBA',
    quality=90
)

# Render animation
await render_animation(
    frame_start=1,
    frame_end=100,
    frame_step=1
)
```

## Exporting

### Export for Game Engines

#### Export to FBX (Unity/Unreal)

```python
await export_fbx(
    filepath="/path/to/export/model.fbx",
    use_selection=False,
    global_scale=1.0,
    apply_unit_scale=True,
    bake_anim=True,
    bake_anim_use_nla_strips=True,
    bake_anim_use_all_actions=False,
    add_leaf_bones=True,
    primary_bone_axis='Y',
    secondary_bone_axis='X'
)
```

#### Export to glTF (Web/Three.js)

```python
await export_gltf(
    filepath="/path/to/export/scene.glb",
    export_format='GLB',
    export_textures=True,
    export_materials='EXPORT',
    export_animations=True,
    export_skins=True,
    export_morph=True,
    export_yup=True
)
```

### Export for 3D Printing (STL)

```python
await export_stl(
    filepath="/path/to/export/object.stl",
    use_selection=True,
    use_mesh_modifiers=True,
    ascii=False,
    use_scene_unit=True,
    global_scale=1.0
)
```

These examples demonstrate common workflows using Blender-MCP tools. For more detailed information about each tool's parameters, please refer to the [Tool Reference](TOOL_REFERENCE.md) documentation.

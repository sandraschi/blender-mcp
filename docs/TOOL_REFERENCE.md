# Blender-MCP Tool Reference

This document provides detailed documentation for all tools available in the Blender-MCP server, organized by category.

## Table of Contents
- [Animation Tools](#animation-tools)
- [Material Tools](#material-tools)
- [Scene Tools](#scene-tools)
- [Export Tools](#export-tools)
- [Advanced Physics Tools](#advanced-physics-tools)
- [Render Tools](#render-tools)

## Animation Tools

### `insert_keyframe`
Inserts a keyframe for the specified object and property.

**Parameters:**
- `object_name`: Name of the object to keyframe
- `data_path`: Path to the property to keyframe (e.g., "location", "rotation_euler")
- `frame`: Frame number for the keyframe
- `index`: Index for vector properties (-1 for all)
- `keyframe_type`: Type of keyframe ('KEYFRAME', 'BREAKDOWN', 'EXTREME', etc.)

### `bake_animation`
Bakes animation for the specified object.

**Parameters:**
- `object_name`: Name of the object to bake
- `frame_start`: Start frame
- `frame_end`: End frame
- `step`: Frame step
- `only_selected`: Only bake selected objects
- `visual_keying`: Use visual keying
- `clear_constraints`: Clear constraints after baking

## Material Tools

### `create_material`
Creates a new material.

**Parameters:**
- `name`: Name of the material
- `material_type`: Type of material ('PRINCIPLED', 'GLASS', 'EMISSION', etc.)
- `color`: Base color as RGB tuple (0-1)
- `metallic`: Metallic value (0-1)
- `roughness`: Roughness value (0-1)

### `assign_material`
Assigns a material to an object.

**Parameters:**
- `object_name`: Name of the object
- `material_name`: Name of the material to assign

## Scene Tools

### `create_scene`
Creates a new scene.

**Parameters:**
- `name`: Name of the new scene
- `use_background_scene`: Whether to use background scene settings

### `set_active_scene`
Sets the active scene.

**Parameters:**
- `name`: Name of the scene to set as active

## Export Tools

### `export_fbx`
Exports the scene to FBX format.

**Parameters:**
- `filepath`: Output file path
- `use_selection`: Export selected objects only
- `use_active_collection`: Export active collection only
- `global_scale`: Scale all data
- `apply_unit_scale`: Apply unit scaling
- `bake_anim`: Export animation
- `bake_anim_use_nla_strips`: Use NLA strips

### `export_gltf`
Exports the scene to glTF/GLB format.

**Parameters:**
- `filepath`: Output file path
- `export_format`: 'GLB' or 'GLTF_SEPARATE'
- `export_textures`: Export textures
- `export_materials`: Export materials
- `export_animations`: Export animations
- `export_skins`: Export skinning

## Advanced Physics Tools

### `setup_cloth_simulation`
Sets up a cloth simulation.

**Parameters:**
- `object_name`: Name of the object to add cloth to
- `quality_preset`: Quality preset ('LOW', 'MEDIUM', 'HIGH')
- `mass`: Mass of the cloth
- `bending_stiffness`: Bending stiffness (0-1)
- `use_collision`: Enable collision
- `use_self_collision`: Enable self-collision

### `setup_fluid_simulation`
Sets up a fluid simulation.

**Parameters:**
- `object_name`: Name of the domain object
- `domain_type`: Type of fluid ('GAS' or 'LIQUID')
- `resolution`: Simulation resolution
- `time_scale`: Time scale
- `viscosity`: Viscosity value

## Render Tools

### `set_render_engine`
Sets the render engine.

**Parameters:**
- `engine`: Render engine ('CYCLES', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH')

### `set_render_resolution`
Sets the render resolution.

**Parameters:**
- `resolution_x`: Horizontal resolution
- `resolution_y`: Vertical resolution
- `resolution_percentage`: Resolution percentage (1-10000)

### `set_render_samples`
Sets the number of render samples.

**Parameters:**
- `render_samples`: Number of render samples
- `preview_samples`: Number of preview samples
- `use_adaptive_sampling`: Use adaptive sampling
- `adaptive_threshold`: Adaptive sampling threshold (0-1)

### `setup_light_paths`
Configures light paths for rendering.

**Parameters:**
- `max_bounces`: Maximum number of bounces
- `diffuse_bounces`: Diffuse bounces
- `glossy_bounces`: Glossy bounces
- `transmission_bounces`: Transmission bounces
- `volume_bounces`: Volume bounces

### `setup_motion_blur`
Configures motion blur settings.

**Parameters:**
- `use_motion_blur`: Enable motion blur
- `motion_blur_shutter`: Shutter speed

### `setup_depth_of_field`
Configures depth of field.

**Parameters:**
- `use_dof`: Enable depth of field
- `focus_object`: Name of the focus object
- `focus_distance`: Focus distance
- `fstop`: F-stop value

### `setup_ambient_occlusion`
Configures ambient occlusion.

**Parameters:**
- `use_ao`: Enable ambient occlusion
- `ao_factor`: AO factor
- `ao_distance`: AO distance

### `setup_volumetrics`
Configures volumetrics.

**Parameters:**
- `use_volumetrics`: Enable volumetrics
- `volumetric_samples`: Number of volumetric samples

### `setup_render_output`
Configures render output settings.

**Parameters:**
- `filepath`: Output file path
- `file_format`: Output format ('PNG', 'JPEG', 'OPEN_EXR', etc.)
- `color_mode`: Color mode ('RGB', 'RGBA', etc.)
- `quality`: Output quality (0-100)

### `render_animation`
Renders an animation.

**Parameters:**
- `frame_start`: Start frame
- `frame_end`: End frame
- `frame_step`: Frame step

### `render_still`
Renders a still image.

**Parameters:**
- `frame`: Frame number to render

### `setup_gpu_rendering`
Configures GPU rendering.

**Parameters:**
- `use_gpu`: Enable GPU rendering
- `device_type`: Device type ('CUDA', 'OPTIX', 'HIP', etc.)

# Blender-MCP Tool Reference

This document provides detailed documentation for all tools available in the Blender-MCP server, organized by category. For practical examples, see [EXAMPLES.md](EXAMPLES.md).

## Table of Contents
- [Animation Tools](#animation-tools)
- [Material & Shading](#material--shading)
- [Scene Management](#scene-management)
- [Object Tools](#object-tools)
- [Physics & Simulation](#physics--simulation)
- [Rendering](#rendering)
- [Lighting](#lighting)
- [Cameras](#cameras)
- [Compositing](#compositing)
- [Import/Export](#importexport)
- [Scripting & Automation](#scripting--automation)

## Animation Tools

### Keyframe Animation

#### `insert_keyframe`
Inserts a keyframe for the specified object and property.

**Parameters:**
- `object_name`: Name of the object to keyframe
- `data_path`: Path to the property to keyframe (e.g., "location", "rotation_euler")
- `frame`: Frame number for the keyframe
- `index`: Index for vector properties (-1 for all)
- `keyframe_type`: Type of keyframe ('KEYFRAME', 'BREAKDOWN', 'EXTREME', 'JITTER', 'KEYFRAME_VEC', 'MOVING_HOLD')
- `options`: Additional options as a dictionary (e.g., {'INSERTKEY_NEEDED', 'INSERTKEY_MATRIX'})
- `keying_set`: Name of the keying set to use

#### `bake_animation`
Bakes animation for the specified object.

**Parameters:**
- `object_name`: Name of the object to bake
- `frame_start`: Start frame
- `frame_end`: End frame
- `step`: Frame step
- `only_selected`: Only bake selected objects
- `visual_keying`: Use visual keying (accounts for constraints)
- `clear_constraints`: Clear constraints after baking
- `bake_types`: Set of properties to bake ('POSE', 'OBJECT', 'SHAPE')
- `use_current_action`: Bake to the current action
- `use_clean_curves`: Clean redundant keyframes

### Armature & Rigging

#### `create_armature`
Creates a new armature object.

**Parameters:**
- `name`: Name for the new armature
- `location`: (x, y, z) location for the armature
- `rotation`: (x, y, z) rotation in radians
- `scale`: (x, y, z) scale factors
- `enter_edit_mode`: Enter edit mode after creation
- `align`: Alignment ('WORLD', 'VIEW', 'CURSOR')

#### `add_bone`
Adds a bone to an armature.

**Parameters:**
- `armature_name`: Name of the armature
- `bone_name`: Name for the new bone
- `head`: (x, y, z) head position
- `tail`: (x, y, z) tail position
- `parent`: Name of parent bone (optional)
- `connected`: Whether to connect to parent bone
- `length`: Length of the bone (alternative to tail)
- `roll`: Roll angle in radians
- `layers`: Array of 32 booleans for layer visibility

### Animation Curves

#### `get_fcurve`
Gets an F-curve for a specific data path.

**Parameters:**
- `object_name`: Name of the object
- `data_path`: Path to the animated property
- `index`: Index for the property (-1 for all)
- `action_name`: Name of the action (defaults to active action)

**Returns:**
- Dictionary containing F-curve data

#### `set_keyframe_points`
Sets keyframe points for an F-curve.

**Parameters:**
- `object_name`: Name of the object
- `data_path`: Path to the animated property
- `index`: Index for the property
- `frames`: List of frame numbers
- `values`: List of values for each frame
- `keyframe_types`: List of keyframe types (optional)
- `interpolation`: Interpolation mode ('CONSTANT', 'LINEAR', 'BEZIER', etc.)
- `easing`: Easing type for interpolation

### NLA (Non-Linear Animation)

#### `create_nla_track`
Creates a new NLA track.

**Parameters:**
- `object_name`: Name of the object
- `track_name`: Name for the new track
- `action_name`: Name of the action to add
- `frame_start`: Starting frame
- `blend_type`: Blend type ('REPLACE', 'COMBINE', 'ADD')
- `blend_in`: Blend in frames
- `blend_out`: Blend out frames
- `extend_mode`: Extend mode ('NOTHING', 'HOLD', 'HOLD_FORWARD')

#### `bake_action`
Bakes an action from the current setup.

**Parameters:**
- `object_name`: Name of the object to bake
- `frame_start`: Start frame
- `frame_end`: End frame
- `step`: Frame step
- `only_selected`: Only bake selected bones/objects
- `visual_keying`: Use visual keying
- `clear_constraints`: Clear constraints after baking
- `clean_curves`: Clean redundant keyframes
- `bake_types`: Set of properties to bake
- `use_current_action`: Bake to the current action

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

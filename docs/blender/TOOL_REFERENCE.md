# Blender-MCP Tool Reference

This document provides detailed documentation for all **40 portmanteau tools** available in the Blender-MCP server. Each tool supports multiple operations via the `operation` parameter.

**🎯 Project AG Integration**: This reference now includes 8 advanced VR tools specifically designed for professional avatar workflows in VRChat, Resonite, and Unity.

## Table of Contents
- [Animation & Motion](#animation--motion)
- [Rigging & Bones](#rigging--bones)
- [VR Avatar Tools](#vr-avatar-tools)
- [Scene Management](#scene-management)
- [Materials](#materials)
- [Mesh & Objects](#mesh--objects)
- [Transform](#transform)
- [Lighting](#lighting)
- [Camera](#camera)
- [Physics & Particles](#physics--particles)
- [Modifiers](#modifiers)
- [Textures & UV](#textures--uv)
- [Selection](#selection)
- [Render](#render)
- [Import & Export](#import--export)
- [Furniture](#furniture)
- [Utility Tools](#utility-tools)

---

## Animation & Motion

### `blender_animation` (21 operations)

Comprehensive animation system supporting keyframes, shape keys, actions, and baking.

#### Basic Animation
| Operation | Description |
|-----------|-------------|
| `set_keyframe` | Insert keyframe for location/rotation/scale |
| `animate_location` | Animate movement between frames |
| `animate_rotation` | Animate rotation between frames |
| `animate_scale` | Animate scale between frames |
| `play_animation` | Start viewport playback |
| `set_frame_range` | Set timeline start/end frames |
| `clear_animation` | Remove all keyframes from object |

#### Shape Keys (VRM Facial Expressions)
| Operation | Description |
|-----------|-------------|
| `list_shape_keys` | Discover all morphs/expressions on mesh |
| `set_shape_key` | Set expression value (0.0-1.0) |
| `keyframe_shape_key` | Insert keyframe for shape key |
| `create_shape_key` | Add new morph target |

#### Action Management
| Operation | Description |
|-----------|-------------|
| `list_actions` | List all animation clips |
| `create_action` | Create new action clip |
| `set_active_action` | Assign action to object |
| `push_to_nla` | Push action to NLA track for layering |

#### Interpolation
| Operation | Description |
|-----------|-------------|
| `set_interpolation` | Set keyframe type (CONSTANT, LINEAR, BEZIER, BOUNCE, ELASTIC) |
| `set_easing` | Set easing (AUTO, EASE_IN, EASE_OUT, EASE_IN_OUT) |

#### Constraints
| Operation | Description |
|-----------|-------------|
| `add_constraint` | Add constraint to object |
| `add_bone_constraint` | Add constraint to pose bone |

#### Baking
| Operation | Description |
|-----------|-------------|
| `bake_action` | Bake constraints to keyframes |
| `bake_all_actions` | Bake NLA to single action |

**Example - VRM Facial Animation:**
```python
# List available expressions
blender_animation(operation="list_shape_keys", object_name="Face")

# Set happy expression
blender_animation(operation="set_shape_key", object_name="Face", 
                  shape_key_name="happy", value=1.0)

# Keyframe at frame 1
blender_animation(operation="keyframe_shape_key", object_name="Face",
                  shape_key_name="happy", frame=1)
```

---

## Rigging & Bones

### `blender_rigging` (12 operations)

Advanced armature creation, bone animation, and rigging for VRM/humanoid models with Project AG enhancements.

| Operation | Description |
|-----------|-------------|
| `create_armature` | Create new armature object |
| `add_bone` | Add bone to armature |
| `create_bone_ik` | Create IK constraint |
| `create_basic_rig` | Generate simple biped rig |
| `list_bones` | List all bones (VRM discovery) |
| `pose_bone` | Set bone rotation/position |
| `set_bone_keyframe` | Keyframe bone pose |
| `reset_pose` | Return to rest position |
| `transfer_weights` | Transfer vertex weights between meshes (clothing workflow) |
| `manage_vertex_groups` | Create/rename/mirror/remove vertex groups |
| `humanoid_mapping` | Apply VRChat/Unity humanoid bone naming standards |

**Example - VRM Bone Posing:**
```python
# Discover bone names
blender_rigging(operation="list_bones", armature_name="Armature")

# Raise left arm
blender_rigging(operation="pose_bone", armature_name="Armature",
                bone_name="leftUpperArm", rotation=[0, 0, 90])

# Keyframe the pose
blender_rigging(operation="set_bone_keyframe", armature_name="Armature",
                bone_name="leftUpperArm", frame=1)

# Transfer weights from body to clothing
blender_rigging(operation="transfer_weights", source_mesh="Body",
                target_mesh="Clothing", armature_name="Armature")

# Apply humanoid bone mapping
blender_rigging(operation="humanoid_mapping", armature_name="Armature",
                mapping_preset="VRCHAT")
```

---

## VR Avatar Tools

### `blender_validation` (2 operations)

Pre-flight validation for VR platforms ensuring avatar compatibility.

| Operation | Description |
|-----------|-------------|
| `validate_avatar` | Check polycount, bones, materials against platform limits |
| `spawn_benny` | Spawn test German Shepherd for state persistence verification |

**Platform Limits:**
- VRChat: 70k triangles, 256 bones, 8 materials max
- Resonite: 100k triangles, 512 bones
- Unity: 32k triangles recommended for mobile

**Example - VRChat Validation:**
```python
# Validate avatar for VRChat
blender_validation(operation="validate_avatar", target_platform="VRCHAT")
# Returns: polycount check, bone count, material density, transform validation
```

### `blender_splatting` (4 operations)

Gaussian Splatting (3DGS) support for hybrid environments and high-fidelity scene creation.

| Operation | Description |
|-----------|-------------|
| `import_gs` | Import .ply/.spz splat files with proxy objects |
| `crop_and_clean` | Remove noise/floater splats from scans |
| `generate_collision_mesh` | Create walkable collision geometry |
| `export_for_resonite` | Export splats with collision for Resonite |

**Example - Environment Creation:**
```python
# Import scanned room
blender_splatting(operation="import_gs", file_path="room_scan.ply",
                  setup_proxy=True)

# Generate collision for walking
blender_splatting(operation="generate_collision_mesh", density_threshold=0.1)

# Export for Resonite
blender_splatting(operation="export_for_resonite", target_format="SPZ",
                  include_collision=True)
```

### `blender_materials_baking` (3 operations)

Advanced material conversion and optimization for cross-platform compatibility.

| Operation | Description |
|-----------|-------------|
| `bake_toon_to_pbr` | Convert cel-shaded materials to PBR textures |
| `consolidate_materials` | Merge materials into atlas textures |
| `convert_vrm_shader_to_pbr` | Convert VRM/MToon shaders to standard PBR |

**Example - VRChat Material Optimization:**
```python
# Convert toon shaders to PBR
blender_materials_baking(operation="convert_vrm_shader_to_pbr",
                        target_mesh="Avatar", resolution=2048)

# Consolidate materials to reduce draw calls
blender_materials_baking(operation="consolidate_materials",
                        target_mesh="Avatar", max_atlas_size=2048)
```

### `blender_vrm_metadata` (5 operations)

VRM-specific metadata management for avatar functionality.

| Operation | Description |
|-----------|-------------|
| `set_first_person_offset` | Configure first-person camera position |
| `setup_blink_viseme_mappings` | Setup facial animation mappings |
| `configure_spring_bones` | Configure dynamic hair/cloth physics |
| `set_vrm_look_at` | Configure eye-tracking behavior |
| `export_vrm_metadata` | Export VRM settings to JSON |

**Example - Complete VRM Setup:**
```python
# Set first person view
blender_vrm_metadata(operation="set_first_person_offset",
                    offset_z=0.15)

# Configure facial animations
blender_vrm_metadata(operation="setup_blink_viseme_mappings",
                    blink_shape_key="blink")

# Setup spring bone hair physics
blender_vrm_metadata(operation="configure_spring_bones",
                    spring_bone_settings={"stiffness": 0.5, "gravity_power": 0.0})

# Export metadata
blender_vrm_metadata(operation="export_vrm_metadata",
                    output_path="//vrm_settings.json")
```

### `blender_atlasing` (4 operations)

Material and texture atlasing for mobile VR performance optimization.

| Operation | Description |
|-----------|-------------|
| `create_material_atlas` | Combine materials into atlas textures |
| `merge_texture_atlas` | Merge multiple texture files |
| `optimize_draw_calls` | Intelligent material consolidation |
| `get_atlas_uv_layout` | Generate UV mapping coordinates |

**Example - Performance Optimization:**
```python
# Create material atlas
blender_atlasing(operation="create_material_atlas",
                target_mesh="Avatar", atlas_size=2048)

# Optimize for mobile VR
blender_atlasing(operation="optimize_draw_calls",
                target_mesh="Avatar", max_materials=4)
```

### `blender_shapekeys` (5 operations)

Advanced facial animation and lip sync support.

| Operation | Description |
|-----------|-------------|
| `create_viseme_shapekeys` | Create VRM visemes (A, I, U, E, O) |
| `create_blink_shapekey` | Setup eyelid blink animation |
| `set_viseme_weights` | Animate mouth shapes for lip sync |
| `create_facial_expression` | Combine visemes into expressions |
| `analyze_shapekeys` | Check VRM compliance and status |

**Example - Lip Sync Setup:**
```python
# Create VRM visemes
blender_shapekeys(operation="create_viseme_shapekeys",
                 viseme_type="vrm", auto_generate=True)

# Setup blink animation
blender_shapekeys(operation="create_blink_shapekey",
                 blink_intensity=1.0)

# Set mouth to "A" sound
blender_shapekeys(operation="set_viseme_weights",
                 viseme_weights={"aa": 1.0}, frame=1)

# Create happy expression
blender_shapekeys(operation="create_facial_expression",
                 expression_name="happy", base_visemes={"ee": 0.8})
```

### `blender_export_presets` (4 operations)

Platform-specific export configurations with validation.

| Operation | Description |
|-----------|-------------|
| `export_with_preset` | Export using platform-specific settings |
| `validate_export_preset` | Pre-export validation against limits |
| `get_platform_presets` | List available platform configurations |
| `create_custom_preset` | Create custom export configuration |

**Platform Presets:**
- `VRCHAT`: Unity scale 1.0, FBX, 256 bones max
- `RESONITE`: GLTF format, 512 bones max
- `UNITY`: Generic Unity export settings
- `LEGACY_VRCHAT`: 0.01 scale for old workflows

**Example - VRChat Export:**
```python
# Validate before export
blender_export_presets(operation="validate_export_preset",
                      target_objects=["Avatar"], platform="VRCHAT")

# Export with VRChat settings
blender_export_presets(operation="export_with_preset",
                      target_objects=["Avatar"], platform="VRCHAT",
                      output_path="//avatar_vrchat.fbx")
```

---

## Scene Management

### `blender_scene` (12 operations)

Scene, collection, view layer, lighting, and camera management.

| Operation | Description |
|-----------|-------------|
| `create_scene` | Create new scene |
| `list_scenes` | List all scenes |
| `clear_scene` | Remove all objects |
| `set_active_scene` | Switch active scene |
| `link_object_to_scene` | Share object between scenes |
| `create_collection` | Create collection |
| `add_to_collection` | Add object to collection |
| `set_active_collection` | Set working collection |
| `set_view_layer` | Control view layers |
| `setup_lighting` | Automated lighting rig |
| `setup_camera` | Camera positioning |
| `set_render_settings` | Configure resolution |

---

## Materials

### `blender_materials` (7 operations)

PBR material creation and assignment.

| Operation | Description |
|-----------|-------------|
| `create_fabric` | Velvet, silk, cotton, linen, wool |
| `create_metal` | Gold, silver, brass, copper, iron |
| `create_wood` | Oak, pine, mahogany, walnut |
| `create_glass` | Clear, tinted, frosted, stained |
| `create_ceramic` | Porcelain, ceramic, terra cotta |
| `assign_to_object` | Assign material to object |
| `create_from_preset` | Use predefined preset |

**Example:**
```python
# Create gold material
blender_materials(operation="create_metal", name="Gold", metal_type="gold")

# Assign to cube
blender_materials(operation="assign_to_object", object_name="Cube", material_name="Gold")
```

---

## Mesh & Objects

### `blender_mesh` (9 operations)

Create and manipulate 3D primitives.

| Operation | Description |
|-----------|-------------|
| `create_cube` | Cube primitive |
| `create_sphere` | Sphere primitive |
| `create_cylinder` | Cylinder primitive |
| `create_cone` | Cone primitive |
| `create_plane` | Plane primitive |
| `create_torus` | Torus primitive |
| `create_monkey` | Suzanne monkey |
| `duplicate_object` | Copy object |
| `delete_object` | Remove object |

---

## Transform

### `blender_transform` (8 operations)

Position, rotate, and scale objects.

| Operation | Description |
|-----------|-------------|
| `set_location` | Set absolute position |
| `set_rotation` | Set rotation (degrees) |
| `set_scale` | Set scale factors |
| `translate` | Move by offset |
| `rotate` | Rotate by angle |
| `scale` | Scale by factor |
| `apply_transform` | Apply to mesh |
| `reset_transform` | Reset to identity |

---

## Lighting

### `blender_lighting` (7 operations)

Light creation and management.

| Operation | Description |
|-----------|-------------|
| `create_sun` | Directional sun light |
| `create_point` | Omnidirectional point light |
| `create_spot` | Focused spotlight |
| `create_area` | Area light (soft shadows) |
| `setup_three_point` | Three-point lighting rig |
| `setup_hdri` | HDRI environment |
| `adjust_light` | Modify light properties |

---

## Camera

### `blender_camera` (3 operations)

Camera creation and settings.

| Operation | Description |
|-----------|-------------|
| `create_camera` | Create new camera |
| `set_active_camera` | Set scene camera |
| `set_camera_lens` | Adjust focal length, sensor |

---

## Physics & Particles

### `blender_physics` (8 operations)

Physics simulation.

| Operation | Description |
|-----------|-------------|
| `enable_rigid_body` | Add rigid body physics |
| `enable_cloth` | Cloth simulation |
| `enable_soft_body` | Soft body simulation |
| `enable_fluid` | Fluid simulation |
| `bake_physics` | Bake to keyframes |
| `add_force_field` | Add force field |
| `set_rigid_body_constraint` | Connect rigid bodies |
| `configure_world` | Physics world settings |

### `blender_particles` (7 operations)

Particle systems.

| Operation | Description |
|-----------|-------------|
| `create_particle_system` | Basic particles |
| `create_hair_particles` | Hair/fur |
| `create_fire_effect` | Fire/smoke |
| `create_water_effect` | Water/splash |
| `control_emission` | Emission settings |
| `bake_particles` | Bake simulation |
| `set_particle_physics` | Physics settings |

---

## Modifiers

### `blender_modifiers` (12 operations)

Mesh modifiers.

| Operation | Description |
|-----------|-------------|
| `add_subsurf` | Subdivision surface |
| `add_bevel` | Bevel edges |
| `add_mirror` | Mirror modifier |
| `add_solidify` | Add thickness |
| `add_array` | Array copies |
| `add_boolean` | Boolean operations |
| `add_decimate` | Reduce polygons |
| `add_displace` | Displacement |
| `add_wave` | Wave deformation |
| `remove_modifier` | Remove modifier |
| `apply_modifier` | Apply to mesh |
| `get_modifiers` | List modifiers |

---

## Textures & UV

### `blender_textures` (7 operations)

Procedural textures.

| Operation | Description |
|-----------|-------------|
| `create_noise` | Noise texture |
| `create_voronoi` | Voronoi texture |
| `create_musgrave` | Musgrave texture |
| `create_wave` | Wave texture |
| `create_checker` | Checker pattern |
| `create_brick` | Brick pattern |
| `create_gradient` | Gradient texture |

### `blender_uv` (5 operations)

UV mapping.

| Operation | Description |
|-----------|-------------|
| `unwrap` | Smart UV unwrap |
| `smart_project` | Smart projection |
| `cube_project` | Cube projection |
| `cylinder_project` | Cylindrical projection |
| `reset_uvs` | Reset UV coordinates |

---

## Selection

### `blender_selection` (6 operations)

Object selection.

| Operation | Description |
|-----------|-------------|
| `select_objects` | Select by name |
| `select_by_type` | Select by type (MESH, LIGHT, etc.) |
| `select_by_material` | Select by material |
| `select_all` | Select everything |
| `select_none` | Deselect all |
| `invert_selection` | Invert selection |

---

## Render

### `blender_render` (4 operations)

Rendering.

| Operation | Description |
|-----------|-------------|
| `render_preview` | Single frame preview |
| `render_turntable` | 360° turntable animation |
| `render_animation` | Full animation sequence |
| `render_current_frame` | Render current frame |

---

## Import & Export

### `blender_import` (2 operations)

File import.

| Operation | Description |
|-----------|-------------|
| `import_[format]` | Import FBX, OBJ, glTF, STL, PLY, VRM |
| `link_asset` | Link external asset |

### `blender_export` (2 operations)

File export.

| Operation | Description |
|-----------|-------------|
| `export_unity` | Unity-compatible export |
| `export_vrchat` | VRChat-compatible export |

---

## Furniture

### `blender_furniture` (9 operations)

Complex object creation.

| Operation | Description |
|-----------|-------------|
| `create_chair` | Dining/office/arm chairs |
| `create_table` | Dining/coffee/desks |
| `create_bed` | Single/double/bunk beds |
| `create_sofa` | Sofas and couches |
| `create_cabinet` | Storage cabinets |
| `create_desk` | Office workstations |
| `create_shelf` | Bookshelves |
| `create_stool` | Stools and bar stools |

---

## Utility Tools

### `blender_help` (5 operations)
Help and documentation system.

### `blender_status` (4 operations)
System status and health checks.

### `blender_download` (2 operations)
Asset download from URLs.

### `blender_view_logs` / `blender_log_stats`
Log viewing and statistics.

### `blender_addons` (3 operations)
Addon management.

---

## Complete VRM Workflow Example

```python
# === PHASE 1: IMPORT & VALIDATION ===

# Import VRM avatar
blender_import(operation="import_gltf", filepath="avatar.vrm")

# Validate against VRChat limits (70k tris, 256 bones, 8 materials)
blender_validation(operation="validate_avatar", target_platform="VRCHAT")

# === PHASE 2: MATERIAL OPTIMIZATION ===

# Convert stylized MToon shaders to PBR for cross-platform compatibility
blender_materials_baking(operation="convert_vrm_shader_to_pbr",
                        target_mesh="Body", resolution=2048)

# Consolidate materials into atlases to reduce draw calls
blender_materials_baking(operation="consolidate_materials",
                        target_mesh="Body", max_atlas_size=2048)

# Create comprehensive material atlas for mobile VR performance
blender_atlasing(operation="create_material_atlas",
                target_mesh="Body", atlas_size=2048)

# === PHASE 3: VRM METADATA SETUP ===

# Configure first-person camera offset (VRChat standard: 0.1-0.2m)
blender_vrm_metadata(operation="set_first_person_offset",
                    target_armature="Armature", offset_z=0.15)

# Setup facial animation mappings for lip sync and expressions
blender_vrm_metadata(operation="setup_blink_viseme_mappings",
                    target_mesh="Face",
                    blink_shape_key="blink",
                    viseme_mappings={"aa": "v_a", "ih": "v_i", "ou": "v_u",
                                   "ee": "v_e", "oh": "v_o"})

# Configure spring bone physics for hair/cloth dynamics
blender_vrm_metadata(operation="configure_spring_bones",
                    target_armature="Armature",
                    spring_bone_settings={"bones": ["hair_front_L", "hair_back_R"],
                                        "stiffness": 0.5, "gravity_power": 0.0})

# Setup eye tracking behavior
blender_vrm_metadata(operation="set_vrm_look_at",
                    target_armature="Armature",
                    look_at_settings={"type": "bone", "horizontal_inner": {"curve": [0,0,0,1]}})

# === PHASE 4: FACIAL ANIMATION SETUP ===

# Create VRM-compliant viseme shape keys (A, I, U, E, O)
blender_shapekeys(operation="create_viseme_shapekeys",
                 target_mesh="Face", viseme_type="vrm", auto_generate=True)

# Setup eyelid blink animation
blender_shapekeys(operation="create_blink_shapekey",
                 target_mesh="Face", blink_intensity=1.0)

# Analyze shape key compliance and completeness
blender_shapekeys(operation="analyze_shapekeys", target_mesh="Face")

# === PHASE 5: RIGGING & WEIGHTS ===

# Apply humanoid bone mapping for VRChat/Unity compatibility
blender_rigging(operation="humanoid_mapping", armature_name="Armature",
                humanoid_preset="VRCHAT")

# If adding clothing, transfer weights from body to clothing mesh
blender_rigging(operation="transfer_weights", source_mesh="Body",
                target_mesh="Clothing", armature_name="Armature")

# === PHASE 6: ANIMATION & POSES ===

# Set animation timeline
blender_animation(operation="set_frame_range", start_frame=1, end_frame=120)

# Create neutral pose at frame 1
blender_rigging(operation="pose_bone", armature_name="Armature",
                bone_name="leftUpperArm", rotation=[0, 0, 0])
blender_rigging(operation="set_bone_keyframe", armature_name="Armature",
                bone_name="leftUpperArm", frame=1)

# Create wave pose at frame 60
blender_rigging(operation="pose_bone", armature_name="Armature",
                bone_name="leftUpperArm", rotation=[0, 0, 120])
blender_rigging(operation="set_bone_keyframe", armature_name="Armature",
                bone_name="leftUpperArm", frame=60)

# Add facial expressions synchronized with poses
blender_shapekeys(operation="set_viseme_weights", target_mesh="Face",
                 viseme_weights={"ee": 1.0}, frame=60)  # Happy mouth

# Set smooth interpolation for natural movement
blender_animation(operation="set_interpolation", object_name="Armature",
                  interpolation="BEZIER")

# Bake animation for export
blender_animation(operation="bake_action", object_name="Armature",
                  start_frame=1, end_frame=120)

# === PHASE 7: FINAL EXPORT VALIDATION ===

# Final validation check before export
blender_export_presets(operation="validate_export_preset",
                      target_objects=["Body", "Armature"], platform="VRCHAT")

# Export with VRChat-optimized settings
blender_export_presets(operation="export_with_preset",
                      target_objects=["Body", "Armature"], platform="VRCHAT",
                      output_path="//exports/avatar_complete_VRC.fbx",
                      include_materials=True, apply_modifiers=True)

# === BONUS: HYBRID ENVIRONMENT CREATION ===

# Import Gaussian Splat environment (if available)
blender_splatting(operation="import_gs", file_path="environment.ply",
                  setup_proxy=True)

# Generate collision mesh for physical interaction
blender_splatting(operation="generate_collision_mesh", density_threshold=0.1)

# Export hybrid environment for Resonite
blender_splatting(operation="export_for_resonite", target_format="SPZ",
                  include_collision=True)
```

# Blender-MCP Tool Reference

This document provides detailed documentation for all **32 portmanteau tools** available in the Blender-MCP server. Each tool supports multiple operations via the `operation` parameter.

## Table of Contents
- [Animation & Motion](#animation--motion)
- [Rigging & Bones](#rigging--bones)
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

### `blender_rigging` (8 operations)

Armature creation and bone animation for VRM/humanoid models.

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
# 1. Import VRM avatar
blender_import(operation="import_gltf", filepath="avatar.vrm")

# 2. Discover bones
blender_rigging(operation="list_bones", armature_name="Armature")
# Returns: hips, spine, chest, neck, head, leftUpperArm, leftLowerArm, ...

# 3. Discover facial expressions
blender_animation(operation="list_shape_keys", object_name="Face")
# Returns: happy, sad, angry, blink, ...

# 4. Create animation at frame 1 (neutral)
blender_animation(operation="set_frame_range", start_frame=1, end_frame=60)

# 5. Set initial pose
blender_rigging(operation="pose_bone", armature_name="Armature",
                bone_name="leftUpperArm", rotation=[0, 0, 0])
blender_rigging(operation="set_bone_keyframe", armature_name="Armature",
                bone_name="leftUpperArm", frame=1)

# 6. Set wave pose at frame 30
blender_rigging(operation="pose_bone", armature_name="Armature",
                bone_name="leftUpperArm", rotation=[0, 0, 120])
blender_rigging(operation="set_bone_keyframe", armature_name="Armature",
                bone_name="leftUpperArm", frame=30)

# 7. Add happy expression at frame 30
blender_animation(operation="set_shape_key", object_name="Face",
                  shape_key_name="happy", value=1.0)
blender_animation(operation="keyframe_shape_key", object_name="Face",
                  shape_key_name="happy", frame=30)

# 8. Set smooth interpolation
blender_animation(operation="set_interpolation", object_name="Armature",
                  interpolation="BEZIER")

# 9. Bake for export
blender_animation(operation="bake_action", object_name="Armature",
                  start_frame=1, end_frame=60)

# 10. Export for VRChat
blender_export(operation="export_vrchat", output_path="avatar_animated.fbx")
```

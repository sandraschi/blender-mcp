---
name: blender-mcp
description: Build, edit, light, animate, render and export Blender 3D scenes via the blender-mcp FastMCP server (agent path) or the local webapp dashboard (human path). Use for any Blender task — primitives, furniture, PBR materials, lighting, Cycles/EEVEE rendering, rigging, keyframe/NLA/shape-key animation, physics, geometry nodes, sculpt, grease pencil, VSE video editing, Gaussian splats, AI mesh generation, VRChat/Resonite/Unity/Unreal/VRM export, and autonomous multi-step 3D workflows.
---

# Blender MCP Skill

Blender 3D automation via the `blender-mcp` FastMCP server + React webapp.
Covers modeling, materials, lighting, animation, rendering, scene management,
physics, video editing, AI generation, and game/VR export.

Repo: `D:\Dev\repos\blender-mcp` — server `src/blender_mcp/`, webapp `webapp/frontend/src/`,
docs `docs/`, addon `addon/blender_bridge_addon.py`, skills `skills/blender-expert/SKILL.md`.

## 1. Who are you? Route first (agent vs human)

There are exactly two consumption paths. Pick one and stay in it.

### Path A — You are an AI AGENT (MCP tools)

You drive Blender through MCP tool calls. The human never touches Blender's UI.
Preferred clients: Claude Desktop, Cursor, VS Code (stdio `uv run blender-mcp --stdio`).

1. Discover: `blender_help(operation="list_tools")` or `blender_help(operation="search", query="...")`.
2. Health: `blender_status(operation="status")` — checks server + Blender executable.
   Deep checks: `system_info`, `health_check`, `performance_monitor`.
3. Build with portmanteau tools (Section 3). Every tool takes `operation=` + params.
4. For vague/creative goals use the AI layer (Section 4), not raw mesh ops.
5. Verify with `blender_render(operation="render_preview" | "screenshot_viewport")`
   and `blender_validation(operation="validate_avatar")` before export.

Never tell the user to click inside Blender unless they explicitly asked for
live-viewport mode. Default to headless — it just works.

### Path B — You are helping a HUMAN using the webapp

The webapp at `http://localhost:10848` (API `http://127.0.0.1:10849`) is itself
an MCP client — every button calls the same tools from Path A via `POST /tool`.
Guide the human to the right page (Section 5), not to raw tool JSON.

- Start: `.\\start.ps1` (from repo root). Flags: `-Headless`, `-BackendOnly`, `-NoBrowser`.
- Chat page (`/chat`) = `ai_chat` tool with `skills/blender-expert/SKILL.md` as system context.
- Construct (`/construct`) + AI Constructor (`/constructor`) = `construct_object` /
  `manage_object_construction` + `generate_blender_script`.
- Agent Tools (`/agent-tools`) = `agentic_blender_workflow` + `intelligent_3d_processing`.
- Script Console (`/scripts`) = `script_execute(code)` — runs `bpy` in Blender.
- Settings → LLM = Ollama / LM Studio / Cloud endpoint for script generation.
  No LLM is needed for direct mesh/material/scene ops.

If the human says "the dashboard is offline": check backend health
`GET /api/v1/health`, then `GET /api/capabilities` (tool count), then
`GET /api/v1/diagnostics` (CPU/RAM + bridge status). Port conflict on
10848/10849 → re-run `start.ps1` (it clears ports first).

## 2. Execution modes (how tools reach Blender)

| Mode | What happens | When to use |
|------|--------------|-------------|
| **Headless (default)** | Server spawns `blender --background --python script.py` per call | All batch work, CI, export, render, VSE, geonodes, most mesh/material ops. No UI needed. |
| **Live session (bridge addon)** | Running Blender GUI + `blender_bridge_addon.py` polls `GET /api/v1/blender/pending`, executes, posts to `/api/v1/blender/result` | Human wants to WATCH the build; viewport screenshots; sculpt with live feedback. |
| **Per-tool override** | `prefer_session=False` forces headless even if bridge is connected | Batch jobs, deterministic renders. |

- Blender is **never bundled**. Install from blender.org (3.0+). Override detection with `BLENDER_EXECUTABLE`.
- Bridge setup: start HTTP MCP → `blender_session(operation="start")` → in Blender
  Edit → Preferences → Add-ons → Install `blender_bridge_addon.py` → enable
  **Blender MCP Bridge** → Scene properties → Start Bridge. Then
  `blender_render(operation="screenshot_viewport")` works.
- Each `script_execute` in headless mode is a fresh Blender process — no
  persistent selection/viewport state. For multi-step stateful work use
  `blender_workflow(operation="execute", steps=[...])` (single execution context).

## 3. Tool catalog (agent path — authoritative)

All tools return `{success, message, ...data}`. Failures carry `error`.
Portmanteau pattern: one tool + `operation=` enum, never 40 separate tools.

**Help / status / config (always start here):**
- `blender_help` — `list_tools | search_tools | tool_info | categories | help`
- `blender_status` — `status | system_info | health_check | performance_monitor`
- `config_get | config_set`, `blender_logs | blender_log_stats`
- `list_local_models` (Ollama + LM Studio discovery only — no pull/remove via MCP)
- `generate_blender_script(prompt, model, ollama_url)` — LLM → `bpy` code
- `script_execute(code)` — run `bpy` in Blender (headless or bridge)

**Scene / transform / selection:**
- `blender_scene` (12 ops) — `create_scene | list_scenes | clear_scene | set_active_scene | link_object_to_scene | create_collection | add_to_collection | set_active_collection | set_view_layer | setup_lighting | setup_camera | set_render_settings`
- `blender_transform` (8) — `set_location | set_rotation (deg) | set_scale | translate | rotate | scale | apply_transform | reset_transform`
- `blender_selection` (6) — `select_objects | select_by_type | select_by_material | select_all | select_none | invert_selection`
- `blender_session` — `start | open | save | merge` (`.blend` file lifecycle)

**Modeling:**
- `blender_mesh` (9) — `create_cube | create_sphere | create_cylinder | create_cone | create_plane | create_torus | create_monkey | duplicate_object | delete_object`. Params: `name, location[x,y,z], rotation[deg], scale`.
- `blender_furniture` (9) — `create_chair | create_table | create_bed | create_sofa | create_cabinet | create_desk | create_shelf | create_stool` (+ `position, rotation, scale`).
- `blender_modifiers` (12) — `add_subsurf | add_bevel | add_mirror | add_solidify | add_array | add_boolean | add_decimate | add_displace | add_wave | remove_modifier | apply_modifier | get_modifiers`
- `blender_sculpt` — remesh, dyntopo, detail flood fill
- `blender_geometry_nodes` — node-group create, set inputs, execute
- `blender_particles` (7) — `create_particle_system | create_hair_particles | create_fire_effect | create_water_effect | control_emission | bake_particles | set_particle_physics`

**Materials / textures / UV / shaders:**
- `blender_materials` (7) — `create_fabric | create_metal | create_wood | create_glass | create_ceramic | assign_to_object | create_from_preset`
- `blender_textures` (7) — `create_noise | create_voronoi | create_musgrave | create_wave | create_checker | create_brick | create_gradient`
- `blender_uv` (5) — `unwrap | smart_project | cube_project | cylinder_project | reset_uvs`
- `blender_shader` — shader-node graph ops; `blender_materials_baking` (3) — `bake_toon_to_pbr | consolidate_materials | convert_vrm_shader_to_pbr`
- `blender_atlasing` (4) — `create_material_atlas | merge_texture_atlas | optimize_draw_calls | get_atlas_uv_layout`

**Lighting / camera / render / compositor:**
- `blender_lighting` (7) — `create_sun | create_point | create_spot | create_area | setup_three_point | setup_hdri | adjust_light`
- `blender_camera` (3) — `create_camera | set_active_camera | set_camera_lens`
- `blender_render` (4+) — `render_preview | render_turntable | render_animation | render_current_frame | screenshot_viewport (bridge only) | setup_camera | set_resolution`. Engines: CYCLES / EEVEE / Workbench.
- `blender_compositor` — render layers, compositor nodes, post-processing

**Animation / rigging / face:**
- `blender_animation` (21) — keyframes (`set_keyframe | animate_location | animate_rotation | animate_scale`), `set_frame_range | play_animation | clear_animation`, shape-key ops (`list_shape_keys | set_shape_key | keyframe_shape_key | create_shape_key`), actions (`list_actions | create_action | set_active_action | push_to_nla`), `set_interpolation (CONSTANT/LINEAR/BEZIER/BOUNCE/ELASTIC) | set_easing | add_constraint | add_bone_constraint | bake_action | bake_all_actions`
- `blender_rigging` (12) — `create_armature | add_bone | create_bone_ik | create_basic_rig | list_bones | pose_bone | set_bone_keyframe | reset_pose | transfer_weights (body→clothing) | manage_vertex_groups | humanoid_mapping (VRCHAT/UNITY preset)`
- `blender_shapekeys` (5) — `create_viseme_shapekeys (A/I/U/E/O, VRM) | create_blink_shapekey | set_viseme_weights | create_facial_expression | analyze_shapekeys`
- `blender_vrm_metadata` (5) — `set_first_person_offset | setup_blink_viseme_mappings | configure_spring_bones | set_vrm_look_at | export_vrm_metadata`
- `blender_physics` (8) — `enable_rigid_body | enable_cloth | enable_soft_body | enable_fluid | bake_physics | add_force_field | set_rigid_body_constraint | configure_world`

**2D / video:**
- `blender_grease_pencil` — strokes, layers, convert-to-mesh; 2D animation tools
- `blender_vse` (20) — strips (`add_movie | add_sound | add_image_sequence | add_scene | add_color | add_text | add_effect`), edit (`delete_strip | cut_strip | trim_strip | move_strip | mute_strip | lock_strip`), props (`set_speed | set_blend | set_transform`), info (`list_strips | get_timeline_info`), output (`render_video H264/H265/THEORA/AV1 | clear_vse`)

**Assets / import / export / VR pipeline:**
- `manage_object_repo` — `save | load | search | list_objects`. Store: `~/.blender-mcp/repository/` (`.blend` + `metadata.json`). Search filters: `query, category, tags, min_quality (1-10)`.
- `manage_blender_addons` — `search | info | install_known | install_url | list_installed | enable | disable`. Known: `gaussian_splat, 3dgs_blender, openscatter, asset_bridge, blender_gis, blender_tools_collection`.
- `blender_download` — `download | info` (then optional import OBJ/FBX/GLB/STL/PLY). Sources: Poly Haven, Sketchfab (`SKETCHFAB_API_TOKEN`), any URL.
- `blender_splatting` (4) — `import_gs (.ply/.spz + proxy) | crop_and_clean | generate_collision_mesh | export_for_resonite`. `worldlabs` op auto-installs the 3DGS addon if missing.
- `blender_import` — `import_[fbx|obj|gltf|stl|ply|vrm|dae] | link_asset`
- `blender_export` — FBX/OBJ/glTF-GLB/VRM/STL/PLY/COLLADA (+ `export_unity | export_vrchat` shortcuts)
- `blender_export_presets` (4) — `export_with_preset | validate_export_preset | get_platform_presets | create_custom_preset`. Presets: `VRCHAT` (FBX, 70k tris, 256 bones, 8 mats), `RESONITE` (glTF, 512 bones), `UNITY`, `LEGACY_VRCHAT`.
- `blender_validation` — `validate_avatar (VRCHAT/RESOINTE/UNITY limits) | spawn_benny (persistence smoke test)`
- `export_for_mcp_handoff(asset_id, target_mcp=vrchat|resonite|unity|unreal)` — cross-fleet handoff with optimization preset + integration commands
- `blender_batch` — resize/convert/watermark/export over `pattern=*.png`
- `blender_workflow(operation="execute", steps=[{tool, operation, ...params}])` — macro: furnished room in one call

## 4. LLM + AI layer (both paths)

| Capability | Agent tool | Webapp page | Notes |
|------------|-----------|-------------|-------|
| Script generation (local LLM) | `generate_blender_script(prompt, model, ollama_url)` | Construct, AI Constructor, Script Console | Needs ONE inference path: Ollama (`OLLAMA_HOST`, default `http://127.0.0.1:11434`) or LM Studio or Cloud/vLLM (`OPENAI_API_BASE/KEY`). Models never bundled. |
| Natural-language build | `construct_object(description, complexity=simple\|standard\|complex, style_preset=realistic\|stylized\|lowpoly\|scifi)` | Construct | LLM writes `bpy`, security pipeline validates (AST + score 0-100), executes, iterates (`max_iterations`, default 3). |
| Modify existing | `manage_object_construction(operation=construct\|modify, ...)` | Construct | `modify` takes `object_name + modification_description`. |
| Text/image-to-3D mesh | `blender_ai_generate(operation, prompt, backend=tripo\|rodin\|hunyuan)` | AI Constructor, Mesh page | External backends, keys `RODIN_*, TRIPO_*` (see `utils/ai_mesh_backends.py`). Returns mesh URL → import. |
| Vision refine | `vision_refine` tools | AI Constructor | Render → vision model critiques → re-generate loop. |
| Chat assistant | `ai_chat(message)` — SKILL.md as system ctx, `ctx.sample()` else Ollama fallback | Chat (`/chat`) | Quick Q&A, next-step suggestions. |
| Conversational assistant (SEP-1577) | `conversational_blender_assistant(user_query, context_level=basic\|comprehensive\|detailed)` | Chat | Probes capabilities before answering; graceful fallback without sampling. |
| Autonomous workflow (SEP-1577) | `agentic_blender_workflow(workflow_prompt, available_operations?, max_steps=5)` | Agent Tools | Client LLM loops over capability probes until plan is done. Requires sampling-capable client (Claude Desktop, Antigravity). Without it → error, fall back to `blender_workflow(execute)`. |
| Batch pipeline planner (SEP-1577) | `intelligent_3d_processing(scenes, processing_goal, available_operations, processing_strategy=adaptive\|parallel\|sequential)` | Agent Tools | Designs per-scene pipeline; does not execute — you execute the returned plan. |

Complexity guide: `simple` = primitives/transforms (<5s); `standard` = modifiers/materials/basic anim (<30s); `complex` = rigging/physics/detailed PBR (slower, batch it).
Style presets bias proportions/material palettes, they do not change topology algorithms.

## 5. Webapp map (human path — 22 pages)

`App.tsx` sidebar groups. Every page calls MCP tools over `POST /tool`.

- **Creation:** Dashboard (`/`, KPIs + launch), Scene Explorer (`/scene` — hierarchy, collections), Construct (`/construct` — NL build), AI Constructor (`/constructor` — backends + vision refine), Material Store (`/materials`), Mesh/Collider/Splat (`/mesh`), Repository (`/repository` — save/load/search depot), Addon Manager (`/addons`).
- **Agent Lab:** Agent Tools (`/agent-tools` — run agentic + batch planners, inspect steps/tool-calls).
- **AI Assistant:** Chat (`/chat`).
- **2D Animation:** Grease Pencil (`/grease-pencil`), 2D Animation (`/animation-2d`), Storyboard (`/storyboard`).
- **Pipeline:** VR Pipeline (`/vr` — validate → bake → atlas → metadata → shapekeys → export), Script Console (`/scripts`), Video Editor (`/video` — VSE timeline + `render_video`).
- **System:** Logs (`/logs` — `GET /api/v1/logs?level&limit&since_minutes&search`), Help & Reference (`/help`), Skills (`/skills` — `GET /api/skills`), System Status (`/status` — diagnostics), App Hub (`/apps`), Settings (`/settings` — LLM providers, Blender path, ports).

REST beyond `/tool`: `GET /health, /api/health, /api/status, /api/v1/status, /api/v1/health, /api/capabilities, /api/v1/diagnostics, /api/v1/logs, /api/skills{,/name}, POST /api/v1/blender/{exec,pending,result}, POST /api/v1/fleet/launch, GET /metrics` (Prometheus).

## 6. Documentation map (read before claiming gaps)

| Doc | Use it for |
|-----|-----------|
| `README.md` | 2-min install, headless-vs-live, hands-in/out, companions |
| `INSTALL.md` | All install paths (mcpb drag-in, npx, manual stdio, dev), bridge addon, webapp, LLM setup, troubleshooting table |
| `docs/CONFIGURATION.md` | Env vars (`BLENDER_EXECUTABLE`, `MCP_PORT=10849`, `OLLAMA_HOST`, `OPENAI_*`, `SKETCHFAB_API_TOKEN`, log/metrics toggles) |
| `docs/FEATURES.md` | Capability narrative (AI construction, VR pipeline, repo, batch/macro) |
| `docs/API.md` | MCP + HTTP + Python API signatures and error shapes |
| `docs/USAGE.md` | CLI, construction examples, repo/batch/material, VR workflow, best practices |
| `docs/ARCHITECTURE.md` | FastMCP layer, validation pipeline, process mgmt, caching/pooling, repo/export design |
| `docs/PRD.md` | Vision, personas (game dev, arch Viz, VR creator, artist, educator), roadmap |
| `docs/EXAMPLES.md` | Copy-paste scene/material/anim/physics/render/export snippets |
| `docs/TROUBLESHOOTING.md` | Blender-not-found, ports, LLM-missing, bridge issues |
| `docs/blender/TOOL_REFERENCE.md` | **Authoritative 41-tool op table** with VRM/VRChat examples — consult before inventing an operation name |
| `docs/blender/{ASSET_REPOSITORIES,BLENDERKIT_GUIDE,FREE_ASSETS_GUIDE,GUI_MODE,VSE_GUIDE}` | Asset sources, GUI-mode specifics, VSE deep dive |
| `docs/TOOLS_AND_REALTIME.md` | What is/isn't realtime; why CLI-only today; bridge addons (Blender Remote, b3dnet) |
| `docs/{ARCHITECTURE,MONITORING,DOCKER,DEVELOPMENT,ROADMAP}` + `DOCUMENTATION_INDEX.md` | Ops, observability (Prometheus/Grafana/Loki), dev recipes, roadmap, full index |

MCP resources (for sampling clients): `blender://api/{identifier}` (bpy doc excerpt),
`blender://scripts/{category}` + `blender://scripts/{category}/{script_name}`
(categories: robots, furniture, rooms, vehicles).

## 7. Blender domain knowledge (apply on every task)

**Data model:** Object (container: location/rotation/scale, parent, constraints) vs
Object Data / Mesh (vertices/edges/faces — shared between objects) vs Material
(slots on object, node tree on data). Collections group objects; View Layers
control visibility/renderability. Always `apply_transform` before export/physics,
else scale bakes wrong. Z-up right-handed, default unit meters — Unity/VRChat
expect 1.0 scale, legacy pipelines 0.01 (see `LEGACY_VRCHAT` preset).

**Modeling:** start primitive → Edit Mode ops (extrude, inset, bevel, loop cut,
knife, bridge, spin/screw) → modifiers (Subsurf → Mirror → Solidify → Array →
Boolean → Decimate, order matters) → `apply_modifier` → cleanup (merge doubles,
recalc normals). Keep quads for deforming meshes; tris OK for static game assets.
`add_decimate` + `optimize_draw_calls` before any VR export.

**Materials (PBR):** Principled BSDF = base color (sRGB 0-1) + metallic (0 dielectric,
1 metal) + roughness (0 mirror, 1 matte) + normal + emission. Procedural textures
(noise/voronoi/musgrave/wave/checker/brick/gradient) feed roughness/bump, not
albedo, for realism. UV first (`smart_project` quick, `unwrap`+pack final), then
bake (`bake_toon_to_pbr`, `consolidate_materials`) to ≤2048 atlases for mobile VR.

**Lighting:** three-point (key area ~1000W + fill + rim) for product shots;
sun (arch Viz, HDRI world for reflections) vs points/spots (interior).
`setup_three_point` is the safe default. Match HDRI rotation to camera azimuth.

**Cameras/render:** set active camera → focal length (24 wide / 50 neutral / 85 portrait)
→ DOF for close-ups → engine: **Cycles** (path-traced, `samples` 128-256 + OpenImageDenoise,
final quality) vs **EEVEE** (rasterized, previews/turntables, 10x faster) vs Workbench
(viewport). Always `set_resolution` + output path/format before `render_animation`;
`render_turntable` (60 frames default) for asset review, `screenshot_viewport` only on bridge.

**Rigging/animation:** armature → bones (naming must match `humanoid_mapping` preset
before Unity/VRChat export) → parent mesh with weights → `transfer_weights` for clothing
→ IK on limbs → keyframes (location/rotation/scale) → interpolation BEZIER for organic,
LINEAR for mechanical → NLA (`push_to_nla`) for layering walk+wave → `bake_action`
before export (bakes constraints). Shape keys drive face (basis + visemes A/I/U/E/O +
blink); keyframe their `value 0-1`. Timeline: `set_frame_range` first, 24/30 fps lock.

**Physics/particles:** rigid body ACTIVE (props) vs PASSIVE (floor); cloth needs
collision object + self-collision for garments; bake (`bake_physics`, `bake_particles`)
to keyframes before render/export or the sim won't travel with the file.

**Geometry Nodes / sculpt:** geonodes for procedural scatter (inputs exposed, then execute);
sculpt with dyntopo for organic, then retopo + decimate — never export raw dyntopo sculpts.

**Grease Pencil / VSE / compositor:** GP strokes live on layers, convert to mesh only
for 3D print/export. VSE channels stack (higher = on top); CROSS/WIPE effects need
overlapping strips; `render_video` needs codec+fps+resolution set together.
Compositor runs after render (denoise → color grade → output).

**Export matrix:** glTF/GLB (web, Resonite, Three.js — keeps PBR+anims), FBX (Unity/Unreal/VRChat —
keeps rig+NLA, needs `apply_modifiers + bake_action`), STL/PLY (3D print, mesh only, check
manifold), USD/ABC (DCC interchange), VRM (avatars — metadata + spring bones + visemes required).
Validate (`validate_export_preset`) BEFORE `export_with_preset`; VRChat fail modes in order:
tris >70k → bones >256 → materials >8 → missing humanoid mapping.

**Gaussian splats:** `.ply/.spz` import creates dense point cloud + hidden proxy box;
`crop_and_clean` floaters, `generate_collision_mesh` for walkable VR, then
`export_for_resonite`. Never try to rig or UV a splat — it is not a mesh.

## 8. Standard recipes (copy the shape, swap nouns)

**A. Red cube on gray floor + sun + preview (smoke test):**
`blender_scene(clear_scene)` → `blender_mesh(create_cube, name=Cube)` →
`blender_mesh(create_plane, name=Floor, scale=[5,5,1])` →
`blender_materials(create_from_preset red → assign_to_object Cube; gray → Floor)` →
`blender_lighting(create_sun)` → `blender_camera(setup_camera)` →
`blender_render(render_preview, resolution 1920x1080, engine=CYCLES)`

**B. Chair + wood + GLB:** `blender_furniture(create_chair)` →
`blender_materials(create_wood oak → assign)` → `blender_uv(smart_project)` →
`blender_export(export, format=glb, path=//exports/chair.glb)`

**C. Bouncing ball:** sphere + plane → `blender_physics(enable_rigid_body ACTIVE ball,
PASSIVE floor, bounce 0.8)` → `set_frame_range 1-100` → `bake_physics` → `render_animation`

**D. Furnished room (one macro):** `blender_workflow(execute, steps=[
scene.clear_scene, furniture.create_sofa, furniture.create_table,
lighting.setup_three_point, camera.setup_camera])`

**E. VRM avatar end-to-end:** import → `validate_avatar(VRCHAT)` →
`convert_vrm_shader_to_pbr + consolidate_materials + create_material_atlas` →
`set_first_person_offset + setup_blink_viseme_mappings + configure_spring_bones + set_vrm_look_at` →
`create_viseme_shapekeys + create_blink_shapekey + analyze_shapekeys` →
`humanoid_mapping(VRCHAT) [+ transfer_weights for clothes]` → animate + `bake_action` →
`validate_export_preset` → `export_with_preset(VRCHAT)`

**F. VSE cut:** `add_movie(clip1,ch1) + add_movie(clip2,ch2)` →
`add_effect(CROSS)` → `add_sound(bgm,ch5)` → `trim/move/mute` →
`list_strips + get_timeline_info` → `render_video(H264, 1080p30)`

**G. Splat room:** `blender_splatting(import_gs room_scan.ply)` →
`crop_and_clean` → `generate_collision_mesh` → `export_for_resonite`

## 9. Safety, errors, troubleshooting

- Generated `bpy` passes AST parse + security score + whitelist before execution.
  Score < threshold → `SecurityError`, no execution. Never bypass by hand-crafting
  `script_execute` with `import os/socket/subprocess` — it will be rejected and logged.
- Common failures: `Blender not found` → set `BLENDER_EXECUTABLE`; `sampling unavailable` →
  use `blender_workflow(execute)` instead of agentic tools; `screenshot_viewport` empty →
  bridge not running (headless has no viewport); script-gen fails → no LLM configured
  (Settings → LLM or `OLLAMA_HOST`); ports busy → re-run `start.ps1`; `uvx mcpb` fails →
  expected, use `npx @anthropic-ai/mcpb`.
- Destructive ops (`clear_scene`, `delete_object`, `clear_vse`, `apply_modifier`)
  are irreversible — confirm scene/object names first via `scene_get_hierarchy` or
  `select_by_type`. Save milestones with `manage_object_repo(save, quality_rating)`.
- Fleet companions (optional, standalone-safe): qcad-mcp (DXF→3D), freecad-mcp (STEP import),
  resonite-mcp (GLTF→VR), speech-mcp (render-complete readout). Never require them.

## 10. Config quick reference

`BLENDER_EXECUTABLE` (or legacy `BLENDER_PATH`), `MCP_TRANSPORT=stdio|http|sse`,
`MCP_HOST=127.0.0.1`, `MCP_PORT=10849`, `MCP_PATH=/mcp`, `OLLAMA_HOST`,
`OPENAI_API_BASE/KEY`, `SKETCHFAB_API_TOKEN`, `RODIN_*/TRIPO_*`,
`BLENDER_MCP_LOG_LEVEL/LOG_FORMAT/METRICS_ENABLED`, `PROMETHEUS_PORT=9091`,
`BLENDER_BRIDGE_HOST/PORT (10850)`. Dashboard `10848`, API `10849`.
Health: `uv run blender-mcp --check-blender`, `--list-tools`, `--show-config`.

# VRM Pipeline (blender-mcp)

blender-mcp is the **3D post-processor** for VRM in the fleet: import, inspect, metadata, re-export, and conversion hub (including MMD PMX sources).

## Role in avatar chain

```text
avatar-mcp stages .vrm
    → blender-mcp blender_validate / reexport (headless script_execute)
    → cleaned .vrm back to avatar-mcp output/
```

avatar-mcp calls blender-mcp via `BLENDER_MCP_URL` (default `http://127.0.0.1:10849`).

## VRM capabilities

See `docs/blender/TOOL_REFERENCE.md` for:

- VRM import/export addon operations
- `blender_vrm_metadata` / shape keys / rigging
- glTF/VRM/FBX export for downstream targets

## MMD conversion

MMD models (PMX) and motions (VMD) are **not** native to avatar-mcp. Typical path:

1. Import PMX in Blender (MMD tools community addon)
2. Fix scale, materials, bone names
3. Export VRM (VRM addon for Blender)
4. Stage via avatar-mcp `hub_stage_file`

VMD → animation: retarget/bake in Blender; future iOS dance player consumes baked clips or VMD with retarget layer.

Explainer: `mcp-central-docs/docs/avatars/MMD_EXPLAINER.md`

## Export to Godot (parallel track)

VRM is for social/VTuber runtimes. For **Godot games**:

1. Export **GLB** from Blender (same rig)
2. godot-mcp `godot_import_glb`

godot-mcp does not import VRM directly. See `godot-mcp/docs/AVATARS_AND_VRM.md`.

## Export to Unity / VRChat

Use unity3d-mcp + VRChat SDK after blender-mcp validation. avatar-mcp handles registry and OSC; Unity path is separate from Godot.

## Central docs

- `mcp-central-docs/docs/avatars/FLEET_VRM_PIPELINE.md`
- `mcp-central-docs/integrations/blender/` (add VRM section reference)

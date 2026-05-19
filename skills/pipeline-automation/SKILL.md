---
name: pipeline-automation
description: Automate 3D asset pipelines, including batch optimization, material baking, and exports for platforms like Unity and VRChat.
---

# Pipeline Automation Skill

**Description:** 3D pipeline technical artist skill for batch processing multiple assets with consistent optimization settings. Covers batch rendering, asset pipeline, format conversion, headless batch operations, material baking, and platform-specific export configurations.

## Trigger Phrases

- "Batch optimize all assets for [platform]"
- "Export the entire scene for Unity"
- "Bake materials on all selected objects"
- "Convert all FBX files to GLB"
- "Run headless batch render on all cameras"
- "Set up a render farm job for this scene"
- "Apply LODs to all high-poly meshes"

## Tools

- `intelligent_3d_processing(prompt="...")` — Multi-step batch processing with natural language prompt. Handles decimation, material unlinking, export, and optimization.
- `optimize_3d_scene(target_platform="...", decimation_ratio=0.5)` — Get an optimization plan for a specific platform (Unity, Unreal, VRChat, Web).
- `batch_render(output_path="...", format="PNG", cameras=["..."])` — Batch render all or selected cameras.
- `convert_format(input_path="...", output_format="glb", ...)` — Convert between 3D formats (FBX, GLB, OBJ, STL, BLEND).
- `apply_modifier(modifier_type="decimate", ratio=0.5)` — Apply geometry modifiers in batch.

## Workflow

1. **Target identification**: Determine target platform — Unity (Prefab + FBX/GLB), Unreal (FBX + LODs), VRChat (GLB + optimized mesh), Web (GLB with compression).
2. **Plan generation**: Use `optimize_3d_scene(target_platform="...")` to get per-platform optimization guidelines (poly count budgets, texture sizes, material limits).
3. **Batch execution**: Use `intelligent_3d_processing(prompt="...")` to execute decimations, material unlinking, and export in one pass. Specify the platform's format requirements.
4. **Verification**: Check export paths and file formats match platform specs. Validate poly counts and texture references.

## Examples

### Batch Optimization
"Optimize all meshes in the scene for VRChat and export as GLB." → `optimize_3d_scene(target_platform="vrchat")` → `intelligent_3d_processing(prompt="Batch decimate to 50% and export as GLB for VRChat")`

### Render Farm
"Batch render all cameras to PNG at 4K." → `batch_render(cameras=["all"], output_path="//render/exports", format="PNG", resolution="4K")`

### Format Pipeline
"Convert all FBX props to GLB for web." → `convert_format(input_pattern="*.fbx", output_format="glb")`

---
name: pipeline-automation
description: Automate 3D asset pipelines, including batch optimization, material baking, and exports for platforms like Unity and VRChat.
---

# Pipeline Automation Skill

You are a 3D pipeline technical artist. This skill enables you to process multiple 3D assets with consistent optimization settings.

## Instructions

1. **Targeting**: Determine the target platform (e.g., Unity, Unreal, VRChat).
2. **Optimization**: Use the `optimize-3d-scene` prompt to get a plan.
3. **Execution**: Use the `intelligent_3d_processing` tool to batch execute decimations and material unlinking.
4. **Export**: Verify the export path and file format (GLB/FBX).

## Examples

### Batch Optimization
"Optimize all meshes in the scene for VRChat and export as GLB."
-> Load `pipeline-automation` skill.
-> Invoke `optimize_3d_scene(target_platform="vrchat")` to get guidelines.
-> Execute `intelligent_3d_processing(prompt="Batch decimate and export as GLB for VRChat")`.

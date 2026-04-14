---
name: autonomous-modeling
description: Use this skill to autonomously design and model complex 3D objects in Blender. Perfect for generating chassis, robots, and environment props from natural language.
---

# Autonomous Modeling Skill

You are an expert Blender 3D modeler capable of autonomous orchestration. This skill empowers you to use the `agentic_blender_workflow` tool to plan and execute multi-step modeling tasks.

## Instructions

1. **Discovery**: Always start by calling the `blender_status` or `blender_list_tools` if you are unsure of the current scene state.
2. **Planning**: Use `agentic_blender_workflow` to create a high-level plan.
3. **Refinement**: If the initial model is too simple, use the `intelligent_3d_processing` tool to refine materials or add modifiers.
4. **Validation**: Check for mesh integrity before finalization.

## Examples

### Creating a Sci-Fi Robot
"I need a steampunk robot with exposed gears and Copper plates."
-> Load `autonomous-modeling` skill.
-> Invoke `agentic_blender_workflow(workflow_prompt="steampunk robot with gears and copper plates")`.

### Environment Props
"Create a modular scifi wall panel with indented vents."
-> Load `autonomous-modeling` skill.
-> Invoke `agentic_blender_workflow(workflow_prompt="scifi wall panel with vents")`.

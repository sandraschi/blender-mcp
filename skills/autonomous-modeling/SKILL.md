---
name: autonomous-modeling
description: Use this skill to autonomously design and model complex 3D objects in Blender. Perfect for generating chassis, robots, and environment props from natural language.
---

# Autonomous Modeling Skill

**Description:** Expert Blender 3D modeler for autonomous procedural generation, parametric modeling, topology optimization, and script-based creation. Covers multi-step modeling workflows, procedural generation pipelines, and geometry node-based asset creation.

## Trigger Phrases

- "Model a [object] with [features]"
- "Generate a procedural [part/asset]"
- "Create a parametric [object] with adjustable parameters"
- "Design a [style] [object] with detailed [elements]"
- "Optimize topology on this mesh"
- "Generate a low-poly version of [object]"
- "Create a modular kit of [theme] parts"

## Tools

- `agentic_blender_workflow(workflow_prompt="...")` — Autonomous multi-step modeling via natural language. Plans and executes: create, modify, texture, validate.
- `intelligent_3d_processing(prompt="...", context="...")` — Refine existing models: add modifiers, adjust materials, fix geometry issues.
- `blender_status()` — Current scene state: object count, active object, render engine, viewport mode.
- `blender_list_tools()` — Available Blender MCP capabilities and their parameters.
- `add_mesh(type="...", location=[...], size=...)` — Add primitive mesh objects.
- `apply_modifier(modifier_type="...", ...)` — Apply modifiers (subdivision, mirror, boolean, bevel, solidify).
- `set_material(object_name="...", material="...", color=[...])` — Assign or create materials.

## Workflow

1. **Discovery**: Call `blender_status()` to assess current scene state. Use `blender_list_tools()` if unsure of available operations.
2. **Planning**: Use `agentic_blender_workflow(workflow_prompt="...")` to generate a high-level modeling plan with step breakdown.
3. **Execution**: Create base geometry with `add_mesh()`, refine with `apply_modifier()`, texture with `set_material()`.
4. **Refinement**: If the initial model is too simple, use `intelligent_3d_processing(prompt="...")` for detail pass — add edge loops, bevels, or extruded details.
5. **Validation**: Check for mesh integrity (non-manifold edges, zero-area faces, ngons) before finalization. Use Blender's 3D print toolbox if available.

## Examples

### Creating a Sci-Fi Robot
"I need a steampunk robot with exposed gears and copper plates." → `agentic_blender_workflow(workflow_prompt="steampunk robot with gears and copper plates")` → `intelligent_3d_processing(prompt="Add gear details to joints and copper material finish")`

### Modular Environment Kit
"Create a modular sci-fi wall panel with indented vents, 4 units wide." → `agentic_blender_workflow(workflow_prompt="modular scifi wall panel 4u with vents")` → verify repeatability via array modifier

### Parametric Object
"Generate a parametric gear with adjustable teeth count and radius." → `add_mesh(type="cylinder")` → `apply_modifier("geometry_nodes", node_group="parametric_gear")`

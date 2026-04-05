"""
Agentic Workflow Tools for Blender MCP

FastMCP 3.1 multi-step SEP-1577 sampling for autonomous 3D creation workflows.
Each agentic tool borrows the client LLM (via ctx.sample) across multiple
tool-call loops until the goal is achieved or max_steps is exhausted.
"""

from __future__ import annotations

import logging
from typing import Any

from .app import get_app

try:
    from fastmcp.server.context import Context
except ImportError:
    Context = Any  # type: ignore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Capability-probe tools (passed to ctx.sample so the LLM can query them)
# ---------------------------------------------------------------------------


def get_blender_modeling_capabilities() -> str:
    """Return available 3D modeling operations. Call to see what mesh/object ops are supported."""
    return (
        "Modeling: add_primitive (cube, sphere, cylinder, plane, cone, torus), "
        "edit_mesh (extrude, inset, bevel, loop_cut, dissolve, merge), "
        "apply_modifier (subdivision, mirror, array, solidify, boolean, decimate, shrinkwrap), "
        "transform (move, rotate, scale, snap), set_origin, join_objects, separate_mesh, "
        "knife_cut, bridge_edge_loops, spin, screw, skin_modifier."
    )


def get_blender_materials_capabilities() -> str:
    """Return available material and texture operations. Call to see shader/PBR options."""
    return (
        "Materials: create_material (PBR, emission, glass, toon), set_base_color (hex/rgb), "
        "set_metallic, set_roughness, set_emission_strength, add_texture (image, procedural, "
        "noise, voronoi, musgrave, gradient), UV_unwrap (smart_project, lightmap_pack, "
        "follow_active_quads), bake_texture (diffuse, normal, ao, roughness), "
        "node_group, material_slots, assign_material."
    )


def get_blender_animation_capabilities() -> str:
    """Return available animation and rigging operations. Call to inspect keyframe/armature ops."""
    return (
        "Animation: set_keyframe (location, rotation, scale, custom_prop), "
        "insert_keyframe_range, create_action, NLA_push_down, set_interpolation "
        "(linear, bezier, constant, ease_in, ease_out), "
        "Rigging: add_armature, add_bone, parent_to_armature, weight_paint (vertex_group), "
        "IK_constraint, copy_rotation, track_to, follow_path, "
        "shape_keys (basis, driven), driver (expression, variable)."
    )


def get_blender_scene_capabilities() -> str:
    """Return available scene, lighting, camera and render operations."""
    return (
        "Scene: add_collection, move_to_collection, set_visibility (viewport/render), "
        "link_object, instance_collection, "
        "Lighting: add_light (point, sun, spot, area, hemi), set_light_energy, set_light_color, "
        "HDRI_world_setup, "
        "Camera: add_camera, set_focal_length, set_dof, camera_track_to, "
        "Render: set_render_engine (cycles, eevee, workbench), set_resolution, "
        "set_samples, render_image, render_animation, set_output_path, set_file_format."
    )


def get_blender_io_capabilities() -> str:
    """Return available import/export and cross-MCP pipeline operations."""
    return (
        "Import: import_fbx, import_obj, import_gltf, import_stl, import_dae, import_ply, "
        "Export: export_fbx, export_obj, export_gltf (static/animated), export_stl, export_vrm, "
        "Cross-MCP: export_for_vrchat (avatar_sdk), export_for_resonite, "
        "export_for_unity (prefab), export_for_unreal (fbx+lod), "
        "Repository: save_asset, load_asset, version_asset, list_assets."
    )


# ---------------------------------------------------------------------------
# SEP-1577 helper: one multi-step sampling loop
# ---------------------------------------------------------------------------

_CAPABILITY_TOOLS = [
    get_blender_modeling_capabilities,
    get_blender_materials_capabilities,
    get_blender_animation_capabilities,
    get_blender_scene_capabilities,
    get_blender_io_capabilities,
]


async def _run_sep1577_loop(
    ctx: Context,
    user_message: str,
    system_prompt: str,
    max_steps: int,
    max_tokens: int = 2000,
    temperature: float = 0.3,
) -> dict[str, Any]:
    """
    Core SEP-1577 multi-step loop.

    The client LLM is invoked with the full capability toolset.  It can call
    any capability tool zero or more times per step.  The loop continues until:
      - The LLM produces a final text response (no pending tool calls), OR
      - max_steps is exhausted.

    Returns a dict with 'output' (final text), 'steps' (int), and
    'tool_calls' (list of {tool, result} dicts from all steps).
    """
    messages: list[Any] = [user_message]
    all_tool_calls: list[dict[str, Any]] = []
    step = 0

    while step < max_steps:
        step += 1
        result = await ctx.sample(
            messages=messages,
            system_prompt=system_prompt,
            tools=_CAPABILITY_TOOLS,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Accumulate tool call history from this step
        if hasattr(result, "tool_calls") and result.tool_calls:
            for tc in result.tool_calls:
                all_tool_calls.append(
                    {
                        "step": step,
                        "tool": getattr(tc, "name", str(tc)),
                        "result": getattr(tc, "result", None),
                    }
                )

        # Check if sampling has produced a final text response (no more tool calls)
        final_text = getattr(result, "text", None) or getattr(result, "content", "") or ""
        stop_reason = getattr(result, "stop_reason", None)

        # 'end_turn' or 'stop_sequence' means the LLM is done
        if stop_reason in ("end_turn", "stop_sequence") or (
            final_text and not getattr(result, "tool_calls", None)
        ):
            return {
                "output": final_text,
                "steps": step,
                "tool_calls": all_tool_calls,
            }

        # If the LLM produced partial text + tool calls, append to conversation
        # and continue the loop with enriched context
        if final_text:
            messages.append({"role": "assistant", "content": final_text})
        # Inject tool results back as user context for next iteration
        if all_tool_calls:
            tool_summary = "\n".join(
                f"[{tc['tool']}]: {tc['result']}" for tc in all_tool_calls[-5:]
            )
            messages.append({"role": "user", "content": f"Tool results so far:\n{tool_summary}"})

    # Max steps reached — return whatever we have
    return {
        "output": final_text if "final_text" in dir() else "",
        "steps": step,
        "tool_calls": all_tool_calls,
        "warning": f"Reached max_steps={max_steps} without a final stop signal.",
    }


# ---------------------------------------------------------------------------
# Registered agentic tools
# ---------------------------------------------------------------------------


def register_agentic_tools() -> None:
    """Register multi-step SEP-1577 agentic tools with the FastMCP app."""

    app = get_app()

    @app.tool
    async def agentic_blender_workflow(
        workflow_prompt: str,
        available_operations: list[str] | None = None,
        max_steps: int = 5,
        ctx: Context = None,
    ) -> dict[str, Any]:
        """Execute autonomous multi-step Blender workflows via FastMCP 3.1 SEP-1577 sampling.

        The client LLM plans and executes a 3D workflow step-by-step, autonomously
        calling Blender capability probes to inform each decision, looping until
        the goal is achieved or max_steps is exhausted.

        Args:
            workflow_prompt: Natural language description of the 3D workflow goal
            available_operations: Optional list of operation names to constrain the plan
            max_steps: Maximum LLM-tool reasoning loops (default: 5)
            ctx: FastMCP context — injected automatically when client supports sampling

        Returns:
            dict with success, message (final plan), steps taken, and tool_calls log
        """
        if ctx is None:
            return {
                "success": False,
                "error": "Sampling context unavailable",
                "message": (
                    "Client does not support MCP sampling. Use a client with "
                    "sampling.tools capability (e.g. Claude Desktop, Antigravity)."
                ),
            }

        ops_hint = (
            f"Prefer these operations: {', '.join(available_operations)}."
            if available_operations
            else "Use any available Blender operations."
        )

        system_prompt = (
            "You are an expert Blender 3D workflow orchestrator using FastMCP 3.1 SEP-1577. "
            "You have access to capability-probe tools — call them to discover available Blender "
            "operations before planning. Then produce a concrete, ordered step-by-step plan that "
            "precisely maps to real Blender operations. Be specific: name the exact operations, "
            "parameters, and order. Never hallucinate operations — only use what the probes return."
        )
        user_message = f"Workflow goal: {workflow_prompt}\n{ops_hint}"

        try:
            loop_result = await _run_sep1577_loop(
                ctx=ctx,
                user_message=user_message,
                system_prompt=system_prompt,
                max_steps=max_steps,
            )
            return {
                "success": True,
                "operation": "agentic_blender_workflow",
                "message": loop_result["output"],
                "steps_taken": loop_result["steps"],
                "tool_calls": loop_result["tool_calls"],
                "workflow_prompt": workflow_prompt,
                **({} if "warning" not in loop_result else {"warning": loop_result["warning"]}),
            }
        except Exception as e:
            logger.exception("SEP-1577 workflow sampling failed: %s", e)
            return {
                "success": False,
                "error": str(e),
                "message": "Multi-step sampling failed while generating the 3D workflow plan.",
            }

    @app.tool
    async def intelligent_3d_processing(
        scenes: list[dict[str, Any]],
        processing_goal: str,
        available_operations: list[str],
        processing_strategy: str = "adaptive",
        max_steps: int = 5,
        ctx: Context = None,
    ) -> dict[str, Any]:
        """Intelligent batch 3D scene processing via FastMCP 3.1 SEP-1577 multi-step sampling.

        The LLM autonomously queries material, modeling, and IO capabilities to build
        a processing pipeline tailored to each scene's needs.

        Args:
            scenes: List of scene dicts (keys: name, objects, format, etc.)
            processing_goal: What to achieve (e.g. "optimize all scenes for real-time rendering")
            available_operations: Operations the orchestrator may use
            processing_strategy: "adaptive" | "parallel" | "sequential"
            max_steps: Maximum reasoning loops (default: 5)
            ctx: FastMCP context — injected when client supports sampling

        Returns:
            dict with success, message (processing plan), steps taken, and tool_calls log
        """
        if ctx is None:
            return {
                "success": False,
                "error": "Sampling context unavailable",
                "message": "Client does not support MCP sampling.",
            }

        scene_count = len(scenes) if scenes else 0
        scene_names = [s.get("name", f"scene_{i}") for i, s in enumerate((scenes or [])[:5])]

        system_prompt = (
            "You are a 3D pipeline engineer using FastMCP 3.1 SEP-1577. "
            "Call the capability probes to understand what operations are available, "
            "then design a precise processing pipeline for the given batch of scenes. "
            "Output a numbered plan with: operation name, target scene(s), parameters, "
            "and expected outcome. Only use operations confirmed by the probes."
        )
        user_message = (
            f"Processing goal: {processing_goal}\n"
            f"Scenes ({scene_count}): {scene_names}\n"
            f"Allowed operations: {available_operations}\n"
            f"Strategy: {processing_strategy}"
        )

        try:
            loop_result = await _run_sep1577_loop(
                ctx=ctx,
                user_message=user_message,
                system_prompt=system_prompt,
                max_steps=max_steps,
                max_tokens=1800,
            )
            return {
                "success": True,
                "operation": "intelligent_3d_processing",
                "message": loop_result["output"],
                "steps_taken": loop_result["steps"],
                "tool_calls": loop_result["tool_calls"],
                "processing_goal": processing_goal,
                "scene_count": scene_count,
                "processing_strategy": processing_strategy,
                **({} if "warning" not in loop_result else {"warning": loop_result["warning"]}),
            }
        except Exception as e:
            logger.exception("SEP-1577 batch processing sampling failed: %s", e)
            return {
                "success": False,
                "error": str(e),
                "message": "Multi-step sampling failed while generating the processing plan.",
            }

    @app.tool
    async def conversational_blender_assistant(
        user_query: str,
        context_level: str = "comprehensive",
        max_steps: int = 3,
        ctx: Context = None,
    ) -> dict[str, Any]:
        """Conversational Blender assistant with SEP-1577 multi-step sampling.

        The LLM may probe capabilities to give accurate, operation-specific answers
        before responding. Falls back gracefully when sampling is not available.

        Args:
            user_query: Natural language question about Blender operations
            context_level: "basic" | "comprehensive" | "detailed"
            max_steps: Maximum reasoning loops (default: 3 — keeps it snappy)
            ctx: FastMCP context — injected when client supports sampling

        Returns:
            dict with success, message, and next_steps suggestions
        """
        _fallbacks = {
            "basic": "I can help you create 3D content with Blender.",
            "comprehensive": (
                "I'm your Blender 3D assistant. I support modeling, animation, "
                "materials, lighting, rendering, and agentic workflows."
            ),
            "detailed": (
                "Welcome to Blender MCP (FastMCP 3.1). I support: polygon modeling, "
                "procedural geometry (modifiers), PBR materials, Cycles/EEVEE rendering, "
                "rigging, keyframe animation, shape keys, FBX/GLTF/VRM export, and "
                "multi-step agentic 3D workflows via SEP-1577 sampling."
            ),
        }

        if ctx is None:
            return {
                "success": True,
                "operation": "conversational_assistance",
                "message": _fallbacks.get(context_level, _fallbacks["comprehensive"]),
                "user_query": user_query,
                "context_level": context_level,
                "next_steps": [
                    "Use agentic_blender_workflow for complex multi-step goals",
                    "Use modeling/material/animation tools for direct operations",
                    "Use intelligent_3d_processing for batch scene pipelines",
                ],
                "sampling_available": False,
            }

        system_prompt = (
            "You are a helpful, expert Blender 3D assistant. "
            "If the question is about specific operations, probe the relevant capability tool "
            "first so your answer references real available operations. "
            "Keep answers concise. Always suggest 2-3 concrete next steps (tool names or actions)."
        )

        try:
            loop_result = await _run_sep1577_loop(
                ctx=ctx,
                user_message=user_query,
                system_prompt=system_prompt,
                max_steps=max_steps,
                max_tokens=900,
                temperature=0.4,
            )
            return {
                "success": True,
                "operation": "conversational_assistance",
                "message": loop_result["output"],
                "steps_taken": loop_result["steps"],
                "tool_calls": loop_result["tool_calls"],
                "user_query": user_query,
                "context_level": context_level,
                "sampling_available": True,
                "next_steps": [
                    "Use agentic_blender_workflow for complex multi-step goals",
                    "Use modeling/material/animation tools for direct operations",
                    "Use intelligent_3d_processing for batch scene pipelines",
                ],
            }
        except Exception as e:
            logger.exception("Conversational assistant SEP-1577 sampling failed: %s", e)
            return {
                "success": True,  # degrade gracefully to fallback
                "operation": "conversational_assistance",
                "message": _fallbacks.get(context_level, _fallbacks["comprehensive"]),
                "user_query": user_query,
                "context_level": context_level,
                "sampling_error": str(e),
                "next_steps": [
                    "Use agentic_blender_workflow for complex multi-step goals",
                    "Use modeling/material/animation tools for direct operations",
                ],
            }

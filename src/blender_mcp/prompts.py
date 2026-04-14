"""Prompts for Blender MCP.

This module registers FastMCP 3.2.0 prompts to provide the LLM with
structured templates for complex 3D workflows.
"""

from typing import Any

from .app import get_app


def register_prompts() -> None:
    """Register all prompts with the FastMCP application."""
    app = get_app()

    @app.prompt(
        name="optimize-3d-scene",
        description="Optimize a Blender scene for external platforms like Unity, VRChat, or Resonite.",
    )
    def optimize_3d_scene(
        target_platform: str = "unity",
        include_decimation: bool = True,
        bake_textures: bool = False,
    ) -> list[dict[str, Any]]:
        """Guide the user/LLM through a scene optimization workflow."""
        return [
            {
                "role": "user",
                "content": f"I want to optimize my Blender scene for {target_platform}. "
                f"Decimation: {'enabled' if include_decimation else 'disabled'}. "
                f"Texture baking: {'requested' if bake_textures else 'not requested'}.",
            },
            {
                "role": "assistant",
                "content": (
                    f"Understood. To optimize for {target_platform}, I will perform the following steps:\n"
                    "1. Audit the scene for high-poly meshes and redundant materials.\n"
                    + (
                        "2. Apply Decimate modifiers to reduce polygon count while preserving detail.\n"
                        if include_decimation
                        else ""
                    )
                    + (
                        "3. Bake material nodes into PBR textures (diffuse, normal, roughness).\n"
                        if bake_textures
                        else ""
                    )
                    + f"4. Export the final model with {target_platform}-specific scale and orientation.\n\n"
                    "I'll start by listing all objects in the scene. Please use 'blender_status' if you'd like me to focus on specific objects."
                ),
            },
        ]

    @app.prompt(
        name="agentic-robot-creation",
        description="Launch an autonomous agentic workflow to design a complex 3D robot model.",
    )
    def agentic_robot_creation(
        robot_style: str = "industrial",
        complexity: str = "standard",
    ) -> list[dict[str, Any]]:
        """Kickstart the agentic_blender_workflow with a high-fidelity robot modeling prompt."""
        return [
            {
                "role": "user",
                "content": f"Create a {robot_style} robot with {complexity} detail level using the agentic workflow.",
            },
            {
                "role": "assistant",
                "content": (
                    f"Beginning the agentic creation of a {robot_style} robot. "
                    "I will use the `agentic_blender_workflow` tool to autonomously plan and "
                    "execute the modeling, rigging, and material setup. "
                    "I'll probe modeling capabilities first to decide on the best primitives for the chassis."
                ),
            },
        ]

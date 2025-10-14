"""
Rigging tools for Blender MCP.

Provides tools for creating armatures and character rigging systems.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Union
from blender_mcp.app import get_app


def get_app():
    from blender_mcp.app import app
    return app


def _register_rigging_tools():
    """Register all rigging-related tools."""
    app = get_app()

    @app.tool
    async def blender_rigging(
        operation: str = "create_armature",
        armature_name: str = "Armature",
        bone_name: str = "Bone",
        location: Tuple[float, float, float] = (0, 0, 0),
        head: Tuple[float, float, float] = (0, 0, 0),
        tail: Tuple[float, float, float] = (0, 1, 0),
        parent_bone: str = "",
        connected: bool = False,
        target_bone: str = "",
        pole_target: str = "",
    chain_length: int = 2
    ) -> str:
        """
        Create and manage armatures and character rigging.

        Supports multiple operations through the operation parameter:
        - create_armature: Create a new armature object
        - add_bone: Add a bone to an existing armature
        - create_bone_ik: Create inverse kinematics constraint
        - parent_bone: Parent one bone to another
        - mirror_bones: Mirror bones across axis
        - create_basic_rig: Create basic biped rig

        Args:
            operation: Rigging operation type
            armature_name: Name of armature to work with
            bone_name: Name of bone to create/modify
            location: Position for armature or bone
            head: Head position for bone
            tail: Tail position for bone
            parent_bone: Parent bone name for hierarchy
            connected: Connect bone to parent
            target_bone: Target bone for IK constraints
            pole_target: Pole target for IK
            chain_length: Number of bones in IK chain

        Returns:
            Success message with rigging details
        """
        from blender_mcp.handlers.rigging_handler import (
            create_armature, add_bone, create_bone_ik
        )

        try:
            if operation == "create_armature":
                return await create_armature(
                    name=armature_name,
                    location=location
                )

            elif operation == "add_bone":
                if not armature_name:
                    return "armature_name parameter required"
                return await add_bone(
                    armature_name=armature_name,
                    bone_name=bone_name,
                    head=head,
                    tail=tail,
                    parent=parent_bone if parent_bone else None,
                    connected=connected
                )

            elif operation == "create_bone_ik":
                if not armature_name or not target_bone:
                    return "armature_name and target_bone parameters required"
                return await create_bone_ik(
                    armature_name=armature_name,
                    bone_name=bone_name,
                    target_bone=target_bone,
                    pole_target=pole_target if pole_target else None,
                    chain_length=chain_length
                )

            elif operation == "create_basic_rig":
                # Create a simple biped rig
                armature_result = await create_armature(
                    name=f"{armature_name}_basic",
                    location=location
                )

                # Add basic bones (spine, arms, legs)
                bones = [
                    ("spine", (0, 0, 0), (0, 0, 1)),
                    ("neck", (0, 0, 1), (0, 0, 1.2)),
                    ("head", (0, 0, 1.2), (0, 0, 1.5)),
                    ("arm_L", (0.2, 0, 0.8), (0.5, 0, 0.8)),
                    ("forearm_L", (0.5, 0, 0.8), (0.8, 0, 0.8)),
                    ("arm_R", (-0.2, 0, 0.8), (-0.5, 0, 0.8)),
                    ("forearm_R", (-0.5, 0, 0.8), (-0.8, 0, 0.8)),
                    ("leg_L", (0.1, 0, 0), (0.1, 0, -1)),
                    ("shin_L", (0.1, 0, -1), (0.1, 0, -2)),
                    ("leg_R", (-0.1, 0, 0), (-0.1, 0, -1)),
                    ("shin_R", (-0.1, 0, -1), (-0.1, 0, -2)),
                ]

                for bone_info in bones:
                    await add_bone(
                        armature_name=f"{armature_name}_basic",
                        bone_name=bone_info[0],
                        head=bone_info[1],
                        tail=bone_info[2]
                    )

                return f"Created basic biped rig '{armature_name}_basic' with {len(bones)} bones"

            else:
                return f"Unknown rigging operation: {operation}. Available: create_armature, add_bone, create_bone_ik, create_basic_rig"

        except Exception as e:
            return f"Error in rigging operation '{operation}': {str(e)}"


_register_rigging_tools()

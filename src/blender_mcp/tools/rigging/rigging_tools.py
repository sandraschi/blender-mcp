"""
Rigging tools for Blender MCP.

Provides tools for creating armatures and character rigging systems.
"""

from typing import Tuple

from blender_mcp.app import get_app
from blender_mcp.compat import *


def _register_rigging_tools():
    """Register all rigging-related tools."""
    app = get_app()

    @app.tool
    async def blender_rigging(
        operation: str = "create_armature",
        armature_name: str = "Armature",
        bone_name: str = "Bone",
        location: Tuple[float, float, float] = (0, 0, 0),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        head: Tuple[float, float, float] = (0, 0, 0),
        tail: Tuple[float, float, float] = (0, 1, 0),
        parent_bone: str = "",
        connected: bool = False,
        target_bone: str = "",
        pole_target: str = "",
        chain_length: int = 2,
        frame: int = 1,
        rotation_mode: str = "XYZ",
        # Weight transfer params
        source_mesh: str = "",
        target_mesh: str = "",
        transfer_method: str = "NEAREST_FACE",
        max_distance: float = 0.1,
        # Vertex group management params
        group_operation: str = "create",
        group_name: str = "",
        source_group: str = "",
        new_group_name: str = "",
        vertex_indices: list = None,
        # Humanoid mapping params
        mapping_preset: str = "VRCHAT",
        auto_rename: bool = True,
    ) -> str:
        """
        Create and manage armatures and character rigging.

        Supports multiple operations through the operation parameter:
        - create_armature: Create a new armature object
        - add_bone: Add a bone to an existing armature
        - create_bone_ik: Create inverse kinematics constraint
        - create_basic_rig: Create basic biped rig
        - list_bones: List all bones in an armature (useful for VRM models)
        - pose_bone: Set bone rotation/location in pose mode
        - set_bone_keyframe: Insert keyframe for bone pose
        - reset_pose: Reset armature to rest position
        - transfer_weights: Transfer vertex weights between meshes
        - manage_vertex_groups: Create/rename/mirror/remove vertex groups
        - humanoid_mapping: Apply VRChat/Unity humanoid bone mapping

        Args:
            operation: Rigging operation type
            armature_name: Name of armature to work with
            bone_name: Name of bone to create/modify/pose
            location: Position for armature, bone, or pose offset
            rotation: Rotation in degrees for pose_bone (Euler XYZ)
            head: Head position for bone creation
            tail: Tail position for bone creation
            parent_bone: Parent bone name for hierarchy
            connected: Connect bone to parent
            target_bone: Target bone for IK constraints
            pole_target: Pole target for IK
            chain_length: Number of bones in IK chain
            frame: Frame number for keyframing
            rotation_mode: Euler rotation order (XYZ, ZYX, etc.)
            source_mesh: Source mesh for weight transfer operations
            target_mesh: Target mesh for weight transfer operations
            transfer_method: Method for weight transfer (NEAREST_FACE, RAY_CAST, etc.)
            max_distance: Maximum distance for weight transfer
            group_operation: Vertex group operation type (create, rename, mirror, remove, assign)
            group_name: Name of vertex group for operations
            source_group: Source vertex group for operations like mirror
            new_group_name: New name for rename operations
            vertex_indices: Vertex indices for group assignment
            mapping_preset: Humanoid mapping preset (VRCHAT, UNITY, BLENDER)
            auto_rename: Whether to auto-rename bones to standard names

        Returns:
            Success message with rigging details
        """
        from loguru import logger

        from blender_mcp.handlers.rigging_handler import (
            add_bone,
            create_armature,
            create_bone_ik,
            humanoid_mapping,
            list_bones,
            manage_vertex_groups,
            pose_bone,
            reset_pose,
            set_bone_keyframe,
            transfer_weights,
        )

        logger.info(
            f"🦴 blender_rigging called with operation='{operation}', armature_name='{armature_name}'"
        )

        try:
            # Convert tuple parameters to proper formats
            location_tuple = (
                tuple(float(x) for x in location)
                if hasattr(location, "__iter__") and not isinstance(location, str)
                else location
            )
            head_tuple = (
                tuple(float(x) for x in head)
                if hasattr(head, "__iter__") and not isinstance(head, str)
                else head
            )
            tail_tuple = (
                tuple(float(x) for x in tail)
                if hasattr(tail, "__iter__") and not isinstance(tail, str)
                else tail
            )

            # Validate 3-element vectors
            if len(location_tuple) != 3:
                return f"Error: location must be a 3-element array/tuple, got {len(location_tuple)} elements"
            if len(head_tuple) != 3:
                return (
                    f"Error: head must be a 3-element array/tuple, got {len(head_tuple)} elements"
                )
            if len(tail_tuple) != 3:
                return (
                    f"Error: tail must be a 3-element array/tuple, got {len(tail_tuple)} elements"
                )

            if operation == "create_armature":
                return await create_armature(name=armature_name, location=location_tuple)

            elif operation == "add_bone":
                if not armature_name:
                    return "armature_name parameter required"
                return await add_bone(
                    armature_name=armature_name,
                    bone_name=bone_name,
                    head=head_tuple,
                    tail=tail_tuple,
                    parent=parent_bone if parent_bone else None,
                    connected=connected,
                )

            elif operation == "create_bone_ik":
                if not armature_name or not target_bone:
                    return "armature_name and target_bone parameters required"
                return await create_bone_ik(
                    armature_name=armature_name,
                    bone_name=bone_name,
                    target_bone=target_bone,
                    pole_target=pole_target if pole_target else None,
                    chain_length=chain_length,
                )

            elif operation == "create_basic_rig":
                # Create a simple biped rig
                await create_armature(
                    name=f"{armature_name}_basic", location=location
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
                        tail=bone_info[2],
                    )

                return f"Created basic biped rig '{armature_name}_basic' with {len(bones)} bones"

            elif operation == "list_bones":
                # List all bones in armature (great for VRM models)
                result = await list_bones(armature_name=armature_name)
                return str(result)

            elif operation == "pose_bone":
                # Pose a specific bone (rotate arm, leg, etc.)
                if not bone_name:
                    return "bone_name parameter required for pose_bone"
                rotation_tuple = (
                    tuple(float(x) for x in rotation)
                    if hasattr(rotation, "__iter__") and not isinstance(rotation, str)
                    else rotation
                )
                result = await pose_bone(
                    armature_name=armature_name,
                    bone_name=bone_name,
                    rotation=rotation_tuple,
                    location=location_tuple if any(location_tuple) else None,
                    rotation_mode=rotation_mode,
                )
                return str(result)

            elif operation == "set_bone_keyframe":
                # Keyframe current bone pose
                if not bone_name:
                    return "bone_name parameter required for set_bone_keyframe"
                result = await set_bone_keyframe(
                    armature_name=armature_name,
                    bone_name=bone_name,
                    frame=frame,
                )
                return str(result)

            elif operation == "reset_pose":
                # Reset all bones to rest position
                result = await reset_pose(armature_name=armature_name)
                return str(result)

            elif operation == "transfer_weights":
                # Transfer vertex weights between meshes
                if not source_mesh or not target_mesh or not armature_name:
                    return "source_mesh, target_mesh, and armature_name parameters required for transfer_weights"
                result = await transfer_weights(
                    source_mesh=source_mesh,
                    target_mesh=target_mesh,
                    armature_name=armature_name,
                    method=transfer_method,
                    max_distance=max_distance,
                )
                return _format_weight_transfer_result(result)

            elif operation == "manage_vertex_groups":
                # Manage vertex groups (create, rename, mirror, remove, assign)
                if not target_mesh:
                    return "target_mesh parameter required for manage_vertex_groups"
                result = await manage_vertex_groups(
                    target_mesh=target_mesh,
                    operation=group_operation,
                    group_name=group_name,
                    source_group=source_group,
                    new_name=new_group_name,
                    vertex_indices=vertex_indices,
                )
                return _format_vertex_group_result(result)

            elif operation == "humanoid_mapping":
                # Apply VRChat/Unity humanoid bone mapping
                if not armature_name:
                    return "armature_name parameter required for humanoid_mapping"
                result = await humanoid_mapping(
                    armature_name=armature_name,
                    mapping_preset=mapping_preset,
                    auto_rename=auto_rename,
                )
                return _format_humanoid_mapping_result(result)

            else:
                return f"Unknown rigging operation: {operation}. Available: create_armature, add_bone, create_bone_ik, create_basic_rig, list_bones, pose_bone, set_bone_keyframe, reset_pose, transfer_weights, manage_vertex_groups, humanoid_mapping"

        except Exception as e:
            logger.error(f"❌ Error in rigging operation '{operation}': {str(e)}")
            return f"Error in rigging operation '{operation}': {str(e)}"


def _format_weight_transfer_result(result: dict) -> str:
    """Format weight transfer operation results."""
    status = result.get("status", "unknown")

    if status == "success":
        report = "✅ **Weight Transfer Complete**\n"
        report += "=" * 30 + "\n\n"
        report += f"**Source Mesh:** {result.get('source_mesh', 'Unknown')}\n"
        report += f"**Target Mesh:** {result.get('target_mesh', 'Unknown')}\n"
        report += f"**Armature:** {result.get('armature', 'Unknown')}\n"
        report += f"**Vertex Groups:** {result.get('vertex_groups_before', 0)} → {result.get('vertex_groups_after', 0)}\n"
        report += f"**Transfer Method:** {result.get('transfer_method', 'Unknown')}\n"
        report += f"**Max Distance:** {result.get('max_distance', 0):.3f}\n\n"
        report += f"{result.get('message', '')}\n"

        # Recommendations
        report += "\n💡 **Next Steps:**\n"
        report += "  • Test deformation in pose mode\n"
        report += "  • Adjust weights manually if needed\n"
        report += "  • Run validation checks\n"
    else:
        report = f"❌ **Weight Transfer Failed**\n{result.get('error', 'Unknown error')}"

    return report


def _format_vertex_group_result(result: dict) -> str:
    """Format vertex group management results."""
    status = result.get("status", "unknown")
    operation = result.get("operation", "unknown")

    if status == "success":
        report = f"✅ **Vertex Group Operation: {operation.title()}**\n"
        report += "=" * 35 + "\n\n"
        report += f"**Mesh:** {result.get('mesh_name', 'Unknown')}\n"
        report += f"**Final Groups:** {result.get('final_vertex_groups', 0)}\n\n"

        result_details = result.get("result", {})
        if "created" in result_details:
            report += f"**Created:** {result_details['created']}\n"
        if "renamed" in result_details:
            report += f"**Renamed:** {result_details['renamed']}\n"
        if "mirrored" in result_details:
            report += f"**Mirrored:** {result_details['mirrored']}\n"
        if "removed" in result_details:
            report += f"**Removed:** {result_details['removed']}\n"
        if "assigned" in result_details:
            report += f"**Assigned:** {result_details['assigned']}\n\n"

        report += f"{result.get('message', '')}\n"
    else:
        report = f"❌ **Vertex Group Operation Failed**\n{result.get('error', 'Unknown error')}"

    return report


def _format_humanoid_mapping_result(result: dict) -> str:
    """Format humanoid mapping results."""
    status = result.get("status", "unknown")

    if status == "success":
        report = "✅ **Humanoid Mapping Applied**\n"
        report += "=" * 30 + "\n\n"
        report += f"**Armature:** {result.get('armature_name', 'Unknown')}\n"
        report += f"**Preset:** {result.get('mapping_preset', 'Unknown')}\n"
        report += f"**Total Bones:** {result.get('total_bones', 0)}\n"
        report += f"**Mapped Bones:** {result.get('mapped_bones', 0)}\n"
        report += f"**Auto Rename:** {'Yes' if result.get('auto_rename', False) else 'No'}\n\n"

        renamed = result.get("renamed_bones", [])
        if renamed:
            report += "**Renamed Bones:**\n"
            for rename_info in renamed:
                report += f"  • {rename_info['from']} → {rename_info['to']}\n"
            report += "\n"

        unmapped = result.get("unmapped_humanoid", [])
        if unmapped:
            report += "**Unmapped Humanoid Bones:**\n"
            for bone in unmapped:
                report += f"  • {bone}\n"
            report += "\n"

        report += f"{result.get('message', '')}\n"

        # Recommendations
        if unmapped:
            report += "\n⚠️ **Manual Mapping Needed:**\n"
            report += "  • Some bones couldn't be auto-mapped\n"
            report += "  • Rename manually or check bone naming\n"
        else:
            report += "\n✅ **Ready for Export:**\n"
            report += "  • All humanoid bones properly mapped\n"
            report += "  • Compatible with VRChat/Unity humanoid rigs\n"
    else:
        report = f"❌ **Humanoid Mapping Failed**\n{result.get('error', 'Unknown error')}"

    return report


_register_rigging_tools()

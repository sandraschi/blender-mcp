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
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates 11 related rigging operations into single interface. Prevents tool explosion while maintaining
        full character rigging workflow from armature creation to humanoid mapping. Follows FastMCP 2.14.3 best practices.

        Complete character rigging system for Blender supporting armatures, bones, IK, skinning, and humanoid standards.

        **Armature Operations (4 operations):**
        - **create_armature**: Generate new skeleton object with customizable positioning
        - **add_bone**: Add individual bones to existing armature with parent/child relationships
        - **create_bone_ik**: Set up inverse kinematics constraints for realistic joint movement
        - **create_basic_rig**: Auto-generate complete biped character rig with standard bone structure

        **Bone Management (3 operations):**
        - **list_bones**: Display all bones in armature with hierarchy and properties
        - **pose_bone**: Set bone transformations in pose mode for animation
        - **set_bone_keyframe**: Insert keyframes for bone animation at specific frames

        **Pose & Animation (1 operation):**
        - **reset_pose**: Return armature to rest pose, clearing all pose transformations

        **Skinning & Weights (2 operations):**
        - **transfer_weights**: Copy vertex weights between meshes using various projection methods
        - **manage_vertex_groups**: Create, rename, mirror, or remove vertex groups for weight painting

        **Standards & Compatibility (1 operation):**
        - **humanoid_mapping**: Apply VRChat/Unity humanoid bone naming and structure standards

        Args:
            operation (str, required): The rigging operation to perform. Must be one of: "create_armature",
                "add_bone", "create_bone_ik", "create_basic_rig", "list_bones", "pose_bone", "set_bone_keyframe",
                "reset_pose", "transfer_weights", "manage_vertex_groups", "humanoid_mapping".
                - Armature operations: "create_armature", "add_bone", "create_bone_ik", "create_basic_rig"
                - Bone operations: "list_bones", "pose_bone", "set_bone_keyframe"
                - Pose operations: "reset_pose"
                - Skinning operations: "transfer_weights", "manage_vertex_groups"
                - Standards operations: "humanoid_mapping"
            armature_name (str): Target armature object name. Required for most operations.
                Must exist in scene for bone operations.
            bone_name (str): Name of bone to create, modify, or pose. Required for bone-specific operations.
                Must be unique within armature.
            location (Tuple[float, float, float]): 3D position coordinates (x, y, z) for armature placement.
                Default: (0, 0, 0). Used for: "create_armature".
            rotation (Tuple[float, float, float]): Euler rotation angles in degrees (x, y, z) for bone posing.
                Default: (0, 0, 0). Used for: "pose_bone". Range: -180 to 180 degrees.
            head (Tuple[float, float, float]): Starting point coordinates for new bone creation.
                Required for: "add_bone". Defines bone origin in 3D space.
            tail (Tuple[float, float, float]): Ending point coordinates for new bone creation.
                Required for: "add_bone". Defines bone length and direction.
            parent_bone (str): Name of parent bone for hierarchy. Optional for "add_bone".
                Creates bone chain when specified.
            connected (bool): Whether new bone connects directly to parent tail. Default: False.
                True creates seamless bone chain, False allows bone gaps.
            target_bone (str): Name of target bone for IK constraint. Required for: "create_bone_ik".
                Defines which bone the IK chain reaches toward.
            pole_target (str): Empty object name for IK pole target. Optional for "create_bone_ik".
                Controls IK chain bending direction for natural joint movement.
            chain_length (int): Number of bones in IK chain. Default: 2. Range: 1-10.
                Longer chains provide more flexible but complex IK solutions.
            frame (int): Timeline frame number for keyframe insertion. Default: 1. Range: 1-10000.
                Corresponds to animation timeline frames.
            rotation_mode (str): Euler angle rotation order. One of: "XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX".
                Default: "XYZ". Affects how rotation values are interpreted.
            source_mesh (str): Source mesh object name for weight transfer. Required for: "transfer_weights".
                Mesh containing vertex weights to copy from.
            target_mesh (str): Target mesh object name for weight transfer. Required for: "transfer_weights".
                Mesh to receive copied vertex weights.
            transfer_method (str): Weight projection algorithm. One of: "NEAREST_FACE", "RAY_CAST", "NEAREST_VERTEX".
                Default: "NEAREST_FACE". "RAY_CAST" most accurate but slower.
            max_distance (float): Maximum transfer distance for weight projection. Default: 0.1.
                Range: 0.001-10.0. Larger values capture more distant geometry.
            group_operation (str): Vertex group management operation. One of: "create", "rename", "mirror", "remove", "assign".
                Required for: "manage_vertex_groups".
            group_name (str): Target vertex group name. Required for most group operations.
            source_group (str): Source group name for operations like mirror. Required for: "mirror".
            new_group_name (str): New name for rename operations. Required for: "rename".
            vertex_indices (list): List of vertex indices for group assignment. Optional for "assign".
                Defaults to empty list for manual weight painting.
            mapping_preset (str): Humanoid bone mapping standard. One of: "VRCHAT", "UNITY", "BLENDER".
                Default: "VRCHAT". Defines target bone naming convention.
            auto_rename (bool): Whether to automatically rename bones to standard names. Default: True.
                False preserves original bone names while adding mapping.

        Returns:
            str: Rigging operation result message with success/failure status and details.
                Format: "SUCCESS: {operation} - {details}" or "ERROR: {operation} failed - {error_details}"

        Raises:
            ValueError: If operation parameters are invalid or target objects don't exist
            RuntimeError: If Blender rigging system fails or armature state is invalid

        Examples:
            Basic armature: blender_rigging("create_armature", armature_name="CharacterRig", location=(0, 0, 1))
            Add bone: blender_rigging("add_bone", armature_name="CharacterRig", bone_name="UpperArm", head=(0, 0, 1.5), tail=(0, 0, 0.5))
            IK setup: blender_rigging("create_bone_ik", armature_name="CharacterRig", bone_name="LowerArm", target_bone="Hand", chain_length=2)
            Weight transfer: blender_rigging("transfer_weights", source_mesh="HighPoly", target_mesh="LowPoly", transfer_method="RAY_CAST")
            VRChat mapping: blender_rigging("humanoid_mapping", armature_name="CharacterRig", mapping_preset="VRCHAT")

        Note:
            Armature operations require object mode. Pose operations require pose mode.
            IK constraints improve animation quality but add computational overhead.
            Weight transfer quality depends on mesh topology similarity.
            Humanoid mapping essential for VRChat and Unity character compatibility.
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
            f"blender_rigging called with operation='{operation}', armature_name='{armature_name}'"
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
            logger.error(f"ERROR: Error in rigging operation '{operation}': {str(e)}")
            return f"Error in rigging operation '{operation}': {str(e)}"


def _format_weight_transfer_result(result: dict) -> str:
    """Format weight transfer operation results."""
    status = result.get("status", "unknown")

    if status == "success":
        report = "SUCCESS: **Weight Transfer Complete**\n"
        report += "=" * 30 + "\n\n"
        report += f"**Source Mesh:** {result.get('source_mesh', 'Unknown')}\n"
        report += f"**Target Mesh:** {result.get('target_mesh', 'Unknown')}\n"
        report += f"**Armature:** {result.get('armature', 'Unknown')}\n"
        report += f"**Vertex Groups:** {result.get('vertex_groups_before', 0)} → {result.get('vertex_groups_after', 0)}\n"
        report += f"**Transfer Method:** {result.get('transfer_method', 'Unknown')}\n"
        report += f"**Max Distance:** {result.get('max_distance', 0):.3f}\n\n"
        report += f"{result.get('message', '')}\n"

        # Recommendations
        report += "\nNext Steps:\n"
        report += "  • Test deformation in pose mode\n"
        report += "  • Adjust weights manually if needed\n"
        report += "  • Run validation checks\n"
    else:
        report = f"ERROR: **Weight Transfer Failed**\n{result.get('error', 'Unknown error')}"

    return report


def _format_vertex_group_result(result: dict) -> str:
    """Format vertex group management results."""
    status = result.get("status", "unknown")
    operation = result.get("operation", "unknown")

    if status == "success":
        report = f"SUCCESS: **Vertex Group Operation: {operation.title()}**\n"
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
        report = f"ERROR: **Vertex Group Operation Failed**\n{result.get('error', 'Unknown error')}"

    return report


def _format_humanoid_mapping_result(result: dict) -> str:
    """Format humanoid mapping results."""
    status = result.get("status", "unknown")

    if status == "success":
        report = "SUCCESS: **Humanoid Mapping Applied**\n"
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

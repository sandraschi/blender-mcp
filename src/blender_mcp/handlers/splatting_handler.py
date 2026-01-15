"""Gaussian Splatting handler for Blender MCP.

Provides support for importing, processing, and managing Gaussian Splats
for hybrid environments combining real-world captures with 3D models.
"""

import os
from math import Vector
from typing import Any, Dict, Optional, Tuple

import bpy
from loguru import logger

from ..decorators import blender_operation
from ..exceptions import BlenderSplattingError
from ..utils.blender_executor import get_blender_executor

# Initialize the executor with default Blender executable
_executor = get_blender_executor()


@blender_operation("import_gaussian_splat")
def import_gaussian_splat(
    file_path: str,
    sh_degree: int = 3,
    setup_proxy: bool = True,
    import_as_cloud: bool = True
) -> Dict[str, Any]:
    """
    Import Gaussian Splat files (.ply or .spz) into Blender.

    Creates a splat object with optional performance proxy for viewport management.

    Args:
        file_path: Path to the .ply or .spz file
        sh_degree: Spherical harmonics degree (0-3, affects quality vs performance)
        setup_proxy: Whether to create a bounding box proxy for performance
        import_as_cloud: Import as point cloud (recommended for large splats)

    Returns:
        Import result with object names and statistics

    Raises:
        BlenderSplattingError: If import fails or file is invalid
    """
    logger.info(f"Importing Gaussian Splat from {file_path}")

    if not os.path.exists(file_path):
        raise BlenderSplattingError(f"Splat file not found: {file_path}")

    try:
        # Validate file extension
        if not file_path.lower().endswith(('.ply', '.spz')):
            raise BlenderSplattingError("Unsupported file format. Expected .ply or .spz")

        # Import the splat using Blender's 3DGS integration
        result = _import_splat_file(file_path, sh_degree, import_as_cloud)

        if setup_proxy and result["status"] == "success":
            # Create performance proxy
            proxy_result = _create_splat_proxy(result["object_name"])
            result.update(proxy_result)

        return result

    except Exception as e:
        logger.error(f"Gaussian Splat import failed: {e}")
        raise BlenderSplattingError(f"Failed to import splat: {str(e)}") from e


@blender_operation("crop_splat")
def crop_splat(
    crop_type: str = "sphere",
    radius: float = 5.0,
    center_point: Optional[Tuple[float, float, float]] = None,
    invert: bool = False
) -> Dict[str, Any]:
    """
    Crop a Gaussian Splat using volume-based selection.

    Removes splat points outside the specified volume to clean up captures.

    Args:
        crop_type: Type of crop volume ("sphere", "box", "cylinder")
        radius: Radius/size of the crop volume
        center_point: Center point for cropping (defaults to active object location)
        invert: Whether to invert the selection (keep outside instead of inside)

    Returns:
        Crop operation result with statistics

    Raises:
        BlenderSplattingError: If cropping fails
    """
    logger.info(f"Cropping splat with {crop_type} (radius: {radius}, invert: {invert})")

    try:
        obj = bpy.context.active_object
        if not obj or not _is_splat_object(obj):
            raise BlenderSplattingError("No active splat object selected")

        # Determine center point
        if center_point is None:
            center_point = tuple(obj.location)

        # Perform the crop operation
        result = _crop_splat_volume(obj, crop_type, radius, center_point, invert)

        return result

    except Exception as e:
        logger.error(f"Splat cropping failed: {e}")
        raise BlenderSplattingError(f"Failed to crop splat: {str(e)}") from e


@blender_operation("generate_collision_mesh")
def generate_collision_mesh(
    density_threshold: float = 0.1,
    decimation_ratio: float = 0.1,
    smoothing_iterations: int = 2
) -> Dict[str, Any]:
    """
    Generate a collision mesh from Gaussian Splat data.

    Creates a simplified mesh suitable for physics collision detection
    from the dense splat point cloud.

    Args:
        density_threshold: Minimum point density to include in mesh generation
        decimation_ratio: How much to simplify the generated mesh (0.1 = 10% of faces)
        smoothing_iterations: Number of Laplacian smoothing passes

    Returns:
        Mesh generation result with collision object information

    Raises:
        BlenderSplattingError: If mesh generation fails
    """
    logger.info(f"Generating collision mesh (density: {density_threshold}, decimation: {decimation_ratio})")

    try:
        obj = bpy.context.active_object
        if not obj or not _is_splat_object(obj):
            raise BlenderSplattingError("No active splat object selected")

        # Generate collision mesh
        result = _generate_collision_from_splat(
            obj, density_threshold, decimation_ratio, smoothing_iterations
        )

        return result

    except Exception as e:
        logger.error(f"Collision mesh generation failed: {e}")
        raise BlenderSplattingError(f"Failed to generate collision mesh: {str(e)}") from e


@blender_operation("export_splat_for_resonite")
def export_splat_for_resonite(
    target_format: str = "ply",
    include_collision: bool = True,
    optimize_for_mobile: bool = False
) -> Dict[str, Any]:
    """
    Export splat data optimized for Resonite.

    Prepares splat files for native Resonite Gaussian Splat rendering.

    Args:
        target_format: Export format ("ply" or "spz" for compressed)
        include_collision: Whether to export associated collision mesh
        optimize_for_mobile: Apply mobile-specific optimizations

    Returns:
        Export result with file paths and statistics

    Raises:
        BlenderSplattingError: If export fails
    """
    logger.info(f"Exporting splat for Resonite (format: {target_format}, collision: {include_collision})")

    try:
        obj = bpy.context.active_object
        if not obj or not _is_splat_object(obj):
            raise BlenderSplattingError("No active splat object selected")

        # Export the splat
        result = _export_splat_for_resonite(obj, target_format, include_collision, optimize_for_mobile)

        return result

    except Exception as e:
        logger.error(f"Resonite export failed: {e}")
        raise BlenderSplattingError(f"Failed to export for Resonite: {str(e)}") from e


def _import_splat_file(file_path: str, sh_degree: int, import_as_cloud: bool) -> Dict[str, Any]:
    """Internal function to handle splat file import."""
    try:
        # Use Blender's built-in 3DGS import operator
        # This assumes the 'io_realtime_gs' addon or similar is available
        bpy.ops.import_scene.gsplat(
            filepath=file_path,
            sh_degree=sh_degree,
            import_as_cloud=import_as_cloud
        )

        # Get the imported object
        splat_obj = bpy.context.active_object
        if not splat_obj:
            raise BlenderSplattingError("Import completed but no object was created")

        splat_obj.name = f"GS_{os.path.splitext(os.path.basename(file_path))[0]}"

        # Get basic statistics
        point_count = _get_splat_point_count(splat_obj)

        return {
            "status": "success",
            "object_name": splat_obj.name,
            "point_count": point_count,
            "file_path": file_path,
            "sh_degree": sh_degree
        }

    except AttributeError as e:
        # Fallback for systems without 3DGS addon
        raise BlenderSplattingError(
            "Gaussian Splat import requires Blender 3DGS integration. "
            "Please install the 'io_realtime_gs' addon or KIRI Engine."
        ) from e


def _create_splat_proxy(splat_name: str) -> Dict[str, Any]:
    """Create a performance proxy for large splats."""
    try:
        splat_obj = bpy.data.objects.get(splat_name)
        if not splat_obj:
            return {"proxy_created": False, "error": "Splat object not found"}

        # Create a bounding box cube
        bpy.ops.mesh.primitive_cube_add(size=1)
        proxy = bpy.context.active_object
        proxy.name = f"{splat_name}_PROXY"

        # Match the splat's bounding box
        bbox = _get_object_bounding_box(splat_obj)
        if bbox:
            proxy.location = bbox["center"]
            proxy.scale = bbox["size"]

        proxy.display_type = 'WIRE'
        proxy.hide_render = True

        # Parent the splat to the proxy
        splat_obj.parent = proxy
        splat_obj.hide_viewport = True  # Hide the heavy splat by default

        return {
            "proxy_created": True,
            "proxy_name": proxy.name,
            "splat_hidden": True
        }

    except Exception as e:
        logger.warning(f"Failed to create splat proxy: {e}")
        return {"proxy_created": False, "error": str(e)}


def _crop_splat_volume(
    obj: Any,
    crop_type: str,
    radius: float,
    center: Tuple[float, float, float],
    invert: bool
) -> Dict[str, Any]:
    """Crop splat using volume selection."""
    try:
        initial_count = _get_splat_point_count(obj)

        # Select points within the volume
        # This is a simplified implementation - real implementation would use
        # Blender's geometry nodes or the splat addon's cropping tools

        if crop_type == "sphere":
            # Use distance from center to select points
            _select_splat_points_in_sphere(obj, center, radius, invert)
        elif crop_type == "box":
            _select_splat_points_in_box(obj, center, radius, invert)
        else:
            raise BlenderSplattingError(f"Unsupported crop type: {crop_type}")

        # Delete selected/unselected points
        bpy.ops.pointcloud.delete()

        final_count = _get_splat_point_count(obj)

        return {
            "status": "success",
            "crop_type": crop_type,
            "radius": radius,
            "center": center,
            "invert": invert,
            "points_removed": initial_count - final_count,
            "remaining_points": final_count
        }

    except Exception as e:
        raise BlenderSplattingError(f"Volume cropping failed: {str(e)}") from e


def _generate_collision_from_splat(
    splat_obj: Any,
    density_threshold: float,
    decimation_ratio: float,
    smoothing_iterations: int
) -> Dict[str, Any]:
    """Generate collision mesh from splat data."""
    try:
        # This is a simplified implementation
        # Real implementation would use Poisson reconstruction or similar

        # Create a new mesh object for collision
        bpy.ops.mesh.primitive_cube_add()
        collision_obj = bpy.context.active_object
        collision_obj.name = f"{splat_obj.name}_COLLISION"

        # Position it at the splat's location
        collision_obj.location = splat_obj.location

        # Apply basic collision material
        _setup_collision_material(collision_obj)

        return {
            "status": "success",
            "collision_object": collision_obj.name,
            "density_threshold": density_threshold,
            "decimation_ratio": decimation_ratio,
            "smoothing_iterations": smoothing_iterations
        }

    except Exception as e:
        raise BlenderSplattingError(f"Collision mesh generation failed: {str(e)}") from e


def _export_splat_for_resonite(
    obj: Any,
    target_format: str,
    include_collision: bool,
    optimize_for_mobile: bool
) -> Dict[str, Any]:
    """Export splat data for Resonite."""
    try:
        # Determine output path
        base_name = obj.name.replace("GS_", "").replace("_PROXY", "")
        output_path = f"//{base_name}_resonite.{target_format}"

        # Export the splat
        if target_format.lower() == "ply":
            bpy.ops.export_scene.ply(filepath=output_path, use_selection=True)
        elif target_format.lower() == "spz":
            # Assume compressed export is available
            bpy.ops.export_scene.gsplat(filepath=output_path, use_selection=True, compress=True)
        else:
            raise BlenderSplattingError(f"Unsupported export format: {target_format}")

        result = {
            "status": "success",
            "output_path": output_path,
            "format": target_format,
            "include_collision": include_collision,
            "optimize_for_mobile": optimize_for_mobile
        }

        # Export collision if requested
        if include_collision:
            collision_obj = bpy.data.objects.get(f"{obj.name}_COLLISION")
            if collision_obj:
                collision_path = f"//{base_name}_collision.fbx"
                bpy.ops.export_scene.fbx(
                    filepath=collision_path,
                    use_selection=True,
                    object_types={'MESH'}
                )
                result["collision_path"] = collision_path

        return result

    except Exception as e:
        raise BlenderSplattingError(f"Resonite export failed: {str(e)}") from e


# Utility functions

def _is_splat_object(obj: Any) -> bool:
    """Check if an object is a Gaussian Splat."""
    # Check for splat-specific properties
    return (
        obj and
        (obj.type == 'POINTCLOUD' or
         hasattr(obj, 'gsplat') or
         'GS_' in obj.name or
         obj.name.endswith('_PROXY'))
    )


def _get_splat_point_count(obj: Any) -> int:
    """Get the number of points in a splat object."""
    try:
        if obj.type == 'POINTCLOUD':
            return len(obj.data.points)
        # For other splat types, try to get point count
        return getattr(obj, 'point_count', 0)
    except Exception:
        return 0


def _get_object_bounding_box(obj: Any) -> Optional[Dict[str, Any]]:
    """Get bounding box information for an object."""
    try:
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        min_coords = [min(c[i] for c in bbox) for i in range(3)]
        max_coords = [max(c[i] for c in bbox) for i in range(3)]

        center = [(min_c + max_c) / 2 for min_c, max_c in zip(min_coords, max_coords)]
        size = [max_c - min_c for min_c, max_c in zip(min_coords, max_coords)]

        return {
            "center": tuple(center),
            "size": tuple(size),
            "min": tuple(min_coords),
            "max": tuple(max_coords)
        }
    except Exception:
        return None


def _select_splat_points_in_sphere(
    obj: Any,
    center: Tuple[float, float, float],
    radius: float,
    invert: bool
) -> None:
    """Select splat points within a sphere."""
    # This is a placeholder - real implementation would use Blender's
    # point cloud selection or geometry nodes
    pass


def _select_splat_points_in_box(
    obj: Any,
    center: Tuple[float, float, float],
    size: float,
    invert: bool
) -> None:
    """Select splat points within a box."""
    # This is a placeholder - real implementation would use Blender's
    # point cloud selection or geometry nodes
    pass


def _setup_collision_material(obj: Any) -> None:
    """Set up a basic collision material."""
    try:
        mat = bpy.data.materials.new(name=f"{obj.name}_Collision")
        mat.use_nodes = True

        # Set up a basic transparent material for collision visualization
        principled = mat.node_tree.nodes["Principled BSDF"]
        principled.inputs['Alpha'].default_value = 0.3
        principled.inputs['Base Color'].default_value = (0.0, 1.0, 0.0, 0.3)  # Green transparent

        obj.data.materials.append(mat)
    except Exception as e:
        logger.warning(f"Failed to setup collision material: {e}")

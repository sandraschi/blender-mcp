"""Import operations handler for Blender MCP."""

import logging
from enum import StrEnum
from pathlib import Path
from typing import Any

from ..compat import *

logger = logging.getLogger(__name__)
from ..decorators import blender_operation
from ..utils.blender_executor import get_blender_executor

_executor = get_blender_executor()


class ImportFormat(StrEnum):
    """Supported import formats."""

    # Standard 3D formats
    OBJ = "OBJ"
    FBX = "FBX"
    GLTF = "GLTF"
    GLB = "GLB"  # Binary GLTF
    VRM = "VRM"  # VRChat avatar format (GLTF-based)
    COLLADA = "COLLADA"
    USD = "USD"
    USDA = "USDA"
    USDC = "USDC"
    USDZ = "USDZ"
    ABC = "ALEMBIC"

    # Mesh/geometry formats
    PLY = "PLY"  # Also used for point clouds and gaussian splats
    STL = "STL"

    # Animation/curve formats
    BVH = "BVH"
    SVG = "SVG"
    DXF = "DXF"

    # Point cloud / AI-generated formats
    XYZ = "XYZ"  # Point cloud
    E57 = "E57"  # LiDAR point cloud
    LAS = "LAS"  # LiDAR

    # Legacy
    FBX_BINARY = "FBX_BINARY"


@blender_operation("import_file", log_args=True)
async def import_file(filepath: str, file_format: ImportFormat | str, **kwargs: Any) -> dict[str, Any]:
    """Import a 3D file into the current scene.

    Args:
        filepath: Path to the file to import
        file_format: Format of the file to import
        **kwargs: Additional import options specific to each format
            - OBJ: global_scale, use_split_objects, use_split_groups, etc.
            - FBX: use_manual_orientation, global_scale, use_custom_normals, etc.
            - GLTF: import_pack_images, merge_vertices, import_shading, etc.

    Returns:
        Dict containing import status and imported objects
    """
    # Convert path to absolute and ensure it exists
    filepath = str(Path(filepath).absolute())

    # Format-specific import options
    options = {"filepath": filepath, "filter_glob": f"*.{file_format.lower()}", **kwargs}

    # Generate the import operator call based on format.
    # NOTE (fleet fix 2026-09-18): legacy io_* addon operators
    # (import_scene.obj etc.) do NOT exist under --factory-startup, which the
    # executor always uses. Prefer Blender 4.x native wm.* importers, which are
    # built in. Second trap: the tool wrapper injects global_scale /
    # use_custom_normals / import_shading into EVERY call, but native wm.*
    # importers reject unknown kwargs — so every branch builds an EXPLICIT
    # option set, and unit scaling for ops without a global_scale knob is
    # applied to the imported meshes below (post_scale).
    post_scale = 1.0
    if file_format == ImportFormat.OBJ:
        operator = "bpy.ops.wm.obj_import"
        post_scale = float(kwargs.get("global_scale", 1.0))
        options = {
            "filepath": filepath,
            "forward_axis": "NEGATIVE_Z",
            "up_axis": "Y",
            "use_split_objects": kwargs.get("use_split_objects", True),
            "use_split_groups": kwargs.get("use_split_groups", True),
            "validate_meshes": kwargs.get("validate_meshes", False),
        }

    elif file_format == ImportFormat.FBX:
        operator = "bpy.ops.import_scene.fbx"
        options = {
            "filepath": filepath,
            "global_scale": kwargs.get("global_scale", 1.0),
            "use_manual_orientation": kwargs.get("use_manual_orientation", False),
            "use_custom_normals": kwargs.get("use_custom_normals", True),
        }

    elif file_format in (ImportFormat.GLTF, ImportFormat.GLB, ImportFormat.VRM):
        # GLTF, GLB, and VRM all use the same importer (no global_scale knob).
        # 4.x import_shading enum: NORMALS/FLAT/SMOOTH (not legacy "NORMAL");
        # the tool wrapper injects booleans, so map them (True = file normals).
        operator = "bpy.ops.import_scene.gltf"
        post_scale = float(kwargs.get("global_scale", 1.0))
        _shading = kwargs.get("import_shading", "NORMALS")
        if _shading is True or _shading == "NORMAL":
            _shading = "NORMALS"
        elif _shading is False:
            _shading = "FLAT"
        options = {
            "filepath": filepath,
            "import_pack_images": kwargs.get("import_pack_images", True),
            "merge_vertices": kwargs.get("merge_vertices", False),
            "import_shading": _shading,
        }

    elif file_format == ImportFormat.COLLADA:
        operator = "bpy.ops.wm.collada_import"
        post_scale = float(kwargs.get("global_scale", 1.0))
        options = {
            "filepath": filepath,
            "import_units": kwargs.get("import_units", False),
            "fix_orientation": kwargs.get("fix_orientation", False),
        }

    elif file_format in (ImportFormat.USD, ImportFormat.USDA, ImportFormat.USDC, ImportFormat.USDZ):
        # All USD variants use the same importer
        operator = "bpy.ops.wm.usd_import"
        post_scale = float(kwargs.get("global_scale", 1.0))
        options = {
            "filepath": filepath,
            "import_meshes": kwargs.get("import_meshes", True),
            "import_materials": kwargs.get("import_materials", True),
            "import_lights": kwargs.get("import_lights", True),
            "import_cameras": kwargs.get("import_cameras", True),
        }

    elif file_format == ImportFormat.ABC:
        operator = "bpy.ops.wm.alembic_import"
        post_scale = float(kwargs.get("global_scale", 1.0))
        options = {
            "filepath": filepath,
            "as_background_job": kwargs.get("as_background_job", False),
            "is_sequence": kwargs.get("is_sequence", False),
        }

    elif file_format == ImportFormat.PLY:
        operator = "bpy.ops.wm.ply_import"
        post_scale = float(kwargs.get("global_scale", 1.0))
        options = {
            "filepath": filepath,
            "forward_axis": "NEGATIVE_Z",
            "up_axis": "Y",
        }

    elif file_format == ImportFormat.STL:
        operator = "bpy.ops.wm.stl_import"
        post_scale = float(kwargs.get("global_scale", 1.0))
        options = {
            "filepath": filepath,
            "forward_axis": "NEGATIVE_Z",
            "up_axis": "Y",
            "use_facet_normal": kwargs.get("use_facet_normal", False),
        }

    elif file_format == ImportFormat.BVH:
        operator = "bpy.ops.import_anim.bvh"
        options = {
            "filepath": filepath,
            "global_scale": kwargs.get("global_scale", 1.0),
        }

    elif file_format == ImportFormat.SVG:
        operator = "bpy.ops.import_curve.svg"
        post_scale = float(kwargs.get("global_scale", 1.0))
        options = {"filepath": filepath}

    elif file_format == ImportFormat.DXF:
        operator = "bpy.ops.import_scene.dxf"
        post_scale = float(kwargs.get("global_scale", 1.0))
        options = {"filepath": filepath}

    elif file_format == ImportFormat.BVH:
        operator = "bpy.ops.import_anim.bvh"
        options.setdefault("global_scale", 1.0)

    elif file_format == ImportFormat.SVG:
        operator = "bpy.ops.import_curve.svg"

    elif file_format == ImportFormat.DXF:
        operator = "bpy.ops.import_scene.dxf"

    elif file_format in (ImportFormat.XYZ, ImportFormat.E57, ImportFormat.LAS):
        # Point cloud formats require addons
        # Recommend: "Point Cloud Visualizer" or "E57 Importer" from Blender extensions
        return {
            "status": "ERROR",
            "error": f"Point cloud format {file_format} requires addon installation. "
            f"Install 'Point Cloud Visualizer' or import as PLY instead.",
            "hint": "Convert point cloud to PLY format, or use blender_addons to install a point cloud addon.",
        }

    else:
        return {"status": "ERROR", "error": f"Unsupported import format: {file_format}"}

    # Build the import command
    import_cmd = f"{operator}(**{options})"

    script = f"""
import os

def import_asset():
    # Store existing objects to determine what was imported
    existing_objects = set(bpy.data.objects)

    # Execute the import
    try:
        result = {import_cmd}
        if 'FINISHED' not in result:
            return {{
                'status': 'ERROR',
                'error': f'Import failed with result: {{result}}'
            }}
    except Exception as e:
        return {{
            'status': 'ERROR',
            'error': str(e)
        }}

    # Find newly imported objects
    imported_objects = list(set(bpy.data.objects) - existing_objects)

    # Unit scaling for native importers without a global_scale knob
    # (mm CAD exports -> metres). Scales mesh data directly: no context needed.
    if abs({post_scale} - 1.0) > 1e-12:
        import mathutils
        _m = mathutils.Matrix.Scale({post_scale}, 4)
        for _o in imported_objects:
            _d = getattr(_o, 'data', None)
            if _d is not None and hasattr(_d, 'vertices'):
                _d.transform(_m)
        _m = None

    return {{
        'status': 'SUCCESS',
        'imported_objects': [obj.name for obj in imported_objects],
        'applied_scale': {post_scale},
        'imported_meshes': [m.name for m in bpy.data.meshes if m.users > 0],
        'imported_materials': [m.name for m in bpy.data.materials if m.users > 0],
        'imported_textures': [t.name for t in bpy.data.images if t.users > 0],
        'filepath': r'{filepath}'
    }}

try:
    result = import_asset()
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(str(result))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to import file: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("link_asset", log_args=True)
async def link_asset(filepath: str, asset_name: str, link: bool = True, **kwargs: Any) -> dict[str, Any]:
    """Link or append an asset from another .blend file.

    Args:
        filepath: Path to the .blend file
        asset_name: Name of the asset to link/append
        link: If True, link the asset (default). If False, append it.
        **kwargs: Additional options
            - directory: Subdirectory in the .blend file (e.g., 'Object/', 'Material/')
            - relative_path: Use relative path if True (default: True)

    Returns:
        Dict containing link/append status and asset details
    """
    # Convert path to absolute and ensure it exists
    filepath = str(Path(filepath).absolute())
    directory = kwargs.get("directory", "Object/")
    relative = kwargs.get("relative_path", True)

    script = f"""
import os

def link_asset():
    # Store existing objects/materials to determine what was added
    existing_objects = set(bpy.data.objects)
    existing_materials = set(bpy.data.materials)

    # Determine if we're linking or appending
    operation = 'LINK' if {str(link).lower()} else 'APPEND'

    # Build the operator parameters
    params = {{
        'filepath': os.path.join(r'{directory}', '{asset_name}'),
        'filename': '{asset_name}',
        'directory': os.path.join(r'{filepath}', '{directory}'),
        'link': {str(link).lower()},
        'relative_path': {str(relative).lower()}
    }}

    # Execute the link/append operation
    try:
        if '{directory}'.startswith('Object'):
            result = bpy.ops.wm.link_append(**params, instance_collections=False, instance_object_data=True)
        elif '{directory}'.startswith('Collection'):
            result = bpy.ops.wm.link_append(**params, instance_collections=True, instance_object_data=False)
        else:
            result = bpy.ops.wm.link_append(**params)

        if 'FINISHED' not in result:
            return {{
                'status': 'ERROR',
                'error': f'{{operation}} failed with result: {{result}}'
            }}
    except Exception as e:
        return {{
            'status': 'ERROR',
            'error': str(e)
        }}

    # Find newly added objects/materials
    new_objects = [obj.name for obj in set(bpy.data.objects) - existing_objects]
    new_materials = [mat.name for mat in set(bpy.data.materials) - existing_materials]

    return {{
        'status': 'SUCCESS',
        'operation': operation,
        'asset_name': '{asset_name}',
        'filepath': r'{filepath}',
        'imported_objects': new_objects,
        'imported_materials': new_materials
    }}

try:
    result = link_asset()
except Exception as e:
    result = {{
        'status': 'ERROR',
        'error': str(e)
    }}

print(str(result))
"""

    try:
        output = await _executor.execute_script(script)
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to link/append asset: {e!s}")
        return {"status": "ERROR", "error": str(e)}

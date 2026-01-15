"""Import operations handler for Blender MCP."""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Union

from loguru import logger

from ..compat import *
from ..decorators import blender_operation
from ..utils.blender_executor import get_blender_executor

_executor = get_blender_executor()


class ImportFormat(str, Enum):
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
async def import_file(
    filepath: str, file_format: Union[ImportFormat, str], **kwargs: Any
) -> Dict[str, Any]:
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

    # Generate the import operator call based on format
    if file_format == ImportFormat.OBJ:
        operator = "bpy.ops.import_scene.obj"
        options.setdefault("use_split_objects", True)
        options.setdefault("use_split_groups", True)
        options.setdefault("global_scale", 1.0)

    elif file_format == ImportFormat.FBX:
        operator = "bpy.ops.import_scene.fbx"
        options.setdefault("use_manual_orientation", False)
        options.setdefault("global_scale", 1.0)
        options.setdefault("use_custom_normals", True)

    elif file_format in (ImportFormat.GLTF, ImportFormat.GLB, ImportFormat.VRM):
        # GLTF, GLB, and VRM all use the same importer
        operator = "bpy.ops.import_scene.gltf"
        options.setdefault("import_pack_images", True)
        options.setdefault("merge_vertices", False)
        options.setdefault("import_shading", "NORMAL")

    elif file_format == ImportFormat.COLLADA:
        operator = "bpy.ops.wm.collada_import"
        options.setdefault("import_units", False)
        options.setdefault("fix_orientation", False)

    elif file_format in (ImportFormat.USD, ImportFormat.USDA, ImportFormat.USDC, ImportFormat.USDZ):
        # All USD variants use the same importer
        operator = "bpy.ops.wm.usd_import"
        options.setdefault("import_meshes", True)
        options.setdefault("import_materials", True)
        options.setdefault("import_lights", True)
        options.setdefault("import_cameras", True)

    elif file_format == ImportFormat.ABC:
        operator = "bpy.ops.wm.alembic_import"
        options.setdefault("as_background_job", False)
        options.setdefault("is_sequence", False)

    elif file_format == ImportFormat.PLY:
        operator = "bpy.ops.wm.ply_import"
        options.setdefault("global_scale", 1.0)

    elif file_format == ImportFormat.STL:
        operator = "bpy.ops.wm.stl_import"
        options.setdefault("global_scale", 1.0)

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
            "hint": "Convert point cloud to PLY format, or use blender_addons to install a point cloud addon."
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
    
    return {{
        'status': 'SUCCESS',
        'imported_objects': [obj.name for obj in imported_objects],
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
        logger.error(f"Failed to import file: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("link_asset", log_args=True)
async def link_asset(
    filepath: str, asset_name: str, link: bool = True, **kwargs: Any
) -> Dict[str, Any]:
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
        logger.error(f"Failed to link/append asset: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

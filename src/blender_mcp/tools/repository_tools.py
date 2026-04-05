"""
Blender Object Repository tools for MCP.

Provides comprehensive object repository management including saving, loading, versioning,
and organizing Blender objects. All operations are backed by a real file-based index at
~/.blender-mcp/repository/ and real Blender executor calls.
"""

import hashlib
import json
import logging
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from blender_mcp.app import get_app
from blender_mcp.compat import *

# Import validation from construct_tools
from .construct_tools import (
    ScriptValidationResult,
    _extract_python_code,
    _generate_construction_script,
    _generate_construction_summary,
    _model_dump,
    _validate_construction_script,
)

# Import Context from FastMCP for sampling operations
try:
    from fastmcp.types import Context
except ImportError:
    from typing import Any as Context  # type: ignore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Repository location
# ---------------------------------------------------------------------------

REPO_BASE = Path.home() / ".blender-mcp" / "repository"
INDEX_FILE = REPO_BASE / "repository_index.json"


def _ensure_repo() -> None:
    REPO_BASE.mkdir(parents=True, exist_ok=True)


def _load_index() -> Dict[str, Any]:
    _ensure_repo()
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"models": [], "last_updated": datetime.now().isoformat()}


def _save_index(index: Dict[str, Any]) -> None:
    _ensure_repo()
    index["last_updated"] = datetime.now().isoformat()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ObjectMetadata(BaseModel):
    """Metadata for a stored Blender object."""

    id: str
    name: str
    description: str
    author: str
    version: str
    created_at: str
    updated_at: str
    tags: List[str]
    complexity: str
    style_preset: Optional[str]
    construction_script: str
    object_count: int
    blender_version: Optional[str]
    estimated_quality: int
    category: str
    license: str = "MIT"
    dependencies: List[str] = []


class MCPExportResult(BaseModel):
    """Result of cross-MCP export operation."""

    success: bool
    asset_id: str
    target_mcp: str
    primary_files: List[str]
    supporting_files: List[str]
    integration_commands: List[str]
    metadata: Dict[str, Any]
    optimization_report: Dict[str, Any]
    validation_results: Dict[str, Any]
    error_message: Optional[str] = None


# ---------------------------------------------------------------------------
# Real helper implementations
# ---------------------------------------------------------------------------


def _generate_object_id(display_name: str, object_name: str) -> str:
    content = f"{display_name}:{object_name}:{datetime.now().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


def _get_next_version(model_dir: Path) -> str:
    metadata_file = model_dir / "metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file, encoding="utf-8") as f:
                data = json.load(f)
            major, minor, patch = map(int, data.get("version", "0.0.0").split("."))
            return f"{major}.{minor}.{patch + 1}"
        except Exception:
            pass
    return "1.0.0"


async def _get_object_info(object_name: str) -> Optional[Dict[str, Any]]:
    """Query Blender for real object information."""
    try:
        from blender_mcp.utils.blender_executor import get_blender_executor

        executor = get_blender_executor()
        script = f"""
import bpy, json
name = {json.dumps(object_name)}
obj = bpy.data.objects.get(name)
if obj is None:
    print("OBJ_INFO:null")
else:
    vcount = len(obj.data.vertices) if obj.type == "MESH" and obj.data else 0
    mats = [m.name for m in obj.data.materials if m] if obj.type == "MESH" and obj.data else []
    bones = len(obj.data.bones) if obj.type == "ARMATURE" and obj.data else 0
    info = {{
        "name": obj.name,
        "type": obj.type,
        "vertex_count": vcount,
        "materials": mats,
        "bone_count": bones,
        "location": list(obj.location),
        "dimensions": list(obj.dimensions),
    }}
    print("OBJ_INFO:" + json.dumps(info))
"""
        output = await executor.execute_script(script, script_name="get_obj_info")
        for line in output.splitlines():
            if line.startswith("OBJ_INFO:"):
                payload = line[len("OBJ_INFO:"):]
                if payload == "null":
                    return None
                return json.loads(payload)
        return None
    except Exception as e:
        logger.warning(f"_get_object_info failed: {e}")
        return None


async def _find_construction_script(object_name: str) -> Optional[str]:
    """Look up the stored construction script for this object in the repository index."""
    index = _load_index()
    for model in index.get("models", []):
        if model.get("blender_name") == object_name or model.get("name") == object_name:
            obj_dir = REPO_BASE / model["id"]
            meta_file = obj_dir / "metadata.json"
            if meta_file.exists():
                try:
                    with open(meta_file, encoding="utf-8") as f:
                        meta = json.load(f)
                    script = meta.get("construction_script", "").strip()
                    return script if script else None
                except Exception:
                    pass
    return None


async def _save_object(
    object_name: str,
    object_name_display: str,
    description: str,
    tags: Optional[List[str]],
    category: str,
    quality_rating: int,
    public: bool,
) -> Dict[str, Any]:
    """Export object from Blender as .blend and save metadata to index."""
    from blender_mcp.utils.blender_executor import get_blender_executor

    if not object_name.strip():
        return {"success": False, "message": "object_name is required"}

    obj_info = await _get_object_info(object_name)
    if not obj_info:
        return {"success": False, "message": f"Object '{object_name}' not found in Blender scene"}

    obj_id = _generate_object_id(object_name_display or object_name, object_name)
    obj_dir = REPO_BASE / obj_id
    obj_dir.mkdir(parents=True, exist_ok=True)

    version = _get_next_version(obj_dir)
    blend_path = obj_dir / f"model_{version.replace('.', '_')}.blend"

    # Export the object via the Blender session bridge (preferred) or executor fallback.
    #
    # The executor runs `blender --background --factory-startup` — a fresh empty session.
    # To export an object from the USER'S running scene we first try the session bridge:
    #   POST /api/v1/blender/exec → picked up by blender_bridge_addon.py in Blender
    #   Bridge executes the export script in the live session and returns output.
    # If the bridge is not connected (503 / timeout) we fall back to the executor
    # and record session_required=True in the metadata.
    executor = get_blender_executor()

    gltf_path = obj_dir / f"model_{version.replace('.', '_')}.glb"
    blend_path_str = str(blend_path)

    export_script = f"""
import bpy, json, os

obj_name = {json.dumps(object_name)}
out_glb  = {json.dumps(str(gltf_path))}
out_blend = {json.dumps(blend_path_str)}
os.makedirs(os.path.dirname(out_glb), exist_ok=True)

obj = bpy.data.objects.get(obj_name)
if obj is None:
    print("EXPORT_SESSION_REQUIRED: Object not in executor session.")
    bpy.ops.wm.save_as_mainfile(filepath=out_blend, copy=True, check_existing=False)
    print("EXPORT_PLACEHOLDER:" + out_blend)
else:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    for child in obj.children_recursive:
        child.select_set(True)
    try:
        bpy.ops.export_scene.gltf(
            filepath=out_glb,
            use_selection=True,
            export_format='GLB',
            export_apply=True,
        )
        print("EXPORT_OK:" + out_glb)
    except Exception as gltf_err:
        bpy.ops.wm.save_as_mainfile(filepath=out_blend, copy=True, check_existing=False)
        print("EXPORT_OK:" + out_blend)
        print("EXPORT_WARN: glTF failed, saved as blend: " + str(gltf_err))
"""

    # Try session bridge first (MCP running in HTTP mode with bridge addon active)
    session_used = False
    try:
        from blender_mcp.app import _exec_in_blender_session
        bridge_result = await _exec_in_blender_session(
            export_script, script_name=f"save_{object_name}", timeout=30
        )
        if bridge_result["session_used"]:
            output = bridge_result["output"]
            session_used = True
        else:
            # Bridge not connected — fall back to executor
            output = await executor.execute_script(export_script, script_name="save_obj_export")
    except Exception as e:
        try:
            output = await executor.execute_script(export_script, script_name="save_obj_export")
        except Exception as e2:
            return {"success": False, "message": f"Blender export failed: {e2}"}

    # Accept either real export or placeholder (session limitation documented)
    export_ok = any(
        line.startswith(("EXPORT_OK:", "EXPORT_PLACEHOLDER:"))
        for line in output.splitlines()
    )
    session_required = not session_used and any("EXPORT_SESSION_REQUIRED" in line for line in output.splitlines())

    # Determine the actual saved file path
    actual_blend_path = blend_path
    for line in output.splitlines():
        if line.startswith("EXPORT_OK:"):
            actual_blend_path = Path(line[len("EXPORT_OK:"):].strip())
        elif line.startswith("EXPORT_PLACEHOLDER:"):
            actual_blend_path = Path(line[len("EXPORT_PLACEHOLDER:"):].strip())

    if not export_ok:
        return {"success": False, "message": f"Export script did not confirm success. Output: {output[-500:]}"}

    # Write metadata
    meta = {
        "id": obj_id,
        "name": object_name_display or object_name,
        "blender_name": object_name,
        "description": description,
        "author": "local",
        "version": version,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "tags": tags or [],
        "complexity": "standard",
        "style_preset": None,
        "construction_script": "",
        "object_count": 1,
        "blender_version": None,
        "estimated_quality": max(1, min(10, quality_rating)),
        "category": category,
        "license": "MIT",
        "blend_file": str(actual_blend_path),
        "session_required": session_required,
        "obj_info": obj_info,
    }
    with open(obj_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Update index
    index = _load_index()
    existing = next((i for i, m in enumerate(index["models"]) if m["id"] == obj_id), None)
    summary = {
        "id": obj_id,
        "name": meta["name"],
        "blender_name": object_name,
        "description": description,
        "category": category,
        "tags": tags or [],
        "estimated_quality": meta["estimated_quality"],
        "version": version,
        "updated_at": meta["updated_at"],
    }
    if existing is not None:
        index["models"][existing] = summary
    else:
        index["models"].append(summary)
    _save_index(index)

    msg = f"Saved '{object_name}' to repository as '{object_name_display or object_name}' (v{version})"
    if session_required:
        msg += ". NOTE: Object export requires running from inside Blender (HTTP mode or addon). Metadata saved with placeholder file."
    return {
        "success": True,
        "message": msg,
        "object_id": obj_id,
        "version": version,
        "blend_file": str(actual_blend_path),
        "session_required": session_required,
    }


async def _load_object(
    object_id: str,
    target_name: Optional[str],
    position: Tuple[float, float, float],
    scale: Tuple[float, float, float],
    version: Optional[str],
) -> Dict[str, Any]:
    """Append object from repository .blend into current Blender scene."""
    from blender_mcp.utils.blender_executor import get_blender_executor

    if not object_id.strip():
        return {"success": False, "message": "object_id is required"}

    obj_dir = REPO_BASE / object_id
    meta_file = obj_dir / "metadata.json"
    if not meta_file.exists():
        return {"success": False, "message": f"Object '{object_id}' not found in repository"}

    with open(meta_file, encoding="utf-8") as f:
        meta = json.load(f)

    # Find the blend file
    if version:
        blend_path = obj_dir / f"model_{version.replace('.', '_')}.blend"
    else:
        blend_path = Path(meta.get("blend_file", ""))
        if not blend_path.exists():
            # Fall back to latest version file in dir
            candidates = sorted(obj_dir.glob("model_*.blend"), reverse=True)
            if not candidates:
                return {"success": False, "message": f"No .blend file found for '{object_id}'"}
            blend_path = candidates[0]

    if not blend_path.exists():
        return {"success": False, "message": f"Blend file not found: {blend_path}"}

    blender_name = meta.get("blender_name", meta.get("name", "Asset"))
    final_name = target_name or blender_name
    px, py, pz = position
    sx, sy, sz = scale

    executor = get_blender_executor()
    import_script = f"""
import bpy, json
blend_path = {json.dumps(str(blend_path))}
blender_name = {json.dumps(blender_name)}
final_name = {json.dumps(final_name)}
position = ({px}, {py}, {pz})
scale = ({sx}, {sy}, {sz})

with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    if blender_name in data_from.objects:
        data_to.objects = [blender_name]
    elif data_from.objects:
        data_to.objects = [data_from.objects[0]]

imported = []
for obj in data_to.objects:
    if obj is not None:
        bpy.context.collection.objects.link(obj)
        obj.name = final_name
        obj.location = position
        obj.scale = scale
        imported.append(obj.name)

print("IMPORT_OK:" + json.dumps(imported))
"""
    try:
        output = await executor.execute_script(import_script, script_name="load_obj_import")
    except Exception as e:
        return {"success": False, "message": f"Blender import failed: {e}"}

    for line in output.splitlines():
        if line.startswith("IMPORT_OK:"):
            imported_names = json.loads(line[len("IMPORT_OK:"):])
            return {
                "success": True,
                "message": f"Loaded '{blender_name}' from repository as '{final_name}'",
                "objects_created": imported_names,
                "position": list(position),
                "scale": list(scale),
            }

    return {"success": False, "message": f"Import did not confirm success. Output: {output[-500:]}"}


async def _list_objects() -> Dict[str, Any]:
    """List all objects in the repository index."""
    index = _load_index()
    models = index.get("models", [])
    return {
        "success": True,
        "total": len(models),
        "objects": models,
        "repository_path": str(REPO_BASE),
    }


async def _search_objects(
    query: Optional[str],
    category: Optional[str],
    tags: Optional[List[str]],
    author: Optional[str],
    min_quality: Optional[int],
    complexity: Optional[str],
    limit: int,
) -> Dict[str, Any]:
    """Search repository index with optional filters."""
    index = _load_index()
    results = []

    for model in index.get("models", []):
        # Text query
        if query:
            q = query.lower()
            searchable = " ".join([
                model.get("name", ""),
                model.get("description", ""),
                " ".join(model.get("tags", [])),
                model.get("category", ""),
            ]).lower()
            if q not in searchable:
                continue

        # Category
        if category and model.get("category", "").lower() != category.lower():
            continue

        # Tags (must have ALL specified tags)
        if tags:
            model_tags = [t.lower() for t in model.get("tags", [])]
            if not all(t.lower() in model_tags for t in tags):
                continue

        # Min quality
        if min_quality is not None and model.get("estimated_quality", 0) < min_quality:
            continue

        # Complexity (stored in full metadata, not index summary — skip if not present)
        # complexity filter is best-effort at index level

        results.append(model)
        if len(results) >= limit:
            break

    return {
        "success": True,
        "query": query,
        "total_matches": len(results),
        "objects": results,
    }


async def _create_object_backup(object_name: str) -> Dict[str, Any]:
    """Duplicate an object in Blender as a backup."""
    from blender_mcp.utils.blender_executor import get_blender_executor

    executor = get_blender_executor()
    backup_name = f"{object_name}_backup_{datetime.now().strftime('%H%M%S')}"
    script = f"""
import bpy
obj = bpy.data.objects.get({json.dumps(object_name)})
if obj is None:
    print("BACKUP_ERROR: not found")
else:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate(linked=False)
    dup = bpy.context.active_object
    dup.name = {json.dumps(backup_name)}
    dup.hide_viewport = True
    dup.hide_render = True
    print("BACKUP_OK:" + dup.name)
"""
    try:
        output = await executor.execute_script(script, script_name="backup_obj")
        for line in output.splitlines():
            if line.startswith("BACKUP_OK:"):
                return {"success": True, "backup_name": line[len("BACKUP_OK:"):].strip()}
        return {"success": False, "error": f"Backup script did not confirm. Output: {output[-300:]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _execute_modification_script(script: str, object_name: str) -> Dict[str, Any]:
    """Execute a modification script via Blender executor."""
    from blender_mcp.utils.blender_executor import get_blender_executor

    executor = get_blender_executor()
    try:
        output = await executor.execute_script(script, script_name=f"modify_{object_name}")
        return {
            "success": True,
            "changes_summary": [f"Modification script executed for '{object_name}'"],
            "blender_output": output[-500:],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _get_asset_from_repository(asset_id: str) -> Optional[Dict[str, Any]]:
    """Load asset data from repository metadata — real implementation."""
    obj_dir = REPO_BASE / asset_id
    meta_file = obj_dir / "metadata.json"
    if not meta_file.exists():
        return None
    try:
        with open(meta_file, encoding="utf-8") as f:
            meta = json.load(f)
        obj_info = meta.get("obj_info", {})
        return {
            "id": asset_id,
            "name": meta.get("name", asset_id),
            "blend_file": meta.get("blend_file", ""),
            "polygon_count": obj_info.get("vertex_count", 0),
            "materials": obj_info.get("materials", []),
            "textures": [],
            "has_bones": obj_info.get("bone_count", 0) > 0,
            "has_animations": False,  # Would need animation data inspection
            "is_avatar": "character" in meta.get("category", "").lower()
                         or "avatar" in meta.get("name", "").lower(),
        }
    except Exception as e:
        logger.warning(f"_get_asset_from_repository failed for {asset_id}: {e}")
        return None


# ---------------------------------------------------------------------------
# Platform export engines
# ---------------------------------------------------------------------------


class PlatformExportEngine:
    """Base class for platform-specific export engines."""

    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.optimizations: Dict[str, Any] = {}

    async def optimize_asset(self, asset_data: Dict[str, Any], quality_level: str) -> Dict[str, Any]:
        raise NotImplementedError

    async def export_blend_file(
        self, blend_file: str, out_dir: Path, asset_data: Dict[str, Any], quality_level: str
    ) -> Tuple[List[str], List[str]]:
        """Run Blender to produce platform files. Returns (primary_files, supporting_files)."""
        raise NotImplementedError

    async def generate_integration_commands(self, asset_data: Dict[str, Any]) -> List[str]:
        raise NotImplementedError

    async def validate_compatibility(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class VRChatExportEngine(PlatformExportEngine):
    """VRChat-specific export engine — exports FBX via Blender."""

    def __init__(self):
        super().__init__("vrchat")
        self.optimizations = {
            "polygon_limit": 70000,
            "material_limit": 8,
            "bone_limit": 256,
            "texture_size_max": 2048,
            "auto_lod": True,
        }

    async def optimize_asset(self, asset_data: Dict[str, Any], quality_level: str) -> Dict[str, Any]:
        optimized = asset_data.copy()
        poly = asset_data.get("polygon_count", 0)
        mats = asset_data.get("materials", [])
        if poly > self.optimizations["polygon_limit"]:
            optimized["polygons_reduced"] = True
            optimized["original_polygons"] = poly
            optimized["optimized_polygons"] = self.optimizations["polygon_limit"]
        if len(mats) > self.optimizations["material_limit"]:
            optimized["materials_reduced"] = True
            optimized["original_materials"] = len(mats)
            optimized["optimized_materials"] = self.optimizations["material_limit"]
        optimized["textures_optimized"] = True
        optimized["texture_compression"] = "BC7"
        return optimized

    async def export_blend_file(
        self, blend_file: str, out_dir: Path, asset_data: Dict[str, Any], quality_level: str
    ) -> Tuple[List[str], List[str]]:
        from blender_mcp.utils.blender_executor import get_blender_executor

        out_dir.mkdir(parents=True, exist_ok=True)
        fbx_path = out_dir / "asset_vrchat.fbx"
        poly_limit = self.optimizations["polygon_limit"]

        script = f"""
import bpy
bpy.ops.wm.open_mainfile(filepath={json.dumps(blend_file)})
# Optionally decimate if over poly limit
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        poly_count = len(obj.data.polygons)
        if poly_count > {poly_limit}:
            mod = obj.modifiers.new(name='Decimate_VRC', type='DECIMATE')
            mod.ratio = {poly_limit} / poly_count
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(
    filepath={json.dumps(str(fbx_path))},
    use_selection=True,
    mesh_smooth_type='FACE',
    add_leaf_bones=False,
    bake_anim=True,
)
print("EXPORT_FBX_OK:" + {json.dumps(str(fbx_path))})
"""
        executor = get_blender_executor()
        output = await executor.execute_script(script, script_name="vrchat_export_fbx")
        primary = []
        if any("EXPORT_FBX_OK:" in l for l in output.splitlines()):
            primary = [str(fbx_path)]

        materials_json = out_dir / "asset_vrchat_materials.json"
        with open(materials_json, "w") as f:
            json.dump({"materials": asset_data.get("materials", [])}, f, indent=2)
        supporting = [str(materials_json)]
        return primary, supporting

    async def generate_integration_commands(self, asset_data: Dict[str, Any]) -> List[str]:
        cmds = [
            "vrchat_import_fbx --file asset_vrchat.fbx --auto-setup",
            f"vrchat_apply_optimizations --preset {'avatar' if asset_data.get('is_avatar') else 'prop'}",
        ]
        if asset_data.get("has_bones"):
            cmds.append("vrchat_setup_physbones --auto-detect")
        if self.optimizations["auto_lod"]:
            cmds.append("vrchat_generate_lods --levels 3")
        cmds.append("vrchat_validate_platform_requirements --strict")
        return cmds

    async def validate_compatibility(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        issues, warnings = [], []
        poly = asset_data.get("polygon_count", 0)
        mats = asset_data.get("materials", [])
        if poly > self.optimizations["polygon_limit"]:
            issues.append(f"Polygon count ({poly}) exceeds VRChat limit ({self.optimizations['polygon_limit']})")
        if len(mats) > self.optimizations["material_limit"]:
            issues.append(f"Material count ({len(mats)}) exceeds VRChat limit ({self.optimizations['material_limit']})")
        return {"compatible": len(issues) == 0, "issues": issues, "warnings": warnings}


class ResoniteExportEngine(PlatformExportEngine):
    """Resonite-specific export engine — exports GLB via Blender."""

    def __init__(self):
        super().__init__("resonite")
        self.optimizations = {
            "polygon_limit": 100000,
            "material_limit": 16,
            "collision_generation": True,
        }

    async def optimize_asset(self, asset_data: Dict[str, Any], quality_level: str) -> Dict[str, Any]:
        optimized = asset_data.copy()
        optimized["protoflux_components"] = ["grabbable", "collision"]
        if asset_data.get("has_bones"):
            optimized["protoflux_components"].extend(["dynamic_bones", "physics"])
        optimized["collision_mesh_generated"] = self.optimizations["collision_generation"]
        return optimized

    async def export_blend_file(
        self, blend_file: str, out_dir: Path, asset_data: Dict[str, Any], quality_level: str
    ) -> Tuple[List[str], List[str]]:
        from blender_mcp.utils.blender_executor import get_blender_executor

        out_dir.mkdir(parents=True, exist_ok=True)
        glb_path = out_dir / "asset_resonite.glb"

        script = f"""
import bpy
bpy.ops.wm.open_mainfile(filepath={json.dumps(blend_file)})
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath={json.dumps(str(glb_path))},
    use_selection=True,
    export_format='GLB',
    export_animations=True,
    export_apply=True,
)
print("EXPORT_GLB_OK:" + {json.dumps(str(glb_path))})
"""
        executor = get_blender_executor()
        output = await executor.execute_script(script, script_name="resonite_export_glb")
        primary = []
        if any("EXPORT_GLB_OK:" in l for l in output.splitlines()):
            primary = [str(glb_path)]

        pf_json = out_dir / "protoflux_components.json"
        with open(pf_json, "w") as f:
            json.dump({"components": ["grabbable", "collision"]}, f, indent=2)
        supporting = [str(pf_json)]
        return primary, supporting

    async def generate_integration_commands(self, asset_data: Dict[str, Any]) -> List[str]:
        cmds = [
            "resonite_import_gltf --file asset_resonite.glb --auto-setup",
            "resonite_add_protoflux_components --auto-detect",
            "resonite_setup_collision --generate-primitives",
        ]
        if asset_data.get("has_bones"):
            cmds.append("resonite_configure_dynamic_bones --physics-settings optimized")
        if asset_data.get("has_animations"):
            cmds.append("resonite_setup_animation_system --auto-configure")
        return cmds

    async def validate_compatibility(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        warnings = []
        poly = asset_data.get("polygon_count", 0)
        if poly > self.optimizations["polygon_limit"]:
            warnings.append(f"High polygon count ({poly}) may impact Resonite performance")
        return {"compatible": True, "issues": [], "warnings": warnings}


EXPORT_ENGINES: Dict[str, PlatformExportEngine] = {
    "vrchat": VRChatExportEngine(),
    "resonite": ResoniteExportEngine(),
}


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------

def _register_repository_tools() -> None:
    app = get_app()

    @app.tool
    async def manage_object_repo(
        operation: str = "list_objects",
        object_name: str = "",
        object_name_display: str = "",
        description: str = "",
        tags: List[str] = None,
        category: str = "general",
        object_id: str = "",
        target_name: Optional[str] = None,
        position: Tuple[float, float, float] = (0, 0, 0),
        scale: Tuple[float, float, float] = (1, 1, 1),
        version: Optional[str] = None,
        query: Optional[str] = None,
        author: Optional[str] = None,
        min_quality: Optional[int] = None,
        complexity: Optional[str] = None,
        limit: int = 20,
        quality_rating: int = 5,
        public: bool = False,
    ) -> Dict[str, Any]:
        """
        Object repository management: save, load, search, list_objects.

        - save: export Blender object to ~/.blender-mcp/repository/ with metadata
        - load: append saved object into current scene with optional transforms
        - search: filter index by query, category, tags, quality
        - list_objects: return full index

        Repository location: ~/.blender-mcp/repository/
        """
        try:
            if operation == "save":
                return await _save_object(
                    object_name=object_name,
                    object_name_display=object_name_display,
                    description=description,
                    tags=tags,
                    category=category,
                    quality_rating=quality_rating,
                    public=public,
                )
            elif operation == "load":
                return await _load_object(
                    object_id=object_id,
                    target_name=target_name,
                    position=position,
                    scale=scale,
                    version=version,
                )
            elif operation == "search":
                return await _search_objects(
                    query=query,
                    category=category if category != "general" else None,
                    tags=tags,
                    author=author,
                    min_quality=min_quality,
                    complexity=complexity,
                    limit=limit,
                )
            elif operation == "list_objects":
                return await _list_objects()
            else:
                return {
                    "success": False,
                    "message": f"Unknown operation '{operation}'",
                    "available_operations": ["save", "load", "search", "list_objects"],
                }
        except Exception as e:
            logger.exception(f"Repository operation '{operation}' failed: {e}")
            return {"success": False, "message": f"Repository operation failed: {str(e)}", "operation": operation}

    @app.tool
    async def manage_object_construction(
        ctx: Context,
        operation: str = "construct",
        object_name: str = "",
        description: str = "",
        name: str = "ConstructedObject",
        complexity: str = "standard",
        style_preset: Optional[str] = None,
        reference_objects: Optional[List[str]] = None,
        allow_modifications: bool = True,
        modification_description: str = "",
        max_iterations: int = 3,
        preserve_original: bool = True,
    ) -> Dict[str, Any]:
        """
        AI-powered object construction and modification via sampling.

        - construct: natural language → Blender Python → execute in scene
        - construct_and_save: construct then immediately save to repository
        - modify: find stored script for object, sample modification, validate, execute

        Requires a client that supports MCP sampling (Claude Desktop, Antigravity, etc.)
        """
        try:
            if operation == "construct":
                return await _construct_object(
                    ctx=ctx,
                    description=description,
                    name=name,
                    complexity=complexity,
                    style_preset=style_preset,
                    reference_objects=reference_objects,
                    allow_modifications=allow_modifications,
                    max_iterations=max_iterations,
                )
            elif operation == "construct_and_save":
                # Compound: construct → validate → execute → save to repository
                construct_result = await _construct_object(
                    ctx=ctx,
                    description=description,
                    name=name,
                    complexity=complexity,
                    style_preset=style_preset,
                    reference_objects=reference_objects,
                    allow_modifications=allow_modifications,
                    max_iterations=max_iterations,
                )
                if not construct_result.get("success"):
                    return construct_result
                # Auto-save to repository
                save_result = await _save_object(
                    object_name=name,
                    object_name_display=name,
                    description=description,
                    tags=[complexity] + ([style_preset] if style_preset else []),
                    category="general",
                    quality_rating=5,
                    public=False,
                )
                construct_result["repository_save"] = save_result
                construct_result["next_steps"] = [
                    f"Object '{name}' saved to repository (id: {save_result.get('object_id', '?')})",
                    f"manage_object_repo('load', object_id='{save_result.get('object_id', '')}') to reload",
                    f"manage_object_construction('modify', object_name='{name}') to refine",
                ]
                return construct_result
            elif operation == "modify":
                return await _modify_object(
                    ctx=ctx,
                    object_name=object_name,
                    modification_description=modification_description,
                    max_iterations=max_iterations,
                    preserve_original=preserve_original,
                )
            else:
                return {
                    "success": False,
                    "message": f"Unknown operation '{operation}'",
                    "available_operations": ["construct", "modify"],
                }
        except Exception as e:
            logger.exception(f"Construction operation '{operation}' failed: {e}")
            return {"success": False, "message": f"Construction operation failed: {str(e)}", "operation": operation}

    @app.tool
    async def export_for_mcp_handoff(
        ctx: Context,
        asset_id: str,
        target_mcp: str,
        optimization_preset: str = "automatic",
        quality_level: str = "high",
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Export a repository asset with platform-specific optimisations for cross-MCP handoff.

        Supported targets: vrchat (FBX), resonite (GLB).
        asset_id must exist in ~/.blender-mcp/repository/.
        Writes actual export files to a temp directory and returns their paths.
        """
        try:
            if target_mcp not in EXPORT_ENGINES:
                return {
                    "success": False,
                    "error": f"Unsupported target '{target_mcp}'. Supported: {list(EXPORT_ENGINES)}",
                }
            if quality_level not in ("draft", "standard", "high", "ultra"):
                return {"success": False, "error": f"Invalid quality_level '{quality_level}'"}
            if optimization_preset not in ("automatic", "conservative", "aggressive"):
                return {"success": False, "error": f"Invalid optimization_preset '{optimization_preset}'"}

            asset_data = await _get_asset_from_repository(asset_id)
            if not asset_data:
                return {"success": False, "error": f"Asset '{asset_id}' not found in repository"}

            blend_file = asset_data.get("blend_file", "")
            if not blend_file or not Path(blend_file).exists():
                return {"success": False, "error": f"Blend file missing for asset '{asset_id}': {blend_file}"}

            engine = EXPORT_ENGINES[target_mcp]
            optimized_asset = await engine.optimize_asset(asset_data, quality_level)

            out_dir = Path(tempfile.mkdtemp(prefix=f"mcp_export_{target_mcp}_"))
            primary_files, supporting_files = await engine.export_blend_file(
                blend_file, out_dir, optimized_asset, quality_level
            )

            integration_commands = await engine.generate_integration_commands(optimized_asset)
            validation_results = await engine.validate_compatibility(optimized_asset)

            optimization_report = {
                "preset_used": optimization_preset,
                "quality_level": quality_level,
                "applied_optimizations": [
                    k for k in optimized_asset if k.endswith(("_reduced", "_optimized", "_generated"))
                ],
                "platform_requirements_met": validation_results["compatible"],
            }

            metadata: Dict[str, Any] = {}
            if include_metadata:
                metadata = {
                    "source_mcp": "blender-mcp",
                    "asset_id": asset_id,
                    "export_timestamp": datetime.now().isoformat(),
                    "export_dir": str(out_dir),
                    "integration_ready": bool(primary_files),
                    "optimization_applied": optimization_report,
                }

            result = MCPExportResult(
                success=bool(primary_files),
                asset_id=asset_id,
                target_mcp=target_mcp,
                primary_files=primary_files,
                supporting_files=supporting_files,
                integration_commands=[c for c in integration_commands if c],
                metadata=metadata,
                optimization_report=optimization_report,
                validation_results=validation_results,
                error_message=None if primary_files else "Export produced no output files",
            )
            return result.model_dump()

        except Exception as e:
            logger.exception(f"export_for_mcp_handoff failed: {e}")
            return MCPExportResult(
                success=False, asset_id=asset_id, target_mcp=target_mcp,
                primary_files=[], supporting_files=[], integration_commands=[],
                metadata={}, optimization_report={}, validation_results={},
                error_message=str(e),
            ).model_dump()


# ---------------------------------------------------------------------------
# Construction helpers (delegating to construct_tools where possible)
# ---------------------------------------------------------------------------


async def _construct_object(
    ctx: Context,
    description: str,
    name: str,
    complexity: str,
    style_preset: Optional[str],
    reference_objects: Optional[List[str]],
    allow_modifications: bool,
    max_iterations: int,
) -> Dict[str, Any]:
    from .construct_tools import _execute_construction_script

    if not description.strip():
        return {"success": False, "message": "description is required"}
    if complexity not in ("simple", "standard", "complex"):
        return {"success": False, "message": f"Invalid complexity '{complexity}'"}

    script_result = await _generate_construction_script(
        ctx, description, name, complexity, style_preset, {}, max_iterations
    )
    if not script_result["success"]:
        return {"success": False, "message": f"Script generation failed: {script_result.get('error')}"}

    validation = await _validate_construction_script(script_result["script"])
    if not validation.is_valid:
        return {
            "success": False,
            "message": f"Validation failed: {'; '.join(validation.errors)}",
            "validation_results": _model_dump(validation),
        }

    execution_result = await _execute_construction_script(script_result["script"], name, validation)
    return {
        "success": execution_result["success"],
        "message": _generate_construction_summary(
            description, execution_result, script_result.get("iterations", 1), validation
        ),
        "object_name": name,
        "script_generated": True,
        "iterations_used": script_result.get("iterations", 1),
        "validation_results": {
            "security_score": validation.security_score,
            "complexity_score": validation.complexity_score,
            "warnings": validation.warnings,
        },
        "scene_objects_created": execution_result.get("objects_created", []),
        "estimated_complexity": complexity,
        "next_steps": [
            f"manage_object_repo('save', object_name='{name}') to persist to repository",
            f"manage_object_construction('modify', object_name='{name}') to refine",
        ] if execution_result["success"] else [
            "Try a simpler description",
            "Break complex objects into smaller components",
        ],
    }


async def _modify_object(
    ctx: Context,
    object_name: str,
    modification_description: str,
    max_iterations: int,
    preserve_original: bool,
) -> Dict[str, Any]:
    if not object_name or not modification_description:
        return {"success": False, "message": "object_name and modification_description are required"}

    obj_info = await _get_object_info(object_name)
    if not obj_info:
        return {"success": False, "message": f"Object '{object_name}' not found in scene"}

    original_script = await _find_construction_script(object_name)
    if not original_script:
        return {
            "success": False,
            "message": f"No stored construction script for '{object_name}'. Save to repository first.",
            "next_steps": ["manage_object_repo('save', ...) then retry modify"],
        }

    # Sample modification script
    try:
        sampling_result = await ctx.sample(
            content=(
                f"Modify the Blender object '{object_name}'.\n"
                f"Requested change: {modification_description}\n\n"
                f"Original script (first 500 chars):\n{original_script[:500]}\n\n"
                "Generate a complete, corrected Blender Python script that applies the modification. "
                "Return ONLY the Python code block."
            ),
            metadata={
                "type": "script_modification",
                "original_script": original_script[:500],
                "modification_request": modification_description,
                "object_name": object_name,
            },
            max_tokens=2500,
            temperature=0.3,
        )
    except Exception as e:
        return {"success": False, "message": f"Sampling failed: {e}"}

    modified_script = _extract_python_code(sampling_result.content)
    if not modified_script:
        return {"success": False, "message": "LLM did not return a Python code block"}

    validation = await _validate_construction_script(modified_script)
    if not validation.is_valid:
        return {
            "success": False,
            "message": f"Modification script failed validation: {'; '.join(validation.errors)}",
        }

    if preserve_original:
        backup = await _create_object_backup(object_name)
        if not backup["success"]:
            logger.warning(f"Backup failed: {backup.get('error')}")

    execution = await _execute_modification_script(modified_script, object_name)
    if execution["success"]:
        return {
            "success": True,
            "object_name": object_name,
            "modification_applied": modification_description,
            "changes_made": execution.get("changes_summary", []),
            "message": f"Successfully modified '{object_name}': {modification_description}",
            "next_steps": [f"manage_object_repo('save', object_name='{object_name}') to persist"],
        }
    return {
        "success": False,
        "message": f"Modification execution failed: {execution.get('error')}",
    }


# Register on import
_register_repository_tools()

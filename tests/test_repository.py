"""
Unit tests for the object repository helpers.

Uses a mock BlenderExecutor so no Blender installation is needed.
Tests cover: save, load, list, search, get_object_info, find_construction_script.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def repo_dir(tmp_path: Path) -> Path:
    """Isolated repository directory for each test."""
    return tmp_path / "repository"


@pytest.fixture(autouse=True)
def patch_repo_base(repo_dir: Path, monkeypatch):
    """Redirect REPO_BASE and INDEX_FILE to temp dir."""
    import blender_mcp.tools.repository_tools as rt
    monkeypatch.setattr(rt, "REPO_BASE", repo_dir)
    monkeypatch.setattr(rt, "INDEX_FILE", repo_dir / "repository_index.json")


def make_executor(output: str) -> MagicMock:
    """Create a mock executor that returns the given output string."""
    executor = MagicMock()
    executor.execute_script = AsyncMock(return_value=output)
    return executor


# ---------------------------------------------------------------------------
# _get_object_info
# ---------------------------------------------------------------------------

class TestGetObjectInfo:
    @pytest.mark.asyncio
    async def test_found(self, monkeypatch):
        info = {"name": "Cube", "type": "MESH", "vertex_count": 8, "materials": ["Mat"], "bone_count": 0, "location": [0, 0, 0], "dimensions": [2, 2, 2]}
        executor = make_executor(f'OBJ_INFO:{json.dumps(info)}')
        with patch("blender_mcp.tools.repository_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.repository_tools import _get_object_info
            result = await _get_object_info("Cube")
        assert result is not None
        assert result["vertex_count"] == 8
        assert result["type"] == "MESH"

    @pytest.mark.asyncio
    async def test_not_found(self):
        executor = make_executor("OBJ_INFO:null")
        with patch("blender_mcp.tools.repository_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.repository_tools import _get_object_info
            result = await _get_object_info("DoesNotExist")
        assert result is None

    @pytest.mark.asyncio
    async def test_executor_error(self):
        executor = MagicMock()
        executor.execute_script = AsyncMock(side_effect=RuntimeError("Blender not found"))
        with patch("blender_mcp.tools.repository_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.repository_tools import _get_object_info
            result = await _get_object_info("Cube")
        assert result is None


# ---------------------------------------------------------------------------
# _save_object
# ---------------------------------------------------------------------------

class TestSaveObject:
    @pytest.mark.asyncio
    async def test_save_success(self, repo_dir: Path):
        obj_info = {"name": "Robot", "type": "MESH", "vertex_count": 500, "materials": ["Steel"], "bone_count": 0, "location": [0, 0, 0], "dimensions": [1, 2, 1]}
        info_output = f"OBJ_INFO:{json.dumps(obj_info)}"
        export_output = "EXPORT_OK:/tmp/fake.blend"

        executor = MagicMock()
        executor.execute_script = AsyncMock(side_effect=[info_output, export_output])

        with patch("blender_mcp.tools.repository_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.repository_tools import _save_object
            result = await _save_object(
                object_name="Robot",
                object_name_display="My Robot",
                description="A test robot",
                tags=["robot", "test"],
                category="scifi",
                quality_rating=8,
                public=False,
            )

        assert result["success"] is True
        assert "object_id" in result
        obj_id = result["object_id"]

        # Check index was written
        index_file = repo_dir / "repository_index.json"
        assert index_file.exists()
        with open(index_file) as f:
            index = json.load(f)
        assert len(index["models"]) == 1
        assert index["models"][0]["id"] == obj_id
        assert index["models"][0]["name"] == "My Robot"

        # Check metadata file
        meta_file = repo_dir / obj_id / "metadata.json"
        assert meta_file.exists()
        with open(meta_file) as f:
            meta = json.load(f)
        assert meta["estimated_quality"] == 8
        assert "robot" in meta["tags"]

    @pytest.mark.asyncio
    async def test_save_object_not_found(self):
        executor = make_executor("OBJ_INFO:null")
        with patch("blender_mcp.tools.repository_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.repository_tools import _save_object
            result = await _save_object("Ghost", "Ghost", "", [], "general", 5, False)
        assert result["success"] is False
        assert "not found" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_save_empty_name(self):
        from blender_mcp.tools.repository_tools import _save_object
        result = await _save_object("", "", "", [], "general", 5, False)
        assert result["success"] is False


# ---------------------------------------------------------------------------
# _list_objects / _search_objects
# ---------------------------------------------------------------------------

class TestListAndSearch:
    def _write_index(self, repo_dir: Path, models: list) -> None:
        import blender_mcp.tools.repository_tools as rt
        repo_dir.mkdir(parents=True, exist_ok=True)
        index = {"models": models, "last_updated": "2026-01-01T00:00:00"}
        with open(rt.INDEX_FILE, "w") as f:
            json.dump(index, f)

    @pytest.mark.asyncio
    async def test_list_empty(self):
        from blender_mcp.tools.repository_tools import _list_objects
        result = await _list_objects()
        assert result["success"] is True
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_list_with_objects(self, repo_dir: Path):
        self._write_index(repo_dir, [
            {"id": "abc1", "name": "Chair", "category": "furniture", "tags": ["wood"], "estimated_quality": 7},
            {"id": "abc2", "name": "Robot", "category": "scifi", "tags": ["metal", "robot"], "estimated_quality": 9},
        ])
        from blender_mcp.tools.repository_tools import _list_objects
        result = await _list_objects()
        assert result["total"] == 2

    @pytest.mark.asyncio
    async def test_search_by_query(self, repo_dir: Path):
        self._write_index(repo_dir, [
            {"id": "abc1", "name": "Wooden Chair", "category": "furniture", "tags": ["wood"], "estimated_quality": 7, "description": ""},
            {"id": "abc2", "name": "Robot", "category": "scifi", "tags": ["metal"], "estimated_quality": 9, "description": ""},
        ])
        from blender_mcp.tools.repository_tools import _search_objects
        result = await _search_objects(query="chair", category=None, tags=None, author=None, min_quality=None, complexity=None, limit=10)
        assert result["total_matches"] == 1
        assert result["objects"][0]["id"] == "abc1"

    @pytest.mark.asyncio
    async def test_search_by_min_quality(self, repo_dir: Path):
        self._write_index(repo_dir, [
            {"id": "abc1", "name": "Low", "category": "general", "tags": [], "estimated_quality": 3, "description": ""},
            {"id": "abc2", "name": "High", "category": "general", "tags": [], "estimated_quality": 9, "description": ""},
        ])
        from blender_mcp.tools.repository_tools import _search_objects
        result = await _search_objects(query=None, category=None, tags=None, author=None, min_quality=7, complexity=None, limit=10)
        assert result["total_matches"] == 1
        assert result["objects"][0]["id"] == "abc2"

    @pytest.mark.asyncio
    async def test_search_by_tags(self, repo_dir: Path):
        self._write_index(repo_dir, [
            {"id": "a1", "name": "A", "category": "general", "tags": ["metal", "robot"], "estimated_quality": 5, "description": ""},
            {"id": "a2", "name": "B", "category": "general", "tags": ["wood"], "estimated_quality": 5, "description": ""},
        ])
        from blender_mcp.tools.repository_tools import _search_objects
        result = await _search_objects(query=None, category=None, tags=["robot"], author=None, min_quality=None, complexity=None, limit=10)
        assert result["total_matches"] == 1
        assert result["objects"][0]["id"] == "a1"


# ---------------------------------------------------------------------------
# _find_construction_script
# ---------------------------------------------------------------------------

class TestFindConstructionScript:
    @pytest.mark.asyncio
    async def test_found_in_index(self, repo_dir: Path):
        import blender_mcp.tools.repository_tools as rt
        obj_id = "test123"
        obj_dir = repo_dir / obj_id
        obj_dir.mkdir(parents=True)
        meta = {
            "id": obj_id,
            "name": "Test",
            "blender_name": "TestObject",
            "construction_script": "import bpy\nbpy.ops.mesh.primitive_cube_add()",
        }
        with open(obj_dir / "metadata.json", "w") as f:
            json.dump(meta, f)
        repo_dir.mkdir(parents=True, exist_ok=True)
        index = {"models": [{"id": obj_id, "name": "Test", "blender_name": "TestObject"}], "last_updated": "2026-01-01"}
        with open(rt.INDEX_FILE, "w") as f:
            json.dump(index, f)

        from blender_mcp.tools.repository_tools import _find_construction_script
        script = await _find_construction_script("TestObject")
        assert script is not None
        assert "primitive_cube_add" in script

    @pytest.mark.asyncio
    async def test_not_found(self):
        from blender_mcp.tools.repository_tools import _find_construction_script
        result = await _find_construction_script("NonExistent")
        assert result is None


# ---------------------------------------------------------------------------
# _get_asset_from_repository
# ---------------------------------------------------------------------------

class TestGetAssetFromRepository:
    @pytest.mark.asyncio
    async def test_found(self, repo_dir: Path):
        obj_id = "asset001"
        obj_dir = repo_dir / obj_id
        obj_dir.mkdir(parents=True)
        meta = {
            "id": obj_id,
            "name": "My Asset",
            "category": "character",
            "blend_file": str(obj_dir / "model_1_0_0.blend"),
            "obj_info": {"vertex_count": 1200, "materials": ["Skin", "Hair"], "bone_count": 55},
        }
        with open(obj_dir / "metadata.json", "w") as f:
            json.dump(meta, f)

        from blender_mcp.tools.repository_tools import _get_asset_from_repository
        result = await _get_asset_from_repository(obj_id)
        assert result is not None
        assert result["polygon_count"] == 1200
        assert "Skin" in result["materials"]
        assert result["has_bones"] is True
        assert result["is_avatar"] is True  # "character" in category

    @pytest.mark.asyncio
    async def test_not_found(self):
        from blender_mcp.tools.repository_tools import _get_asset_from_repository
        result = await _get_asset_from_repository("does_not_exist_xyz")
        assert result is None

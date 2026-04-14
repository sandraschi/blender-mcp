"""
Unit tests for splatting handler.

No Blender installation required — executor is mocked.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def make_executor(output: str) -> MagicMock:
    e = MagicMock()
    e.execute_script = AsyncMock(return_value=output)
    return e


class TestImportGaussianSplat:
    @pytest.mark.asyncio
    async def test_file_not_found(self, tmp_path: Path):
        from blender_mcp.handlers.splatting_handler import import_gaussian_splat

        result = await import_gaussian_splat(str(tmp_path / "nonexistent.ply"))
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_unsupported_format(self, tmp_path: Path):
        bad = tmp_path / "model.fbx"
        bad.write_text("dummy")
        from blender_mcp.handlers.splatting_handler import import_gaussian_splat

        result = await import_gaussian_splat(str(bad))
        assert result["status"] == "error"
        assert "format" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_no_operator_available(self, tmp_path: Path):
        ply = tmp_path / "scene.ply"
        ply.write_bytes(b"ply\n")
        gs_output = json.dumps(
            {
                "status": "error",
                "message": "No Gaussian Splat import operator available.",
                "fix": "Install gaussian_splat addon",
            }
        )
        executor = make_executor(f"GS_RESULT:{gs_output}")
        with patch("blender_mcp.handlers.splatting_handler.get_blender_executor", return_value=executor):
            from blender_mcp.handlers.splatting_handler import import_gaussian_splat

            result = await import_gaussian_splat(str(ply))
        assert result["status"] == "error"
        assert "operator" in result["message"].lower() or "addon" in result.get("fix", "").lower()

    @pytest.mark.asyncio
    async def test_successful_import(self, tmp_path: Path):
        ply = tmp_path / "scene.ply"
        ply.write_bytes(b"ply\n")
        gs_output = json.dumps(
            {
                "status": "success",
                "object_name": "GS_scene",
                "point_count": 150000,
                "file_path": str(ply),
                "proxy_name": "GS_scene_PROXY",
                "warnings": [],
            }
        )
        executor = make_executor(f"GS_RESULT:{gs_output}")
        with patch("blender_mcp.handlers.splatting_handler.get_blender_executor", return_value=executor):
            from blender_mcp.handlers.splatting_handler import import_gaussian_splat

            result = await import_gaussian_splat(str(ply))
        assert result["status"] == "success"
        assert result["object_name"] == "GS_scene"
        assert result["point_count"] == 150000

    @pytest.mark.asyncio
    async def test_executor_crash(self, tmp_path: Path):
        ply = tmp_path / "scene.ply"
        ply.write_bytes(b"ply\n")
        executor = MagicMock()
        executor.execute_script = AsyncMock(side_effect=RuntimeError("Blender crashed"))
        with patch("blender_mcp.handlers.splatting_handler.get_blender_executor", return_value=executor):
            from blender_mcp.handlers.splatting_handler import import_gaussian_splat

            result = await import_gaussian_splat(str(ply))
        assert result["status"] == "error"
        assert "crashed" in result["message"].lower()


class TestGenerateCollisionMesh:
    @pytest.mark.asyncio
    async def test_success(self):
        output = json.dumps(
            {
                "status": "success",
                "collision_object": "GS_scene_COLLISION",
                "decimation_ratio": 0.1,
                "smoothing_iterations": 2,
            }
        )
        executor = make_executor(f"COLL_RESULT:{output}")
        with patch("blender_mcp.handlers.splatting_handler.get_blender_executor", return_value=executor):
            from blender_mcp.handlers.splatting_handler import generate_collision_mesh

            result = await generate_collision_mesh()
        assert result["status"] == "success"
        assert "collision_object" in result

    @pytest.mark.asyncio
    async def test_no_active_object(self):
        output = json.dumps({"status": "error", "message": "No active object"})
        executor = make_executor(f"COLL_RESULT:{output}")
        with patch("blender_mcp.handlers.splatting_handler.get_blender_executor", return_value=executor):
            from blender_mcp.handlers.splatting_handler import generate_collision_mesh

            result = await generate_collision_mesh()
        assert result["status"] == "error"


class TestExportSplatForResonite:
    @pytest.mark.asyncio
    async def test_success_ply(self, tmp_path: Path):
        output_path = str(tmp_path / "scene.ply")
        output = json.dumps(
            {
                "status": "success",
                "output_path": output_path,
                "format": "ply",
                "include_collision": True,
                "optimize_for_mobile": False,
            }
        )
        executor = make_executor(f"EXPORT_RESULT:{output}")
        with patch("blender_mcp.handlers.splatting_handler.get_blender_executor", return_value=executor):
            from blender_mcp.handlers.splatting_handler import export_splat_for_resonite

            result = await export_splat_for_resonite("ply", include_collision=True)
        assert result["status"] == "success"
        assert result["format"] == "ply"

    @pytest.mark.asyncio
    async def test_success_glb(self, tmp_path: Path):
        output_path = str(tmp_path / "scene.glb")
        output = json.dumps(
            {
                "status": "success",
                "output_path": output_path,
                "format": "glb",
                "include_collision": False,
                "optimize_for_mobile": False,
            }
        )
        executor = make_executor(f"EXPORT_RESULT:{output}")
        with patch("blender_mcp.handlers.splatting_handler.get_blender_executor", return_value=executor):
            from blender_mcp.handlers.splatting_handler import export_splat_for_resonite

            result = await export_splat_for_resonite("glb")
        assert result["status"] == "success"
        assert result["format"] == "glb"

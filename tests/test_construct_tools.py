"""
Unit tests for construct_tools helpers.

No Blender installation required — executor and ctx.sample are mocked.
Covers:
  - _model_dump compat (pydantic v1/v2)
  - _validate_construction_script (syntax, security, complexity)
  - _gather_construction_context (executor path, graceful failure)
  - _analyze_reference_object (found/not found)
  - _generate_construction_script (prompt sent, code extracted)
  - _extract_python_code (code block / fallback)
  - _execute_construction_script (objects detected, executor error)
  - _generate_construction_summary
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp.tools.construct_tools import (
    ScriptValidationResult,
    _extract_python_code,
    _generate_construction_summary,
    _model_dump,
    _validate_construction_script,
)


# ---------------------------------------------------------------------------
# _model_dump compat
# ---------------------------------------------------------------------------

class TestModelDump:
    def test_pydantic_v2_model_dump(self):
        result = ScriptValidationResult(
            is_valid=True, errors=[], warnings=[], security_score=100, complexity_score=10
        )
        d = _model_dump(result)
        assert d["is_valid"] is True
        assert d["security_score"] == 100

    def test_falls_back_to_dict(self):
        """Simulate a pydantic v1 model that only has .dict()"""
        class FakeModel:
            def dict(self):
                return {"fake": True}

        d = _model_dump(FakeModel())
        assert d == {"fake": True}


# ---------------------------------------------------------------------------
# _validate_construction_script
# ---------------------------------------------------------------------------

class TestValidateConstructionScript:
    @pytest.mark.asyncio
    async def test_valid_simple_script(self):
        script = """
import bpy
bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.active_object
obj.name = "TestCube"
try:
    pass
except Exception:
    pass
"""
        result = await _validate_construction_script(script)
        assert result.is_valid is True
        assert result.security_score > 0

    @pytest.mark.asyncio
    async def test_syntax_error(self):
        result = await _validate_construction_script("def broken(:")
        assert result.is_valid is False
        assert any("syntax" in e.lower() for e in result.errors)
        assert result.security_score == 0

    @pytest.mark.asyncio
    async def test_blocks_os_import(self):
        script = "import os\nimport bpy\nbpy.ops.mesh.primitive_cube_add()"
        result = await _validate_construction_script(script)
        assert result.is_valid is False
        assert any("security" in e.lower() for e in result.errors)

    @pytest.mark.asyncio
    async def test_blocks_exec(self):
        script = "import bpy\nexec('bpy.ops.mesh.primitive_cube_add()')"
        result = await _validate_construction_script(script)
        assert result.is_valid is False

    @pytest.mark.asyncio
    async def test_blocks_open(self):
        script = "import bpy\nopen('/etc/passwd').read()"
        result = await _validate_construction_script(script)
        assert result.is_valid is False

    @pytest.mark.asyncio
    async def test_complexity_score(self):
        # Many bpy calls = higher complexity
        bpy_calls = "\n".join(["bpy.ops.mesh.primitive_cube_add()"] * 60)
        script = f"import bpy\n{bpy_calls}\nobj = bpy.context.active_object\nobj.name = 'X'\ntry:\n    pass\nexcept:\n    pass"
        result = await _validate_construction_script(script)
        assert result.complexity_score > 0


# ---------------------------------------------------------------------------
# _extract_python_code
# ---------------------------------------------------------------------------

class TestExtractPythonCode:
    def test_fenced_code_block(self):
        content = '```python\nimport bpy\nbpy.ops.mesh.primitive_cube_add()\n```'
        code = _extract_python_code(content)
        assert code is not None
        assert "primitive_cube_add" in code

    def test_fallback_import_bpy(self):
        content = "Here is the code:\nimport bpy\nbpy.ops.mesh.primitive_cube_add()\n\nDone."
        code = _extract_python_code(content)
        assert code is not None
        assert "import bpy" in code

    def test_no_code(self):
        result = _extract_python_code("Just plain text, no code here.")
        assert result is None

    def test_empty_code_block(self):
        result = _extract_python_code("```python\n\n```")
        # Empty block after strip should return None or empty
        assert result is None or result == ""


# ---------------------------------------------------------------------------
# _gather_construction_context
# ---------------------------------------------------------------------------

class TestGatherConstructionContext:
    @pytest.mark.asyncio
    async def test_success_with_scene_data(self):
        scene_data = {
            "objects": [{"name": "Cube", "type": "MESH"}, {"name": "Light", "type": "LIGHT"}],
            "materials": ["Mat1", "Mat2"],
            "collections": ["Collection"],
        }
        output = f"SCENE_CTX:{json.dumps(scene_data)}"
        executor = MagicMock()
        executor.execute_script = AsyncMock(return_value=output)

        with patch("blender_mcp.tools.construct_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.construct_tools import _gather_construction_context
            result = await _gather_construction_context(None, None, True)

        assert result["scene_info"]["objects_count"] == 2
        assert result["scene_info"]["materials_count"] == 2
        assert result["allow_modifications"] is True

    @pytest.mark.asyncio
    async def test_graceful_failure(self):
        executor = MagicMock()
        executor.execute_script = AsyncMock(side_effect=RuntimeError("Blender not found"))

        with patch("blender_mcp.tools.construct_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.construct_tools import _gather_construction_context
            result = await _gather_construction_context(None, None, False)

        # Should return empty context without raising
        assert result["scene_info"] == {}
        assert result["reference_objects"] == []

    @pytest.mark.asyncio
    async def test_with_reference_objects(self):
        scene_output = f"SCENE_CTX:{json.dumps({'objects': [], 'materials': [], 'collections': []})}"
        ref_output = json.dumps({
            "name": "RefObj", "type": "MESH", "vertex_count": 200,
            "materials": ["M1"], "modifiers": ["SUBSURF"], "dimensions": [1, 1, 1]
        })
        ref_output_line = f"REF_OBJ:{ref_output}"

        executor = MagicMock()
        executor.execute_script = AsyncMock(side_effect=[scene_output, ref_output_line])

        with patch("blender_mcp.tools.construct_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.construct_tools import _gather_construction_context
            result = await _gather_construction_context(None, ["RefObj"], True)

        assert len(result["reference_objects"]) == 1
        assert result["reference_objects"][0]["name"] == "RefObj"


# ---------------------------------------------------------------------------
# _analyze_reference_object
# ---------------------------------------------------------------------------

class TestAnalyzeReferenceObject:
    @pytest.mark.asyncio
    async def test_found(self):
        info = {
            "name": "MyObj", "type": "MESH", "vertex_count": 100,
            "materials": ["Mat"], "modifiers": [], "dimensions": [1, 2, 3]
        }
        executor = MagicMock()
        executor.execute_script = AsyncMock(return_value=f"REF_OBJ:{json.dumps(info)}")

        with patch("blender_mcp.tools.construct_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.construct_tools import _analyze_reference_object
            result = await _analyze_reference_object("MyObj")

        assert result is not None
        assert result["vertex_count"] == 100

    @pytest.mark.asyncio
    async def test_not_found(self):
        executor = MagicMock()
        executor.execute_script = AsyncMock(return_value="REF_OBJ:null")

        with patch("blender_mcp.tools.construct_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.construct_tools import _analyze_reference_object
            result = await _analyze_reference_object("Ghost")

        assert result is None

    @pytest.mark.asyncio
    async def test_executor_crash_returns_none(self):
        executor = MagicMock()
        executor.execute_script = AsyncMock(side_effect=RuntimeError("boom"))

        with patch("blender_mcp.tools.construct_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.construct_tools import _analyze_reference_object
            result = await _analyze_reference_object("AnyObj")

        assert result is None


# ---------------------------------------------------------------------------
# _generate_construction_script
# ---------------------------------------------------------------------------

class TestGenerateConstructionScript:
    @pytest.mark.asyncio
    async def test_success(self):
        mock_ctx = MagicMock()
        sampling_result = MagicMock()
        sampling_result.content = "```python\nimport bpy\nbpy.ops.mesh.primitive_cube_add()\n```"
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        from blender_mcp.tools.construct_tools import _generate_construction_script
        result = await _generate_construction_script(
            mock_ctx, "a red cube", "RedCube", "simple", None, {}, 3
        )

        assert result["success"] is True
        assert "primitive_cube_add" in result["script"]
        # Verify the full prompt was sent (not the old empty string)
        call_args = mock_ctx.sample.call_args
        prompt = call_args[1].get("content") or call_args[0][0]
        assert "red cube" in prompt
        assert "RedCube" in prompt
        assert "simple" in prompt

    @pytest.mark.asyncio
    async def test_no_code_in_response(self):
        mock_ctx = MagicMock()
        sampling_result = MagicMock()
        sampling_result.content = "I cannot help with that."
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        from blender_mcp.tools.construct_tools import _generate_construction_script
        result = await _generate_construction_script(
            mock_ctx, "a cube", "Cube", "simple", None, {}, 1
        )

        assert result["success"] is False
        assert "No valid Python code" in result["error"]

    @pytest.mark.asyncio
    async def test_sampling_failure(self):
        mock_ctx = MagicMock()
        mock_ctx.sample = AsyncMock(side_effect=RuntimeError("Client disconnected"))

        from blender_mcp.tools.construct_tools import _generate_construction_script
        result = await _generate_construction_script(
            mock_ctx, "a cube", "Cube", "simple", None, {}, 1
        )

        assert result["success"] is False
        assert "failed" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_style_preset_in_prompt(self):
        mock_ctx = MagicMock()
        sampling_result = MagicMock()
        sampling_result.content = "```python\nimport bpy\nbpy.ops.mesh.primitive_sphere_add()\n```"
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        from blender_mcp.tools.construct_tools import _generate_construction_script
        await _generate_construction_script(
            mock_ctx, "a sphere", "MySphere", "standard", "scifi", {}, 3
        )

        call_args = mock_ctx.sample.call_args
        prompt = call_args[1].get("content") or call_args[0][0]
        assert "scifi" in prompt


# ---------------------------------------------------------------------------
# _execute_construction_script
# ---------------------------------------------------------------------------

class TestExecuteConstructionScript:
    @pytest.mark.asyncio
    async def test_objects_detected(self):
        obj_list = ["Cube", "Cube.001", "NewRobot"]
        output = f"CREATED_OBJECTS:{json.dumps(obj_list)}\nBLENDER_SCRIPT_SUCCESS: construct_TestObj"
        executor = MagicMock()
        executor.execute_script = AsyncMock(return_value=output)

        validation = ScriptValidationResult(
            is_valid=True, errors=[], warnings=[], security_score=95, complexity_score=20
        )

        with patch("blender_mcp.tools.construct_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.construct_tools import _execute_construction_script
            result = await _execute_construction_script("import bpy", "TestObj", validation)

        assert result["success"] is True
        assert "Cube" in result["objects_created"]

    @pytest.mark.asyncio
    async def test_detection_error_still_succeeds(self):
        """DETECTION_ERROR in output still counts as success — main script ran."""
        output = "CREATED_OBJECTS:[]\nDETECTION_ERROR: something minor"
        executor = MagicMock()
        executor.execute_script = AsyncMock(return_value=output)

        validation = ScriptValidationResult(
            is_valid=True, errors=[], warnings=[], security_score=90, complexity_score=5
        )

        with patch("blender_mcp.tools.construct_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.construct_tools import _execute_construction_script
            result = await _execute_construction_script("import bpy", "Obj", validation)

        assert result["success"] is True
        assert result["objects_created"] == []

    @pytest.mark.asyncio
    async def test_executor_exception(self):
        executor = MagicMock()
        executor.execute_script = AsyncMock(side_effect=RuntimeError("Blender crashed"))

        validation = ScriptValidationResult(
            is_valid=True, errors=[], warnings=[], security_score=90, complexity_score=5
        )

        with patch("blender_mcp.tools.construct_tools.get_blender_executor", return_value=executor):
            from blender_mcp.tools.construct_tools import _execute_construction_script
            result = await _execute_construction_script("import bpy", "Obj", validation)

        assert result["success"] is False
        assert "crashed" in result["error"].lower()


# ---------------------------------------------------------------------------
# _generate_construction_summary
# ---------------------------------------------------------------------------

class TestGenerateConstructionSummary:
    def test_success_single_object(self):
        validation = ScriptValidationResult(
            is_valid=True, errors=[], warnings=[], security_score=100, complexity_score=10
        )
        summary = _generate_construction_summary(
            "a red cube",
            {"success": True, "objects_created": ["RedCube"]},
            1,
            validation,
        )
        assert "RedCube" in summary
        assert "red cube" in summary

    def test_success_multiple_objects(self):
        validation = ScriptValidationResult(
            is_valid=True, errors=[], warnings=["High complexity"], security_score=80, complexity_score=80
        )
        summary = _generate_construction_summary(
            "a robot",
            {"success": True, "objects_created": ["Body", "Head", "ArmL", "ArmR"]},
            2,
            validation,
        )
        assert "4 objects" in summary
        assert "optimization" in summary

    def test_failure(self):
        validation = ScriptValidationResult(
            is_valid=True, errors=[], warnings=[], security_score=100, complexity_score=5
        )
        summary = _generate_construction_summary(
            "a castle",
            {"success": False, "error": "AttributeError: 'NoneType'"},
            3,
            validation,
        )
        assert "failed" in summary.lower() or "❌" in summary
        assert "castle" in summary

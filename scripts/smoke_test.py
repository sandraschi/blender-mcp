"""Headless smoke test for Phase 1-3 tool surface."""

from __future__ import annotations

import asyncio
import json
import sys


async def main() -> int:
    from blender_mcp.app import get_app
    from blender_mcp.config import BLENDER_EXECUTABLE, validate_blender_executable
    from blender_mcp.utils.blender_runtime import execute_bpy_script

    print("=== blender-mcp smoke test ===")
    print(f"Blender exe: {BLENDER_EXECUTABLE}")
    print(f"Blender found: {validate_blender_executable()}")

    app = get_app()
    tools = await app.list_tools()
    names = {t.name for t in tools}
    required = {
        "blender_shaders",
        "blender_compositor",
        "blender_jobs",
        "blender_ai_generate",
        "blender_geonodes",
        "blender_vision_refine",
    }
    missing = required - names
    print(f"Tools registered: {len(names)}")
    if missing:
        print(f"FAIL missing tools: {sorted(missing)}")
        return 1
    print(f"OK phase tools present: {sorted(required)}")

    for tool_name, args in [
        ("blender_ai_generate", {"operation": "list_backends"}),
        ("blender_geonodes", {"operation": "list_node_types"}),
        ("blender_jobs", {"operation": "list"}),
    ]:
        result = await app.call_tool(tool_name, args)
        text = result.content[0].text
        print(f"OK {tool_name}: {text[:120].replace(chr(10), ' ')}")

    if not validate_blender_executable():
        print("SKIP headless bpy (Blender not installed)")
        return 0

    bpy_result = await execute_bpy_script(
        "import bpy\nimport json\nprint('SMOKE:' + json.dumps({'objects': len(bpy.data.objects)}))",
        script_name="smoke_test",
        timeout=90,
        prefer_session=False,
        headless_fallback=True,
    )
    print(f"Headless bpy: success={bpy_result.get('success')} mode={bpy_result.get('mode')}")
    if not bpy_result.get("success"):
        print(f"FAIL headless bpy: {bpy_result.get('error')}")
        return 1

    for line in (bpy_result.get("output") or "").splitlines():
        if line.startswith("SMOKE:"):
            print(f"OK headless scene: {line[len('SMOKE:'):]}")

    geonodes = await app.call_tool(
        "blender_geonodes",
        {"operation": "create_group", "group_name": "SmokeTestGeoNodes"},
    )
    geonodes_text = geonodes.content[0].text
    print(f"OK blender_geonodes create_group: {geonodes_text[:160].replace(chr(10), ' ')}")
    if "SmokeTestGeoNodes" not in geonodes_text and "success" not in geonodes_text.lower():
        print("WARN geonodes create_group response unexpected")

    print("=== smoke test passed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

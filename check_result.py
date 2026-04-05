import asyncio

from blender_mcp.app import get_app


async def check():
    app = get_app()
    from blender_mcp.agentic import register_agentic_tools

    register_agentic_tools()

    # Try calling a simple tool
    try:
        result = await app.call_tool("blender_status", {})
        mcp_result = result.to_mcp_result()
        print(f"MCP Result is a tuple of length {len(mcp_result)}")
        for i, val in enumerate(mcp_result):
            print(f"Element {i} type: {type(val)}")
            print(f"Element {i} value: {val}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(check())

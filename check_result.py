import asyncio
import logging

from blender_mcp.app import get_app

logger = logging.getLogger(__name__)


async def check():
    app = get_app()
    from blender_mcp.agentic import register_agentic_tools

    register_agentic_tools()

    # Try calling a simple tool
    try:
        result = await app.call_tool("blender_status", {})
        mcp_result = result.to_mcp_result()
        for _i, _val in enumerate(mcp_result):
            pass
    except Exception as e:
        logger.debug("Status call failed: %s", e)


if __name__ == "__main__":
    asyncio.run(check())

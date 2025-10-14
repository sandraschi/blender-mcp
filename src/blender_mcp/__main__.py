"""Main entry point for blender_mcp package when run as module."""

import asyncio
from blender_mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())

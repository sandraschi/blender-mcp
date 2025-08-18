"""Main entry point for blender_mcp package when run as module."""

from .server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

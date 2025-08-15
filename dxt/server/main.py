#!/usr/bin/env python3
"""Blender MCP Server DXT Entry Point.

This is the main entry point for the DXT packaged Blender MCP server.
"""

import sys
import os
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))
sys.path.insert(0, str(server_dir / "lib"))

# Import and run the main server
if __name__ == "__main__":
    from blender_mcp.server import main
    import asyncio
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Shutting down Blender MCP server")
    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        sys.exit(1)
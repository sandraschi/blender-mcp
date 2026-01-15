#!/usr/bin/env python3
"""
Blender MCP Server - MCPB Package Entry Point

This is the main entry point for the MCPB-packaged Blender MCP server.
It provides AI-powered 3D creation and manipulation capabilities.
"""

import sys
import os

# Add the lib directory to Python path for dependencies
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

# Import and run the actual server
from blender_mcp.server import main

if __name__ == "__main__":
    main()






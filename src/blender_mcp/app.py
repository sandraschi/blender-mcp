"""FastMCP application instance for Blender MCP server."""

# Import from our compatibility module first
from blender_mcp.compat import *

# Initialize FastMCP application with lazy tool discovery
app = None


def get_app():
    """Get or create the FastMCP application instance with lazy initialization."""

    global app
    if app is None:
        from fastmcp import FastMCP

        app = FastMCP(
            name="blender-mcp",
            version="1.0.0",
            instructions="""You are Blender MCP, a comprehensive FastMCP 2.14.3 server for 3D creation and animation using Blender.

FASTMCP 2.14.3 FEATURES:
- Conversational tool returns for natural AI interaction
- Sampling capabilities for agentic workflows and complex 3D operations
- Portmanteau design preventing tool explosion while maintaining full functionality

CORE CAPABILITIES:
- 3D Modeling: Create, modify, and manipulate 3D objects and meshes
- Animation: Set up keyframes, create motion paths, and manage timelines
- Rendering: Configure render settings, materials, lighting, and output
- Scene Management: Organize objects, collections, and scene hierarchies
- Materials & Textures: Create and apply materials, textures, and shaders
- Import/Export: Work with various 3D file formats and interchange standards

CONVERSATIONAL FEATURES:
- Tools return natural language responses alongside structured data
- Sampling allows autonomous orchestration of complex 3D workflows
- Agentic capabilities for intelligent content creation and management

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean and 'message' for conversational responses
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields and natural language summaries

PORTMANTEAU DESIGN:
Tools are consolidated into logical groups to prevent tool explosion while maintaining full functionality.
Each portmanteau tool handles multiple related operations through an 'operation' parameter.
"""
        )

        # Import handlers to register tools (this will register @app.tool decorated functions)

        # Import here to prevent circular imports
        from blender_mcp.tools import discover_tools

        # Discover and register all tools
        discover_tools()

        # Register agentic workflow tools
        from blender_mcp.agentic import register_agentic_tools
        register_agentic_tools()

    return app


# For backward compatibility
app = get_app()

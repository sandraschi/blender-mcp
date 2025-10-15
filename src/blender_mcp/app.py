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

        app = FastMCP(name="blender-mcp", version="1.0.0")

        # Import handlers to register tools (this will register @app.tool decorated functions)

        # Import here to prevent circular imports
        from blender_mcp.tools import discover_tools

        # Discover and register all tools
        discover_tools()

    return app


# For backward compatibility
app = get_app()

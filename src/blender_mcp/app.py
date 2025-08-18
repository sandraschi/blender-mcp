"""FastMCP application instance for Blender MCP server."""

from fastmcp import FastMCP

# Initialize FastMCP application - this gets imported by both server and handlers
app = FastMCP(
    name="blender-mcp",
    version="1.0.0"
)

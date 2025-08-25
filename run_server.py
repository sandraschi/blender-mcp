import sys
import os

# Add both project root and src directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')
for path in [project_root, src_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

print("Python path:", '\n'.join(sys.path))  # Debugging

# Import and run the server
from blender_mcp.server import main
print("Starting Blender MCP server...")
main()
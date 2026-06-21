import _strptime
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, "src")
for path in [project_root, src_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

from blender_mcp.server import main

main()

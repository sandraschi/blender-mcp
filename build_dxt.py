"""Build script for creating a DXT package following Claude Desktop standards.

Key principles:
- No shell-style variable substitution
- No hardcoded external paths
- No CLI prompting
- Uses proper user configuration
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional

def create_manifest() -> Dict[str, Any]:
    """Create a DXT manifest with proper user configuration."""
    return {
        "dxt_version": "0.1",
        "name": "blender-mcp",
        "version": "1.0.0",
        "description": "Blender Model Control Protocol (MCP) server",
        "author": {"name": "Windsurf Technologies", "email": "support@windsurf.tech"},
        "user_config": {
            "blender_path": {
                "type": "file",
                "title": "Blender Executable",
                "description": "Path to Blender executable",
                "required": True,
                "default": "${PROGRAM_FILES}\\Blender Foundation\\Blender\\blender.exe",
                "filter": [".exe"],
                "validation": {"must_exist": True, "executable": True}
            }
        },
        "server": {
            "type": "python",
            "entry_point": "blender_mcp/server.py",
            "mcp_config": {
                "command": "python",
                "args": ["-m", "blender_mcp.server", "--http", "--blender", "${user_config.blender_path}"],
                "env": {}
            }
        },
        "dependencies": [
            "fastmcp>=2.10.0",
            "pydantic>=2.0.0",
            "httpx>=0.25.0",
            "loguru>=0.7.0",
            "typing-extensions>=4.8.0"
        ]
    }

def install_dependencies(temp_dir: Path) -> None:
    """Install all dependencies into a temporary directory."""
    requirements = [
        "fastmcp>=2.10.0",
        "pydantic>=2.0.0",
        "httpx>=0.25.0",
        "loguru>=0.7.0",
        "typing-extensions>=4.8.0"
    ]
    
    # Create a requirements file
    req_file = temp_dir / "requirements.txt"
    with open(req_file, 'w') as f:
        f.write('\n'.join(requirements))
    
    # Use pip to install dependencies
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "-r", str(req_file),
        "--target", str(temp_dir / "dependencies"),
        "--no-deps"
    ])

def create_dxt_package() -> Path:
    """Create a complete DXT package with all dependencies."""
    # Create output directory
    output_dir = Path("dist")
    output_dir.mkdir(exist_ok=True)
    
    # Create manifest
    manifest = create_manifest()
    package_name = manifest["name"]
    version = manifest["version"]
    
    # Create a temporary directory for building the package
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        
        # Install dependencies
        install_dependencies(temp_dir)
        
        # Add tools to manifest
        manifest.update({
            "tools": [
                {
                    "name": "create_mesh",
                    "description": "Create and manipulate 3D meshes in Blender"
                },
                {
                    "name": "apply_material",
                    "description": "Apply materials and textures to 3D objects"
                },
                {
                    "name": "render_scene",
                    "description": "Render the current scene with specified settings"
                },
                {
                    "name": "export_model",
                    "description": "Export 3D models in various formats"
                }
            ],
            "tools_generated": False,
            "keywords": ["blender", "3d", "modeling", "rendering", "automation"],
            "requirements": ["Blender>=3.0.0"]
        })
        
        # Create output file
        output_file = output_dir / f"{package_name}-{version}.dxt"
        
        # Create the zip file
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add manifest.json
            zipf.writestr('manifest.json', json.dumps(manifest, indent=2))
            
            # Add source files
            src_dir = Path("src") / "blender_mcp"
            if src_dir.exists():
                for root, _, files in os.walk(src_dir):
                    for file in files:
                        if file.endswith(('.py', '.md', '.txt')):
                            file_path = Path(root) / file
                            arcname = str(file_path.relative_to('src'))
                            zipf.write(file_path, arcname)
            
            # Add dependencies
            deps_dir = temp_dir / "dependencies"
            if deps_dir.exists():
                for root, _, files in os.walk(deps_dir):
                    for file in files:
                        if file.endswith(('.py', '.so', '.pyd', '.dll', '.pyd')):
                            file_path = Path(root) / file
                            arcname = str(file_path.relative_to(temp_dir))
                            zipf.write(file_path, arcname)
    
    return output_file

def main() -> None:
    """Main function to create the DXT package."""
    try:
        output_file = create_dxt_package()
        print(f"\n✅ Successfully created DXT package: {output_file.absolute()}")
        print("\nTo install in Claude Desktop:")
        print(f"1. Open Claude Desktop")
        print(f"2. Go to Extensions > Install from File")
        print(f"3. Select: {output_file.absolute()}")
        print("4. Follow the on-screen instructions")
    except Exception as e:
        print(f"\n❌ Error creating DXT package: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()

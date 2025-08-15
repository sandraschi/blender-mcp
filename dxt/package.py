"""Package the Blender MCP extension as a DXT file.

This script creates a distributable DXT package containing all necessary files.
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from typing import List, Dict, Any

# Configuration
PACKAGE_NAME = "blender-mcp"
VERSION = "1.0.0"
DXT_CONFIG = "dxt.json"
OUTPUT_DIR = "dist"

# Files to include in the package
INCLUDE_PATTERNS = [
    "src/**/*.py",
    "pyproject.toml",
    "README.md",
    "LICENSE"
]

def load_dxt_config() -> Dict[str, Any]:
    """Load and validate the DXT configuration."""
    with open(DXT_CONFIG, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Update version if needed
    config['version'] = VERSION
    return config

def create_package_directory() -> Path:
    """Create the package directory structure."""
    package_dir = Path(OUTPUT_DIR) / f"{PACKAGE_NAME}-{VERSION}"
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Create necessary subdirectories
    (package_dir / PACKAGE_NAME).mkdir(exist_ok=True)
    return package_dir

def copy_package_files(package_dir: Path) -> None:
    """Copy all package files to the target directory."""
    # Copy Python package
    src_dir = Path("src") / PACKAGE_NAME.replace("-", "_")
    dst_dir = package_dir / PACKAGE_NAME / PACKAGE_NAME.replace("-", "_")
    
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)
    
    # Copy other required files
    for pattern in ["pyproject.toml", "README.md", "LICENSE"]:
        if Path(pattern).exists():
            shutil.copy2(pattern, package_dir / PACKAGE_NAME)
    
    # Copy the DXT configuration
    shutil.copy2(DXT_CONFIG, package_dir)
    
    # Copy the install script
    shutil.copy2("dxt/install.py", package_dir)

def create_dxt_file(package_dir: Path) -> None:
    """Create the final DXT zip file."""
    output_file = Path(OUTPUT_DIR) / f"{PACKAGE_NAME}-{VERSION}.dxt"
    
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    print(f"Created DXT package: {output_file}")

def main() -> None:
    """Main packaging function."""
    print(f"Packaging {PACKAGE_NAME} v{VERSION}...")
    
    # Load and validate DXT config
    config = load_dxt_config()
    
    # Create package directory
    package_dir = create_package_directory()
    
    # Copy all necessary files
    copy_package_files(package_dir)
    
    # Update DXT config with package contents
    with open(package_dir / DXT_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    # Create the final DXT file
    create_dxt_file(package_dir)
    
    print("Packaging complete!")

if __name__ == "__main__":
    main()

"""
Script to convert relative imports to absolute imports in Python files.

This script will recursively scan all Python files in the src directory and convert
any relative imports to absolute imports using the package name 'blender_mcp'.
"""

import os
import re
from pathlib import Path

def convert_imports(file_path: Path, package_name: str = 'blender_mcp') -> bool:
    """Convert relative imports to absolute imports in a Python file.
    
    Args:
        file_path: Path to the Python file to process
        package_name: The root package name (default: 'blender_mcp')
        
    Returns:
        bool: True if changes were made, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Skip if not a Python file or in __pycache__
        if not file_path.suffix == '.py' or '__pycache__' in str(file_path):
            return False
            
        # Pattern to match relative imports (e.g., from ..module import name or from .module import name)
        pattern = r'^((?:from\s+)(\.+\.*)(\s+import\s+.*))$'
        
        # Find all relative imports
        lines = content.splitlines()
        modified = False
        
        for i, line in enumerate(lines):
            match = re.match(pattern, line, re.MULTILINE)
            if match:
                # Get the relative import part (e.g., '..module' or '.module')
                relative_import = match.group(2).strip()
                
                # Calculate the absolute import path
                if relative_import.startswith('..'):
                    # For parent directory imports (e.g., '..module' -> 'blender_mcp.module')
                    new_import = f'from {package_name}{relative_import[1:]}'
                else:
                    # For same directory imports (e.g., '.module' -> 'blender_mcp.submodule.module')
                    # First, get the relative path from the package root
                    rel_path = file_path.parent.relative_to(Path(__file__).parent / 'src' / package_name)
                    if str(rel_path) == '.':
                        new_import = f'from {package_name}{relative_import}'
                    else:
                        module_path = str(rel_path).replace(os.sep, '.')
                        new_import = f'from {package_name}.{module_path}{relative_import}'
                
                # Replace the line
                lines[i] = f'{new_import} {match.group(3)}'
                modified = True
        
        # Write back if changes were made
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')
            print(f"Updated: {file_path}")
            return True
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return False

def main():
    # Get the root directory of the project
    root_dir = Path(__file__).parent / 'src' / 'blender_mcp'
    
    if not root_dir.exists():
        print(f"Error: Directory not found: {root_dir}")
        return
    
    print(f"Scanning for Python files in: {root_dir}")
    
    # Process all Python files
    modified_count = 0
    for file_path in root_dir.rglob('*.py'):
        if convert_imports(file_path):
            modified_count += 1
    
    print(f"\nDone! Updated {modified_count} files.")

if __name__ == '__main__':
    main()

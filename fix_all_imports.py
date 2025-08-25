"""
Script to convert all relative imports to absolute imports in the Blender MCP project.

This script will recursively scan all Python files in the project and convert
any relative imports to absolute imports using the package name 'blender_mcp'.
"""

import os
import re
from pathlib import Path

def convert_imports(file_path: Path, project_root: Path):
    """Convert relative imports to absolute imports in a Python file.
    
    Args:
        file_path: Path to the Python file to process
        project_root: Root directory of the project
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if not a Python file or in __pycache__
        if not file_path.suffix == '.py' or '__pycache__' in str(file_path):
            return False
        
        # Calculate the relative path from project root to the current file
        rel_path = file_path.relative_to(project_root)
        
        # Convert Windows path to module path
        module_parts = list(rel_path.parts)
        if module_parts[0] == 'src':
            module_parts = module_parts[1:]  # Remove 'src' from the path
        module_path = '.'.join(module_parts).replace('.py', '')
        
        # Pattern to match relative imports (e.g., from ..module import name or from .module import name)
        patterns = [
            (r'^from\s+(\.+\.*)(\s+import\s+.*)$', r'from blender_mcp.\1\2'),  # from ..module import x
            (r'^import\s+(\.+\.*\s+as\s+\w+)$', r'import blender_mcp.\1'),  # import ..module as x
            (r'^import\s+(\.+\.*)$', r'import blender_mcp.\1'),  # import ..module
        ]
        
        # Process each line
        lines = content.splitlines()
        modified = False
        
        for i, line in enumerate(lines):
            for pattern, replacement in patterns:
                if re.match(pattern, line):
                    # Count the number of dots to determine the relative level
                    dots = len(re.match(r'^\s*(?:\.+\.*)', line).group().strip())
                    
                    # Skip if it's already an absolute import
                    if 'blender_mcp' in line:
                        continue
                        
                    # Replace the relative import with absolute
                    new_line = re.sub(pattern, replacement, line)
                    
                    # Remove any double dots
                    new_line = new_line.replace('...', '.').replace('..', '.')
                    
                    # Update the line if it was changed
                    if new_line != line:
                        lines[i] = new_line
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
    project_root = Path(__file__).parent
    src_dir = project_root / 'src'
    
    if not src_dir.exists():
        print(f"Error: Directory not found: {src_dir}")
        return
    
    print(f"Scanning for Python files in: {src_dir}")
    
    # Process all Python files
    modified_count = 0
    for file_path in src_dir.rglob('*.py'):
        if convert_imports(file_path, src_dir):
            modified_count += 1
    
    print(f"\nDone! Updated {modified_count} files.")

if __name__ == '__main__':
    main()

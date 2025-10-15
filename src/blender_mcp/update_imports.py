"""
Script to update imports in tool files to use the new compatibility module.

This script will:
1. Find all Python files in the tools directory
2. Update imports to use the compatibility module
3. Remove direct imports of JSONType from fastmcp.types
"""

import os
import re
from pathlib import Path


def update_file(file_path: Path) -> bool:
    """Update imports in a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip if already updated
        if "from ..compat import" in content:
            return False

        # Replace JSONType imports
        content = re.sub(
            r"from\s+fastmcp\.types\s+import\s+JSONType\s*\n",
            "from ..compat import JSONType\n",
            content,
        )

        # Update typing imports to use compat
        typing_imports = [
            "Dict",
            "List",
            "Any",
            "Optional",
            "Union",
            "Type",
            "TypeVar",
            "Callable",
            "Awaitable",
            "TypeAlias",
        ]

        for type_name in typing_imports:
            content = re.sub(
                rf"from\s+typing\s+import\s+(?:[^\n,]*\b{type_name}\b[^\n,]*)(?:,\s*)?", "", content
            )

            # Remove empty typing imports
            content = re.sub(r"from\s+typing\s+import\s*\n", "", content)

        # Add compat import if not present
        if "from ..compat import" not in content:
            content = content.replace(
                "from __future__ import annotations\n\n",
                "from __future__ import annotations\n\nfrom ..compat import *\n",
                1,  # Only replace first occurrence
            )

        # Write changes back to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def main():
    """Update imports in all tool files."""
    tools_dir = Path(__file__).parent / "blender_mcp" / "tools"
    updated = 0

    for root, _, files in os.walk(tools_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py" and file != "compat.py":
                file_path = Path(root) / file
                if update_file(file_path):
                    print(f"Updated: {file_path}")
                    updated += 1

    print(f"\n✅ Updated {updated} files")


if __name__ == "__main__":
    main()

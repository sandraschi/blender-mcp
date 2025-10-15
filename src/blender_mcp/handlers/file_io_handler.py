"""File I/O operations handler for Blender MCP."""

import os
from pathlib import Path
from typing import Dict, Any, Union
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()


class FileType(str, Enum):
    TEXT = "TEXT"
    BINARY = "BINARY"
    IMAGE = "IMAGE"
    BLEND = "BLEND"


@blender_operation("read_file", log_args=True)
async def read_file(
    filepath: str, file_type: Union[FileType, str] = FileType.TEXT, **kwargs: Any
) -> Dict[str, Any]:
    """Read a file's contents."""
from ..compat import *

    filepath = str(Path(filepath).absolute())

    try:
        if file_type == FileType.TEXT:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        elif file_type == FileType.BINARY:
            with open(filepath, "rb") as f:
                content = f.read().decode("latin1")
        else:
            return {"status": "ERROR", "error": f"Unsupported file type: {file_type}"}

        return {
            "status": "SUCCESS",
            "filepath": filepath,
            "content": content,
            "size": os.path.getsize(filepath),
        }
    except Exception as e:
        logger.error(f"Failed to read file: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("write_file", log_args=True)
async def write_file(
    filepath: str, content: str, file_type: Union[FileType, str] = FileType.TEXT, **kwargs: Any
) -> Dict[str, Any]:
    """Write content to a file."""
    filepath = str(Path(filepath).absolute())

    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        if file_type == FileType.TEXT:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        elif file_type == FileType.BINARY:
            with open(filepath, "wb") as f:
                f.write(content.encode("latin1"))
        else:
            return {"status": "ERROR", "error": f"Unsupported file type: {file_type}"}

        return {"status": "SUCCESS", "filepath": filepath}
    except Exception as e:
        logger.error(f"Failed to write file: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("list_directory", log_args=True)
async def list_directory(directory: str, recursive: bool = False, **kwargs: Any) -> Dict[str, Any]:
    """List contents of a directory."""
    from pathlib import Path

    try:
        path = Path(directory).absolute()
        if not path.exists() or not path.is_dir():
            return {"status": "ERROR", "error": "Not a directory"}

        results = []
        if recursive:
            for p in path.rglob("*"):
                if p.is_file() or p.is_dir():
                    results.append(
                        {
                            "path": str(p.relative_to(path)),
                            "name": p.name,
                            "is_dir": p.is_dir(),
                            "size": p.stat().st_size if p.is_file() else 0,
                        }
                    )
        else:
            for p in path.iterdir():
                if p.is_file() or p.is_dir():
                    results.append(
                        {
                            "path": p.name,
                            "name": p.name,
                            "is_dir": p.is_dir(),
                            "size": p.stat().st_size if p.is_file() else 0,
                        }
                    )

        return {"status": "SUCCESS", "directory": str(path), "files": results}
    except Exception as e:
        logger.error(f"Failed to list directory: {str(e)}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("create_directory", log_args=True)
async def create_directory(directory: str, **kwargs: Any) -> Dict[str, Any]:
    """Create a directory."""
    try:
        os.makedirs(directory, exist_ok=True)
        return {"status": "SUCCESS", "directory": directory}
    except Exception as e:
        logger.error(f"Failed to create directory: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

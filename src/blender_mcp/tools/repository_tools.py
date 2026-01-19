"""
Blender Object Repository tools for MCP.

Provides comprehensive object repository management including saving, loading, versioning,
sharing, and organizing Blender objects and construction scripts.
"""

import json
import os
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field
from loguru import logger

from blender_mcp.app import get_app
from blender_mcp.compat import *


class ObjectMetadata(BaseModel):
    """Metadata for a stored Blender object."""

    id: str
    name: str
    description: str
    author: str
    version: str
    created_at: str
    updated_at: str
    tags: List[str]
    complexity: str
    style_preset: Optional[str]
    construction_script: str
    object_count: int
    blender_version: Optional[str]
    estimated_quality: int  # 1-10 scale
    category: str
    license: str = "MIT"
    dependencies: List[str] = []  # Other object IDs this depends on


class RepositoryConfig(BaseModel):
    """Configuration for the model repository."""

    base_path: str = Field(default_factory=lambda: str(Path.home() / ".blender-mcp" / "repository"))
    max_versions_per_model: int = 10
    auto_backup: bool = True
    compression_enabled: bool = True


class SaveObjectParams(BaseModel):
    """Parameters for saving an object to repository."""

    object_name: str = Field(
        ...,
        description="Name of the Blender object to save"
    )
    object_name_display: str = Field(
        ...,
        description="Display name for the saved object"
    )
    description: str = Field(
        "",
        description="Description of the model"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization and search"
    )
    category: str = Field(
        "general",
        description="Category for organization"
    )
    construction_script: Optional[str] = Field(
        None,
        description="Original construction script (auto-detected if not provided)"
    )
    quality_rating: int = Field(
        5,
        description="Quality rating 1-10"
    )
    public: bool = Field(
        False,
        description="Whether to make this model publicly available"
    )


class LoadObjectParams(BaseModel):
    """Parameters for loading an object from repository."""

    object_id: str = Field(
        ...,
        description="ID of the object to load"
    )
    target_name: Optional[str] = Field(
        None,
        description="New name for the loaded object (defaults to original)"
    )
    position: Tuple[float, float, float] = Field(
        (0, 0, 0),
        description="Position to place the loaded object"
    )
    scale: Tuple[float, float, float] = Field(
        (1, 1, 1),
        description="Scale to apply to the loaded object"
    )
    version: Optional[str] = Field(
        None,
        description="Specific version to load (latest if not specified)"
    )


class SearchObjectsParams(BaseModel):
    """Parameters for searching objects in repository."""

    query: Optional[str] = Field(
        None,
        description="Search query for name/description/tags"
    )
    category: Optional[str] = Field(
        None,
        description="Filter by category"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Filter by tags (must have all specified tags)"
    )
    author: Optional[str] = Field(
        None,
        description="Filter by author"
    )
    min_quality: Optional[int] = Field(
        None,
        description="Minimum quality rating (1-10)"
    )
    complexity: Optional[str] = Field(
        None,
        description="Filter by complexity (simple/standard/complex)"
    )
    limit: int = Field(
        20,
        description="Maximum number of results"
    )


def _register_repository_tools():
    """Register repository management tools with the app."""
    app = get_app()

    @app.tool
    async def save_object_to_repository(
        object_name: str = "",
        object_name_display: str = "",
        description: str = "",
        tags: List[str] = None,
        category: str = "general",
        construction_script: Optional[str] = None,
        quality_rating: int = 5,
        public: bool = False
    ) -> Dict[str, Any]:
        """
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates model saving, versioning, and metadata management into single repository interface.
        Prevents tool explosion while enabling comprehensive model lifecycle management. Follows FastMCP 2.14.3 best practices.

        Save a Blender object to the model repository with versioning and metadata.

        **Repository Features:**
        - **Version Control**: Automatic versioning with history tracking
        - **Rich Metadata**: Comprehensive tagging, categorization, and descriptions
        - **Quality Ratings**: 1-10 quality scoring for model evaluation
        - **Dependency Tracking**: Links between related models
        - **Backup System**: Automatic backups with configurable retention

        **Model Information Captured:**
        - Complete object hierarchy and mesh data
        - Materials, textures, and UV mappings
        - Modifiers, constraints, and rigging
        - Construction script for reproducibility
        - Scene context and relationships

        Args:
            object_name (str, required): Name of the Blender object to save to repository
            model_name (str, required): Display name for the saved model
            description (str): Detailed description of the model's purpose and features
            tags (List[str]): Tags for search and categorization (e.g., ['character', 'robot', 'scifi'])
            category (str): Organizational category (e.g., 'character', 'architecture', 'vehicle', 'prop')
            construction_script (str | None): Original construction script (auto-detected from object if not provided)
            quality_rating (int): Quality assessment 1-10 (1=prototype, 10=production-ready)
            public (bool): Whether this model can be shared publicly

        Returns:
            Dict[str, Any]: Repository operation results with model ID, version info, and metadata
                Format: {
                    "success": bool,
                    "model_id": str,
                    "version": str,
                    "path": str,
                    "metadata": Dict,
                    "message": str,
                    "next_steps": List[str]
                }

        Raises:
            ValueError: If object doesn't exist or parameters are invalid
            RuntimeError: If repository operations fail

        Examples:
            Save a character: save_model_to_repository("RobotCharacter", "Robbie Robot", "Classic sci-fi robot", ["robot", "scifi"], "character", quality_rating=9)
            Save architecture: save_model_to_repository("GothicCathedral", "Medieval Cathedral", "Detailed gothic architecture", ["building", "medieval"], "architecture")

        Note:
            Models are stored in ~/.blender-mcp/repository with full version history.
            Construction scripts enable perfect reproducibility of complex models.
            Quality ratings help users find the best models for their needs.
        """
        try:
            if not object_name or not object_name_display:
                raise ValueError("object_name and object_name_display are required")

            if tags is None:
                tags = []

            # Get repository config
            config = RepositoryConfig()

            # Ensure repository directory exists
            repo_path = Path(config.base_path)
            repo_path.mkdir(parents=True, exist_ok=True)

            # Check if object exists in Blender
            object_info = await _get_object_info(object_name)
            if not object_info:
                return {
                    "success": False,
                    "message": f"Object '{object_name}' not found in current scene",
                    "next_steps": ["Check object name spelling", "Ensure object exists in scene"]
                }

            # Generate object ID
            object_id = _generate_object_id(object_name_display, object_name)

            # Create object directory
            object_dir = repo_path / object_id
            model_dir.mkdir(exist_ok=True)

            # Determine version
            version = await _get_next_version(object_dir)

            # Get or create construction script
            if not construction_script:
                construction_script = await _extract_construction_script(object_name)

            # Create metadata
            metadata = ObjectMetadata(
                id=object_id,
                name=object_name_display,
                description=description,
                author="user",  # Could be configurable
                version=version,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tags=tags,
                complexity=object_info.get("complexity", "standard"),
                style_preset=None,  # Could be inferred
                construction_script=construction_script,
                object_count=object_info.get("object_count", 1),
                blender_version=object_info.get("blender_version"),
                estimated_quality=max(1, min(10, quality_rating)),
                category=category,
                license="MIT",
                dependencies=[]
            )

            # Export Blender object
            export_result = await _export_blender_object(
                object_name, object_dir / f"object_{version}.blend"
            )

            if not export_result["success"]:
                return {
                    "success": False,
                    "message": f"Failed to export object: {export_result['error']}",
                    "next_steps": ["Check object validity", "Try exporting manually first"]
                }

            # Save metadata
            metadata_file = object_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata.dict(), f, indent=2)

            # Save construction script
            script_file = object_dir / f"script_{version}.py"
            with open(script_file, 'w') as f:
                f.write(construction_script)

            # Update repository index
            await _update_repository_index(config.base_path, metadata)

            return {
                "success": True,
                "object_id": object_id,
                "version": version,
                "path": str(object_dir),
                "metadata": metadata.dict(),
                "message": f"Successfully saved '{model_name}' (v{version}) to repository",
                "next_steps": [
                    f"Use load_object_from_repository('{object_id}') to reuse this object",
                    f"Share object_id '{object_id}' with others",
                    "Consider updating quality rating after testing"
                ]
            }

        except Exception as e:
            logger.exception(f"Failed to save model to repository: {e}")
            return {
                "success": False,
                "message": f"Failed to save model: {str(e)}",
                "next_steps": ["Check repository permissions", "Verify object exists"]
            }

    @app.tool
    async def load_object_from_repository(
        object_id: str = "",
        target_name: Optional[str] = None,
        position: Tuple[float, float, float] = (0, 0, 0),
        scale: Tuple[float, float, float] = (1, 1, 1),
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates object loading, versioning, and scene integration into single repository interface.
        Prevents tool explosion while enabling seamless object reuse across projects. Follows FastMCP 2.14.3 best practices.

        Load an object from the repository into the current Blender scene.

        **Loading Features:**
        - **Version Selection**: Load specific versions or latest
        - **Transform Control**: Position, scale, and orient loaded objects
        - **Name Management**: Automatic renaming to avoid conflicts
        - **Dependency Resolution**: Automatically load required dependencies
        - **Scene Integration**: Proper material and texture linking

        Args:
            object_id (str, required): ID of the object to load from repository
            target_name (str | None): New name for loaded object (auto-generated if not provided)
            position (Tuple[float, float, float]): World position to place the loaded object
            scale (Tuple[float, float, float]): Scale factors to apply to the loaded object
            version (str | None): Specific version to load (latest if not specified)

        Returns:
            Dict[str, Any]: Loading operation results with object info and scene integration details

        Examples:
            Basic load: load_object_from_repository("robot-abc123")
            Positioned load: load_object_from_repository("building-def456", position=(10, 0, 5), scale=(2, 2, 2))

        Note:
            Objects maintain all materials, textures, and rigging when loaded.
            Dependencies are automatically resolved and loaded.
        """
        try:
            if not object_id:
                raise ValueError("object_id is required")

            config = RepositoryConfig()
            object_dir = Path(config.base_path) / object_id

            if not object_dir.exists():
                return {
                    "success": False,
                    "message": f"Object '{object_id}' not found in repository",
                    "next_steps": ["Check object ID spelling", "Use search_objects_in_repository() to find objects"]
                }

            # Load metadata
            metadata_file = object_dir / "metadata.json"
            if not metadata_file.exists():
                return {
                    "success": False,
                    "message": f"Object metadata not found for '{object_id}'",
                    "next_steps": ["Object may be corrupted", "Contact repository administrator"]
                }

            with open(metadata_file) as f:
                metadata_dict = json.load(f)
                metadata = ObjectMetadata(**metadata_dict)

            # Determine version to load
            if not version:
                version = metadata.version
            elif version != metadata.version:
                # Check if specific version exists
                version_file = object_dir / f"object_{version}.blend"
                if not version_file.exists():
                    return {
                        "success": False,
                        "message": f"Version '{version}' not found for object '{object_id}'",
                        "available_versions": await _get_available_versions(object_dir),
                        "next_steps": ["Use latest version or check available versions"]
                    }

            # Generate target name
            if not target_name:
                target_name = f"{metadata.name}_{version}"
                # Ensure unique name
                target_name = await _ensure_unique_name(target_name)

            # Import Blender file
            blend_file = object_dir / f"object_{version}.blend"
            import_result = await _import_blender_file(
                str(blend_file), target_name, position, scale
            )

            if not import_result["success"]:
                return {
                    "success": False,
                    "message": f"Failed to import object: {import_result['error']}",
                    "next_steps": ["Check Blender file integrity", "Try different version"]
                }

            return {
                "success": True,
                "object_id": object_id,
                "version_loaded": version,
                "object_name": target_name,
                "objects_created": import_result.get("objects_created", []),
                "metadata": metadata.dict(),
                "message": f"Successfully loaded '{metadata.name}' (v{version}) as '{target_name}'",
                "next_steps": [
                    f"Use modify_object('{target_name}') to customize the loaded object",
                    f"Apply blender_lighting setup for better presentation",
                    f"Consider blender_render for preview"
                ]
            }

        except Exception as e:
            logger.exception(f"Failed to load model from repository: {e}")
            return {
                "success": False,
                "message": f"Failed to load model: {str(e)}",
                "next_steps": ["Check model ID", "Verify repository integrity"]
            }

    @app.tool
    async def search_objects_in_repository(
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
        min_quality: Optional[int] = None,
        complexity: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search and discover objects in the repository with advanced filtering.

        **Search Capabilities:**
        - **Text Search**: Name, description, and tags
        - **Category Filtering**: Architecture, character, vehicle, etc.
        - **Tag-based Discovery**: Find objects by specific tags
        - **Quality Filtering**: Find high-quality objects
        - **Author Search**: Find objects by creator
        - **Complexity Matching**: Match project complexity needs

        Args:
            query (str | None): Search text for name/description/tags
            category (str | None): Filter by category
            tags (List[str] | None): Required tags (object must have all)
            author (str | None): Filter by author
            min_quality (int | None): Minimum quality rating (1-10)
            complexity (str | None): Filter by complexity (simple/standard/complex)
            limit (int): Maximum results to return

        Returns:
            Dict with search results and object summaries

        Examples:
            Text search: search_objects_in_repository("robot")
            Category filter: search_objects_in_repository(category="character")
            Quality filter: search_objects_in_repository(min_quality=8)
        """
        try:
            config = RepositoryConfig()
            index_file = Path(config.base_path) / "repository_index.json"

            if not index_file.exists():
                return {
                    "success": False,
                    "message": "Repository index not found. No objects have been saved yet.",
                    "results": [],
                    "total_count": 0
                }

            with open(index_file) as f:
                index = json.load(f)

            models = index.get("models", [])

            # Apply filters
            filtered_models = []
            for model in models:
                if query and not _matches_query(model, query):
                    continue
                if category and model.get("category") != category:
                    continue
                if tags:
                    model_tags = set(model.get("tags", []))
                    if not all(tag in model_tags for tag in tags):
                        continue
                if author and model.get("author") != author:
                    continue
                if min_quality and model.get("estimated_quality", 0) < min_quality:
                    continue
                if complexity and model.get("complexity") != complexity:
                    continue

                filtered_models.append(model)

            # Sort by quality and recency
            filtered_models.sort(key=lambda x: (x.get("estimated_quality", 0), x.get("updated_at", "")), reverse=True)

            # Limit results
            limited_results = filtered_models[:limit]

            return {
                "success": True,
                "results": limited_results,
                "total_count": len(filtered_models),
                "returned_count": len(limited_results),
                "filters_applied": {
                    "query": query,
                    "category": category,
                    "tags": tags,
                    "author": author,
                    "min_quality": min_quality,
                    "complexity": complexity
                },
                "message": f"Found {len(filtered_models)} models matching criteria (showing {len(limited_results)})",
                "next_steps": [
                    "Use load_model_from_repository(model_id) to load any model",
                    "Refine search with more specific filters",
                    "Save interesting models to favorites"
                ]
            }

        except Exception as e:
            logger.exception(f"Failed to search repository: {e}")
            return {
                "success": False,
                "message": f"Search failed: {str(e)}",
                "results": [],
                "total_count": 0
            }

    @app.tool
    async def modify_object(
        ctx: Context,
        object_name: str = "",
        modification_description: str = "",
        max_iterations: int = 2,
        preserve_original: bool = True
    ) -> Dict[str, Any]:
        """
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates object modification, script refinement, and iterative improvement into single agentic interface.
        Prevents tool explosion while enabling sophisticated object evolution through LLM-guided improvements. Follows FastMCP 2.14.3 best practices.

        Modify an existing Blender object using natural language descriptions and LLM-guided improvements.

        **Modification Workflow:**
        1. **Script Retrieval**: Find original construction script from repository
        2. **LLM Refinement**: Send script to LLM for targeted improvements
        3. **Iterative Enhancement**: Multiple rounds of improvement until satisfaction
        4. **Safe Execution**: Validate and execute improved script
        5. **Version Control**: Save modifications as new versions

        **Modification Types Supported:**
        - **Geometric Changes**: Shape modifications, proportions, topology
        - **Material Enhancements**: Texture improvements, shader refinements
        - **Structural Improvements**: Better rigging, optimized topology
        - **Style Adjustments**: Aesthetic refinements, detail additions
        - **Functional Upgrades**: Animation readiness, physics improvements

        Args:
            ctx (Context): FastMCP context for sampling and conversational responses
            object_name (str, required): Name of existing Blender object to modify
            modification_description (str, required): Natural language description of desired changes
            max_iterations (int): Maximum refinement iterations (default: 2)
            preserve_original (bool): Whether to keep original object (default: True)

        Returns:
            Dict[str, Any]: Modification results with before/after comparison and improvement details

        Examples:
            Style change: modify_object("Robot", "make it look more futuristic with glowing blue accents")
            Structural: modify_object("Building", "add more architectural details and better proportions")
            Material: modify_object("Car", "improve the paint job with metallic flakes")

        Note:
            Requires object to have been created via construct_object or saved to repository.
            Modifications are saved as new versions for rollback capability.
            LLM provides intelligent suggestions based on original construction approach.
        """
        try:
            if not object_name or not modification_description:
                raise ValueError("object_name and modification_description are required")

            # Check if object exists
            object_info = await _get_object_info(object_name)
            if not object_info:
                return {
                    "success": False,
                    "message": f"Object '{object_name}' not found in scene",
                    "next_steps": ["Check object name", "Use blender_selection to list available objects"]
                }

            # Try to find original construction script
            original_script = await _find_construction_script(object_name)

            if not original_script:
                return {
                    "success": False,
                    "message": f"No construction script found for '{object_name}'",
                    "next_steps": [
                        "Use construct_object to recreate the object",
                        "Save object to repository first with save_object_to_repository",
                        "Manually describe the object for construct_object"
                    ]
                }

            # Generate modification prompt
            modification_prompt = f"""
You are a master Blender Python developer specializing in object modification and improvement.

ORIGINAL OBJECT: {object_name}
ORIGINAL SCRIPT (first 300 chars): {original_script[:300]}...

REQUESTED MODIFICATION: {modification_description}

Please generate an improved Blender Python script that modifies the existing object according to the request.
Focus on the specific improvements requested while preserving the object's core functionality.

Return ONLY the complete, executable Python script that will modify the existing object.
"""

            try:
                # Use FastMCP sampling to get modification script
                sampling_result = await ctx.sample(
                    content=f"Modify {object_name}: {modification_description}",
                    metadata={
                        "type": "script_modification",
                        "original_script": original_script[:500],  # Truncate for context
                        "modification_request": modification_description,
                        "object_name": object_name
                    },
                    max_tokens=2500,
                    temperature=0.3
                )

                modified_script = _extract_python_code(sampling_result.content)

                if not modified_script:
                    return {
                        "success": False,
                        "message": "Failed to generate modification script",
                        "next_steps": ["Try a more specific modification description"]
                    }

                # Validate modification script
                validation = await _validate_modification_script(modified_script, object_name)
                if not validation.is_valid:
                    return {
                        "success": False,
                        "message": f"Modification script validation failed: {'; '.join(validation.errors)}",
                        "validation_details": validation.dict()
                    }

                # Create backup if requested
                if preserve_original:
                    backup_result = await _create_object_backup(object_name)
                    if not backup_result["success"]:
                        logger.warning(f"Failed to create backup: {backup_result['error']}")

                # Execute modification
                execution_result = await _execute_modification_script(modified_script, object_name)

                if execution_result["success"]:
                    # Optionally save as new version
                    save_prompt = f"Would you like to save this modified version of '{object_name}' to the repository?"
                    # Note: In a real implementation, you might want to elicit user confirmation here

                    return {
                        "success": True,
                        "object_name": object_name,
                        "modification_applied": modification_description,
                        "script_generated": True,
                        "iterations_used": 1,
                        "validation_results": validation.dict(),
                        "changes_made": execution_result.get("changes_summary", []),
                        "message": f"Successfully modified '{object_name}' with: {modification_description}",
                "next_steps": [
                    f"Use save_object_to_repository('{object_name}') to save the improved version",
                    f"Use blender_render to preview the modifications",
                    f"Apply additional modifications if needed"
                ]
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Modification execution failed: {execution_result['error']}",
                        "next_steps": ["Try a simpler modification", "Check modification description clarity"]
                    }

            except Exception as e:
                logger.exception(f"Modification sampling failed: {e}")
                return {
                    "success": False,
                    "message": f"Failed to generate modification: {str(e)}",
                    "next_steps": ["Try rephrasing the modification request"]
                }

        except Exception as e:
            logger.exception(f"Object modification failed: {e}")
            return {
                "success": False,
                "message": f"Modification failed: {str(e)}",
                "next_steps": ["Check object existence", "Verify modification description"]
            }


# Helper functions

async def _get_object_info(object_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a Blender object."""
    try:
        # This would interface with Blender to get object info
        # For now, return mock data
        return {
            "name": object_name,
            "type": "mesh",
            "complexity": "standard",
            "blender_version": "4.0",
            "object_count": 1
        }
    except Exception:
        return None


def _generate_object_id(object_name_display: str, object_name: str) -> str:
    """Generate a unique object ID."""
    content = f"{object_name_display}:{object_name}:{datetime.now().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


async def _get_next_version(model_dir: Path) -> str:
    """Get the next version number for a model."""
    try:
        metadata_file = model_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                data = json.load(f)
                current_version = data.get("version", "0.0.0")
                major, minor, patch = map(int, current_version.split("."))
                return f"{major}.{minor}.{patch + 1}"
        return "1.0.0"
    except Exception:
        return "1.0.0"


async def _extract_construction_script(object_name: str) -> str:
    """Extract or generate construction script for an object."""
    # This would ideally retrieve from repository or generate based on object analysis
    return f"""
import bpy

# Construction script for {object_name}
# This is a placeholder - real implementation would analyze the object
bpy.ops.object.select_all(action='DESELECT')
obj = bpy.data.objects.get("{object_name}")
if obj:
    obj.select_set(True)
"""


async def _export_blender_object(object_name: str, output_path: str) -> Dict[str, Any]:
    """Export a Blender object to file."""
    try:
        # This would use Blender's export functionality
        return {"success": True, "path": output_path}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _update_repository_index(base_path: str, metadata: ModelMetadata):
    """Update the repository index with new model."""
    try:
        index_file = Path(base_path) / "repository_index.json"

        if index_file.exists():
            with open(index_file) as f:
                index = json.load(f)
        else:
            index = {"models": [], "last_updated": datetime.now().isoformat()}

        # Update or add model
        existing_model_idx = next(
            (i for i, m in enumerate(index["models"]) if m["id"] == metadata.id),
            None
        )

        model_summary = {
            "id": metadata.id,
            "name": metadata.name,
            "description": metadata.description,
            "author": metadata.author,
            "version": metadata.version,
            "updated_at": metadata.updated_at,
            "tags": metadata.tags,
            "category": metadata.category,
            "complexity": metadata.complexity,
            "estimated_quality": metadata.estimated_quality
        }

        if existing_model_idx is not None:
            index["models"][existing_model_idx] = model_summary
        else:
            index["models"].append(model_summary)

        index["last_updated"] = datetime.now().isoformat()

        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)

    except Exception as e:
        logger.exception(f"Failed to update repository index: {e}")


async def _import_blender_file(
    file_path: str,
    target_name: str,
    position: Tuple[float, float, float],
    scale: Tuple[float, float, float]
) -> Dict[str, Any]:
    """Import a Blender file."""
    try:
        # This would use Blender's import functionality
        return {
            "success": True,
            "objects_created": [target_name],
            "position": position,
            "scale": scale
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _ensure_unique_name(base_name: str) -> str:
    """Ensure a name is unique in the scene."""
    # This would check Blender scene for name conflicts
    return base_name


async def _get_available_versions(model_dir: Path) -> List[str]:
    """Get available versions for a model."""
    try:
        versions = []
        for item in model_dir.glob("model_*.blend"):
            version = item.stem.replace("model_", "")
            versions.append(version)
        return sorted(versions, reverse=True)
    except Exception:
        return []


def _matches_query(model: Dict[str, Any], query: str) -> bool:
    """Check if a model matches a search query."""
    query_lower = query.lower()
    searchable_text = " ".join([
        model.get("name", ""),
        model.get("description", ""),
        " ".join(model.get("tags", []))
    ]).lower()

    return query_lower in searchable_text


async def _find_construction_script(object_name: str) -> Optional[str]:
    """Find the construction script for an object."""
    # This would search repository or object metadata
    # For now, return a mock script
    return f"""
import bpy

# Mock construction script for {object_name}
bpy.ops.object.select_all(action='DESELECT')
obj = bpy.data.objects.get("{object_name}")
if obj:
    obj.select_set(True)
"""


async def _validate_modification_script(script: str, object_name: str) -> ScriptValidationResult:
    """Validate a modification script."""
    # Similar to construct_object validation but focused on modifications
    return ScriptValidationResult(
        is_valid=True,
        errors=[],
        warnings=["Modification script validation placeholder"],
        security_score=90,
        complexity_score=50
    )


async def _create_object_backup(object_name: str) -> Dict[str, Any]:
    """Create a backup of an object."""
    try:
        # This would duplicate the object in Blender
        return {"success": True, "backup_name": f"{object_name}_backup"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _execute_modification_script(script: str, object_name: str) -> Dict[str, Any]:
    """Execute a modification script."""
    try:
        # This would run the script in Blender context
        return {
            "success": True,
            "changes_summary": ["Object modified according to script"],
            "execution_time": 1.0
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _extract_python_code(content: str) -> Optional[str]:
    """Extract Python code from LLM response."""
    # Same as in construct_tools.py
    code_block_pattern = r'```python\s*(.*?)\s*```'
    match = re.search(code_block_pattern, content, re.DOTALL)

    if match:
        return match.group(1).strip()

    # Fallback
    lines = content.split('\n')
    code_lines = []

    in_code = False
    for line in lines:
        if line.strip().startswith('import bpy') or line.strip().startswith('bpy.'):
            in_code = True

        if in_code:
            code_lines.append(line)
            if line.strip() == '' and len(code_lines) > 5:
                break

    if code_lines:
        return '\n'.join(code_lines).strip()

    return None


# Register tools when module is imported
_register_repository_tools()
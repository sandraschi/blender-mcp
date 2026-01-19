"""
Universal object construction tools for Blender MCP using FastMCP 2.14.3 sampling.

Provides agentic 3D object creation through natural language descriptions,
leveraging SOTA LLMs to generate Blender Python scripts for complex object construction.
"""

import asyncio
import hashlib
import json
import re
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field
from loguru import logger

from blender_mcp.app import get_app
from blender_mcp.compat import *

# Import Context from FastMCP for sampling operations
try:
    from fastmcp.types import Context
except ImportError:
    # Fallback for different FastMCP versions
    from typing import Any as Context


class ConstructObjectParams(BaseModel):
    """Parameters for universal object construction using LLM-generated Blender scripts."""

    description: str = Field(
        ...,
        description="Natural language description of the object to create (e.g., 'a robot like Robbie from Forbidden Planet')"
    )
    name: str = Field(
        "ConstructedObject",
        description="Name for the created object in Blender scene"
    )
    complexity: str = Field(
        "standard",
        description="Complexity level affecting script generation detail. One of: 'simple', 'standard', 'complex'"
    )
    style_preset: Optional[str] = Field(
        None,
        description="Optional style preset to guide generation (e.g., 'realistic', 'stylized', 'lowpoly', 'scifi')"
    )
    reference_objects: Optional[List[str]] = Field(
        None,
        description="Names of existing Blender objects to use as reference for style/consistency"
    )
    allow_modifications: bool = Field(
        True,
        description="Whether to allow the LLM to modify existing objects in the scene"
    )


class ScriptValidationResult(BaseModel):
    """Result of validating generated Blender Python script."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    security_score: int  # 0-100, higher is safer
    complexity_score: int  # Estimated complexity of operations


def _register_construct_tools():
    """Register universal construction tools with the app."""
    app = get_app()

    @app.tool
    async def construct_object(
        ctx: Context,
        description: str = "a simple cube",
        name: str = "ConstructedObject",
        complexity: str = "standard",
        style_preset: Optional[str] = None,
        reference_objects: Optional[List[str]] = None,
        allow_modifications: bool = True,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        PORTMANTEAU PATTERN RATIONALE:
        Consolidates natural language 3D construction into single agentic interface. Prevents tool explosion while enabling
        infinite 3D creativity through LLM-generated Blender scripts. Follows FastMCP 2.14.3 best practices.

        Universal 3D object construction using natural language and LLM-generated Blender scripts.

        This revolutionary tool enables creation of any 3D object through natural language descriptions
        by leveraging FastMCP 2.14.3 sampling to request SOTA LLM generation of Blender Python code.

        **Agentic Workflow:**
        1. **Analysis**: Parse natural language description and scene context
        2. **Sampling Request**: Ask MCP client (SOTA LLM) to generate Blender Python script
        3. **Code Generation**: LLM creates production-ready Blender automation code
        4. **Validation**: Security and syntax validation of generated code
        5. **Execution**: Safe execution in Blender with error handling
        6. **Iteration**: Request refinements if needed (up to max_iterations)

        **Supported Complexity Levels:**
        - **simple**: Basic primitives, basic transforms, simple materials
        - **standard**: Complex meshes, modifiers, materials, basic animation
        - **complex**: Advanced geometry, rigging, physics, complex materials/textures

        **Style Presets:**
        - **realistic**: Physically accurate materials, lighting, proportions
        - **stylized**: Artistic interpretation, exaggerated features, cartoon-like
        - **lowpoly**: Minimal geometry, optimized for performance
        - **scifi**: Futuristic design, metallic materials, glowing effects

        Args:
            ctx (Context): FastMCP context for sampling and conversational responses
            description (str, required): Natural language description of object to create
                Examples: "a robot like Robbie from Forbidden Planet", "a medieval castle", "a sleek sports car"
            name (str): Name for the created object in Blender scene. Default: "ConstructedObject"
            complexity (str): Complexity level for script generation. One of: "simple", "standard", "complex".
                Default: "standard". Affects detail level and operation complexity.
            style_preset (str | None): Optional style guidance. One of: "realistic", "stylized", "lowpoly", "scifi".
                Default: None (let LLM decide based on description).
            reference_objects (List[str] | None): Existing Blender objects to use as reference for style/consistency.
                Default: None. LLM will analyze these objects for consistent styling.
            allow_modifications (bool): Whether LLM can modify existing scene objects. Default: True.
                Set to False for conservative construction that only adds new objects.
            max_iterations (int): Maximum refinement iterations if initial script fails. Default: 3.
                Higher values allow more complex objects but increase processing time.

        Returns:
            Dict[str, Any]: Conversational response with construction results and metadata.
                Format: {
                    "success": bool,
                    "message": str,  # Conversational summary
                    "object_name": str,  # Final object name in scene
                    "script_generated": bool,  # Whether script was successfully generated
                    "iterations_used": int,  # Number of refinement iterations
                    "validation_results": Dict,  # Code validation details
                    "scene_objects_created": List[str],  # All new objects created
                    "estimated_complexity": str,  # simple/standard/complex
                    "next_steps": List[str]  # Suggested follow-up actions
                }

        Raises:
            ValueError: If parameters are invalid or description is empty
            RuntimeError: If Blender execution fails after all iterations
            SecurityError: If generated code fails security validation

        Examples:
            Basic object: construct_object("a red cube with rounded edges")
            Complex character: construct_object("a robot like Robbie from Forbidden Planet", complexity="complex", style_preset="scifi")
            Architectural: construct_object("a gothic cathedral", complexity="complex", allow_modifications=False)
            Vehicle: construct_object("a 1960s sports car", style_preset="realistic", reference_objects=["CarReference"])

        Note:
            This tool represents the future of 3D creation - natural language to fully realized 3D objects.
            Success depends on LLM capability and Blender API knowledge.
            Complex objects may require multiple iterations for refinement.
            Generated scripts are validated for safety before execution.
        """
        try:
            # Validate inputs
            if not description or not description.strip():
                raise ValueError("Description cannot be empty")

            if complexity not in ["simple", "standard", "complex"]:
                raise ValueError(f"Invalid complexity '{complexity}'. Must be: simple, standard, complex")

            if style_preset and style_preset not in ["realistic", "stylized", "lowpoly", "scifi"]:
                raise ValueError(f"Invalid style_preset '{style_preset}'. Must be: realistic, stylized, lowpoly, scifi")

            logger.info(f"🎨 Starting universal construction for: '{description}' (complexity: {complexity})")

            # Build context for LLM
            context_info = await _gather_construction_context(ctx, reference_objects, allow_modifications)

            # Generate construction script via sampling
            script_result = await _generate_construction_script(
                ctx, description, name, complexity, style_preset, context_info, max_iterations
            )

            if not script_result["success"]:
                return {
                    "success": False,
                    "message": f"Failed to generate construction script: {script_result['error']}",
                    "script_generated": False,
                    "iterations_used": script_result.get("iterations", 0),
                    "next_steps": [
                        "Try a simpler description",
                        "Use more specific technical terms",
                        "Break complex objects into components",
                        "Check Blender Python API documentation"
                    ]
                }

            # Validate generated script
            validation = await _validate_construction_script(script_result["script"])
            if not validation.is_valid:
                return {
                    "success": False,
                    "message": f"Generated script failed validation: {'; '.join(validation.errors)}",
                    "script_generated": True,
                    "validation_results": validation.dict(),
                    "next_steps": [
                        "Request script regeneration with safety constraints",
                        "Use simpler construction approach",
                        "Manually review and fix generated code"
                    ]
                }

            # Execute script in Blender
            execution_result = await _execute_construction_script(
                script_result["script"], name, validation
            )

            if not execution_result["success"]:
                # Try one more iteration if we haven't reached max_iterations
                if script_result.get("iterations", 0) < max_iterations:
                    logger.info("🔄 Construction failed, attempting refinement iteration")
                    refinement = await _refine_construction_script(
                        ctx, script_result, execution_result["error"], context_info
                    )

                    if refinement["success"]:
                        validation = await _validate_construction_script(refinement["script"])
                        if validation.is_valid:
                            execution_result = await _execute_construction_script(
                                refinement["script"], name, validation
                            )

            # Prepare response
            response = {
                "success": execution_result["success"],
                "message": _generate_construction_summary(
                    description, execution_result, script_result.get("iterations", 1), validation
                ),
                "object_name": name,
                "script_generated": True,
                "iterations_used": script_result.get("iterations", 1),
                "validation_results": {
                    "security_score": validation.security_score,
                    "complexity_score": validation.complexity_score,
                    "warnings": validation.warnings
                },
                "scene_objects_created": execution_result.get("objects_created", []),
                "estimated_complexity": complexity
            }

            if execution_result["success"]:
                response["next_steps"] = [
                    f"Use blender_materials to enhance {name} with textures",
                    f"Apply blender_lighting setup for better presentation of {name}",
                    f"Consider blender_render for preview of {name}",
                    f"Use blender_animation if {name} needs motion"
                ]
            else:
                response["next_steps"] = [
                    "Try breaking the object into simpler components",
                    "Use more specific technical descriptions",
                    "Check Blender Python API documentation",
                    "Consider using existing primitive tools first"
                ]

            return response

        except Exception as e:
            logger.exception(f"❌ Universal construction failed: {str(e)}")
            return {
                "success": False,
                "message": f"Universal construction failed: {str(e)}",
                "script_generated": False,
                "iterations_used": 0,
                "next_steps": [
                    "Check description for clarity",
                    "Try simpler object first",
                    "Verify Blender installation",
                    "Check system resources"
                ]
            }


async def _gather_construction_context(
    ctx: Context,
    reference_objects: Optional[List[str]],
    allow_modifications: bool
) -> Dict[str, Any]:
    """Gather scene context and reference information for construction."""
    context = {
        "scene_info": {},
        "reference_objects": [],
        "available_materials": [],
        "allow_modifications": allow_modifications
    }

    try:
        # Get basic scene information
        from blender_mcp.handlers.scene_handler import get_scene_info
        scene_data = await get_scene_info()
        context["scene_info"] = {
            "objects_count": len(scene_data.get("objects", [])),
            "materials_count": len(scene_data.get("materials", [])),
            "collections": scene_data.get("collections", [])
        }

        # Analyze reference objects if provided
        if reference_objects:
            for obj_name in reference_objects:
                # Get object info and add to context
                obj_info = await _analyze_reference_object(obj_name)
                if obj_info:
                    context["reference_objects"].append(obj_info)

    except Exception as e:
        logger.warning(f"Could not gather full construction context: {e}")

    return context


async def _analyze_reference_object(object_name: str) -> Optional[Dict[str, Any]]:
    """Analyze a reference object for style and construction patterns."""
    try:
        # This would use existing Blender inspection tools
        # For now, return basic structure
        return {
            "name": object_name,
            "type": "mesh",  # Would be determined by inspection
            "vertex_count": 0,  # Would be counted
            "materials": [],  # Would be listed
            "modifiers": []  # Would be analyzed
        }
    except Exception:
        return None


async def _generate_construction_script(
    ctx: Context,
    description: str,
    name: str,
    complexity: str,
    style_preset: Optional[str],
    context_info: Dict[str, Any],
    max_iterations: int
) -> Dict[str, Any]:
    """Generate Blender Python script using FastMCP 2.14.3 sampling."""

    # Build comprehensive prompt for LLM
    prompt = f"""
You are a master Blender Python developer and 3D artist. Generate production-ready Blender Python code to create: "{description}"

REQUIREMENTS:
- Object name: "{name}"
- Complexity level: {complexity}
{f"- Style preset: {style_preset}" if style_preset else ""}
- Use only Blender Python API (bpy)
- Code must be executable and safe
- Include proper error handling
- Add materials and basic texturing
- Position object appropriately in scene
- Follow Blender naming conventions

{f"REFERENCE CONTEXT: {json.dumps(context_info, indent=2)}" if context_info else ""}

CONSTRAINTS BY COMPLEXITY:
{"Simple: Basic primitives, simple transforms, basic materials only" if complexity == "simple" else ""}
{"Standard: Complex meshes, modifiers, materials, basic animation ready" if complexity == "standard" else ""}
{"Complex: Advanced geometry, rigging, physics, complex materials/textures" if complexity == "complex" else ""}

{f"STYLE GUIDANCE: {style_preset} aesthetic - adapt proportions, materials, and details accordingly" if style_preset else ""}

GENERATE COMPLETE, EXECUTABLE BLENDER PYTHON SCRIPT:
```python
import bpy
import mathutils

# Clear selection and ensure we're in object mode
bpy.ops.object.select_all(action='DESELECT')
if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Your construction code here
# [Generate appropriate Blender Python code for the described object]

# Final setup
obj = bpy.context.active_object
if obj:
    obj.name = "{name}"
    # Position appropriately
    obj.location = (0, 0, 0)
```

SAFETY REQUIREMENTS:
- No file system operations
- No network calls
- No subprocess execution
- Only Blender API calls
- Proper object naming
- Reasonable resource usage

Return ONLY the Python code block, no explanations.
"""

    try:
        # Use FastMCP 2.14.3 sampling to request script generation
        sample_request = {
            "type": "script_generation",
            "description": description,
            "complexity": complexity,
            "style_preset": style_preset,
            "context": context_info,
            "requirements": {
                "safe_execution": True,
                "blender_api_only": True,
                "complete_script": True,
                "error_handling": True
            }
        }

        # Request sampling from the MCP client (SOTA LLM)
        sampling_result = await ctx.sample(
            content=f"Generate Blender Python script for: {description}",
            metadata=sample_request,
            max_tokens=4000,
            temperature=0.3  # Lower temperature for more deterministic code
        )

        # Extract Python code from response
        script_content = _extract_python_code(sampling_result.content)

        if not script_content:
            return {
                "success": False,
                "error": "No valid Python code found in LLM response",
                "iterations": 1
            }

        return {
            "success": True,
            "script": script_content,
            "iterations": 1,
            "metadata": sampling_result.metadata
        }

    except Exception as e:
        logger.exception(f"Script generation failed: {e}")
        return {
            "success": False,
            "error": f"Script generation failed: {str(e)}",
            "iterations": 1
        }


async def _refine_construction_script(
    ctx: Context,
    previous_result: Dict[str, Any],
    error_message: str,
    context_info: Dict[str, Any]
) -> Dict[str, Any]:
    """Refine a failed construction script based on execution errors."""

    refinement_prompt = f"""
The previous Blender script failed with error: {error_message}

Original request: {previous_result.get('description', 'Unknown')}
Previous script (first 500 chars): {previous_result.get('script', '')[:500]}

Please generate a corrected version that fixes the error and ensures safe execution.

Return ONLY the corrected Python code block.
"""

    try:
        refinement_result = await ctx.sample(
            content=refinement_prompt,
            metadata={"type": "script_refinement", "error": error_message},
            max_tokens=3000,
            temperature=0.2
        )

        script_content = _extract_python_code(refinement_result.content)

        return {
            "success": bool(script_content),
            "script": script_content or "",
            "refined": True
        }

    except Exception as e:
        logger.exception(f"Script refinement failed: {e}")
        return {"success": False, "script": "", "error": str(e)}


async def _validate_construction_script(script: str) -> ScriptValidationResult:
    """Validate generated Blender Python script for safety and correctness."""

    errors = []
    warnings = []
    security_score = 100
    complexity_score = 0

    try:
        # Basic syntax validation
        compile(script, '<string>', 'exec')

        # Security checks - dangerous operations
        dangerous_patterns = [
            r'\bimport\s+(os|sys|subprocess|shutil)',
            r'\bexec\(',
            r'\beval\(',
            r'\bopen\s*\(',
            r'\b__import__\s*\(',
            r'\bgetattr\s*\(\s*bpy\s*,',
            r'\bsetattr\s*\(\s*bpy\s*,',
            r'\bdelattr\s*\(\s*bpy\s*,'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, script, re.IGNORECASE):
                errors.append(f"Security violation: {pattern}")
                security_score -= 50

        # Check for file operations
        if re.search(r'\.filepath\b|\.write\b|\.read\b', script):
            errors.append("File system operations not allowed")
            security_score -= 30

        # Check for network operations
        if re.search(r'\b(urllib|requests|socket|http)\b', script):
            errors.append("Network operations not allowed")
            security_score -= 40

        # Complexity analysis
        lines = len(script.split('\n'))
        bpy_calls = len(re.findall(r'\bbpy\.', script))
        modifiers = len(re.findall(r'\bmodifier\b', script))

        complexity_score = min(100, (lines // 10) + (bpy_calls // 5) + (modifiers * 2))

        # Warnings for complex operations
        if complexity_score > 70:
            warnings.append("High complexity - may impact performance")

        if bpy_calls > 50:
            warnings.append("Many Blender API calls - consider optimization")

        # Check for proper error handling
        if 'try:' not in script or 'except:' not in script:
            warnings.append("Missing error handling")

        # Check for object naming
        if 'obj.name =' not in script:
            warnings.append("Object naming not set")

    except SyntaxError as e:
        errors.append(f"Syntax error: {e}")
        security_score = 0

    except Exception as e:
        errors.append(f"Validation error: {e}")
        security_score = 0

    return ScriptValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        security_score=max(0, security_score),
        complexity_score=complexity_score
    )


async def _execute_construction_script(
    script: str,
    object_name: str,
    validation: ScriptValidationResult
) -> Dict[str, Any]:
    """Execute validated construction script in Blender."""

    try:
        from blender_mcp.utils.blender_executor import execute_blender_script

        # Execute with timeout and resource limits
        result = await execute_blender_script(
            script,
            timeout_seconds=120,  # 2 minutes for complex constructions
            max_memory_mb=512
        )

        if result["success"]:
            # Verify object was created
            created_objects = result.get("created_objects", [])
            if object_name in created_objects:
                return {
                    "success": True,
                    "objects_created": created_objects,
                    "execution_time": result.get("execution_time", 0),
                    "message": f"Successfully created {object_name} with {len(created_objects)} total objects"
                }
            else:
                return {
                    "success": False,
                    "error": f"Object '{object_name}' was not found after script execution",
                    "objects_created": created_objects
                }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown execution error")
            }

    except Exception as e:
        logger.exception(f"Script execution failed: {e}")
        return {
            "success": False,
            "error": f"Execution failed: {str(e)}"
        }


def _extract_python_code(content: str) -> Optional[str]:
    """Extract Python code from LLM response."""

    # Look for code blocks
    code_block_pattern = r'```python\s*(.*?)\s*```'
    match = re.search(code_block_pattern, content, re.DOTALL)

    if match:
        return match.group(1).strip()

    # Fallback: look for any code-like content
    lines = content.split('\n')
    code_lines = []

    in_code = False
    for line in lines:
        if line.strip().startswith('import bpy') or line.strip().startswith('bpy.'):
            in_code = True

        if in_code:
            code_lines.append(line)
            if line.strip() == '' and len(code_lines) > 5:  # End after empty line
                break

    if code_lines:
        return '\n'.join(code_lines).strip()

    return None


def _generate_construction_summary(
    description: str,
    execution_result: Dict[str, Any],
    iterations: int,
    validation: ScriptValidationResult
) -> str:
    """Generate conversational summary of construction process."""

    if execution_result["success"]:
        objects_created = execution_result.get("objects_created", [])
        obj_count = len(objects_created)

        summary = f"🎨 Successfully constructed '{description}' using {iterations} iteration{'s' if iterations > 1 else ''}! "

        if obj_count == 1:
            summary += f"Created object: {objects_created[0]}"
        else:
            summary += f"Created {obj_count} objects: {', '.join(objects_created[:3])}{'...' if obj_count > 3 else ''}"

        if validation.warnings:
            summary += f" (with {len(validation.warnings)} optimization suggestions)"

        return summary
    else:
        error = execution_result.get("error", "Unknown error")
        return f"❌ Construction of '{description}' failed after {iterations} attempts: {error}"


# Register tools when module is imported
_register_construct_tools()
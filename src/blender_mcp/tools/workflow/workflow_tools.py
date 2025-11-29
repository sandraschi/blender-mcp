"""
Workflow/macro tool for Blender MCP.

Execute multiple Blender operations in a single call, reducing round-trips
and enabling complex workflows to be saved and reused.
"""

from blender_mcp.compat import *

from typing import List, Dict, Any, Optional, Literal
import json
from blender_mcp.app import get_app


# Predefined workflow templates
WORKFLOW_TEMPLATES = {
    "product_shot": {
        "description": "Create a product visualization setup",
        "steps": [
            {"tool": "blender_scene", "operation": "clear_scene"},
            {"tool": "blender_scene", "operation": "setup_lighting", "light_type": "AREA"},
            {"tool": "blender_scene", "operation": "setup_camera", "location": [0, -5, 2]},
            {"tool": "blender_mesh", "operation": "create_plane", "name": "Ground", "scale": [10, 10, 1]},
        ]
    },
    "turntable_setup": {
        "description": "Setup for 360° turntable render",
        "steps": [
            {"tool": "blender_scene", "operation": "setup_lighting", "light_type": "AREA"},
            {"tool": "blender_scene", "operation": "setup_camera", "location": [0, -5, 1.5]},
            {"tool": "blender_animation", "operation": "set_frame_range", "start_frame": 1, "end_frame": 120},
        ]
    },
    "vrm_import": {
        "description": "Import VRM and prepare for animation",
        "steps": [
            {"tool": "blender_scene", "operation": "clear_scene"},
            # Note: filepath must be provided via params
        ]
    },
    "simple_scene": {
        "description": "Create a simple scene with cube, light, and camera",
        "steps": [
            {"tool": "blender_scene", "operation": "clear_scene"},
            {"tool": "blender_mesh", "operation": "create_cube", "name": "Cube"},
            {"tool": "blender_lighting", "operation": "create_sun"},
            {"tool": "blender_scene", "operation": "setup_camera", "location": [5, -5, 3]},
        ]
    },
}


def _register_workflow_tools():
    """Register workflow/macro tools."""
    app = get_app()

    @app.tool
    async def blender_workflow(
        operation: Literal["execute", "list_templates", "get_template"] = "list_templates",
        # For execute operation
        steps: Optional[List[Dict[str, Any]]] = None,
        template: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        # For get_template operation
        template_name: Optional[str] = None,
        stop_on_error: bool = True,
    ) -> str:
        """
        Execute multiple Blender operations in a single call (macro/batch).

        This tool enables complex workflows without multiple round-trips to the MCP server.
        Operations are executed sequentially, with optional variable passing between steps.

        OPERATIONS:
        - list_templates: List available workflow templates
        - get_template: Get details of a specific template
        - execute: Execute a workflow (from steps or template)

        STEP FORMAT:
        Each step is a dict with:
        - tool: The blender tool name (e.g., "blender_mesh")
        - operation: The operation within that tool
        - ...other parameters for that operation
        - as: (optional) Store result with this name for later steps
        - if_result: (optional) Only run if previous result contains this string

        VARIABLE REFERENCES:
        Use $varname to reference results from previous steps.
        Use ${varname.field} to reference specific fields from JSON results.

        Args:
            operation: Workflow operation (execute, list_templates, get_template)
            steps: List of operation steps to execute (for execute)
            template: Name of predefined template to use (for execute)
            params: Parameters to override in template steps
            template_name: Template name (for get_template)
            stop_on_error: Stop execution on first error (default: True)

        Returns:
            Execution results or template information

        Examples:
            # List available templates
            blender_workflow(operation="list_templates")

            # Execute a template
            blender_workflow(operation="execute", template="simple_scene")

            # Execute custom steps
            blender_workflow(operation="execute", steps=[
                {"tool": "blender_mesh", "operation": "create_cube", "name": "MyCube"},
                {"tool": "blender_transform", "operation": "set_location", "object_name": "MyCube", "x": 5},
                {"tool": "blender_materials", "operation": "create_metal", "name": "Gold", "metal_type": "gold"},
                {"tool": "blender_materials", "operation": "assign_to_object", "object_name": "MyCube", "material_name": "Gold"}
            ])

            # Execute template with parameter overrides
            blender_workflow(operation="execute", template="product_shot", 
                            params={"light_type": "SUN"})
        """
        from loguru import logger

        if operation == "list_templates":
            result = {"templates": {}}
            for name, template_def in WORKFLOW_TEMPLATES.items():
                result["templates"][name] = {
                    "description": template_def["description"],
                    "step_count": len(template_def["steps"])
                }
            return json.dumps(result, indent=2)

        elif operation == "get_template":
            if not template_name:
                return "Error: template_name required for get_template"
            if template_name not in WORKFLOW_TEMPLATES:
                return f"Error: Template '{template_name}' not found. Available: {list(WORKFLOW_TEMPLATES.keys())}"
            return json.dumps(WORKFLOW_TEMPLATES[template_name], indent=2)

        elif operation == "execute":
            # Get steps from template or direct input
            workflow_steps = []
            
            if template:
                if template not in WORKFLOW_TEMPLATES:
                    return f"Error: Template '{template}' not found. Available: {list(WORKFLOW_TEMPLATES.keys())}"
                workflow_steps = [dict(s) for s in WORKFLOW_TEMPLATES[template]["steps"]]
                
                # Apply parameter overrides
                if params:
                    for step in workflow_steps:
                        for key, value in params.items():
                            if key in step or key in ["name", "object_name", "filepath"]:
                                step[key] = value
            elif steps:
                workflow_steps = steps
            else:
                return "Error: Either 'steps' or 'template' required for execute"

            # Execute steps
            results = []
            variables = {}  # Store named results
            
            for i, step in enumerate(workflow_steps):
                step_num = i + 1
                tool_name = step.get("tool")
                tool_operation = step.get("operation")
                var_name = step.pop("as", None)
                condition = step.pop("if_result", None)
                
                if not tool_name or not tool_operation:
                    error = f"Step {step_num}: Missing 'tool' or 'operation'"
                    if stop_on_error:
                        return json.dumps({"success": False, "error": error, "step": step_num, "results": results})
                    results.append({"step": step_num, "error": error})
                    continue

                # Check condition
                if condition and results:
                    last_result = results[-1].get("result", "")
                    if condition not in str(last_result):
                        results.append({"step": step_num, "skipped": f"Condition not met: {condition}"})
                        continue

                # Substitute variables in parameters
                step_params = {}
                for key, value in step.items():
                    if key in ["tool", "operation"]:
                        continue
                    if isinstance(value, str) and value.startswith("$"):
                        var_ref = value[1:]
                        if "." in var_ref:
                            var_name_ref, field = var_ref.split(".", 1)
                            if var_name_ref in variables:
                                try:
                                    var_data = json.loads(variables[var_name_ref]) if isinstance(variables[var_name_ref], str) else variables[var_name_ref]
                                    value = var_data.get(field, value)
                                except:
                                    pass
                        elif var_ref in variables:
                            value = variables[var_ref]
                    step_params[key] = value

                # Get the tool function
                try:
                    # Import tool modules dynamically
                    tool_func = None
                    if tool_name == "blender_mesh":
                        from blender_mcp.tools.mesh.mesh_tools import _register_mesh_tools
                        tool_func = app._tool_manager._tools.get("blender_mesh")
                    elif tool_name == "blender_animation":
                        tool_func = app._tool_manager._tools.get("blender_animation")
                    elif tool_name == "blender_rigging":
                        tool_func = app._tool_manager._tools.get("blender_rigging")
                    elif tool_name == "blender_scene":
                        tool_func = app._tool_manager._tools.get("blender_scene")
                    elif tool_name == "blender_materials":
                        tool_func = app._tool_manager._tools.get("blender_materials")
                    elif tool_name == "blender_transform":
                        tool_func = app._tool_manager._tools.get("blender_transform")
                    elif tool_name == "blender_lighting":
                        tool_func = app._tool_manager._tools.get("blender_lighting")
                    elif tool_name == "blender_camera":
                        tool_func = app._tool_manager._tools.get("blender_camera")
                    elif tool_name == "blender_render":
                        tool_func = app._tool_manager._tools.get("blender_render")
                    elif tool_name == "blender_import":
                        tool_func = app._tool_manager._tools.get("blender_import")
                    elif tool_name == "blender_export":
                        tool_func = app._tool_manager._tools.get("blender_export")
                    else:
                        # Try to get directly
                        tool_func = app._tool_manager._tools.get(tool_name)

                    if not tool_func:
                        error = f"Step {step_num}: Tool '{tool_name}' not found"
                        if stop_on_error:
                            return json.dumps({"success": False, "error": error, "step": step_num, "results": results})
                        results.append({"step": step_num, "error": error})
                        continue

                    # Execute the tool
                    logger.info(f"🔧 Workflow step {step_num}: {tool_name}.{tool_operation}")
                    step_params["operation"] = tool_operation
                    
                    # Call the tool's function
                    if hasattr(tool_func, 'fn'):
                        result = await tool_func.fn(**step_params)
                    else:
                        result = await tool_func(**step_params)
                    
                    # Store result
                    step_result = {"step": step_num, "tool": tool_name, "operation": tool_operation, "result": result}
                    results.append(step_result)
                    
                    # Store named variable
                    if var_name:
                        variables[var_name] = result

                except Exception as e:
                    error = f"Step {step_num}: {str(e)}"
                    logger.error(f"❌ Workflow error: {error}")
                    if stop_on_error:
                        return json.dumps({"success": False, "error": error, "step": step_num, "results": results}, indent=2)
                    results.append({"step": step_num, "error": error})

            return json.dumps({
                "success": True,
                "steps_executed": len(results),
                "results": results
            }, indent=2)

        else:
            return f"Unknown operation: {operation}. Available: execute, list_templates, get_template"


_register_workflow_tools()


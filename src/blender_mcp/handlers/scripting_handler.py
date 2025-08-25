from ..compat import *

"""Scripting operations handler for Blender MCP."""

import json
import base64
import textwrap
from typing import Optional, Dict, Any, Union, List, Tuple
from enum import Enum
from pathlib import Path
import tempfile
import uuid
import inspect
import sys
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()

class ScriptLanguage(str, Enum):
    """Supported scripting languages."""
    PYTHON = "PYTHON"
    EXPRESSION = "EXPRESSION"
    TEXT_BLOCK = "TEXT_BLOCK"
    EXTERNAL_FILE = "EXTERNAL_FILE"

class ScriptScope(str, Enum):
    """Script execution scopes."""
    SCENE = "SCENE"
    OBJECT = "OBJECT"
    MATERIAL = "MATERIAL"
    NODES = "NODES"
    ANIMATION = "ANIMATION"
    RENDER = "RENDER"
    FRAME_CHANGE = "FRAME_CHANGE"

@blender_operation("execute_script", log_args=True)
async def execute_script(
    script: str,
    script_type: Union[ScriptLanguage, str] = ScriptLanguage.PYTHON,
    **kwargs: Any
) -> Dict[str, Any]:
    """Execute a script in Blender.
    
    Args:
        script: The script code to execute or path to script file
        script_type: Type of script to execute
        **kwargs: Additional parameters
            - scope: Scope of execution (ScriptScope)
            - target: Target object/material name for scoped execution
            - as_module: Execute as a module (for Python scripts)
            - return_result: Return the result of the last expression (Python only)
            - args: Arguments to pass to the script
            - context_vars: Dictionary of variables to inject into the script context
            
    Returns:
        Dict containing execution status and result/output
    """
    script_type = script_type.upper()
    scope = kwargs.get('scope', ScriptScope.SCENE).upper()
    target = kwargs.get('target')
    as_module = kwargs.get('as_module', False)
    return_result = kwargs.get('return_result', True)
    script_args = kwargs.get('args', {})
    context_vars = kwargs.get('context_vars', {})
    
    # Generate a unique ID for this script execution
    exec_id = f"script_{uuid.uuid4().hex[:8]}"
    
    # Handle different script types
    if script_type == ScriptLanguage.EXTERNAL_FILE:
        # Read the script from file
        script_path = Path(script)
        if not script_path.exists():
            return {"status": "ERROR", "error": f"Script file not found: {script}"}
        script = script_path.read_text(encoding='utf-8')
    
    # Prepare the script for execution
    if script_type == ScriptLanguage.PYTHON:
        # For Python scripts, we need to handle return values and context
        wrapped_script = f"""
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

# Store the original stdout to restore later
_original_stdout = sys.stdout
_original_stderr = sys.stderr

# Create a buffer to capture output
import io
_output_buffer = io.StringIO()
sys.stdout = _output_buffer
sys.stderr = _output_buffer

# Result storage
_result = None
_error = None

# Inject context variables
_context = {context_vars}
for k, v in _context.items():
    globals()[k] = v

try:
    # Execute the script
    _script_globals = globals().copy()
    _script_locals = locals().copy()
    
    # Add script arguments to locals
    _script_locals.update({script_args})
    
    # Execute the script
    if {as_module}:
        import importlib.util
        import tempfile
        import os
        
        # Create a temporary module
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as f:
            f.write('''{script}''')
            temp_path = f.name
        
        try:
            # Import the module
            module_name = os.path.splitext(os.path.basename(temp_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, temp_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            _result = module
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
    else:
        # Execute as a code block
        _code = compile('''{script}''', '<string>', 'exec')
        exec(_code, _script_globals, _script_locals)
        
        # If the script defined a 'main' function, call it
        if 'main' in _script_locals and callable(_script_locals['main']):
            _result = _script_locals['main'](**{script_args})
        elif {return_result} and '_result' in _script_locals:
            _result = _script_locals['_result']
        elif {return_result} and len(_script_locals) == 1 and len(_script_globals) > 1:
            # If only one local variable was created, assume it's the result
            locals_diff = set(_script_locals.keys()) - set(globals().keys())
            if len(locals_diff) == 1:
                _result = _script_locals[list(locals_diff)[0]]
    
    # Capture any remaining output
    sys.stdout.flush()
    sys.stderr.flush()
    
except Exception as e:
    import traceback
    _error = {{
        'type': type(e).__name__,
        'message': str(e),
        'traceback': traceback.format_exc()
    }}

# Restore original stdout/stderr
sys.stdout = _original_stdout
sys.stderr = _original_stderr

# Get the captured output
_output = _output_buffer.getvalue()

# Prepare the result
_result_data = {{
    'status': 'ERROR' if _error else 'SUCCESS',
    'output': _output,
    'result': _result,
    'error': _error
}}

# Print the result as JSON
print(json.dumps(_result_data, default=str))
"""
    else:
        # For non-Python scripts, we'll execute them directly
        wrapped_script = script
    
    try:
        # Execute the script in Blender
        output = await _executor.execute_script(wrapped_script)
        
        # Parse the output if it's JSON
        try:
            if script_type == ScriptLanguage.PYTHON and output.strip():
                result = json.loads(output)
                return result
            return {"status": "SUCCESS", "output": output}
        except json.JSONDecodeError:
            return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to execute script: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("create_driver", log_args=True)
async def create_driver(
    target: str,
    data_path: str,
    expression: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Create a driver for a property.
    
    Args:
        target: Target object/data path (e.g., 'Cube.location' or 'Material.001.node_tree.nodes["Principled BSDF"].inputs[0]')
        data_path: Data path to drive (e.g., 'location', 'scale', 'inputs[0].default_value')
        expression: Driver expression (e.g., 'frame / 10' or 'sin(frame/10) * 2')
        **kwargs: Additional parameters
            - variable_type: Type of variable ('SINGLE_PROP', 'TRANSFORMS', 'ROTATION_DIFF', etc.)
            - variables: List of variable definitions for the driver
            - use_self: Use 'self' in the expression
            - is_simple_expression: Whether the expression is simple (no variables)
            
    Returns:
        Dict containing driver creation status and details
    """
    variable_type = kwargs.get('variable_type', 'SINGLE_PROP')
    variables = kwargs.get('variables', [])
    use_self = kwargs.get('use_self', False)
    is_simple_expression = kwargs.get('is_simple_expression', False)
    
    script = f"""
import json

def create_driver():
    try:
        # Parse the target path
        parts = '{target}'.split('.')
        obj_name = parts[0]
        prop_path = '.'.join(parts[1:]) if len(parts) > 1 else ''
        
        # Get the target data
        data = None
        if obj_name in bpy.data.objects:
            data = bpy.data.objects[obj_name]
        elif obj_name in bpy.data.materials:
            data = bpy.data.materials[obj_name]
        elif obj_name in bpy.data.meshes:
            data = bpy.data.meshes[obj_name]
        elif obj_name in bpy.data.lights:
            data = bpy.data.lights[obj_name]
        elif obj_name in bpy.data.cameras:
            data = bpy.data.cameras[obj_name]
        else:
            return {{"status": "ERROR", "error": f"Target not found: {{obj_name}}"}}
        
        # Navigate the data path if needed
        if prop_path:
            try:
                # Handle dictionary access with square brackets
                import re
                path_parts = re.split(r'(\.|\[|\])', prop_path)
                path_parts = [p for p in path_parts if p and p not in ('.', '[', ']')]
                
                current = data
                for part in path_parts:
                    if part.startswith('"') and part.endswith('"'):
                        part = part[1:-1]  # Remove quotes
                    
                    # Handle list/dict access
                    if '[' in part and ']' in part:
                        key = part[part.find('[')+1:part.rfind(']')]
                        if key.startswith('"') and key.endswith('"'):
                            key = key[1:-1]  # Remove quotes from string key
                        elif key.isdigit():
                            key = int(key)  # Convert to int for list indices
                        current = current[key]
                    else:
                        current = getattr(current, part)
                
                data = current
            except (AttributeError, KeyError, IndexError) as e:
                return {{"status": "ERROR", "error": f"Invalid data path: {{prop_path}} - {{str(e)}}"}}
        
        # Create the driver
        data_path = '{data_path}'
        
        # Check if driver already exists
        if hasattr(data, 'animation_data') and data.animation_data and data.animation_data.drivers:
            for fcurve in data.animation_data.drives:
                if fcurve.data_path == data_path:
                    return {{"status": "ERROR", "error": f"Driver for {{data_path}} already exists"}}
        
        # Create animation data if it doesn't exist
        if not hasattr(data, 'animation_data') or not data.animation_data:
            data.animation_data_create()
        
        # Create the driver
        driver = data.driver_add(data_path)
        
        # Set driver expression
        driver.driver.expression = '''{expression}'''
        
        # Set driver type
        driver.driver.type = 'SCRIPTED'
        
        # Add variables if provided
        if {variables}:
            for var_def in {variables}:
                var = driver.driver.variables.new()
                var.name = var_def.get('name', 'var')
                var.type = var_def.get('type', 'SINGLE_PROP')
                
                # Set variable targets
                for i, target in enumerate(var_def.get('targets', [])):
                    if i >= len(var.targets):
                        break
                    
                    t = var.targets[i]
                    if 'id' in target:
                        # Resolve ID (object, material, etc.)
                        id_parts = target['id'].split('.')
                        if id_parts[0] in bpy.data:
                            t.id = bpy.data[id_parts[0]]
                    
                    if 'data_path' in target:
                        t.data_path = target['data_path']
                    if 'id_type' in target:
                        t.id_type = target['id_type']
        
        return {{
            "status": "SUCCESS",
            "target": '{target}',
            "data_path": '{data_path}',
            "expression": '''{expression}'''
        }}
    
    except Exception as e:
        import traceback
        return {{
            "status": "ERROR",
            "error": str(e),
            "traceback": traceback.format_exc()
        }}

try:
    result = create_driver()
    print(json.dumps(result, default=str))
except Exception as e:
    print(json.dumps({{"status": "ERROR", "error": str(e)}}, default=str))
"""
    
    try:
        output = await _executor.execute_script(script)
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create driver: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("create_text_block", log_args=True)
async def create_text_block(
    name: str,
    text: str = "",
    **kwargs: Any
) -> Dict[str, Any]:
    """Create or update a text block in Blender.
    
    Args:
        name: Name of the text block
        text: Text content
        **kwargs: Additional parameters
            - overwrite: Overwrite if text block exists (default: True)
            - as_module: Mark as a Python module (adds .py extension if needed)
            
    Returns:
        Dict containing text block creation status and details
    """
    overwrite = kwargs.get('overwrite', True)
    as_module = kwargs.get('as_module', False)
    
    if as_module and not name.endswith('.py'):
        name += '.py'
    
    script = f"""
import json

def create_text():
    try:
        # Check if text block already exists
        text_block = bpy.data.texts.get('{name}')
        
        if text_block:
            if {overwrite}:
                # Clear existing text
                text_block.clear()
                text_block.write('''{text}''')
                action = 'updated'
            else:
                return {{"status": "ERROR", "error": f"Text block '{{name}}' already exists"}}
        else:
            # Create new text block
            text_block = bpy.data.texts.new('{name}')
            text_block.write('''{text}''')
            action = 'created'
        
        return {{
            "status": "SUCCESS",
            "action": action,
            "name": text_block.name,
            "characters": len(text_block.as_string())
        }}
    
    except Exception as e:
        return {{"status": "ERROR", "error": str(e)}}

try:
    result = create_text()
    print(json.dumps(result, default=str))
except Exception as e:
    print(json.dumps({{"status": "ERROR", "error": str(e)}}, default=str))
"""
    
    try:
        output = await _executor.execute_script(script)
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {"status": "SUCCESS", "output": output}
    except Exception as e:
        logger.error(f"Failed to create text block: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

# Tool Docstring Migration Guide

**Status:** In Progress  
**Standard:** [TOOL_DOCSTRING_STANDARD.md](./TOOL_DOCSTRING_STANDARD.md)  
**Started:** October 10, 2025

---

## Migration Status

### Completed ✅
- [x] query_tools.py - execute_query (reference implementation)

### In Progress 🔄
- [ ] query_tools.py - quick_data_sample
- [ ] query_tools.py - export_query_results

### Pending 📋

**Connection Tools** (connection_tools.py) - 5 tools
- [ ] list_supported_databases
- [ ] register_database_connection  
- [ ] list_database_connections
- [ ] test_database_connection
- [ ] test_all_database_connections

**Schema Tools** (schema_tools.py) - 4 tools
- [ ] list_databases
- [ ] list_tables
- [ ] describe_table
- [ ] get_schema_diff

**Data Tools** (data_tools.py)
- [ ] All tools need review

**FTS Tools** (fts_tools.py)
- [ ] All tools need review

**Management Tools** (management_tools.py)
- [ ] All tools need review

**Registry Tools** (registry_tools.py)
- [ ] All tools need review

**Windows Tools** (windows_tools.py)
- [ ] All tools need review

**Calibre Tools** (calibre_tools.py)
- [ ] All tools need review

**Media/Plex Tools** (media_tools.py, plex_tools.py)
- [ ] All tools need review

**Firefox Tools** (firefox/*.py) - ~15 files
- [ ] All tools need review

**Help Tools** (help_tools.py)
- [ ] help
- [ ] tool_help

**Init Tools** (init_tools.py)
- [ ] init_database

---

## Migration Steps

### For Each Tool:

1. **Review Current Docstring**
   - Identify what's missing
   - Check for triple quotes inside docstring
   - Note any technical debt

2. **Update Following Standard**
   ```python
   '''Brief description.
   
   Detailed description...
   
   Parameters:
       param1: Description
           - Details
       param2: Description (default: value)
           - Details
   
   Returns:
       Dictionary containing:
           - key1: Description
           - key2: Description
   
   Usage:
       When to use...
       
       Common scenarios:
       - Scenario 1
       - Scenario 2
   
   Examples:
       Basic usage:
           code
           # Returns: output
       
       Advanced usage:
           code
           # Returns: output
       
       Error handling:
           code
           # Returns: error output
   
   Raises:
       Exception: When...
   
   Notes:
       - Note 1
       - Note 2
   
   See Also:
       - related_tool: Description
   '''
   ```

3. **Test**
   - Verify no syntax errors
   - Check docstring renders correctly
   - Validate examples are accurate

4. **Update This File**
   - Move tool from Pending to Completed
   - Add any notes about special cases

---

## Common Issues and Solutions

### Issue 1: Triple Quotes in Examples

**Problem:**
```python
def tool():
    """
    Examples:
        query = """SELECT * FROM table"""  # BREAKS!
    """
```

**Solution:**
```python
def tool():
    '''
    Examples:
        query = "SELECT * FROM table"  # Use single-line string
        # Or describe the string instead of showing it
    '''
```

### Issue 2: Missing Parameters

**Problem:**
```python
def tool(param1, param2):
    """Does stuff."""  # No parameter docs!
```

**Solution:**
```python
def tool(param1, param2):
    '''Does specific stuff.
    
    Parameters:
        param1: First parameter description
            - Details about param1
        param2: Second parameter description
            - Details about param2
    '''
```

### Issue 3: No Examples

**Problem:**
```python
def tool():
    """Returns data."""  # How do I use it?
```

**Solution:**
```python
def tool():
    '''Returns data from database.
    
    Examples:
        Basic usage:
            result = await tool()
            # Returns: {'success': True, 'data': [...]}
        
        Error case:
            result = await tool()
            if not result['success']:
                print(result['error'])
    '''
```

---

## Batch Update Script

Use this Python script to check tool docstrings:

```python
#!/usr/bin/env python3
'''Check tool docstrings for compliance with standard.'''

import ast
import os
import re
from pathlib import Path

def check_docstring(func_name, docstring):
    '''Check if docstring meets standard.'''
    issues = []
    
    if not docstring:
        issues.append("Missing docstring")
        return issues
    
    # Check for required sections
    required_sections = ['Parameters:', 'Returns:', 'Usage:', 'Examples:']
    for section in required_sections:
        if section not in docstring:
            issues.append(f"Missing {section} section")
    
    # Check for triple quotes inside
    if '"""' in docstring and docstring.count('"""') > 2:
        issues.append("Contains triple quotes inside docstring")
    
    # Check for examples with output
    if 'Examples:' in docstring:
        example_section = docstring.split('Examples:')[1]
        if '# Returns:' not in example_section and '#' not in example_section:
            issues.append("Examples missing expected output comments")
    
    return issues

def scan_tool_file(filepath):
    '''Scan a Python file for tool docstrings.'''
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    results = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if it has @mcp.tool() decorator
            has_mcp_tool = any(
                isinstance(d, ast.Call) and 
                hasattr(d.func, 'attr') and 
                d.func.attr == 'tool'
                for d in node.decorator_list
            )
            
            if has_mcp_tool:
                docstring = ast.get_docstring(node)
                issues = check_docstring(node.name, docstring)
                if issues:
                    results.append({
                        'function': node.name,
                        'line': node.lineno,
                        'issues': issues
                    })
    
    return results

def main():
    '''Main entry point.'''
    tools_dir = Path('src/database_operations_mcp/tools')
    
    all_issues = {}
    
    for py_file in tools_dir.rglob('*.py'):
        if py_file.name.startswith('_'):
            continue
        
        issues = scan_tool_file(py_file)
        if issues:
            all_issues[str(py_file)] = issues
    
    # Print report
    if all_issues:
        print("Tool Docstring Issues Found:\n")
        for filepath, issues in all_issues.items():
            print(f"📄 {filepath}")
            for issue in issues:
                print(f"  ⚠️  {issue['function']} (line {issue['line']})")
                for problem in issue['issues']:
                    print(f"      - {problem}")
            print()
    else:
        print("✅ All tool docstrings are compliant!")

if __name__ == '__main__':
    main()
```

**Usage:**
```bash
cd /path/to/database-operations-mcp
python check_docstrings.py
```

---

## Priority Order

Update in this order for maximum impact:

1. **High Priority** - Most used tools
   - execute_query ✅
   - register_database_connection
   - list_tables
   - describe_table
   - list_database_connections

2. **Medium Priority** - Frequently used
   - test_database_connection
   - quick_data_sample
   - export_query_results
   - list_databases

3. **Low Priority** - Specialized tools
   - Windows registry tools
   - Media/Plex tools
   - Firefox bookmark tools
   - Calibre tools

---

## Notes

- Use single quotes (') for docstrings to avoid conflicts
- Keep examples realistic and runnable
- Show both success and error cases
- Document all parameters, even obvious ones
- Link related tools in See Also section

---

## Completion Checklist

Before marking migration complete:

- [ ] All tools have compliant docstrings
- [ ] No triple quotes inside docstrings
- [ ] All examples include expected output
- [ ] Validation script passes
- [ ] Documentation updated
- [ ] Tests updated if needed

---

*Migration Guide v1.0.0*  
*Part of MCPB Documentation*  
*Location: `mcpb/docs/TOOL_DOCSTRING_MIGRATION.md`*


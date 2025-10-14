# MCP Tool Docstring Standard

**Version:** 1.0.0  
**Last Updated:** October 10, 2025  
**Status:** MANDATORY for all tools

---

## Overview

All MCP tools MUST have comprehensive multiline docstrings following this standard.

## Required Sections

Every tool docstring MUST include:

1. **Brief Description** (1-2 sentences)
2. **Parameters** section with all arguments
3. **Returns** section with structure
4. **Usage** section with context
5. **Examples** section with code samples

## Format Rules

### ✅ REQUIRED

- Use triple double-quotes (`"""`) to delimit docstrings
- Start docstring immediately after function definition
- Brief description on first line
- Blank line after brief description
- All sections properly formatted

### ❌ PROHIBITED

- **NO triple quotes (`"""`) inside docstrings** - Use single quotes or escape
- NO missing parameter documentation
- NO examples without expected output
- NO vague descriptions

---

## Template

```python
@mcp.tool()
async def tool_name(
    param1: str,
    param2: int = 10,
    param3: Optional[List[str]] = None
) -> Dict[str, Any]:
    '''Brief one-line description of what the tool does.
    
    Detailed description providing context, use cases, and important notes about
    the tool's behavior. This should help users understand when and how to use it.
    
    Parameters:
        param1: Description of the first parameter
            - Required/Optional status
            - Valid values or constraints
            - Default value if applicable
        
        param2: Description of second parameter (default: 10)
            - Mention defaults in description
            - Explain acceptable ranges
        
        param3: Description of third parameter (default: None)
            - Explain None behavior
            - Describe list element types
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - data: The actual data returned
            - metadata: Additional information about the operation
            - error: Error message if success is False
    
    Usage:
        This tool is used when you need to [explain use case]. It works by
        [explain mechanism]. Best practices include [list recommendations].
        
        Common scenarios:
        - Scenario 1: When to use this tool
        - Scenario 2: Another use case
        - Scenario 3: Special considerations
    
    Examples:
        Basic usage:
            result = await tool_name("value1", 20)
            # Returns: {'success': True, 'data': [...]}
        
        With optional parameters:
            result = await tool_name(
                "value1", 
                param2=50,
                param3=["option1", "option2"]
            )
            # Returns: {'success': True, 'data': [...], 'metadata': {...}}
        
        Error handling:
            result = await tool_name("invalid_value")
            if not result['success']:
                print(f"Error: {result['error']}")
            # Returns: {'success': False, 'error': 'Invalid value provided'}
    
    Raises:
        ValueError: When parameter validation fails
        ConnectionError: When database connection is unavailable
        TimeoutError: When operation exceeds timeout limit
    
    Notes:
        - Important consideration 1
        - Important consideration 2
        - Performance implications
        - Security considerations
    
    See Also:
        - related_tool_name: For related functionality
        - another_tool: For alternative approach
    '''
    # Implementation
    pass
```

---

## Section Details

### 1. Brief Description

**Format:**
```python
'''Single sentence describing the tool's primary purpose.'''
```

**Requirements:**
- One sentence maximum
- Action-oriented (starts with verb)
- Clear and concise
- No technical jargon unless necessary

**Examples:**
- ✅ `'''Execute SQL query on specified database connection.'''`
- ✅ `'''List all available database connections with their status.'''`
- ❌ `'''Does stuff'''` (too vague)
- ❌ `'''This tool is used to maybe do things with databases'''` (too wordy)

---

### 2. Detailed Description

**Format:**
```python
'''Brief description.

Detailed explanation spanning multiple lines that provides full context,
explains use cases, and describes the tool's behavior in detail.
'''
```

**Requirements:**
- Blank line after brief description
- 2-5 sentences typical
- Explain WHAT, WHY, and WHEN
- Mention any important limitations

---

### 3. Parameters Section

**Format:**
```python
Parameters:
    param_name: Parameter description
        - Additional details about parameter
        - Valid values or constraints
        - Default if applicable
    
    another_param: Another description (default: value)
        - More details
```

**Requirements:**
- List ALL parameters
- Indent parameter descriptions
- Include type information if not in signature
- Mention defaults
- Explain constraints and valid values
- Use bullet points for complex parameters

**Example:**
```python
Parameters:
    connection_name: Name of the registered database connection
        - Must be alphanumeric with underscores only
        - Connection must be registered before use
        - Case-sensitive
    
    query: SQL query string to execute
        - Must be valid SQL for the target database type
        - Parameterized queries recommended for security
        - Maximum length: 10,000 characters
    
    timeout: Maximum execution time in seconds (default: 30)
        - Must be positive integer
        - None means no timeout
        - Minimum: 1, Maximum: 3600
```

---

### 4. Returns Section

**Format:**
```python
Returns:
    Dictionary containing:
        - key1: Description of first key
        - key2: Description of second key
        - key3: Optional key (only present when...)
```

**Requirements:**
- Describe the return type structure
- List all keys in returned dictionaries
- Indicate optional vs required keys
- Show nested structure if applicable
- Give example values

**Example:**
```python
Returns:
    Dictionary containing:
        - success: Boolean indicating if operation succeeded
        - data: List of database records (empty list if none found)
        - metadata: Dictionary with query execution details
            - execution_time: Time in milliseconds
            - row_count: Number of rows returned
            - query_hash: Hash of executed query
        - error: Error message string (only present if success is False)
        - warnings: List of warning messages (optional)
```

---

### 5. Usage Section

**Format:**
```python
Usage:
    Explain when and how to use this tool. Describe the context,
    common scenarios, and best practices.
    
    Common scenarios:
    - Scenario 1: Description
    - Scenario 2: Description
```

**Requirements:**
- Explain WHEN to use the tool
- Describe typical workflows
- List common scenarios
- Mention best practices
- Note any prerequisites

**Example:**
```python
Usage:
    Use this tool to retrieve a sample of data from any table for quick
    inspection or validation. This is ideal for data exploration, schema
    verification, or debugging purposes.
    
    Common scenarios:
    - Quick peek at table contents before running complex queries
    - Verify data structure after schema migration
    - Debug data quality issues
    - Generate sample data for documentation
    
    Best practices:
    - Start with small sample sizes (10-50 rows)
    - Use column filters to reduce data transfer
    - Combine with describe_table for full context
```

---

### 6. Examples Section

**Format:**
```python
Examples:
    Basic usage:
        code_example
        # Expected output or behavior
    
    Advanced usage:
        code_example
        # Expected output or behavior
    
    Error handling:
        code_example
        # Expected error output
```

**Requirements:**
- Provide at least 3 examples
- Show basic, intermediate, and advanced usage
- Include expected output
- Show error handling
- Use realistic values
- Make examples runnable
- Add comments explaining behavior

**Example:**
```python
Examples:
    Basic query execution:
        result = await execute_query(
            connection_name="production_db",
            query="SELECT * FROM users WHERE active = true"
        )
        # Returns: {
        #     'success': True,
        #     'data': [{'id': 1, 'name': 'John', 'active': True}, ...],
        #     'metadata': {'row_count': 42, 'execution_time': 125}
        # }
    
    Parameterized query with limit:
        result = await execute_query(
            connection_name="production_db",
            query="SELECT * FROM users WHERE age > :min_age",
            parameters={"min_age": 18},
            limit=100
        )
        # Returns: Limited to 100 rows matching criteria
    
    Error handling:
        result = await execute_query(
            connection_name="nonexistent_db",
            query="SELECT * FROM users"
        )
        if not result['success']:
            print(f"Query failed: {result['error']}")
            # Logs: Query failed: Connection not found: nonexistent_db
    
    Complex query with all options:
        result = await execute_query(
            connection_name="analytics_db",
            query='''
                SELECT department, COUNT(*) as emp_count
                FROM employees
                WHERE hire_date > :start_date
                GROUP BY department
                HAVING COUNT(*) > :min_count
                ORDER BY emp_count DESC
            ''',
            parameters={
                "start_date": "2023-01-01",
                "min_count": 5
            },
            limit=20
        )
        # Returns: Top 20 departments with most recent hires
```

---

### 7. Raises Section (Optional but Recommended)

**Format:**
```python
Raises:
    ExceptionType: Description of when this exception occurs
    AnotherException: Description of another exception
```

**Example:**
```python
Raises:
    ValueError: If connection_name is empty or contains invalid characters
    ConnectionError: If database connection cannot be established
    QueryError: If SQL query is malformed or cannot be executed
    TimeoutError: If query execution exceeds the specified timeout
    PermissionError: If user lacks necessary database permissions
```

---

### 8. Notes Section (Optional)

**Format:**
```python
Notes:
    - Important note 1
    - Important note 2
    - Performance consideration
    - Security consideration
```

**Example:**
```python
Notes:
    - Large result sets may consume significant memory
    - Query timeout defaults to 30 seconds but can be adjusted
    - Parameterized queries are strongly recommended to prevent SQL injection
    - Connection pooling is automatically managed
    - Transactions are not implicitly started; use begin_transaction() if needed
```

---

### 9. See Also Section (Optional)

**Format:**
```python
See Also:
    - related_tool: Description of relation
    - another_tool: Why you might use this instead
```

**Example:**
```python
See Also:
    - quick_data_sample: For getting sample data without writing queries
    - export_query_results: For executing queries and exporting to files
    - describe_table: For understanding table schema before querying
```

---

## Avoiding Triple Quotes Inside Docstrings

### The Problem

This will break:
```python
def tool():
    '''
    Example usage:
        data = {"key": """value"""}  # ❌ BREAKS!
    '''
```

### Solutions

**Option 1: Use Single Quotes**
```python
def tool():
    '''
    Example usage:
        data = {"key": "value"}  # ✅ GOOD
    '''
```

**Option 2: Use Escaped Quotes**
```python
def tool():
    '''
    Example usage:
        # Use escaped quotes for multi-line strings
        query = "SELECT * FROM table"  # ✅ GOOD
    '''
```

**Option 3: Describe Instead of Show**
```python
def tool():
    '''
    Example usage:
        # For multi-line strings, use appropriate quoting
        query = "Your SQL query here"  # ✅ GOOD
    '''
```

---

## Quick Checklist

Before committing tool code, verify:

- [ ] Brief description is clear and action-oriented
- [ ] All parameters documented with types and defaults
- [ ] Return structure fully described
- [ ] Usage section explains when/why to use tool
- [ ] At least 3 examples provided
- [ ] Examples show expected output
- [ ] Error handling example included
- [ ] NO triple quotes inside docstring
- [ ] Raises section lists possible exceptions
- [ ] Notes section includes important details

---

## Validation

Use this regex to find tools with potentially bad docstrings:

```bash
# Find tools without examples
grep -r "@mcp.tool" --include="*.py" -A 20 | grep -L "Examples:"

# Find docstrings with triple quotes inside
grep -r '""".*""".*"""' --include="*.py"
```

---

## Enforcement

This standard is:

- **MANDATORY** for all new tools
- **REQUIRED** for all modified tools
- **RECOMMENDED** for existing tools (gradual update)

Tools without proper docstrings will:
- Fail code review
- Not be included in releases
- Not appear in generated documentation

---

## Benefits

Following this standard provides:

- **Better UX**: Users understand tools quickly
- **Self-Documenting**: Code explains itself
- **Fewer Support Issues**: Clear examples reduce questions
- **Auto-Generated Docs**: Tools can parse these docstrings
- **IDE Support**: Better autocomplete and hints
- **Maintainability**: Future developers understand intent

---

*Tool Docstring Standard v1.0.0*  
*Part of MCPB Packaging Documentation*  
*Location: `mcpb/docs/TOOL_DOCSTRING_STANDARD.md`*


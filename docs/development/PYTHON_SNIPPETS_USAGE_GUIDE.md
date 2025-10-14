# 🐍 Python Snippets Usage Guide

**Complete Practical Guide: How to Use Python Snippets from Documentation**
**Real-World Examples, Common Issues, and Step-by-Step Instructions**

---

## 🎯 **Overview**

This guide explains **exactly how to use** the Python snippets shown in the MCP server documentation. You'll learn:

- ✅ **How to create Python files** from snippets
- ✅ **What imports are needed** for each snippet type
- ✅ **How to install dependencies** and run code
- ✅ **How to test and debug** your MCP servers
- ✅ **Common mistakes to avoid** and how to fix them

---

## 🚀 **Quick Start: Copy-Paste-Run**

### **Step 1: Create Your Python File**

**Method 1: VS Code/Cursor**
1. **File** → **New File**
2. **Save As**: `my_mcp_server.py`
3. **Copy snippet** from documentation into the file

**Method 2: Command Line**
```bash
# Create new file
touch my_mcp_server.py

# Edit with any editor
code my_mcp_server.py  # VS Code
notepad my_mcp_server.py  # Notepad
```

### **Step 2: Install Dependencies**

```bash
# Install FastMCP and required packages
pip install fastmcp pydantic

# For async support (if using async tools)
pip install aiohttp

# For logging (recommended)
pip install structlog

# For monitoring (optional)
pip install prometheus-client
```

### **Step 3: Copy & Modify Snippets**

#### **Basic Server Example**
```python
#!/usr/bin/env python3
"""
My First MCP Server
"""

from fastmcp import FastMCP

# Create your server
app = FastMCP("my-server")

@app.tool()
def hello_world() -> str:
    """A simple hello world tool."""
    return "Hello from my MCP server!"

if __name__ == "__main__":
    print("Starting MCP server...")
    app.run()
```

#### **Server with Parameters**
```python
#!/usr/bin/env python3
"""
MCP Server with Parameters
"""

from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Annotated

class ToolParams(BaseModel):
    name: Annotated[str, {"description": "Name to greet"}]
    age: Annotated[int, {"description": "Age of person"}] = None

app = FastMCP("my-server")

@app.tool()
def greet_person(params: ToolParams) -> str:
    """Greet a person with optional age."""
    if params.age:
        return f"Hello {params.name}! You are {params.age} years old."
    else:
        return f"Hello {params.name}!"

if __name__ == "__main__":
    app.run()
```

#### **Async Tool Example**
```python
#!/usr/bin/env python3
"""
Async MCP Server Example
"""

import asyncio
from fastmcp import FastMCP

app = FastMCP("async-server")

@app.tool()
async def async_operation(task_name: str) -> str:
    """An async tool that simulates I/O operations."""
    print(f"Starting async task: {task_name}")
    await asyncio.sleep(1)  # Simulate async work
    print(f"Completed async task: {task_name}")
    return f"Async task '{task_name}' completed successfully!"

if __name__ == "__main__":
    app.run()
```

### **Step 4: Run Your Server**

**Simple Run:**
```bash
python my_mcp_server.py
```

**With Environment Variables:**
```bash
# Windows
set LOG_LEVEL=debug
python my_mcp_server.py

# Linux/Mac
export LOG_LEVEL=debug
python my_mcp_server.py
```

### **Step 5: Test Your Server**

**Method 1: MCPJam (Recommended)**
```bash
# Install MCPJam globally
npm install -g mcpjam

# Test your server
mcpjam test --server "python my_mcp_server.py"

# Interactive testing
mcpjam interactive --server "python my_mcp_server.py"
```

**Method 2: HTTP API Test**
```bash
# List tools
curl -X POST http://localhost:8000/tools \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

# Call tool
curl -X POST http://localhost:8000/tools \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "hello_world"}}'
```

---

## 📦 **Complete Working Example**

**Create file**: `complete_example.py`

```python
#!/usr/bin/env python3
"""
Complete MCP Server Example
Copy and modify this for your own server
"""

from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server
app = FastMCP("complete-example")

# Simple tool
@app.tool()
def health_check() -> dict:
    """Check server health."""
    return {
        "status": "healthy",
        "server": "complete-example",
        "version": "1.0.0"
    }

# Tool with parameters
class MathParams(BaseModel):
    operation: str  # "add", "subtract", "multiply", "divide"
    a: float
    b: float

@app.tool()
def calculate(params: MathParams) -> float:
    """Perform mathematical calculations."""
    logger.info(f"Calculating: {params.a} {params.operation} {params.b}")

    if params.operation == "add":
        return params.a + params.b
    elif params.operation == "subtract":
        return params.a - params.b
    elif params.operation == "multiply":
        return params.a * params.b
    elif params.operation == "divide":
        if params.b == 0:
            raise ValueError("Cannot divide by zero")
        return params.a / params.b
    else:
        raise ValueError(f"Unknown operation: {params.operation}")

# Async tool example
import asyncio

@app.tool()
async def async_task(task_name: str) -> str:
    """Simulate an async task."""
    logger.info(f"Starting async task: {task_name}")
    await asyncio.sleep(1)  # Simulate work
    logger.info(f"Completed async task: {task_name}")
    return f"Task '{task_name}' completed successfully!"

if __name__ == "__main__":
    print("🚀 Complete MCP Server Example")
    print("Available tools:")
    print("- health_check() -> dict")
    print("- calculate(operation: MathParams) -> float")
    print("- async_task(task_name: str) -> str")
    print()
    print("Run with: python complete_example.py")
    print("Test with: mcpjam test --server 'python complete_example.py'")

    app.run()
```

**Run this example:**
```bash
python complete_example.py
```

---

## 🔧 **Common Imports Reference**

### **Basic Imports**
```python
# Basic FastMCP
from fastmcp import FastMCP

# Pydantic models
from pydantic import BaseModel, field_validator
from typing import Annotated

# Logging
import logging
import sys

# Standard library
from datetime import datetime
from typing import Dict, Any, List, Optional
```

### **Advanced Imports**
```python
# Async support
import asyncio
import aiohttp

# HTTP server for testing
from fastmcp.server import FastMCPServer

# Monitoring
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# File operations
import os
import json

# Error handling
from functools import wraps
```

### **Environment & Configuration**
```python
# Environment variables
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration from env
SERVER_NAME = os.getenv("SERVER_NAME", "my-server")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PORT = int(os.getenv("PORT", "8000"))
```

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: "Module not found"**
```bash
# ❌ Error: ImportError: No module named 'fastmcp'
# ✅ Solution: Install dependencies
pip install fastmcp pydantic

# Check Python path
python -c "import sys; print(sys.path)"

# Verify installation
python -c "import fastmcp; print('FastMCP installed successfully')"
```

### **Issue 2: "Port already in use"**
```python
# ❌ Error: Address already in use
# ✅ Solution: Change port
app = FastMCP("my-server", host="127.0.0.1", port=8001)

# Or use dynamic port allocation
import socket

def find_free_port(start=8000, end=9000):
    for port in range(start, end):
        try:
            with socket.socket() as s:
                s.bind(("", port))
                return port
        except OSError:
            continue
    raise RuntimeError("No free ports")

PORT = find_free_port()
app = FastMCP("my-server", port=PORT)
```

### **Issue 3: "Import errors with FastMCP 2.12"**
```python
# ❌ Wrong imports (FastMCP 1.x)
from fastmcp import Tool, Client

# ✅ Correct imports (FastMCP 2.12)
from fastmcp import FastMCP

app = FastMCP("my-server")

@app.tool()
def my_function():
    return "Hello World"
```

### **Issue 4: "Server starts but disconnects"**
```python
# ❌ Wrong: Using stdout for logging
print("Server started")  # Breaks stdio protocol

# ✅ Correct: Use logging or stderr
import logging
logger = logging.getLogger(__name__)
logger.info("Server started")

# OR use stderr for debugging
import sys
print("Debug info", file=sys.stderr)
```

### **Issue 5: "Pydantic validation errors"**
```python
# ❌ Wrong: Pydantic V1 syntax
from pydantic import BaseModel, validator

class User(BaseModel):
    email: str

    @validator('email')
    def validate_email(cls, v):
        return v.lower()

# ✅ Correct: Pydantic V2 syntax
from pydantic import BaseModel, field_validator

class User(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.lower()
```

---

## 🧪 **Testing Your MCP Server**

### **Method 1: MCPJam Testing**
```bash
# Install MCPJam
npm install -g mcpjam

# Basic test
mcpjam test --server "python my_mcp_server.py"

# Interactive testing
mcpjam interactive --server "python my_mcp_server.py"

# Load testing
mcpjam load --server "python my_mcp_server.py" --requests 100

# Performance profiling
mcpjam profile --server "python my_mcp_server.py"
```

### **Method 2: Python Unit Tests**
```python
# test_my_server.py
import pytest
from my_mcp_server import app

def test_health_check():
    result = app.call_tool("health_check", {})
    assert result["status"] == "healthy"

def test_calculate_add():
    result = app.call_tool("calculate", {
        "operation": "add",
        "a": 5,
        "b": 3
    })
    assert result == 8

if __name__ == "__main__":
    test_health_check()
    test_calculate_add()
    print("✅ All tests passed!")
```

### **Method 3: HTTP API Testing**
```bash
# Test tool listing
curl -X POST http://localhost:8000/tools \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' \
     | python -m json.tool

# Test tool execution
curl -X POST http://localhost:8000/tools \
     -H "Content-Type: application/json" \
     -d '{
         "jsonrpc": "2.0",
         "id": 2,
         "method": "tools/call",
         "params": {
             "name": "calculate",
             "arguments": {
                 "operation": "add",
                 "a": 10,
                 "b": 5
             }
         }
     }' | python -m json.tool
```

---

## 📊 **Debugging Workflow**

### **Step 1: Test Imports First**
```bash
# Test if all imports work
python -c "
try:
    from fastmcp import FastMCP
    from pydantic import BaseModel
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
"
```

### **Step 2: Test Individual Functions**
```python
# Test tool functions before MCP integration
def test_my_function():
    # Test your tool logic
    result = my_tool_function("test_input")
    print(f"Function result: {result}")
    return result

# Run test
test_my_function()
```

### **Step 3: Test Server Startup**
```bash
# Start server in test mode
python -c "
from my_mcp_server import app
print('✅ Server imports work')

# Test individual tools
try:
    result = app.call_tool('hello_world', {})
    print(f'✅ Tool call successful: {result}')
except Exception as e:
    print(f'❌ Tool call failed: {e}')
"
```

### **Step 4: Full Server Test**
```bash
# Run full server
python my_mcp_server.py

# In another terminal, test with MCPJam
mcpjam test --server "python my_mcp_server.py"
```

---

## 🚨 **Common Mistakes to Avoid**

### **❌ DON'T: Use print() to stdout**
```python
# ❌ WRONG - Breaks stdio protocol
print("Server started")
print(f"Error: {error}")

# ✅ CORRECT - Use logging
logger.info("Server started")
logger.error(f"Error: {error}")

# ✅ ACCEPTABLE - Debug info to stderr
print("Debug: Processing request...", file=sys.stderr)
```

### **❌ DON'T: Mix sync/async incorrectly**
```python
# ❌ WRONG - Async/sync mismatch
@app.tool()
def mixed_tool():
    return asyncio.run(async_function())  # Wrong!

# ✅ CORRECT - Proper async patterns
@app.tool()
async def async_tool():
    return await async_function()  # Correct!
```

### **❌ DON'T: Ignore error handling**
```python
# ❌ WRONG - No error handling
@app.tool()
def risky_tool(param: str):
    return 1 / int(param)  # Will crash on "0"

# ✅ CORRECT - Comprehensive error handling
@app.tool()
def safe_tool(param: str):
    try:
        result = 1 / int(param)
        return f"Result: {result}"
    except ValueError:
        return "Invalid number"
    except ZeroDivisionError:
        return "Cannot divide by zero"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Error: {str(e)}"
```

### **❌ DON'T: Use Pydantic V1 syntax**
```python
# ❌ WRONG - Pydantic V1
from pydantic import BaseModel, validator

class User(BaseModel):
    email: str

    @validator('email')
    def validate_email(cls, v):
        return v.lower()

# ✅ CORRECT - Pydantic V2
from pydantic import BaseModel, field_validator

class User(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.lower()
```

---

## 🎯 **Best Practices Summary**

### **✅ DO: Follow These Patterns**

1. **Use proper logging** instead of print statements
2. **Handle all errors** gracefully in tool functions
3. **Test incrementally** - each change should be tested
4. **Use type hints** for better IDE support
5. **Document your tools** with clear descriptions
6. **Validate inputs** using Pydantic models
7. **Use async properly** for I/O operations
8. **Test with MCPJam** before production use

### **✅ DO: Structure Your Code**

```python
# Good structure
from fastmcp import FastMCP
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server
app = FastMCP("my-server")

@app.tool()
def my_tool(param: str) -> str:
    """Clear description of what this tool does."""
    try:
        # Your logic here
        result = process_param(param)
        logger.info(f"Processed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"Error processing request: {str(e)}"

if __name__ == "__main__":
    app.run()
```

---

## 📈 **Success Metrics**

### **You Are Successful If:**
- ✅ **Server starts** without import errors
- ✅ **Tools appear** in Claude Desktop/MCPJam
- ✅ **Tools execute** and return correct results
- ✅ **Error handling** works properly
- ✅ **Logging** provides useful debugging info
- ✅ **No stdio errors** (no stdout print statements)

### **You Need Help If:**
- ❌ **Import errors** on startup
- ❌ **Tools don't appear** in interface
- ❌ **Server disconnects** immediately
- ❌ **Stdio transport errors** in logs
- ❌ **Pydantic validation errors** for tool parameters

---

## 🚀 **Next Steps**

1. **Copy any snippet** from the documentation
2. **Create a new .py file** with the snippet
3. **Install dependencies** with pip
4. **Test with MCPJam** or HTTP calls
5. **Debug any issues** using the troubleshooting section
6. **Add your own logic** to customize the tools

---

## 🎉 **Ready to Build MCP Servers!**

**You now have everything needed to:**
- ✅ **Create MCP servers** from documentation snippets
- ✅ **Test and debug** your servers properly
- ✅ **Avoid common mistakes** that break functionality
- ✅ **Deploy production-ready** MCP servers
- ✅ **Integrate with Claude Desktop** seamlessly

**Start by copying the "Complete Working Example" above into a new file and running it!**

**What type of MCP server would you like to create?** 🐍🔧✨

---

**This guide is maintained in basic-memory for easy reference:**
- **Search**: `search_notes("python snippets", project="claude-depot-consolidated")`
- **Read**: `read_note("PYTHON_SNIPPETS_USAGE_GUIDE", project="claude-depot-consolidated")`

**Happy coding!** 🚀🐍


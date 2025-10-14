# 🔍 Claude Desktop MCP Server Debugging Guide

**The Mystery of "Server Starts, Then Dies"**  
**Real-World Debugging Experience from nest-protect MCP**

---

## 🎭 The Mysterious Behavior

### **What Users Experience**

You see this pattern in Claude Desktop logs:
```
2025-09-19T19:52:08.612Z [your-server] [info] Server started and connected successfully
2025-09-19T19:52:08.760Z [your-server] [info] Message from client: {"method":"initialize"...}
[... normal operation for 5-10 seconds ...]
2025-09-19 21:52:13,700 - your_server - INFO - Kill argument received - exiting gracefully  
2025-09-19T19:52:14.266Z [your-server] [info] Server transport closed
2025-09-19T19:52:14.266Z [your-server] [error] Server disconnected
```

### **What Users Think**
- "Claude is randomly killing my server!"
- "The connection is unstable!"  
- "Something is wrong with my Claude Desktop installation!"

### **The Reality**
**Claude Desktop NEVER randomly kills servers.** The `--kill` signal is always a response to the server crashing or becoming unresponsive during normal operation.

---

## 🕵️ The Investigation Process

### **Step 1: Understanding the Timeline**

```
T+0s:    Server process starts
T+0.1s:  Claude Desktop connects via STDIO
T+0.2s:  Initial handshake (method: "initialize")
T+0.3s:  Claude Desktop requests tool list (method: "tools/list")  ← **CRITICAL MOMENT**
T+0.5s:  Tool discovery and validation happens
T+?s:    Something crashes during tool loading/validation
T+5-10s: Claude Desktop detects server is unresponsive
T+10s:   Claude Desktop sends --kill to cleanup zombie process
```

**The crash usually happens at the "CRITICAL MOMENT" - during tool discovery.**

### **Step 2: The Real Culprits**

#### **Culprit #1: Import Errors During Tool Loading**

**The Trap**:
```python
# This looks innocent but is a time bomb
@app.tool()
async def my_tool():
    from some_module import missing_function  # ❌ Import happens when tool is called
    return {"result": "ok"}
```

**What happens**:
1. ✅ Server starts (import not triggered yet)
2. ✅ Claude connects successfully
3. ✅ Tool registration appears to work
4. ❌ Claude tries to validate tools → import error!
5. ❌ Unhandled ImportError crashes the server
6. ❌ Claude detects dead server, sends --kill

**The Fix**:
```python
# Import at module level
from some_module import missing_function

@app.tool()
async def my_tool():
    return {"result": missing_function()}  # ✅ Import already validated
```

#### **Culprit #2: Configuration Validation Bombs**

**The Trap**:
```python
# Module-level instantiation with validation
config = MyConfig()  # ❌ Validates immediately on import

@app.tool()
async def my_tool():
    value = config.some_field  # ❌ If config validation failed, this crashes
    return {"result": value}
```

**What happens**:
1. ✅ Server starts (but config validation might fail silently)
2. ✅ Claude connects
3. ❌ Tool access triggers Pydantic validation error
4. ❌ ValidationError crashes the server
5. ❌ Claude sends --kill

**The Fix**:
```python
config = None  # ✅ Defer instantiation

def get_config():
    global config
    if config is None:
        try:
            config = MyConfig()
        except ValidationError as e:
            # Handle gracefully
            config = MyConfig.default()
    return config

@app.tool()
async def my_tool():
    cfg = get_config()
    return {"result": cfg.some_field}
```

#### **Culprit #3: Missing Dependencies in Tool Functions**

**The Trap**:
```python
@app.tool()
async def network_tool():
    import aiohttp  # ❌ What if aiohttp isn't installed?
    async with aiohttp.ClientSession() as session:
        # ...
```

**The Fix**:
```python
# Test imports at startup
try:
    import aiohttp
    import requests
    # ... other dependencies
except ImportError as e:
    print(f"Missing dependency: {e}", file=sys.stderr)
    sys.exit(1)

@app.tool()
async def network_tool():
    # ✅ We know aiohttp is available
    async with aiohttp.ClientSession() as session:
        # ...
```

---

## 🔬 Debugging Techniques

### **Technique 1: Comprehensive Logging**

```python
import logging
import sys

# Set up logging that appears in Claude Desktop logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # ← This is key!
        logging.FileHandler('debug.log')    # ← Also save to file
    ]
)

logger = logging.getLogger(__name__)

@app.tool()
async def my_tool():
    logger.info("Tool called - starting execution")
    try:
        # Your logic here
        result = await some_operation()
        logger.info(f"Tool completed successfully: {result}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Tool failed with exception: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
```

### **Technique 2: Startup Validation**

```python
def validate_environment():
    """Validate all dependencies and configuration before starting."""
    logger.info("Starting environment validation...")
    
    # Test imports
    try:
        import aiohttp
        import pydantic
        import your_custom_module
        logger.info("✅ All imports successful")
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        raise
    
    # Test configuration
    try:
        config = MyConfig()
        logger.info("✅ Configuration validation passed")
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        raise
    
    # Test external connections
    try:
        # Test API connectivity, file access, etc.
        logger.info("✅ External dependencies validated")
    except Exception as e:
        logger.error(f"❌ External validation failed: {e}")
        raise
    
    logger.info("🎉 Environment validation complete")

if __name__ == "__main__":
    validate_environment()  # ✅ Fail fast if something is wrong
    app.run()
```

### **Technique 3: Tool Function Testing**

```python
async def test_all_tools():
    """Test that every tool can be called without import/validation errors."""
    tools_to_test = [
        ("tool1", {}),
        ("tool2", {"param": "test"}),
        ("tool3", {"device_id": "test-device"}),
    ]
    
    for tool_name, test_params in tools_to_test:
        try:
            logger.info(f"Testing tool: {tool_name}")
            # Get the tool function
            tool_func = globals().get(tool_name)
            if tool_func:
                result = await tool_func(**test_params)
                logger.info(f"✅ {tool_name}: {result}")
            else:
                logger.error(f"❌ {tool_name}: Tool function not found")
        except Exception as e:
            logger.error(f"❌ {tool_name}: {e}", exc_info=True)
            raise  # Fail fast on tool issues

# Call this during development/testing
# await test_all_tools()
```

### **Technique 4: Minimal Reproduction**

When debugging, create a minimal version:

```python
# minimal_server.py
from fastmcp import FastMCP
import logging
import sys

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stderr)])
logger = logging.getLogger(__name__)

app = FastMCP("minimal-test")

@app.tool()
async def hello() -> dict:
    """Simple test tool."""
    logger.info("Hello tool called")
    return {"message": "Hello, World!"}

@app.tool()
async def test_import() -> dict:
    """Test importing your problematic module."""
    try:
        from your_module import your_function  # ← Test your specific import
        logger.info("Import successful")
        return {"status": "import_ok"}
    except Exception as e:
        logger.error(f"Import failed: {e}")
        return {"status": "import_failed", "error": str(e)}

if __name__ == "__main__":
    logger.info("Starting minimal server...")
    app.run()
```

If this works but your main server doesn't, you've isolated the problem to your specific implementation.

---

## 🎯 Real Examples from Our Debugging

### **Example 1: The state_manager.py Import Bomb**

**What we had**:
```python
# state_manager.py
def get_app_state():
    import time  # ❌ This import was failing silently
    import os
    # ... rest of function
```

**The problem**: When tools tried to call `get_app_state()`, the import inside the function failed, but the error wasn't properly handled.

**The symptom**: Server started fine, crashed when first tool was called.

**The fix**:
```python
# state_manager.py
import time  # ✅ Move to top of file
import os
from typing import Optional

def get_app_state():
    # Function body without imports
```

### **Example 2: The Pydantic Validation Time Bomb**

**What we had**:
```python
# models.py
class ProtectConfig(BaseModel):
    project_id: str  # ❌ Required field, no default
    client_id: str   # ❌ Required field, no default

# server.py  
config = ProtectConfig()  # ❌ Instant validation error if fields missing
```

**The problem**: Server started, but when tools tried to access config, Pydantic validation failed.

**The fix**:
```python
# models.py
class ProtectConfig(BaseModel):
    project_id: str = Field("", description="Project ID")  # ✅ Default value
    client_id: str = Field("", description="Client ID")    # ✅ Default value

# server.py
config = None  # ✅ Defer instantiation

def get_config():
    global config
    if config is None:
        config = ProtectConfig()  # ✅ Instantiate when needed
    return config
```

### **Example 3: The Async/Sync Confusion**

**What we had**:
```python
# __main__.py
async def main():
    app.run()  # ❌ app.run() is blocking, doesn't need async

asyncio.run(main())  # ❌ Creates event loop conflicts
```

**The symptom**: Server appeared to start but had weird async behavior issues.

**The fix**:
```python
# __main__.py
def main():  # ✅ Keep it simple
    app.run()

if __name__ == "__main__":
    main()  # ✅ Direct call
```

---

## 🚨 Warning Signs to Watch For

### **In Your Code**

- ✅ **Module-level imports** - Good
- ❌ **Function-level imports** - Danger zone
- ✅ **Deferred instantiation** - Good
- ❌ **Module-level object creation with validation** - Danger zone
- ✅ **Comprehensive error handling** - Good
- ❌ **Naked try/except or no error handling** - Danger zone

### **In Claude Desktop Logs**

- ✅ **Long-running sessions** - Good
- ❌ **5-10 second pattern** - Something crashes during tool discovery
- ✅ **Detailed error messages** - Good
- ❌ **Generic "Server disconnected"** - Hidden crash, needs better logging

### **In Your Testing**

- ✅ **Tools work individually** - Good
- ❌ **Tools fail when called from Claude** - Integration issue
- ✅ **Consistent behavior** - Good
- ❌ **Intermittent failures** - Timing or state issues

---

## 🛠️ Emergency Debugging Kit

### **Quick Diagnostic Server**

```python
# diagnostic_server.py
from fastmcp import FastMCP
import logging
import sys
import traceback

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stderr)])
logger = logging.getLogger(__name__)

app = FastMCP("diagnostic")

@app.tool()
async def test_imports() -> dict:
    """Test all your imports."""
    results = {}
    imports_to_test = [
        "aiohttp",
        "pydantic", 
        "your_custom_module",
        # Add your specific imports here
    ]
    
    for module in imports_to_test:
        try:
            __import__(module)
            results[module] = "✅ OK"
        except Exception as e:
            results[module] = f"❌ FAILED: {e}"
    
    return {"import_results": results}

@app.tool()
async def test_config() -> dict:
    """Test your configuration loading."""
    try:
        # Your config loading logic here
        from your_module import YourConfig
        config = YourConfig()
        return {"config_status": "✅ OK", "config": str(config)}
    except Exception as e:
        return {"config_status": f"❌ FAILED: {e}", "traceback": traceback.format_exc()}

if __name__ == "__main__":
    logger.info("Starting diagnostic server...")
    app.run()
```

### **Logging Configuration Template**

```python
import logging
import sys
from datetime import datetime

def setup_debug_logging():
    """Set up comprehensive logging for debugging."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # Console handler (appears in Claude Desktop)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    # File handler (for detailed analysis)
    file_handler = logging.FileHandler(f'debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return logging.getLogger(__name__)

# Use in your server
logger = setup_debug_logging()
```

---

## 🎯 Action Plan for Troubled Servers

### **Phase 1: Isolate the Problem (15 minutes)**

1. **Create minimal server** with just one simple tool
2. **Test minimal server** in Claude Desktop
3. **If minimal works**: Problem is in your tool implementation
4. **If minimal fails**: Problem is in your environment/setup

### **Phase 2: Add Complexity Gradually (30 minutes)**

1. **Add logging** to your minimal server
2. **Add one tool at a time** from your main server
3. **Test after each addition** 
4. **When it breaks**: You've found the problematic tool

### **Phase 3: Fix the Root Cause (Variable)**

1. **Import issues**: Move imports to module level
2. **Validation issues**: Add default values or defer instantiation
3. **Dependency issues**: Add proper error handling
4. **State issues**: Centralize state management

### **Phase 4: Validate the Fix (10 minutes)**

1. **Test full functionality** in Claude Desktop
2. **Verify logs show no errors**
3. **Test edge cases** that previously failed
4. **Document the fix** for future reference

---

## 📚 Resources for Other Projects

### **For avatarmcp Issues**
- Check image processing library imports
- Validate model file paths exist
- Add timeout handling for generation
- Test with minimal avatar requests first

### **For local llms Issues**  
- Verify model loading doesn't happen at import time
- Add memory monitoring for large models
- Test model inference separately
- Handle model download/cache issues

### **For tapo Issues**
- Test device discovery separately 
- Add network connectivity validation
- Handle device offline scenarios
- Test authentication before tool registration

---

## 🏆 Success Indicators

**You've fixed the "start and kill" issue when**:

✅ Server runs for minutes/hours without disconnection  
✅ All tools respond correctly in Claude Desktop  
✅ Logs show normal operation, not error patterns  
✅ Tool discovery happens without crashes  
✅ Error handling gracefully manages edge cases  

**Remember**: Claude Desktop is not the enemy. It's trying to help by cleaning up crashed servers. Fix the crash, and the killing stops! 🔧🎯

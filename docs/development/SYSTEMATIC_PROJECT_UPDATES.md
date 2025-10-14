# 🔄 Systematic Project-Wide Updates with AI

**The Challenge of Comprehensive Changes**  
**Based on Real FastMCP 2.12 Migration Experience**  
**Timeline**: September 2025

---

## 🎯 The Problem: AI Can't "Catch Them All"

### **What We Need vs. What AI Can Do**

**What Developers Need**:
- ✅ **Check ALL files** for import issues in one pass
- ✅ **Update ALL tools** with correct decorators systematically  
- ✅ **Fix ALL type hints** across the entire project
- ✅ **Validate ALL functions** follow the same pattern
- ✅ **Comprehensive project-wide consistency**

**What AI Actually Does**:
- ❌ **Processes 3-5 files** then "forgets" about the rest
- ❌ **Focuses on examples** rather than comprehensive coverage
- ❌ **Misses edge cases** in files not explicitly mentioned
- ❌ **Inconsistent application** of patterns across files
- ❌ **Requires multiple requests** to "catch them all"

### **Real Example from Our FastMCP Migration**

**The Task**: Update all tools from old pattern to FastMCP 2.12 pattern

**What We Needed**:
```
tools/
├── device_status.py     ← Update 3 tools
├── device_control.py    ← Update 5 tools  
├── system_status.py     ← Update 3 tools
├── auth_tools.py        ← Update 3 tools
├── config_tools.py      ← Update 5 tools
├── help_tool.py         ← Update 3 tools
└── about_tool.py        ← Update 2 tools
Total: 24 tools across 7 files
```

**What Happened with AI**:
- 🔄 **Request 1**: Fixed device_status.py and device_control.py
- 🔄 **Request 2**: Fixed auth_tools.py and config_tools.py  
- 🔄 **Request 3**: Fixed help_tool.py (but missed some functions)
- 🔄 **Request 4**: Fixed remaining functions in help_tool.py
- 🔄 **Request 5**: Fixed system_status.py
- 🔄 **Request 6**: Finally got around to about_tool.py

**Result**: Required **6 separate requests** to accomplish what should have been one systematic update.

---

## 🛠️ Systematic Approach for Comprehensive Updates

### **Phase 1: Project Inventory and Planning**

#### **Step 1: Create Complete File List**
```bash
# Get comprehensive view of what needs updating
find src/ -name "*.py" -type f | grep -E "(tools|server)" | sort

# Example output:
src/nest_protect_mcp/tools/__init__.py
src/nest_protect_mcp/tools/auth_tools.py
src/nest_protect_mcp/tools/config_tools.py
src/nest_protect_mcp/tools/device_control.py
src/nest_protect_mcp/tools/device_status.py
src/nest_protect_mcp/tools/help_tool.py
src/nest_protect_mcp/tools/system_status.py
src/nest_protect_mcp/fastmcp_server.py
src/nest_protect_mcp/server.py
```

#### **Step 2: Analyze Current Patterns**
```bash
# Find all decorator patterns
grep -r "@" src/nest_protect_mcp/tools/ --include="*.py"

# Find all import patterns  
grep -r "from.*import" src/nest_protect_mcp/tools/ --include="*.py"

# Find all function definitions
grep -r "def " src/nest_protect_mcp/tools/ --include="*.py"
```

#### **Step 3: Create Systematic Checklist**

**Template Checklist**:
```markdown
## Import Fixes Needed
- [ ] src/nest_protect_mcp/tools/device_status.py
- [ ] src/nest_protect_mcp/tools/device_control.py  
- [ ] src/nest_protect_mcp/tools/system_status.py
- [ ] src/nest_protect_mcp/tools/auth_tools.py
- [ ] src/nest_protect_mcp/tools/config_tools.py
- [ ] src/nest_protect_mcp/tools/help_tool.py
- [ ] src/nest_protect_mcp/tools/about_tool.py

## Decorator Updates Needed  
- [ ] device_status.py: list_devices, get_device_status, get_device_events
- [ ] device_control.py: hush_alarm, run_safety_check, set_led_brightness, sound_alarm, arm_disarm_security
- [ ] system_status.py: get_system_status, get_process_status, get_api_status  
- [ ] auth_tools.py: initiate_oauth_flow, handle_oauth_callback, refresh_access_token
- [ ] config_tools.py: get_config, update_config, reset_config, export_config, import_config
- [ ] help_tool.py: list_available_tools, get_tool_help, search_tools
- [ ] about_tool.py: about_server, get_supported_devices

Total: 24 functions across 7 files
```

### **Phase 2: Batched AI Requests Strategy**

#### **Request Template for Systematic Updates**

**Request Format**:
```
I need to systematically update [X] files for [specific change]. 

FILES TO UPDATE (in this batch):
1. src/nest_protect_mcp/tools/device_status.py
2. src/nest_protect_mcp/tools/device_control.py
3. src/nest_protect_mcp/tools/system_status.py

SPECIFIC CHANGES NEEDED:
- Remove `from ..tools import tool` imports
- Remove `@tool` decorators from all functions  
- Add proper Pydantic models for parameters
- Keep all function logic EXACTLY the same
- Do NOT add mocks or simplify functionality

FUNCTIONS TO UPDATE:
device_status.py: list_devices(), get_device_status(), get_device_events()
device_control.py: hush_alarm(), run_safety_check(), set_led_brightness(), sound_alarm(), arm_disarm_security()  
system_status.py: get_system_status(), get_process_status(), get_api_status()

Please update ALL files and ALL functions in this batch. I will make separate requests for the remaining files.
```

#### **Batch Strategy for Large Projects**

**Batch 1: Core Tools (3 files)**
- device_status.py, device_control.py, system_status.py

**Batch 2: Auth & Config (2 files)**  
- auth_tools.py, config_tools.py

**Batch 3: Help & Documentation (2 files)**
- help_tool.py, about_tool.py

**Batch 4: Server Integration (1 file)**
- fastmcp_server.py (update all tool registrations)

**Validation After Each Batch**:
```bash
# Check that changes were applied correctly
grep -r "@tool" src/nest_protect_mcp/tools/  # Should find none
grep -r "from ..tools import tool" src/nest_protect_mcp/tools/  # Should find none
```

### **Phase 3: Verification and Completeness Check**

#### **Automated Verification Scripts**

**Check Import Consistency**:
```python
# check_imports.py
import os
import ast

def check_file_imports(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"from {module} import {alias.name}")
    
    return imports

# Check all tool files
tools_dir = "src/nest_protect_mcp/tools/"
for filename in os.listdir(tools_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        filepath = os.path.join(tools_dir, filename)
        imports = check_file_imports(filepath)
        print(f"\n{filename}:")
        for imp in imports:
            print(f"  {imp}")
```

**Check Decorator Patterns**:
```python
# check_decorators.py
import os
import ast

def check_function_decorators(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            decorators = [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]
            functions.append({
                'name': node.name,
                'decorators': decorators,
                'is_async': isinstance(node, ast.AsyncFunctionDef)
            })
    
    return functions

# Check all tool files  
tools_dir = "src/nest_protect_mcp/tools/"
for filename in os.listdir(tools_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        filepath = os.path.join(tools_dir, filename)
        functions = check_function_decorators(filepath)
        print(f"\n{filename}:")
        for func in functions:
            print(f"  {func['name']}: decorators={func['decorators']}, async={func['is_async']}")
```

#### **Manual Verification Checklist**

**After Each Batch, Verify**:
- [ ] All files in batch were actually updated
- [ ] All functions in each file were updated
- [ ] No functions were missed or overlooked
- [ ] Patterns are consistently applied
- [ ] No functionality was removed or simplified

**Final Project Verification**:
- [ ] `grep -r "@tool" src/` returns no results (old decorators removed)
- [ ] `grep -r "from ..tools import tool" src/` returns no results (old imports removed)
- [ ] All 24 tools still exist and have correct patterns
- [ ] Server starts without import errors
- [ ] All tools respond correctly in Claude Desktop

---

## 🎯 Advanced Strategies for Complex Projects

### **Strategy 1: Progressive File Updates**

**For projects with 20+ files**:

```
Round 1: Update 3-4 core files
├── Verify changes work
├── Test server startup  
└── Commit working state

Round 2: Update next 3-4 files
├── Apply same patterns
├── Test integration
└── Commit working state

Round 3: Continue until complete
├── Maintain consistency
├── Regular testing
└── Regular commits
```

### **Strategy 2: Pattern-Based Requests**

**Instead of file-based batches, use pattern-based**:

**Request 1: Import Pattern Updates**
```
Update imports in ALL tool files:
- Remove: from ..tools import tool
- Remove: from ..tools import Tool  
- Add: (no tool-specific imports needed)

Files: ALL files in src/nest_protect_mcp/tools/
```

**Request 2: Decorator Pattern Updates**
```
Update decorators in ALL tool files:
- Remove: @tool decorators from all functions
- Keep: async def function signatures
- Keep: all function logic unchanged

Files: ALL files in src/nest_protect_mcp/tools/
```

**Request 3: Parameter Model Updates**
```
Add Pydantic models for ALL tool functions:
- Create BaseModel classes for each function's parameters
- Keep parameter names and types exactly the same
- Add proper Field descriptions

Files: ALL files in src/nest_protect_mcp/tools/
```

### **Strategy 3: Validation-Driven Updates**

**Use validation to drive completeness**:

```python
# comprehensive_check.py
def validate_all_tools():
    """Ensure every tool follows the correct pattern."""
    
    tools_expected = [
        ('device_status', ['list_devices', 'get_device_status', 'get_device_events']),
        ('device_control', ['hush_alarm', 'run_safety_check', 'set_led_brightness', 'sound_alarm', 'arm_disarm_security']),
        ('system_status', ['get_system_status', 'get_process_status', 'get_api_status']),
        ('auth_tools', ['initiate_oauth_flow', 'handle_oauth_callback', 'refresh_access_token']),
        ('config_tools', ['get_config', 'update_config', 'reset_config', 'export_config', 'import_config']),
        ('help_tool', ['list_available_tools', 'get_tool_help', 'search_tools']),
        ('about_tool', ['about_server', 'get_supported_devices'])
    ]
    
    for module_name, expected_functions in tools_expected:
        print(f"\nValidating {module_name}.py:")
        
        # Check file exists
        filepath = f"src/nest_protect_mcp/tools/{module_name}.py"
        if not os.path.exists(filepath):
            print(f"  ❌ File missing: {filepath}")
            continue
            
        # Check functions exist  
        functions = check_function_decorators(filepath)
        function_names = [f['name'] for f in functions]
        
        for expected_func in expected_functions:
            if expected_func in function_names:
                print(f"  ✅ {expected_func} found")
            else:
                print(f"  ❌ {expected_func} MISSING")
        
        # Check for old patterns
        with open(filepath, 'r') as f:
            content = f.read()
            
        if "@tool" in content:
            print(f"  ❌ Old @tool decorators still present")
        if "from ..tools import tool" in content:
            print(f"  ❌ Old tool imports still present")

if __name__ == "__main__":
    validate_all_tools()
```

---

## 🚨 Common Pitfalls and Solutions

### **Pitfall 1: AI "Forgets" Files**

**Problem**: AI updates 3 files, ignores the other 4

**Solution**: 
- ✅ **Explicit file enumeration** in each request
- ✅ **Batch size limits** (3-4 files max per request)
- ✅ **Verification after each batch**

### **Pitfall 2: Inconsistent Pattern Application**

**Problem**: AI applies patterns differently across files

**Solution**:
- ✅ **Provide exact code examples** for the pattern
- ✅ **Request consistency checks** after updates
- ✅ **Use automated validation scripts**

### **Pitfall 3: Partial Function Updates**

**Problem**: AI updates some functions in a file, misses others

**Solution**:
- ✅ **List ALL functions explicitly** in requests
- ✅ **Function-by-function verification**
- ✅ **Use grep to verify completeness**

### **Pitfall 4: Silent Functionality Loss**

**Problem**: AI simplifies or removes functionality during updates

**Solution**:
- ✅ **Explicit "keep all logic unchanged" instructions**
- ✅ **Before/after comparison** of critical functions
- ✅ **Functional testing** after each batch

---

## 🎯 Template for Systematic Updates

### **Request Template for AI**

```
SYSTEMATIC UPDATE REQUEST

OBJECTIVE: [specific change needed]

FILES IN THIS BATCH:
1. [file1]
2. [file2] 
3. [file3]

SPECIFIC CHANGES:
- [change 1]
- [change 2]
- [change 3]

CRITICAL REQUIREMENTS:
- Update ALL files listed above
- Update ALL functions in each file
- Keep ALL existing functionality unchanged
- Do NOT add mocks or placeholder code
- Maintain consistent patterns across all files

FUNCTIONS TO UPDATE:
[file1]: [function1(), function2(), function3()]
[file2]: [function1(), function2()]  
[file3]: [function1(), function2(), function3(), function4()]

VERIFICATION:
After updates, I should be able to verify:
- [ ] All files were modified
- [ ] All functions follow new pattern
- [ ] No old patterns remain
- [ ] All functionality preserved

Please confirm you understand the scope and will update ALL files and ALL functions listed.
```

### **Post-Update Verification Template**

```bash
# Verification script after AI updates
echo "Checking batch completion..."

# Check all expected files were modified
echo "Modified files:"
git status --porcelain

# Check old patterns are removed
echo "Checking for old patterns:"
grep -r "@tool" src/nest_protect_mcp/tools/ || echo "✅ No old @tool decorators found"
grep -r "from ..tools import tool" src/nest_protect_mcp/tools/ || echo "✅ No old imports found"

# Check new patterns are present
echo "Checking for new patterns:"
grep -r "BaseModel" src/nest_protect_mcp/tools/ && echo "✅ Pydantic models found"

# Test server startup
echo "Testing server startup:"
python -m nest_protect_mcp --test-startup
```

---

## 🏆 Success Example: Our FastMCP Migration

### **How We Should Have Done It Systematically**

**If we had followed this systematic approach**:

**Day 1**: 
- Batch 1: device_status.py, device_control.py, system_status.py
- Verification and testing
- Commit working state

**Day 2**:
- Batch 2: auth_tools.py, config_tools.py  
- Batch 3: help_tool.py, about_tool.py
- Verification and testing
- Commit working state

**Day 3**:
- Server integration updates
- Final verification
- Production deployment

**Total**: 3 days with systematic progress vs. our actual scattered approach

### **Lessons Learned**

**What Worked**:
- ✅ **Multiple requests** were necessary (AI limitation)
- ✅ **Verification after changes** caught missed files
- ✅ **Git commits** provided safety nets

**What Could Have Been Better**:
- ✅ **Systematic batching** instead of ad-hoc requests
- ✅ **Automated verification** scripts  
- ✅ **Explicit function enumeration** in requests
- ✅ **Pattern consistency checking**

---

## 🎯 Recommendations for Large Projects

### **For 50+ Files Projects**
- **Batch size**: 2-3 files per request
- **Automation**: Use verification scripts between batches
- **Git strategy**: Commit after each successful batch
- **Testing**: Automated testing after each batch

### **For 20+ Tools Projects**  
- **Pattern-based batching**: Group by change type, not file location
- **Function enumeration**: List every function explicitly
- **Consistency checking**: Automated pattern verification
- **Safety nets**: Multiple backup strategies

### **For Complex Integration Projects**
- **Incremental approach**: One integration layer at a time
- **Validation-driven**: Let verification scripts guide completeness  
- **Conservative batching**: Smaller batches for complex changes
- **Rollback readiness**: Easy rollback after each batch

**Bottom Line**: AI tools can't "catch them all" in one pass, but with systematic batching and verification, you can achieve complete project-wide consistency efficiently! 🎯🔄

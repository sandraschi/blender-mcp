# 🎯 Serena - What To Do After Restart

**You just restarted Cursor with Serena configured - here's what to do next!**

---

## ✅ **Step 1: Verify Serena is Available**

### **Check MCP Tools**

In Cursor, look for Serena tools in the MCP tools list.

**Common Serena tools**:
- `serena_find_symbol` - Search for classes, functions
- `serena_find_references` - Find where symbols are used
- `serena_get_symbols_overview` - Get project structure
- `serena_onboarding` - Initialize project
- `serena_read_file` - Efficient file reading
- And more (~15 tools total)

**Can't see them?**
- Check `.cursor/mcp.json` exists
- Verify JSON syntax (no trailing commas)
- Check Cursor logs: `%APPDATA%\Cursor\logs\`

---

## 🚀 **Step 2: Run Onboarding**

**In Cursor Composer (`Ctrl+I`), type:**

```
@Composer Run Serena onboarding for this project
```

or just:

```
Run onboarding
```

**What happens** (30 seconds - 2 minutes):
1. ✅ Serena scans notepadpp-mcp project
2. ✅ Creates `.serena/` folder
3. ✅ Generates memory files about the project
4. ✅ Starts Python language server
5. ✅ Opens dashboard: http://localhost:24282
6. ✅ Indexes all symbols (functions, classes, etc.)

**Watch the dashboard!** It shows the indexing in real-time! 🎨

---

## 📊 **Step 3: Open the Dashboard**

### **URL**: http://localhost:24282/dashboard/index.html

**Should auto-open during onboarding**, but if not:

```powershell
Start-Process "http://localhost:24282/dashboard/index.html"
```

### **What You'll See**

**Dashboard Tabs**:

1. **Overview**
   - Project name: notepadpp-mcp
   - Files indexed: ~50 Python files
   - Symbols found: ~500+ (functions, classes)
   - Language servers: Python LSP (running)

2. **Tool Usage**
   - Real-time log of AI tool calls
   - Token savings estimates
   - Most-used tools

3. **Memories**
   - `.serena/memories/architecture.md`
   - `.serena/memories/main-components.md`
   - Auto-generated project understanding

4. **Language Servers**
   - Python LSP: ✅ Running
   - Status: Active/Idle
   - Performance metrics

---

## 🧪 **Step 4: Test Serena**

### **Test 1: Find a Symbol**

**In Composer:**
```
@Composer Use Serena to find the get_status function
```

**Expected**:
- Serena uses `find_symbol` tool
- Returns: `server.py:123` (exact location)
- **WAY faster than reading entire file!**

---

### **Test 2: Find References**

**In Composer:**
```
@Composer Use Serena to find all places where open_file is called
```

**Expected**:
- Serena uses `find_references` tool
- Shows all call sites
- Across multiple files if needed

---

### **Test 3: Get Overview**

**In Composer:**
```
@Composer Use Serena to give me an overview of the notepadpp-mcp project structure
```

**Expected**:
- Serena analyzes project
- Returns high-level architecture
- Lists main components
- Identifies key classes/functions

---

### **Test 4: Navigate Large File**

**In Composer:**
```
@Composer Use Serena to show me all the tools defined in server.py
```

**Expected**:
- Serena lists all `@app.tool()` decorated functions
- **Without reading the entire 2,424 line file!**
- Token savings: Massive! 🎉

---

## 📁 **Step 5: Check What Was Created**

**Look for `.serena/` folder in your project:**

```powershell
Get-ChildItem .serena -Recurse

# Expected structure:
# .serena/
#   project.yml          ← Config
#   memories/            ← Project understanding
#     architecture.md
#     main-components.md
#   index/               ← Symbol cache
```

**These files help Serena understand your project!**

---

## 💡 **Step 6: Use Serena Naturally**

**Now just work normally!** Serena is available via `@Composer`.

### **Good Prompts for Serena**

**Code Navigation:**
```
"Find all functions that handle file operations"
"Show me where NotePadPPController is defined"
"List all classes in the project"
```

**Code Analysis:**
```
"Analyze the relationship between the tools and controller"
"What does the error handling flow look like?"
"Find potential issues in the window management code"
```

**Code Editing:**
```
"Refactor the get_status function to use better error handling"
"Add docstrings to all tools in server.py"
"Extract the Windows API calls into a separate module"
```

---

## 🎨 **Dashboard Exploration**

### **Cool Things to Watch**

**While using Serena, keep dashboard open!**

**Real-time view of**:
- Which tools AI is calling
- Token savings per query
- Language server activity
- Memory file updates

**Try this**: Ask a complex question and watch the dashboard light up! 🌟

---

## 📊 **Token Savings Example**

### **Without Serena**

**Prompt**: "Find all functions that use pywin32"

**What happens**:
- Cursor reads server.py (2,424 lines)
- Reads controller.py
- Reads utils files
- Sends ~50,000 tokens to AI
- **Cost**: ~$0.50 (at typical rates)

### **With Serena**

**Same prompt**: "Find all functions that use pywin32"

**What happens**:
- Serena uses `find_symbol` to search imports
- Serena uses LSP to find "win32" references
- Returns only 8 relevant functions
- Sends ~5,000 tokens to AI
- **Cost**: ~$0.05
- **Savings**: 90%! 🎉

**Over 100 queries**: Save $45!

---

## 🛠️ **Customization**

### **Disable Dashboard Auto-Open**

If dashboard annoys you:

Edit `.serena/project.yml`:
```yaml
dashboard:
  auto_open: false
```

### **Ignore Folders**

Speed up scanning:

```yaml
ignored_dirs:
  - node_modules
  - .venv
  - dist
  - build
  - __pycache__
  - .git
```

### **Read-Only Mode**

Only want analysis (no editing):

```yaml
read_only: true
```

---

## ⚠️ **Important Notes**

**Per-Project Installation**:
- ✅ Serena is configured ONLY for notepadpp-mcp folder
- ✅ Other repos won't have it (unless you copy config)
- ✅ Each repo needs its own `.cursor/mcp.json`

**To add to other repos**:
- Copy `.cursor/mcp.json` to new repo
- Update the `--project` path
- Restart Cursor in that folder

---

## 🎯 **Success Checklist**

**Serena is working if**:
- [ ] Dashboard opens at localhost:24282
- [ ] `.serena/` folder created
- [ ] Can find symbols via Composer
- [ ] Dashboard shows tool calls
- [ ] Language servers running

**If any fail**, check:
- `.cursor/mcp.json` syntax
- Cursor logs for errors
- `uv --version` works
- Fully restarted Cursor

---

## 🎓 **Learning Resources**

**Watch the dashboard** while asking questions - you'll see:
- How AI uses semantic tools
- Which queries save tokens
- How LSP resolves symbols
- Real-time MCP tool usage

**It's educational AND useful!** 🎓

---

## 📝 **Quick Commands Reference**

```
# Onboarding
@Composer Run onboarding

# Find symbol
@Composer Find the NotePadPPController class

# Get references
@Composer Find all calls to open_file

# Overview
@Composer Give me a project structure overview

# Edit code
@Composer Refactor the get_status function

# Create memory
@Composer Create a memory about the tool architecture
```

---

**Now go test it! Ask Cursor to find a function and watch the magic happen!** ✨

**Dashboard**: http://localhost:24282 🎨



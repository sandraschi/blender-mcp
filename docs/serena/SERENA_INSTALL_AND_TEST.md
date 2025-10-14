# Serena MCP - Installation & Testing Guide for Sandra

**Date:** 2025-10-09  
**Target:** Test Serena on myai or veogen (large, half-built repos)  
**Setup:** Claude Desktop + Cursor IDE

---

## 🔍 Quick Stats - Is This Worth It?

**GitHub:** 13.8K stars (April 2025 release!)  
**Developer:** Oraios AI (Germany, founder-driven)  
**License:** MIT - **100% FOSS, NO paid tier**  
**Business Model:** Sponsor-funded (Microsoft/VSCode contributed)  
**Reception:** "Game changer", "secret weapon", "70% token savings"

**Why It's Interesting:**
- Only MCP server using LSP (Language Server Protocol) for semantic code understanding
- Dashboard visualization at localhost:24282
- Works with Claude's FREE tier
- Supports 20+ languages out of the box
- Community loves it for large, complex codebases

---

## 📋 Prerequisites

### 1. Install `uv` (Python Package Manager)

Serena uses `uv` to manage itself. Install it first:

```powershell
# PowerShell (as Admin)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

**Restart PowerShell** after installation for PATH updates.

---

## 🚀 Installation

### Option A: Quick Test (Recommended First)

Run Serena directly without installing:

```powershell
# Test run (downloads and runs on-the-fly)
uvx --from git+https://github.com/oraios/serena serena start-mcp-server --help
```

If this works, you're ready to configure.

### Option B: Local Clone (For Development)

```powershell
Set-Location "D:\Dev\repos"
git clone https://github.com/oraios/serena
Set-Location serena

# Test local installation
uv run serena start-mcp-server --help
```

---

## ⚙️ Configuration

### For Claude Desktop

**File:** `C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json`

Add this to your `mcpServers` section:

```json
{
  "mcpServers": {
    "serena": {
      "command": "C:\\Users\\sandr\\AppData\\Local\\Microsoft\\WindowsApps\\uvx.exe",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server"
      ]
    }
  }
}
```

**Windows Path Note:** Find your uvx.exe location with:
```powershell
where.exe uvx
```

### For Cursor IDE

**File:** `C:\Users\sandr\.cursor\mcp.json` (global) OR `.cursor\mcp.json` (per-project)

**Recommendation:** Use **per-project** config for myai/veogen testing.

#### Global Config (`~\.cursor\mcp.json`):

```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant"
      ]
    }
  }
}
```

#### Per-Project Config (Better for Testing):

Create `D:\Dev\repos\myai\.cursor\mcp.json`:

```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant",
        "--project",
        "D:\\Dev\\repos\\myai"
      ]
    }
  }
}
```

**Important:** Use `--context ide-assistant` for Cursor (optimizes for IDE integration).

---

## 🧪 Testing on myai or veogen

### Step 1: Choose Test Project

**myai** or **veogen** - both are good candidates (large, half-built).

Let's use **myai** for this example:

```powershell
Set-Location "D:\Dev\repos\myai"

# Create .cursor folder if it doesn't exist
New-Item -Path ".cursor" -ItemType Directory -Force
```

### Step 2: Create Per-Project Config

```powershell
# PowerShell
$config = @"
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant",
        "--project",
        "D:\\Dev\\repos\\myai"
      ]
    }
  }
}
"@

$config | Out-File -FilePath ".cursor\mcp.json" -Encoding UTF8
```

### Step 3: Index the Project (Recommended)

For large projects, pre-indexing speeds up Serena dramatically:

```powershell
Set-Location "D:\Dev\repos\myai"

# Index the project (takes 1-5 minutes depending on size)
uvx --from git+https://github.com/oraios/serena serena project index
```

This creates `.serena/` folder with:
- `project.yml` (config)
- Language server indexes
- Memories folder

### Step 4: Restart Cursor

Close and reopen Cursor IDE. Serena should appear in the MCP tools.

---

## 🎯 Testing Scenarios

### Test 1: Symbol Search (Token Saver!)

**Without Serena:**
```
Cursor Agent: "Find all functions that handle user authentication"
→ Reads entire files, massive token usage
```

**With Serena:**
```
Cursor Composer: "Use Serena to find all functions that handle user authentication"
→ Uses find_symbol tool
→ Returns only relevant symbols
→ 70% fewer tokens!
```

**Try:**
```
@Composer Use Serena's find_symbol tool to locate all React components related to the dashboard
```

### Test 2: Code Navigation

**Prompt:**
```
@Composer Using Serena, find all references to the User class and show me where it's used
```

**What Serena Does:**
- Uses `find_referencing_symbols` tool
- Returns precise locations
- No need to read entire codebase

### Test 3: Refactoring

**Prompt:**
```
@Composer Use Serena to replace the body of the authenticateUser function with improved error handling
```

**What Serena Does:**
- Uses `replace_symbol_body` tool
- Surgical edits (not entire file rewrites)
- Preserves surrounding code

### Test 4: Project Overview

**Prompt:**
```
@Composer Use Serena to give me an overview of the main architecture in this project
```

**What Serena Does:**
- Uses `get_symbols_overview` tool
- Reads project structure semantically
- Generates high-level summary

---

## 📊 Dashboard Access

Serena runs a local dashboard:

**URL:** http://localhost:24282/dashboard/index.html

**Features:**
- Real-time tool usage stats
- Session logs
- Project visualization
- Manual shutdown (if MCP zombie processes)

**Enable Stats Tracking:**

Edit `C:\Users\sandr\.serena\serena_config.yml`:

```yaml
record_tool_usage_stats: true
```

---

## 🔧 Troubleshooting

### Problem: "uvx not found"

**Solution:**
```powershell
# Refresh PATH in current session
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

# Verify
where.exe uvx
```

### Problem: Cursor doesn't see Serena tools

**Solution:**
1. Check MCP logs: `C:\Users\sandr\.cursor\logs\`
2. Verify JSON syntax (no trailing commas!)
3. Restart Cursor completely
4. Try in Cursor Composer with `@Composer` prefix

### Problem: Serena is slow on first use

**Expected!** Language servers initialize on first run. Pre-index the project:

```powershell
Set-Location "D:\Dev\repos\myai"
uvx --from git+https://github.com/oraios/serena serena project index
```

### Problem: Dashboard won't open

**Solution:**
```powershell
# Manually open
Start-Process "http://localhost:24282/dashboard/index.html"

# Check if port is in use
netstat -ano | findstr "24282"
```

### Problem: "zombie" MCP processes

Serena's dashboard has a shutdown button. If processes linger:

```powershell
# Kill all uvx processes
Get-Process uvx -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

## 🎓 Cursor Best Practices

### 1. Always Use Context

**Good:**
```
@Composer Use Serena to find the AuthService class
```

**Better:**
```
@Composer Use Serena's find_symbol tool to locate AuthService and show me its methods
```

### 2. Check Available Tools

**Prompt:**
```
@Composer What Serena tools are available?
```

**Common Tools:**
- `find_symbol` - Search for classes, functions, variables
- `find_referencing_symbols` - Find where symbols are used
- `get_symbols_overview` - Get file structure
- `replace_symbol_body` - Edit specific functions
- `read_file` - Read files efficiently
- `execute_shell_command` - Run commands (with permission)

### 3. Pre-Index Large Projects

Before heavy work sessions:

```powershell
Set-Location "D:\Dev\repos\myai"
uvx --from git+https://github.com/oraios/serena serena project index
```

### 4. Use Memories for Long Tasks

Serena can create "memories" in `.serena/memories/`:

**Prompt:**
```
@Composer Create a Serena memory about the current authentication architecture so we can continue this work later
```

### 5. Monitor Token Usage

Compare Cursor usage before/after Serena:
- Check Cursor's token usage stats
- Note conversation lengths
- Watch for reduced context dumping

---

## 📝 Configuration Files

### Global Config

**Location:** `C:\Users\sandr\.serena\serena_config.yml`

**Key Settings:**
```yaml
# Enable dashboard stats
record_tool_usage_stats: true

# Dashboard port
dashboard_port: 24282

# Disable GUI tool (Windows-only, experimental)
gui_tool_enabled: false
```

### Project Config

**Location:** `D:\Dev\repos\myai\.serena\project.yml` (auto-generated)

**Key Settings:**
```yaml
# Project name (for reactivation)
name: myai

# Read-only mode (analysis only, no edits)
read_only: false

# Language-specific settings
languages:
  python:
    enable: true
  typescript:
    enable: true
  javascript:
    enable: true
```

---

## 🎯 Success Metrics

Track these to evaluate Serena's value:

### Week 1 Testing:
- [ ] Serena successfully installed in Cursor
- [ ] Dashboard accessible at localhost:24282
- [ ] At least 5 symbol searches completed
- [ ] Token usage comparison (with/without Serena)
- [ ] No crashes or zombie processes

### Week 2 Evaluation:
- [ ] Noticed faster code navigation?
- [ ] Token savings >50% on complex queries?
- [ ] Dashboard visualizations useful?
- [ ] Would continue using after trial?

### Decision Criteria:

**Keep Serena If:**
- ✅ Token savings >50% on large projects
- ✅ Dashboard provides useful insights
- ✅ Faster navigation than manual file reading
- ✅ No performance/stability issues

**Remove Serena If:**
- ❌ Token savings <30%
- ❌ Constant crashes or slow performance
- ❌ Dashboard is useless
- ❌ More hassle than benefit

---

## 🚀 Quick Start Checklist

### Day 1: Installation
- [ ] Install `uv` via PowerShell
- [ ] Test `uvx` works
- [ ] Add Serena to Cursor config (per-project)
- [ ] Restart Cursor
- [ ] Verify Serena tools appear

### Day 2: First Test
- [ ] Index myai project
- [ ] Run 3 symbol searches in Cursor Composer
- [ ] Open dashboard at localhost:24282
- [ ] Check tool usage stats
- [ ] Compare token usage

### Day 3: Real Work
- [ ] Use Serena for actual myai debugging
- [ ] Try refactoring with `replace_symbol_body`
- [ ] Create a memory for long task
- [ ] Test cross-file navigation

### Week 1 Review:
- [ ] Evaluate token savings
- [ ] Check dashboard insights
- [ ] Decide: keep, tweak, or remove?

---

## 📚 Resources

**Official:**
- GitHub: https://github.com/oraios/serena
- Docs: (in repo README)
- Dashboard: http://localhost:24282/dashboard/index.html

**Community:**
- Reddit: Search "Serena MCP" on r/ClaudeAI, r/ClaudeCode
- YouTube: Multiple tutorial videos
- Blog posts: Medium, Apidog have detailed guides

**Your Setup:**
- Repos: `D:\Dev\repos\`
- Temp: `d:\dev\repos\temp\`
- Config: `C:\Users\sandr\.serena\`
- Claude Config: `C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json`
- Cursor Config: `C:\Users\sandr\.cursor\mcp.json`

---

## 🎉 Final Verdict

**Is Serena Worth It?**

**Pros:**
- ✅ Completely FREE (no hidden paid tier)
- ✅ 13.8K stars, active community
- ✅ Real 70% token savings reported
- ✅ Dashboard is genuinely interesting
- ✅ Works with Claude's free tier
- ✅ German founders (Sandra likes supporting EU tech)

**Cons:**
- ⚠️ Requires `uv` dependency
- ⚠️ Setup is manual (not one-click)
- ⚠️ Best for large projects (overkill for small ones)
- ⚠️ Still new (April 2025 release)

**Recommendation for Sandra:**

**YES, test it on myai or veogen for 1-2 weeks.**

Rationale:
1. **Zero cost** - aligns with €100/month AI budget
2. **Token savings** - helps with Cursor Pro usage
3. **Dashboard** - interesting for MCP development insights
4. **Active community** - good for troubleshooting
5. **Low risk** - can remove easily if not useful

**Best case:** 70% token savings + useful visualizations = keep it  
**Worst case:** Not useful, waste of 2 hours setup = remove it

**Either way, you learn about LSP integration and semantic code analysis - useful for your own MCP servers!**

---

**Ready to install? Start with the Quick Start Checklist above!** 🚀

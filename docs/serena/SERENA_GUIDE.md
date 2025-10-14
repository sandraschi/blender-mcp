# Serena MCP - Complete Installation & Usage Guide

**Date:** 2025-10-09  
**Status:** Production-ready FOSS project  
**GitHub:** https://github.com/oraios/serena  
**Stars:** 9.8k+ (very active!)

---

## 🎯 What is Serena?

**Serena** is a FREE, open-source MCP server that makes AI assistants (Claude, Cursor, etc.) WAY smarter at coding by giving them **semantic code understanding** - not just text reading.

### The Problem Serena Solves

**Without Serena:**
- AI reads your ENTIRE codebase every time (wastes tokens 💸)
- AI only sees text, not code structure (like class relationships, function calls)
- Large projects hit token limits fast
- AI can't find specific functions/classes efficiently

**With Serena:**
- AI reads ONLY what it needs (70% token savings! 🎉)
- AI understands code semantically (via Language Server Protocol)
- AI can search by meaning: "find all authentication functions"
- Creates project "memories" in `.serena/memories/` for context
- Works like a real IDE with symbol navigation, references, etc.

### How It Works

1. **First run (Onboarding):**
   - Serena scans your project
   - Creates index of all code symbols (classes, functions, etc.)
   - Generates "memory" files in `.serena/memories/` with project understanding
   - Starts language servers (Python, TypeScript, Java, etc.)

2. **During conversation:**
   - AI asks Serena specific questions like "find_symbol", "get_references"
   - Serena uses language servers to get exact answers
   - Only relevant code is sent to AI (not the whole project)
   - AI has semantic understanding (not just text search)

3. **Automatic optimization:**
   - Serena caches results
   - Updates indexes when files change
   - Manages memory files automatically

---

## 📋 Supported Languages

**Fully Supported (Auto-configured):**
- Python (pylsp)
- JavaScript/TypeScript (typescript-language-server)
- Rust (rust-analyzer)
- Go (gopls)
- Java, C#, C++, and 8+ more

**Works Best For:**
- Large projects (10,000+ lines)
- Multi-file codebases with complex relationships
- Projects with good structure (not single-file scripts)

---

## 🔧 Installation Guide

### Prerequisites

**Required:**
- Python 3.10+ (you have 3.13 ✅)
- `uv` package manager (Python's new fast package tool)

**Install uv (Windows PowerShell):**
```powershell
# Run this command
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

**Or via winget:**
```powershell
winget install astral-sh.uv
```

---

## 🚀 Quick Setup (Recommended Method)

### Method 1: Direct Run (No Clone Needed) ⭐ EASIEST

This uses `uvx` to run Serena directly from GitHub:

**For Claude Desktop:**

1. Open Claude Desktop config:
   ```
   C:\Users\sandr\AppData\Roaming\Claude\claude_desktop_config.json
   ```

2. Add Serena entry:
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
         ],
         "env": {
           "PYTHONUNBUFFERED": "1"
         }
       }
     }
   }
   ```

3. Restart Claude Desktop **completely** (quit from system tray!)

4. Verify: Look for hammer icon 🔨 next to your message box

**For Cursor:**

1. Open/create Cursor MCP config:
   ```
   C:\Users\sandr\.cursor\mcp.json
   ```

2. Add Serena entry:
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

3. Restart Cursor

---

### Method 2: Clone & Run (More Control)

**For Sandra's setup:**

```powershell
# Navigate to repos
Set-Location "d:\dev\repos"

# Clone Serena
git clone https://github.com/oraios/serena
Set-Location "d:\dev\repos\serena"

# Test it works
uv run serena start-mcp-server --help
```

**Claude Desktop config:**
```json
{
  "mcpServers": {
    "serena": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "d:\\dev\\repos\\serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

## 🎮 Using Serena

### First Time in a Project

When you start working on a project, Serena needs to "onboard":

**In Claude/Cursor, say:**
```
"Run onboarding for this project"
```

Or just start coding naturally:
```
"Analyze the authentication flow in this project"
```

Serena will:
1. Scan your project structure
2. Create `.serena/memories/` folder
3. Generate memory files (project structure, key components, etc.)
4. Index all code symbols
5. Start language servers

**This takes 30 seconds to 2 minutes** depending on project size.

### After Onboarding

Serena is ready! It has deep understanding of your code.

**What You Can Ask:**

**Code Navigation:**
```
"Find all functions that handle user authentication"
"Show me where UserService is defined"
"Find all references to the authenticate() method"
"List all classes in the auth module"
```

**Code Analysis:**
```
"Explain the relationship between UserController and UserService"
"What does the payment processing flow look like?"
"Find potential security issues in the login code"
"Analyze code complexity in the database layer"
```

**Code Editing:**
```
"Add logging to all API endpoints"
"Refactor the UserService to use dependency injection"
"Fix all TODO comments in the project"
"Add error handling to database queries"
```

**Project Understanding:**
```
"What does this project do?"
"Where is the main entry point?"
"How is authentication implemented?"
"Show me the API structure"
```

### Serena's Tools (What It Can Do)

Serena provides these tools to the AI:

- `get_symbol_definition` - Get code for a specific symbol
- `get_symbol_references` - Find all uses of a symbol
- `search_symbols` - Search for symbols by name/pattern
- `find_patterns` - Search code by regex pattern
- `list_memories` - Show available memory files
- `read_memory` - Read a memory file
- `read_file` - Read any project file
- `replace_lines` - Edit code by line ranges
- `replace_symbol_body` - Replace entire function/class
- `list_dir` - Browse project structure
- `onboarding` - Initialize project understanding
- `prepare_for_new_conversation` - Continue with context

**You don't call these directly!** The AI decides when to use them.

---

## 📊 The Dashboard (Very Cool!)

Serena runs a **local web dashboard** for monitoring:

**Access:** http://localhost:24282/dashboard/index.html

**Shows:**
- All tool calls Serena makes
- Language server status
- Project memory files
- Token usage estimates
- Real-time logs

**Auto-opens** when you start Serena (unless disabled)

---

## ⚙️ Configuration

### Project Config (.serena/serena_config.yml)

After first run, edit `.serena/serena_config.yml` in your project:

```yaml
# Ignore certain directories (important!)
ignored_dirs:
  - node_modules
  - .venv
  - venv
  - __pycache__
  - dist
  - build
  - .git

# Read-only mode (no editing)
read_only: false

# Disable dangerous shell commands
disabled_tools:
  - execute_shell_command

# Language-specific settings
languages:
  python:
    language_server: "pylsp"
  typescript:
    language_server: "typescript-language-server"
```

### Contexts (Behavior Modes)

Serena has different "contexts" for different use cases:

- `desktop-app` - Default for Claude Desktop
- `ide-assistant` - Best for Cursor/IDEs (recommended)
- `agent` - For autonomous operation
- `planning` - Focus on analysis
- `editing` - Optimize for code changes

**Set context in config:**
```json
"args": [
  "serena",
  "start-mcp-server",
  "--context",
  "ide-assistant"
]
```

---

## 🛡️ Safety & Best Practices

### Critical Warnings

1. **Backup your work!** Serena can edit code.
   - Use git: `git add -A && git commit -m "before serena"`

2. **Inspect commands:** When Serena wants to run shell commands, CHECK THEM!

3. **Use read-only mode** if you only want analysis:
   ```yaml
   read_only: true
   ```

4. **Ignore large folders:** Add to `ignored_dirs` or it will scan forever:
   ```yaml
   ignored_dirs:
     - node_modules
     - .venv
     - data
     - logs
   ```

### Known Issues

**Serena hangs on startup:**
- Usually due to large virtual environments
- **Fix:** Add venv folders to `ignored_dirs`
- **Fix:** Delete `.serena/` folder and restart

**Language server not starting:**
- Check Serena dashboard logs
- Serena auto-installs servers, but might fail
- **Fix:** Manually install (e.g., `pip install python-lsp-server`)

**Token limits hit:**
- Serena helps but doesn't eliminate limits
- **Fix:** Use more focused prompts
- **Fix:** Work on smaller modules at a time

---

## 📈 Performance Tips

### Maximize Token Savings

1. **Good project structure:**
   - Well-organized folders
   - Clear naming conventions
   - Serena navigates better = fewer tokens

2. **Use memories:**
   ```
   "Read the memories for this project first"
   ```
   Then ask your question

3. **Specific prompts:**
   ```
   ❌ "Improve this project"
   ✅ "Refactor the UserService class to use interfaces"
   ```

4. **Let Serena prepare:**
   ```
   "Run prepare_for_new_conversation"
   ```
   Before starting new chat

### Speed Up Onboarding

- Configure `ignored_dirs` BEFORE first run
- Start with smaller modules
- Use `.gitignore` (Serena respects it)

---

## 💡 Real-World Examples

### Example 1: Bug Hunting

```
You: "Find all database queries that don't have error handling"
Serena: *searches symbols, analyzes code*
Serena: "Found 5 instances in UserRepository, OrderRepository..."

You: "Add try-catch blocks to all of them"
Serena: *edits files with replace_symbol_body*
```

### Example 2: Refactoring

```
You: "The UserService class is too large. Split it into UserAuthService and UserProfileService"
Serena: *analyzes dependencies, creates new files, updates imports*
```

### Example 3: Understanding New Project

```
You: "I just inherited this codebase. Explain the architecture"
Serena: *reads memories, analyzes structure*
Serena: "This is a 3-tier architecture with..."
```

---

## 🎓 Advanced Usage

### Custom Memory Files

You can manually add memory files to `.serena/memories/`:

**Example:** `.serena/memories/deployment.md`
```markdown
# Deployment Process

1. Run tests: npm test
2. Build: npm run build
3. Deploy: ./deploy.sh production

Database migrations run automatically.
```

Serena will read this when relevant!

### Multiple Projects

Each project gets its own `.serena/` folder with separate:
- Memory files
- Index
- Configuration

You can copy memory files between projects for consistency.

### Integration with Claude Code

**Claude Code CLI** has special Serena integration:

```bash
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)
```

This automatically configures Serena for the current directory!

---

## 🔧 Troubleshooting

### Serena Not Showing Up

**Check:**
1. Config file syntax is valid JSON
2. You fully restarted the IDE (not just closed window!)
3. Look for hammer icon 🔨 in chat
4. Check IDE logs for MCP errors

**Claude Desktop logs:**
```
C:\Users\sandr\AppData\Roaming\Claude\logs\
```

**Cursor logs:**
```
%APPDATA%\Cursor\logs\
```

### Serena Hangs on Startup

**Common causes:**
- Scanning large `node_modules` or `venv`
- Too many files

**Fixes:**
1. Add to `.gitignore` (Serena respects it)
2. Configure `ignored_dirs` in `serena_config.yml`
3. Delete `.serena/` and restart

### Commands Not Working

**Try:**
```
"Use the onboarding tool"
"Use the find_symbol tool to search for UserService"
```

Be explicit about tool names!

### Out of Context Errors

Even with Serena, you can hit limits on huge files.

**Solutions:**
- Work on smaller modules
- Split large files
- Use focused prompts
- Start new conversation with `prepare_for_new_conversation`

---

## 📝 Summary: Serena Cheat Sheet

**Installation:**
```powershell
# Quick method
Add to claude_desktop_config.json:
{
  "serena": {
    "command": "uvx",
    "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "ide-assistant"]
  }
}
```

**First Use:**
```
"Run onboarding for this project"
```

**Common Commands:**
```
"Find all functions that..."
"Show me where X is defined"
"Refactor X to use Y"
"Explain the architecture"
"Add logging to all endpoints"
```

**Dashboard:**
```
http://localhost:24282/dashboard/index.html
```

**Memory Location:**
```
<your-project>/.serena/memories/
```

**Config:**
```
<your-project>/.serena/serena_config.yml
```

---

## 🎯 Is Serena Right for You?

**YES, if:**
- ✅ Working on medium/large projects (1000+ lines)
- ✅ Multi-file codebases with structure
- ✅ Want to save tokens/API costs
- ✅ Need semantic code understanding
- ✅ Projects in Python, JS/TS, Java, Rust, Go

**MAYBE NOT, if:**
- ❌ Single-file scripts
- ❌ Very small projects (<100 lines)
- ❌ Just need basic text editing
- ❌ Don't want to manage another tool

---

## 🔗 Resources

- **GitHub:** https://github.com/oraios/serena
- **Issues:** https://github.com/oraios/serena/issues
- **Changelog:** https://github.com/oraios/serena/releases
- **Roadmap:** Check GitHub discussions

---

**Built by:** Oraios AI  
**License:** MIT (Free Open Source)  
**Status:** Active development, 9.8k+ stars, production-ready

---

**Try it!** It's free, open source, and can save you 70% of tokens. What's not to love? 🚀

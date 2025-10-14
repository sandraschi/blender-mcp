# 🚀 Serena MCP - Quick Install Template

**Copy this to any repo for instant Serena setup!**

---

## ⚡ **5-Minute Install**

### **Step 1: Ensure `uv` is installed**

```powershell
# Check if installed
uv --version

# If not, install:
winget install astral-sh.uv
```

---

### **Step 2: Create Cursor config**

**In your project root**, run:

```powershell
# Create .cursor folder
New-Item -Path ".cursor" -ItemType Directory -Force

# Get current directory path
$projectPath = (Get-Location).Path

# Create config (COPY THIS ENTIRE BLOCK!)
@"
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
        "$($projectPath.Replace('\', '\\'))"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
"@ | Out-File -FilePath ".cursor\mcp.json" -Encoding UTF8

Write-Host "✅ Serena configured for: $projectPath" -ForegroundColor Green
```

---

### **Step 3: Add to .gitignore**

Add this line to `.gitignore`:

```
# Serena
.serena/
```

---

### **Step 4: Restart Cursor**

1. Close Cursor completely
2. Reopen in this folder
3. Serena tools will be available!

---

## 🎯 **First Use**

### **In Cursor Composer, say:**

```
@Composer Run Serena onboarding for this project
```

**What happens**:
- Serena scans your project (30 sec - 2 min)
- Creates `.serena/` folder with memories
- Starts Python/TypeScript language servers
- Opens dashboard at http://localhost:24282
- Ready to use!

---

## 🔧 **Quick Test**

After onboarding, try:

```
@Composer Use Serena to find all functions in this project
```

or

```
@Composer Use Serena to give me an overview of the project structure
```

---

## 📊 **Dashboard**

**Open**: http://localhost:24282/dashboard/index.html

**Shows**:
- Real-time tool calls
- Token savings estimates
- Language server status
- Project memories

---

## ⚙️ **Configuration (Optional)**

After first run, edit `.serena/project.yml`:

```yaml
# Ignore large folders
ignored_dirs:
  - node_modules
  - .venv
  - venv
  - __pycache__
  - dist
  - build

# Read-only mode (no editing)
read_only: false

# Disable shell commands (safer)
disabled_tools:
  - execute_shell_command
```

---

## 🛠️ **Troubleshooting**

### **Serena not showing up?**
- Verify `.cursor/mcp.json` has valid JSON (no trailing commas!)
- Fully restart Cursor (close all windows)
- Check Cursor logs: `%APPDATA%\Cursor\logs\`

### **Slow first startup?**
- Expected! Language servers initialize
- Pre-index to speed up:
  ```powershell
  uvx --from git+https://github.com/oraios/serena serena project index
  ```

### **Dashboard won't open?**
- Manually navigate: http://localhost:24282/dashboard/index.html
- Check port: `netstat -ano | findstr "24282"`

---

## ✅ **That's It!**

**Three files added**:
- `.cursor/mcp.json` - Serena config
- `.gitignore` entry - Exclude Serena cache
- `.serena/` folder - Created on first run

**Ready to save 70% tokens!** 🎉

---

## 📚 **Full Guides**

For complete documentation, see:
- `SERENA_GUIDE.md` - Complete usage guide
- `SERENA_INSTALL_AND_TEST.md` - Detailed testing procedures

---

*Quick Install Template*  
*Copy to any repo for instant Serena setup*  
*Time: 5 minutes*  
*Token savings: Up to 70%*

**Happy coding with semantic understanding!** 🧠✨



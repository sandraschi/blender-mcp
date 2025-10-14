# 📋 Copy Serena to Other Repos - One Command

**Use this to add Serena to any other repo (myai, veogen, etc.)**

---

## ⚡ **One-Command Install**

**Copy this entire block and run in target repo**:

```powershell
# Navigate to your repo
Set-Location "D:\Dev\repos\YOUR-REPO-NAME"  # ← CHANGE THIS

# Create .cursor folder
New-Item -Path ".cursor" -ItemType Directory -Force

# Get project path
$projectPath = (Get-Location).Path

# Create Serena config
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

# Add to .gitignore
if (Test-Path ".gitignore") {
    $gitignore = Get-Content ".gitignore" -Raw
    if ($gitignore -notmatch "\.serena") {
        Add-Content ".gitignore" "`n# Serena`n.serena/`n"
        Write-Host "✅ Added .serena/ to .gitignore" -ForegroundColor Green
    }
} else {
    @"
# Serena
.serena/
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✅ Created .gitignore with Serena entry" -ForegroundColor Green
}

# Success message
Write-Host "`n✅ Serena configured for: $projectPath" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Restart Cursor" -ForegroundColor Yellow
Write-Host "2. Say: '@Composer Run onboarding'" -ForegroundColor Yellow
Write-Host "3. Dashboard: http://localhost:24282" -ForegroundColor Yellow
```

---

## 🎯 **For Specific Repos**

### **For myai**

```powershell
Set-Location "D:\Dev\repos\myai"
# Then run the one-command install above
```

### **For veogen**

```powershell
Set-Location "D:\Dev\repos\veogen"
# Then run the one-command install above
```

### **For any repo**

```powershell
Set-Location "D:\Dev\repos\<repo-name>"
# Then run the one-command install above
```

---

## 📊 **Which Repos Benefit Most?**

**Best candidates** for Serena:

✅ **Large projects** (1,000+ lines)  
✅ **Multi-file codebases**  
✅ **Complex relationships** (classes, imports)  
✅ **Active development** (frequent navigation needed)  
✅ **Python, TypeScript, Rust, Go** (best LSP support)  

**Skip for**:
❌ Single-file scripts  
❌ Very small projects (<100 lines)  
❌ Pure data/config repos  

---

## 🔧 **Advanced: Pre-Index Large Projects**

**For huge repos** (10,000+ lines), pre-index before first use:

```powershell
Set-Location "D:\Dev\repos\YOUR-REPO"
uvx --from git+https://github.com/oraios/serena serena project index
```

**This takes 1-5 minutes** but makes first Serena use much faster!

---

## 🗑️ **Uninstall Serena from a Repo**

**If you decide Serena isn't useful for a specific project**:

```powershell
# Remove config
Remove-Item ".cursor\mcp.json" -Force

# Remove Serena cache
Remove-Item ".serena" -Recurse -Force

# Restart Cursor
```

**Easy!** No global state, no mess.

---

## 📚 **After Installing in Multiple Repos**

**Check dashboard** to see all projects:
- http://localhost:24282/dashboard/index.html
- Dashboard shows ALL projects Serena is working on
- Compare token savings across projects

---

*Quick Copy Template*  
*Add Serena to any repo in 30 seconds*  
*No global installation*  
*Easy to remove*

**Copy and adapt for your repos!** 🚀



# 🛡️ Git Repository Backup & Recovery Guide

**Your Complete Protection Strategy for notepadpp-mcp**

---

## 🎯 **TL;DR - Quick Protection**

```powershell
# 1. Create backup branch (do this NOW)
git branch backup-safe
git push origin backup-safe

# 2. Run manual backup
.\scripts\backup-repo.ps1

# 3. Done! You're protected.
```

---

## 📊 **Multi-Layer Protection Strategy**

Your repository is protected by **5 independent layers**:

| Layer | What It Protects | Recovery Time | Auto? |
|-------|------------------|---------------|-------|
| **1. GitHub Remote** | All commits, history | Instant | ✅ |
| **2. Git Reflog** | Local operations (90 days) | Instant | ✅ |
| **3. Backup Branches** | Known-good states | Instant | Manual |
| **4. Local Bundles** | Complete repo copy | 5 minutes | Setup |
| **5. Multiple Remotes** | GitHub outages | Instant | Setup |

---

## 🚨 **Layer 1: GitHub Already Protects You!**

### What GitHub Keeps

Even if your local repo is "borked":
- ✅ **All commits** - Full history is on GitHub
- ✅ **All branches** - Including deleted ones (30 days)
- ✅ **All tags** - Including deleted ones (can restore)
- ✅ **Pull request history** - Even if closed
- ✅ **Issue history** - All discussions

### Recovery from GitHub

```powershell
# If local repo is broken, just re-clone
cd D:\Dev\repos
Rename-Item notepadpp-mcp notepadpp-mcp-broken
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp

# Your code is back! ✅
```

**This works even if Cursor/AI messed up your local copy.**

---

## 🔄 **Layer 2: Git Reflog (Auto-Backup)**

Git automatically tracks EVERYTHING you do for 90 days:

### View All Operations

```powershell
# See everything that happened (even "deleted" commits)
git reflog

# Output shows:
# b4b21d3 HEAD@{0}: commit: Release v1.2.0
# abc1234 HEAD@{1}: commit: Previous commit
# def5678 HEAD@{2}: reset: moving to HEAD~1
# (and so on for 90 days)
```

### Recover "Lost" Work

```powershell
# Undo last 3 operations
git reset --hard HEAD@{3}

# Or recover specific commit
git reflog  # Find the commit hash
git cherry-pick abc1234  # Restore that commit

# Or create branch from old state
git branch recovered-work HEAD@{5}
```

**The reflog is your time machine - use it freely!**

---

## 🌿 **Layer 3: Backup Branches (Recommended)**

### Strategy: Snapshot Before Major Changes

```powershell
# Before ANY risky operation, create a backup branch
git branch backup-before-cursor-push
git push origin backup-before-cursor-push

# Now do risky operation...
# If it fails, you can restore:
git reset --hard backup-before-cursor-push
```

### Automated Backup Branch

Add to your workflow:

```powershell
# Create daily backup branch (add to Task Scheduler)
$Date = Get-Date -Format "yyyy-MM-dd"
git branch "backup-$Date"
git push origin "backup-$Date"

# Clean old backup branches (keep 30 days)
git branch | Where-Object { $_ -match 'backup-\d{4}-\d{2}-\d{2}' } | 
    Where-Object { 
        $BranchDate = [DateTime]::ParseExact($_.Substring(7), "yyyy-MM-dd", $null)
        $BranchDate -lt (Get-Date).AddDays(-30)
    } | ForEach-Object {
        git branch -D $_
        git push origin --delete $_
    }
```

---

## 📦 **Layer 4: Local Git Bundles (Best Practice)**

### What Are Git Bundles?

A **single file** containing your entire repository:
- ✅ All commits, branches, tags
- ✅ Complete history
- ✅ Can restore ANYWHERE
- ✅ ~2-5 MB per backup

### Manual Backup

```powershell
# Create backup
.\scripts\backup-repo.ps1

# Default location: D:\Backups\notepadpp-mcp\
# Creates: notepadpp-mcp_2025-10-08_14-30-00.bundle
```

### Automated Daily Backups

#### Setup Windows Task Scheduler

```powershell
# Create scheduled task (run as Administrator)
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"D:\Dev\repos\notepadpp-mcp\scripts\backup-repo.ps1`""

$Trigger = New-ScheduledTaskTrigger -Daily -At 3:00AM

$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName "Notepadpp-MCP Backup" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Daily backup of notepadpp-mcp repository"

# Verify
Get-ScheduledTask -TaskName "Notepadpp-MCP Backup"
```

#### Test the Backup

```powershell
# Run backup manually
.\scripts\backup-repo.ps1

# Should create: D:\Backups\notepadpp-mcp\notepadpp-mcp_[timestamp].bundle
```

### Restore from Bundle

```powershell
# Option 1: Clone from bundle to new directory
git clone D:\Backups\notepadpp-mcp\notepadpp-mcp_2025-10-08.bundle restored-repo
cd restored-repo
git remote set-url origin https://github.com/sandraschi/notepadpp-mcp.git

# Option 2: Restore to existing repo
cd D:\Dev\repos\notepadpp-mcp
git bundle unbundle D:\Backups\notepadpp-mcp\notepadpp-mcp_2025-10-08.bundle
git reset --hard origin/main
```

---

## 🌐 **Layer 5: Multiple Git Remotes (Advanced)**

### Add Backup Remote (GitLab, Bitbucket, etc.)

```powershell
# Add GitLab as backup remote
git remote add backup https://gitlab.com/yourusername/notepadpp-mcp.git

# Push to both remotes
git push origin main
git push backup main

# Or push to both at once
git remote set-url --add --push origin https://github.com/sandraschi/notepadpp-mcp.git
git remote set-url --add --push origin https://gitlab.com/yourusername/notepadpp-mcp.git

# Now 'git push origin main' pushes to BOTH!
```

### Local Network Backup

```powershell
# Create bare repo on network drive or second disk
git clone --bare . E:\GitBackups\notepadpp-mcp.git

# Add as remote
git remote add localbackup E:\GitBackups\notepadpp-mcp.git

# Push to local backup
git push localbackup --all
git push localbackup --tags
```

---

## 🔧 **Protection Best Practices**

### Before Using Cursor/AI for Git Operations

```powershell
# 1. Create safety branch
git branch pre-cursor-operation
git push origin pre-cursor-operation

# 2. Check current state
git status
git log --oneline -5

# 3. Now let Cursor/AI do its thing
# 4. If something goes wrong:
git reset --hard pre-cursor-operation
```

### Branch Protection Rules (GitHub)

Enable on GitHub to prevent force-pushes:

1. Go to: `Settings` > `Branches`
2. Click `Add rule` for `main`
3. Enable:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass
   - ✅ Do not allow force pushes
   - ✅ Do not allow deletions

**This prevents Cursor from force-pushing to main!**

### Review Before Pushing

```powershell
# Always review what will be pushed
git log origin/main..HEAD  # Commits to be pushed
git diff origin/main HEAD  # Changes to be pushed

# If you see something wrong, DON'T PUSH
# Instead, fix it locally first
```

---

## 🚑 **Emergency Recovery Scenarios**

### Scenario 1: Cursor Pushed Wrong Code

```powershell
# Find the good commit
git log --oneline -10

# Reset to good commit (local only)
git reset --hard abc1234

# Force push (if you're sure)
git push origin main --force-with-lease

# Or create new branch and PR
git branch fix-cursor-mistake
git push origin fix-cursor-mistake
# Then merge via GitHub PR
```

### Scenario 2: Accidentally Deleted Branch

```powershell
# Find the branch in reflog
git reflog | Select-String "branch-name"

# Restore it
git branch branch-name abc1234  # Use commit hash from reflog
git push origin branch-name
```

### Scenario 3: Local Repo Completely Broken

```powershell
# Nuclear option: Re-clone
cd D:\Dev\repos
Rename-Item notepadpp-mcp notepadpp-mcp-broken
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp

# Copy over any uncommitted work
Copy-Item ..\notepadpp-mcp-broken\scripts\new-script.ps1 .\scripts\
```

### Scenario 4: Lost Uncommitted Work

```powershell
# Check git stash
git stash list

# Restore from stash
git stash pop

# Or use VS Code local history (if enabled)
# File > Preferences > Settings > "Local History"
```

---

## 📋 **Recommended Setup Checklist**

### Immediate (Do Now)

- [ ] Create backup branch: `git branch backup-safe; git push origin backup-safe`
- [ ] Run manual backup: `.\scripts\backup-repo.ps1`
- [ ] Enable GitHub branch protection on `main`
- [ ] Test recovery: Clone from GitHub to verify

### This Week

- [ ] Set up automated daily backups (Task Scheduler)
- [ ] Create second remote (GitLab or local)
- [ ] Document your backup locations
- [ ] Test bundle restore procedure

### Monthly Maintenance

- [ ] Verify backups are running
- [ ] Test restore from bundle
- [ ] Clean old backup branches
- [ ] Review reflog for any issues

---

## 🎯 **Your Current Protection Status**

Based on what we just set up:

✅ **Layer 1**: GitHub remote (automatic)  
✅ **Layer 2**: Git reflog (automatic, 90 days)  
🔄 **Layer 3**: Backup branches (manual, but easy)  
✅ **Layer 4**: Bundle script created (needs scheduling)  
⏳ **Layer 5**: Multiple remotes (optional, not set up)

**Protection Level**: **GOOD** (3/5 layers active)  
**Recommendation**: Set up automated bundling for **EXCELLENT**

---

## 💡 **Daily Workflow Tips**

### Before Major Operations

```powershell
# Quick safety snapshot
git branch backup-$(Get-Date -Format 'yyyy-MM-dd-HHmm')
git push origin backup-$(Get-Date -Format 'yyyy-MM-dd-HHmm')
```

### After Cursor Makes Changes

```powershell
# Review changes before committing
git status
git diff

# If unsure, create branch first
git checkout -b cursor-changes
git add .
git commit -m "Cursor changes"

# Test, then merge to main
git checkout main
git merge cursor-changes
```

### Weekly Health Check

```powershell
# Verify backups exist
Get-ChildItem D:\Backups\notepadpp-mcp\*.bundle | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 5

# Verify GitHub is synced
git fetch origin
git status
```

---

## 🏆 **Summary: You're Protected!**

Your repository is protected by **multiple independent layers**:

1. **GitHub** keeps everything (even if local is broken)
2. **Git reflog** is a 90-day time machine
3. **Backup branches** for known-good states
4. **Local bundles** for offline recovery
5. **Multiple remotes** for redundancy

**Bottom Line**: It's almost impossible to permanently lose your code with these protections in place.

---

## 📞 **Need Help?**

If something goes wrong:

1. **DON'T PANIC** - Your code is safe on GitHub
2. **Check reflog** - `git reflog`
3. **Check backups** - `Get-ChildItem D:\Backups\notepadpp-mcp\`
4. **Re-clone if needed** - GitHub has everything
5. **Ask for help** - With reflog output

**Remember**: Git is designed to be hard to break permanently!

---

*Document created: October 8, 2025*  
*Backup script: `scripts/backup-repo.ps1`*  
*Your code is safe! 🛡️*


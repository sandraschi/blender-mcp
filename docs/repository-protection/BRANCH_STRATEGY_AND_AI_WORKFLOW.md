# 🌿 Branch Strategy & AI Collaboration Workflow

**Your Safe AI Playground with Production Protection**

---

## 🎯 **Branch Structure (Now Set Up)**

```
┌─────────────────────────────────────────────────────┐
│  main                    [PROTECTED] Production     │ ← Users get this
│  ↑ Pull Request only                                │
│  │                                                   │
│  develop                 [INTEGRATION] Testing      │ ← Stable features
│  ↑ Pull Request after testing                       │
│  │                                                   │
│  feature/experimental    [PLAYGROUND] AI Creativity │ ← GO WILD HERE!
│  ↑ Anything goes!                                   │
└─────────────────────────────────────────────────────┘
```

### **Created Branches**

✅ **main** - Production (already exists)  
✅ **develop** - Integration branch (just created)  
✅ **feature/experimental** - AI playground (just created)

---

## 🛡️ **Branch Protection Rules**

### **Why Enable Protection?**

**Without protection**, Cursor/AI could:
- ❌ Force push to main (losing history)
- ❌ Delete main branch
- ❌ Push broken code directly
- ❌ Bypass reviews

**With protection**:
- ✅ AI can't accidentally destroy main
- ✅ All changes go through PR review
- ✅ Tests must pass before merging
- ✅ You control what reaches production

### **Recommended Settings**

#### **For `main` Branch (STRICT)**

Enable these protections:

1. ✅ **Require pull request before merging**
   - Require approvals: 0 (you can self-approve)
   - Dismiss stale reviews: Yes
   
2. ✅ **Require status checks to pass**
   - Require branches to be up to date
   - Status checks: CI tests, linting
   
3. ✅ **Do not allow bypassing**
   - Include administrators: Yes
   
4. ✅ **Restrict force pushes**
   - No one can force push
   
5. ✅ **Restrict deletions**
   - Cannot delete main branch

#### **For `develop` Branch (MODERATE)**

Enable these:

1. ✅ **Require pull request** (optional)
2. ⚠️ Allow force pushes (if needed for cleanup)
3. ✅ Restrict deletions

#### **For `feature/*` Branches (OPEN)**

- ⚠️ No restrictions - freedom to experiment!
- Can force push, delete, rewrite history
- This is your AI playground

---

## 📋 **Setting Up Branch Protection (GitHub)**

### **Step-by-Step Instructions**

1. **Go to Repository Settings**
   - Open: https://github.com/sandraschi/notepadpp-mcp
   - Click: `Settings` tab (top right)

2. **Navigate to Branch Protection**
   - Left sidebar: `Branches`
   - Under "Branch protection rules"
   - Click: `Add rule` or `Add branch protection rule`

3. **Configure Main Branch Protection**
   
   **Branch name pattern**: `main`
   
   **Enable these checkboxes**:
   
   ```
   ✅ Require a pull request before merging
      ✅ Require approvals: 1 (or 0 if you're solo)
      ✅ Dismiss stale pull request approvals when new commits are pushed
      
   ✅ Require status checks to pass before merging
      ✅ Require branches to be up to date before merging
      (Select: CI tests when they appear)
      
   ✅ Require conversation resolution before merging
   
   ✅ Do not allow bypassing the above settings
      ✅ Include administrators
      
   ✅ Restrict who can push to matching branches
      (Leave empty to allow PR merges only)
      
   ✅ Allow force pushes
      ❌ UNCHECKED (disable force pushes)
      
   ✅ Allow deletions
      ❌ UNCHECKED (prevent deletion)
   ```

4. **Click**: `Create` or `Save changes`

5. **Optional: Protect `develop` branch**
   - Repeat with pattern: `develop`
   - Use lighter restrictions

---

## 🚀 **AI Collaboration Workflow**

### **Scenario 1: "Add Some Cool Feature!"**

**YOU SAY**: *"Hey AI, add a feature to export sessions to JSON!"*

**AI WORKFLOW**:

```bash
# 1. AI switches to experimental branch
git checkout feature/experimental

# 2. AI creates the feature
# ... coding magic happens ...

# 3. AI commits
git add .
git commit -m "Add session export to JSON"

# 4. AI pushes
git push origin feature/experimental

# 5. YOU review on GitHub
# See the changes in a PR: feature/experimental → develop

# 6. If you like it, merge to develop
# 7. Test on develop branch
# 8. If all good, create PR: develop → main
```

**Result**: Main is protected, but AI had full freedom to experiment!

### **Scenario 2: "Go Wild! Add Crazy Features!"**

**YOU SAY**: *"Add 10 experimental Notepad++ automation features, try bold ideas!"*

**AI WORKFLOW**:

```bash
# AI is on feature/experimental
git checkout feature/experimental

# AI can do ANYTHING here:
# - Try experimental APIs
# - Add unfinished features
# - Break things temporarily
# - Force push, rewrite history
# - Experiment with abandon!

# Nothing affects main or develop!
```

**Safety**: Main is 100% protected. Develop is safe. Experiments stay isolated.

### **Scenario 3: "Quick Bug Fix Needed!"**

**YOU SAY**: *"Fix the invisible text bug ASAP"*

**AI WORKFLOW**:

```bash
# 1. Create hotfix branch from main
git checkout main
git checkout -b hotfix/invisible-text

# 2. AI fixes the bug
# ... fix code ...

# 3. Commit and push
git commit -am "Fix invisible text issue"
git push origin hotfix/invisible-text

# 4. Create PR to main
# GitHub PR: hotfix/invisible-text → main

# 5. YOU review and approve
# 6. Merge to main (protection allows this via PR)
# 7. Also merge to develop to keep in sync
```

**Result**: Bug fixed in production, but still went through PR review.

---

## 🎨 **Branch Usage Guide**

### **`main` - Production Code**

**Purpose**: What users download  
**Rules**: PROTECTED - PR only  
**Quality**: Must work 100%

**Who commits here**:
- No one directly!
- Only via approved Pull Requests
- After testing on develop

**Commands**:
```bash
# View main (safe to look)
git checkout main
git pull origin main

# NEVER commit directly!
# Use PRs instead
```

### **`develop` - Integration & Testing**

**Purpose**: Stable features being tested  
**Rules**: Moderate protection  
**Quality**: Should work, but testing allowed

**Who commits here**:
- Merge from feature branches
- Direct commits OK for small fixes
- Pre-production testing

**Commands**:
```bash
# Work on develop
git checkout develop
git pull origin develop

# Make changes
git add .
git commit -m "Update feature"
git push origin develop

# When ready, PR to main
```

### **`feature/experimental` - AI Playground** 🎪

**Purpose**: Try ANYTHING!  
**Rules**: NO RESTRICTIONS  
**Quality**: Can be broken, that's OK!

**Who commits here**:
- AI experimenting with new ideas
- Prototypes and proof-of-concepts
- Bold features you're not sure about
- Learning and testing

**Commands**:
```bash
# AI playground - GO WILD!
git checkout feature/experimental

# Try experimental features
# ... anything goes ...

# Can force push, no problem
git push origin feature/experimental --force

# Can rewrite history
git rebase -i HEAD~5
git push --force

# Can delete and recreate
git branch -D feature/experimental
git checkout -b feature/experimental
```

**Permission granted**: Break things, try ideas, have fun! 🚀

---

## 📊 **Workflow Diagrams**

### **New Feature Development**

```
1. Start
   ↓
2. AI works on feature/experimental
   ↓
3. You review changes
   ↓
4. Like it? → Create PR to develop
   ↓
5. Merge to develop
   ↓
6. Test on develop
   ↓
7. Works? → Create PR to main
   ↓
8. Merge to main (via PR, protection allows)
   ↓
9. Release! 🎉
```

### **Experimental Feature Testing**

```
feature/experimental (AI adds 5 wild ideas)
   ↓
You review: "I like ideas 1, 3, and 4"
   ↓
Cherry-pick those commits → develop
   ↓
Test
   ↓
If good → PR to main
```

---

## 🎯 **Quick Command Reference**

### **For You (Human)**

```bash
# Review AI's work
git checkout feature/experimental
git log --oneline -10
git diff develop

# Merge experimental feature to develop
git checkout develop
git merge feature/experimental

# Create PR to main (do on GitHub)
# OR via command line:
gh pr create --base main --head develop --title "Release v1.3.0"
```

### **For AI (When Experimenting)**

```bash
# Switch to playground
git checkout feature/experimental

# Do experimental work
# ... code ...

# Commit (descriptive message)
git add .
git commit -m "Experiment: Add voice control for Notepad++"

# Push (can force push here)
git push origin feature/experimental --force-with-lease
```

### **For AI (When Making Release)**

```bash
# Never push directly to main!
# Instead, create PR

git checkout develop
git merge feature/experimental
git push origin develop

# Then on GitHub: Create PR develop → main
# Wait for human approval
```

---

## 🚨 **Protection Examples**

### **What Protection Prevents**

```bash
# ❌ This will be BLOCKED on main
git checkout main
git commit -am "Quick fix"
git push origin main
# Error: Protected branch main cannot be pushed to directly

# ❌ This will be BLOCKED on main  
git push origin main --force
# Error: Force push to protected branch not allowed

# ❌ This will be BLOCKED
git push origin :main  # Delete main
# Error: Cannot delete protected branch
```

### **What Protection Allows**

```bash
# ✅ This WORKS - PR workflow
git checkout -b fix/bug
git commit -am "Fix bug"
git push origin fix/bug
# Create PR on GitHub
# Merge via PR interface → ALLOWED

# ✅ This WORKS - experimental branch
git checkout feature/experimental
git push --force  # Allowed! No protection here
```

---

## 🎨 **AI Prompts for Each Branch**

### **On `feature/experimental`**

**You can say**:
- ✅ "Add 10 wild experimental features!"
- ✅ "Try implementing [crazy idea]"
- ✅ "Prototype a voice-controlled Notepad++"
- ✅ "Add machine learning text prediction"
- ✅ "Go nuts with the plugin API!"

**AI thinks**: *"I can experiment freely here!"*

### **On `develop`**

**You can say**:
- ✅ "Integrate the session export feature"
- ✅ "Merge the working experimental features"
- ✅ "Prepare for v1.3.0 release"
- ⚠️ "Test this thoroughly before main"

**AI thinks**: *"This needs to work, but can still iterate"*

### **On `main`**

**You can say**:
- ❌ "Push this directly to main"
- ✅ "Create a PR to main"
- ✅ "Merge develop to main via PR"
- ✅ "Tag this as a release"

**AI thinks**: *"Must use PR workflow, main is protected"*

---

## 📋 **Setup Checklist**

### **Branch Setup** (Already Done ✅)

- [x] Created `develop` branch
- [x] Created `feature/experimental` branch
- [x] Pushed both to GitHub
- [ ] **TODO**: Enable branch protection on GitHub (manual step)

### **Protection Setup** (Your Turn)

Go to: https://github.com/sandraschi/notepadpp-mcp/settings/branches

- [ ] Add rule for `main` (strict protection)
- [ ] Add rule for `develop` (optional, moderate)
- [ ] Leave `feature/*` unprotected (freedom!)

**Time needed**: ~5 minutes

### **Test the Setup**

```bash
# Test 1: Try to push to main (should fail)
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test"
git push origin main
# Should see: "Protected branch" error ✅

# Test 2: Experimental branch (should work)
git checkout feature/experimental  
echo "experiment" >> test.txt
git add test.txt
git commit -m "test"
git push origin feature/experimental --force
# Should work! ✅

# Clean up test
git checkout main
git reset --hard HEAD~1
git checkout feature/experimental
git reset --hard HEAD~1
git push origin feature/experimental --force
```

---

## 🎯 **Recommended Workflow Summary**

**For New Features**:
1. AI works on `feature/experimental`
2. You review
3. Merge to `develop`
4. Test
5. PR to `main`
6. Release

**For Experiments**:
1. AI goes wild on `feature/experimental`
2. You pick what you like
3. Cherry-pick to `develop`
4. Rest can stay or be discarded

**For Hotfixes**:
1. Branch from `main`
2. Fix bug
3. PR to `main`
4. Also merge to `develop`

---

## 🏆 **Benefits of This Setup**

✅ **Safety**: Main is protected from accidents  
✅ **Freedom**: AI can experiment without fear  
✅ **Quality**: Features are tested before release  
✅ **Recovery**: Easy to discard failed experiments  
✅ **History**: Clean main branch history  
✅ **Collaboration**: Clear workflow for human+AI  

---

## 💡 **Pro Tips**

### **For Experimentation Sessions**

```bash
# Start fresh experimental branch
git checkout develop
git branch -D feature/experimental
git checkout -b feature/experimental
git push origin feature/experimental --force

# Now AI has clean slate to experiment!
```

### **For Keeping Branches Synced**

```bash
# Update develop from main periodically
git checkout develop
git merge main
git push origin develop

# Update experimental from develop
git checkout feature/experimental
git merge develop
git push origin feature/experimental
```

### **For Cherry-Picking Good Ideas**

```bash
# AI made 10 commits on experimental
# You only want commits 3, 5, and 7

git checkout develop
git cherry-pick abc1234  # commit 3
git cherry-pick def5678  # commit 5
git cherry-pick ghi9012  # commit 7
git push origin develop
```

---

## 🎊 **You're All Set!**

**Current Status**:
- ✅ Three-branch strategy created
- ✅ Branches pushed to GitHub
- ⏳ Branch protection (needs setup on GitHub)

**Next Step**:
1. Go to GitHub settings
2. Enable branch protection for `main`
3. Tell AI: *"Let's experiment on feature/experimental!"*

**Now you can safely say**:
> *"Hey AI, go wild on feature/experimental and add some crazy cool features!"*

And your production code stays safe! 🛡️🎨

---

*Document created: October 8, 2025*  
*Branches created: develop, feature/experimental*  
*Status: Ready for protected experimentation!*


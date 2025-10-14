# Branch Protection Settings - Quick Reference

**For Repository**: notepadpp-mcp  
**Setup Time**: ~5 minutes

---

## 🚀 Quick Setup Instructions

### 1. Go to Settings

**URL**: https://github.com/sandraschi/notepadpp-mcp/settings/branches

Or:
1. Open repository on GitHub
2. Click `Settings` tab
3. Click `Branches` in left sidebar

---

## 2. Add Rule for `main` Branch

Click: **Add branch protection rule** or **Add rule**

### **Branch name pattern**
```
main
```

### **Protection Settings to Enable**

Copy these exact settings:

#### ✅ **Protect matching branches**

- [x] **Require a pull request before merging**
  - [x] Require approvals: `0` (you can self-approve)
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners (optional)

- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - Select status checks when available:
    - [ ] `ci` (will appear after first CI run)
    - [ ] `build` (will appear after first build)

- [x] **Require conversation resolution before merging**

- [x] **Require signed commits** (optional, skip if you don't use GPG)

- [x] **Include administrators**
  - This prevents even YOU from bypassing protections
  - Ensures safety from accidental force pushes

#### ❌ **Do NOT enable** (leave unchecked)

- [ ] ~~Allow force pushes~~ - **LEAVE UNCHECKED**
- [ ] ~~Allow deletions~~ - **LEAVE UNCHECKED**

#### ✅ **Additional Settings**

- [x] **Restrict who can push to matching branches**
  - Leave empty (allows PR merges only)
  - Or add specific users/teams if desired

- [x] **Require deployments to succeed before merging** (optional)

---

### Click: `Create` or `Save changes`

---

## 3. Optional: Protect `develop` Branch

**Branch name pattern**: `develop`

Use lighter restrictions:

- [x] **Require a pull request before merging** (optional)
  - [ ] Require approvals: `0`
  
- [ ] Allow force pushes (enabled for cleanup)
- [x] Restrict deletions

---

## 4. Leave `feature/*` Branches Unprotected

**Do NOT create rules for**:
- `feature/experimental`
- `feature/*`
- Other feature branches

**Why**: These are playground branches - AI needs full freedom here!

---

## ✅ Verification

After setup, test the protection:

```powershell
# Should FAIL (protected)
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "test"
git push origin main
# Expected: "remote: error: GH006: Protected branch update failed"

# Should SUCCEED (unprotected)
git checkout feature/experimental
echo "test" >> test.txt
git add test.txt  
git commit -m "test"
git push origin feature/experimental
# Expected: Success!

# Clean up
git reset --hard HEAD~1
git checkout main
```

---

## 🎯 What Protection Does

### **Prevents** ❌
- Direct pushes to `main`
- Force pushes to `main`
- Deleting `main` branch
- Merging without review
- Bypassing CI checks

### **Allows** ✅
- Pull Request merges (after review)
- Emergency hotfixes (via PR)
- Tag creation
- Branch creation
- Full freedom on `feature/*` branches

---

## 📋 Visual Settings Checklist

When you see the settings page, it should look like this:

```
Branch name pattern
┌────────────────────────────────────┐
│ main                                │
└────────────────────────────────────┘

Protect matching branches
☑ Require a pull request before merging
  ☑ Require approvals: [0]
  ☑ Dismiss stale pull request approvals
  
☑ Require status checks to pass
  ☑ Require branches to be up to date
  
☑ Require conversation resolution

☑ Include administrators

Restrict who can push
┌────────────────────────────────────┐
│ [empty - no restrictions]           │
└────────────────────────────────────┘

☐ Allow force pushes          [UNCHECKED]
☐ Allow deletions             [UNCHECKED]
```

---

## 🚨 Common Issues

### "I can't push to main anymore!"

**This is correct!** ✅ You now need to:
1. Create a branch
2. Make changes
3. Create Pull Request
4. Merge via PR

### "AI says it can't push to main"

**Perfect!** ✅ Tell AI to use:
1. Work on `feature/experimental`
2. Create PR when ready
3. You review and merge

### "I need to make an urgent fix!"

**No problem!** ✅
1. Create hotfix branch: `git checkout -b hotfix/urgent`
2. Make fix
3. Push branch: `git push origin hotfix/urgent`
4. Create PR on GitHub
5. Merge immediately (you can self-approve)

---

## 🎊 After Setup

**You can now safely say to AI**:

> "Work on feature/experimental and try adding [wild idea]!"

> "Go crazy on the experimental branch!"

> "Add 10 experimental features and let's see what works!"

**And your production code on `main` stays 100% safe!**

---

## 📞 Need Help?

If protection blocks something you need:

1. **Check**: Are you using the PR workflow?
2. **Temporarily disable**: Settings → Branches → Edit rule → Disable
3. **Make change**: Do what you need
4. **Re-enable**: Turn protection back on

**Or just ask AI**: "The branch protection is blocking me, help!"

---

*Setup Guide created: October 8, 2025*  
*Estimated setup time: 5 minutes*  
*Difficulty: Easy*


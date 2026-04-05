# Glama.ai Repository Rescan Guide

## How to Trigger Repository Updates on Glama.ai

Since Glama.ai automatically scans repositories, here are the most effective ways to ensure your recent documentation updates (status clarifications) are reflected on their platform.

## 🎯 **Primary Methods to Trigger Rescan**

### 1. **Create a New Release** (Most Effective - Immediate)

```bash
# Create and push a new git tag
git tag -a v1.0.1 -m "docs: improve metadata and Glama.ai conformance"
git push origin v1.0.1

# Then create a GitHub release on the repo page
```

**Why this works**: New releases are high-priority triggers for repository scanners and will update the listing within hours.

### 2. **Push Significant Commits** (Fast - Within 24 hours)

```bash
# Make a meaningful commit with the documentation updates
git add .
git commit -m "docs: standardize metadata for Glama.ai conformance"
git push origin main
```

**Why this works**: Significant commits trigger daily scans for active repositories.

### 3. **Contact Glama.ai Support** (Manual - Fastest if urgent)

**Email**: support@glama.ai

**Subject**: "Request repository rescan for metadata updates - blender-mcp"

**Message**:
```
Hello Glama.ai Team,

Our repository (sandraschi/blender-mcp) has recently updated its documentation
and added a glama.json file to improve its discoverability and metadata quality.

Could you please trigger a rescan to update our listing with the corrected metadata?

Repository: https://github.com/sandraschi/blender-mcp
Glama.ai URL: https://glama.ai/mcp/servers/%40sandraschi/blender-mcp

Thank you!
```

### 4. **Wait for Automatic Scan** (Slowest - Up to 1 week)

Glama.ai automatically scans repositories:
- **Daily**: For repositories with recent activity
- **Weekly**: For all indexed repositories

---

*Last Updated: 2026-01-25*

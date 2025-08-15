# GitHub DXT Building and Release Documentation

## 🚀 Automated DXT Building on GitHub

### Overview
Our GitHub repository automatically builds and releases DXT extensions using GitHub Actions, following our AI-first DXT building standards.

### Repository Structure
```
blender-mcp/
├── .github/
│   └── workflows/
│       └── build-dxt.yml          # GitHub Actions workflow
├── dxt/
│   ├── manifest.json              # AI-generated DXT manifest
│   └── assets/                    # Icons, screenshots
├── src/
│   └── blender_mcp/              # Python MCP server code
├── docs/
│   └── DXT_BUILDING_STANDARDS.md # Our definitive standards
├── build_github.py               # GitHub-compatible build script
├── requirements.txt              # Python dependencies
└── README.md
```

### Build Triggers

#### 1. Tag-Based Releases (Production)
```bash
git tag v1.0.0
git push origin v1.0.0
```
- Automatically builds DXT extension
- Creates GitHub release with .dxt file attached
- Uses tag version (e.g., v1.0.0 → blender-mcp-1.0.0.dxt)

#### 2. Manual Workflow Dispatch (Testing)
- Go to GitHub Actions → "Build and Release DXT Extension"
- Click "Run workflow"
- Specify version number
- Downloads .dxt file as artifact

### Build Process

#### Step 1: Environment Setup
- Ubuntu latest runner
- Python 3.11
- Node.js 18
- DXT CLI: `npm install -g @anthropic-ai/dxt`

#### Step 2: Validation
```bash
dxt validate dxt/manifest.json
```
- Validates AI-generated manifest.json
- Ensures all required fields present
- Checks template literal syntax

#### Step 3: Package Building
```bash
cd dxt
dxt pack . ../dist/blender-mcp-{version}.dxt
```
- Uses official DXT toolchain (NOT our deprecated build_dxt.py)
- Packages entire extension with dependencies
- Outputs to dist/ directory

#### Step 4: Optional Signing
```bash
dxt sign dist/blender-mcp-*.dxt --key signing.key
```
- Signs package if DXT_SIGNING_KEY secret is set
- Uses self-signed certificate for testing
- Production packages should use proper certificates

#### Step 5: Release Creation
- Uploads .dxt file as GitHub release asset
- Auto-generates release notes from commits
- Creates downloadable extension package

### GitHub Secrets Configuration

#### Required Secrets
- `GITHUB_TOKEN`: Automatically provided by GitHub

#### Optional Secrets
- `DXT_SIGNING_KEY`: Private key for signing extensions
- `DXT_CERTIFICATE`: Certificate for signing (production)

### Local Development

#### Build Locally
```bash
python build_github.py
```
- Uses same process as GitHub Actions
- Outputs to local dist/ directory
- Validates manifest before building

#### Test Installation
```bash
# Build extension
python build_github.py

# Install in Claude Desktop
# Drag dist/blender-mcp-1.0.0.dxt to Claude Desktop
```

### AI-First Manifest Management

#### Never Edit Manually
- ❌ Don't use `dxt init` primitive prompting
- ❌ Don't manually edit manifest.json fields
- ✅ Generate with AI prompts for comprehensive configurations

#### Update Process
1. Use AI to generate new manifest.json
2. Copy to `dxt/manifest.json`
3. Validate locally: `dxt validate dxt/manifest.json`
4. Commit and push changes
5. GitHub Actions rebuilds automatically

### Distribution Strategies

#### GitHub Releases (Primary)
- Automatic on version tags
- Discoverable via GitHub
- Direct .dxt download links
- Release notes and changelogs

#### DXT Extension Directory (Future)
- Submit to Anthropic's official directory
- Community discovery
- Automatic updates for users
- Enhanced distribution reach

#### FastMCP Integration (Planned)
- Submit to FastMCP.me when DXT support launches
- Multi-platform compatibility
- Enhanced community features

### Quality Assurance

#### Automated Checks
- Manifest validation
- Dependency verification
- Package integrity tests
- Cross-platform compatibility checks

#### Manual Testing
- Install on clean Claude Desktop
- Test user configuration flow
- Verify Blender detection
- Validate tool functionality

### Deployment Workflow

#### Development
```bash
# 1. AI-generate updated manifest.json
# 2. Test locally
python build_github.py

# 3. Test installation
# Drag dist/*.dxt to Claude Desktop

# 4. Commit changes
git add dxt/manifest.json
git commit -m "feat: updated manifest with new tools"
git push
```

#### Release
```bash
# 1. Create release tag
git tag v1.1.0
git push origin v1.1.0

# 2. GitHub Actions automatically:
#    - Builds DXT package
#    - Creates GitHub release
#    - Attaches .dxt file for download
```

### Error Handling

#### Build Failures
- Check manifest.json validation
- Verify all dependencies in requirements.txt
- Ensure DXT CLI installation successful
- Review GitHub Actions logs

#### Installation Issues
- Test user_config flow for Blender path selection
- Verify template literals resolve correctly
- Check permissions and compatibility sections
- Validate on multiple operating systems

### Monitoring and Analytics

#### GitHub Insights
- Download counts per release
- Popular extension versions
- Geographic distribution of users
- Issue and discussion tracking

#### Extension Metrics
- Installation success rates
- User configuration completion
- Tool usage patterns (if telemetry enabled)
- Error reporting and debugging

This automated approach ensures consistent, reliable DXT extension building while maintaining our AI-first development methodology and avoiding primitive CLI tooling.

# 📖 MkDocs Documentation Viewer

**Complete MkDocs setup for viewing Blender MCP documentation with beautiful sidebar navigation and search.**

## Overview

This directory contains the MkDocs configuration and documentation files that provide a modern, searchable documentation viewer for the entire Blender MCP project. MkDocs transforms your Markdown files into a professional documentation website with sidebar navigation, full-text search, and responsive design.

## What is MkDocs?

**MkDocs** is a fast, simple static site generator that's geared towards building project documentation. It takes your Markdown files and builds a complete website with:

- **Beautiful Themes**: Material Design theme with dark/light modes
- **Sidebar Navigation**: Expandable file tree navigation
- **Full-Text Search**: Instant search across all documentation
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Version Control Integration**: Git-aware with last modified dates
- **Extensible**: Plugins for additional features

### Why MkDocs for Blender MCP?

- **Perfect for Technical Docs**: Designed for API references, guides, and tutorials
- **Markdown Native**: Write documentation in familiar Markdown format
- **Fast Development**: Live reload during editing
- **Professional Output**: Production-ready documentation sites
- **Searchable**: Users can find information instantly
- **Customizable**: Themes, layouts, and features can be customized

## Quick Start

### Prerequisites
```bash
# Install MkDocs and Material theme
pip install mkdocs mkdocs-material

# Optional: Install additional plugins
pip install mkdocs-git-revision-date-localized-plugin mkdocs-git-committers-plugin-2 mkdocs-minify-plugin
```

### Serve Documentation Locally

#### Option 1: Direct MkDocs Command
```bash
# From project root (recommended)
mkdocs serve -f docs/docsviewer/mkdocs.yml

# Or change to docsviewer directory
cd docs/docsviewer
mkdocs serve
```

#### Option 2: Convenience Scripts
```bash
# Windows PowerShell
./docs/docsviewer/serve_docs.ps1

# Linux/macOS Bash
./docs/docsviewer/serve_docs.sh
```

**Access at:** http://127.0.0.1:7333

### Build Static Site
```bash
# Build for deployment
mkdocs build

# Output goes to site/ directory
# Can be hosted on any web server
```

## Directory Structure

```
docs/docsviewer/
├── mkdocs.yml              # Main configuration file
├── README.md               # MkDocs documentation and setup guide
├── index.md                # Homepage
├── installation.md         # Installation guide
├── quickstart.md           # Quick start guide
├── configuration.md        # Configuration reference
├── log_tools.md            # Log tools documentation
├── download_tools.md       # Download tools documentation
├── serve_docs.ps1          # Windows PowerShell script
└── serve_docs.sh           # Linux/macOS Bash script
```

## Configuration (mkdocs.yml)

The `mkdocs.yml` file controls all aspects of your documentation site:

### Site Information
```yaml
site_name: Blender MCP Documentation
site_description: Complete Blender automation and asset management documentation
site_author: Blender MCP Team
```

### Theme Configuration
```yaml
theme:
  name: material
  language: en
  palette:
    - scheme: default    # Light mode
      primary: blue
      accent: blue
    - scheme: slate      # Dark mode
      primary: blue
      accent: blue
```

### Features
```yaml
features:
  - announce.dismiss           # Dismissible announcements
  - content.action.edit        # Edit links
  - content.action.view        # View source links
  - navigation.expand          # Expandable navigation
  - navigation.instant         # Instant loading
  - search.highlight           # Search highlighting
  - search.suggest             # Search suggestions
  - toc.follow                 # Table of contents follows scroll
```

### Navigation Structure
```yaml
nav:
  - Home: index.md
  - Getting Started:
      - Installation: installation.md
      - Quick Start: quickstart.md
      - Configuration: configuration.md
  - User Guide:
      - Blender MCP: '../blender/README.md'
      - Tool Reference: '../blender/TOOL_REFERENCE.md'
      # ... more sections
```

## Writing Documentation

### Markdown Features

MkDocs supports standard Markdown plus extensions:

#### Headers and Structure
```markdown
# H1 Header
## H2 Header
### H3 Header

- Bullet points
- More bullets

1. Numbered lists
2. More numbers
```

#### Code Blocks
```python
# Python code with syntax highlighting
def hello_world():
    print("Hello, Blender MCP!")
```

#### Admonitions (Callouts)
```markdown
!!! note
    This is a note

!!! warning
    This is a warning

!!! tip
    This is a tip
```

#### Tables
```markdown
| Feature | Status | Description |
|---------|--------|-------------|
| Tool A  | ✅     | Working     |
| Tool B  | 🚧     | In progress |
```

### Cross-References
```markdown
[Link to another page](installation.md)
[Link to section](installation.md#prerequisites)
[Link to external site](https://blender.org)
```

## Advanced Features

### Plugins

#### Git Revision Date
Shows when pages were last modified:
```yaml
plugins:
  - git-revision-date-localized:
      enable_creation_date: true
      type: timeago
```

#### Git Committers
Shows who contributed to each page:
```yaml
plugins:
  - git-committers:
      repository: sandraschi/blender-mcp
      branch: main
```

#### Minification
Optimizes the built site:
```yaml
plugins:
  - minify:
      minify_html: true
```

### Custom Themes

#### Color Customization
```yaml
theme:
  palette:
    primary: blue
    accent: blue
  font:
    text: Roboto
    code: Roboto Mono
```

#### Logo and Icons
```yaml
theme:
  logo: images/logo.png
  icon:
    repo: fontawesome/brands/github
```

### Search Configuration
```yaml
plugins:
  - search:
      separator: '[\s\u200b\-_,:!=\[\]()"`/]+|\.(?!\d)|&[lg]t;|(?!\b)(?=[A-Z][a-z])'
```

## Deployment Options

### GitHub Pages
```bash
# Deploy to GitHub Pages
mkdocs gh-deploy

# Access at: https://username.github.io/repository/
```

### Netlify
```bash
# Build the site
mkdocs build

# Upload site/ directory to Netlify
```

### Self-Hosted
```bash
# Build the site
mkdocs build

# Serve with any web server
# Apache, Nginx, or simple Python server
python -m http.server 8000 -d site/
```

### Docker
```dockerfile
FROM squidfunk/mkdocs-material
COPY . /docs
RUN mkdocs build
EXPOSE 8000
CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]
```

## Development Workflow

### Local Development
```bash
# Start development server
mkdocs serve

# Edit files and see changes instantly
# Server auto-reloads on file changes
```

### Content Organization
- Keep documentation in logical sections
- Use consistent naming conventions
- Cross-reference related content
- Include examples and code samples

### Version Control
- Commit documentation changes regularly
- Use meaningful commit messages
- Review documentation in pull requests

## Customization

### Custom CSS
Create `docs/docsviewer/styles/extra.css`:
```css
/* Custom styles */
:root {
  --md-primary-fg-color: #1976d2;
  --md-accent-fg-color: #1976d2;
}
```

### Custom JavaScript
Create `docs/docsviewer/javascript/extra.js`:
```javascript
// Custom JavaScript
document.addEventListener('DOMContentLoaded', function() {
  console.log('MkDocs site loaded');
});
```

### Theme Overrides
Override theme templates in `docs/docsviewer/overrides/`:
```
overrides/
├── main.html
├── partials/
│   ├── header.html
│   └── footer.html
└── styles/
    └── extra.css
```

## Best Practices

### Content Guidelines
- **Clear Structure**: Use headings and sections logically
- **Consistent Formatting**: Follow Markdown conventions
- **Code Examples**: Include practical, runnable examples
- **Cross-References**: Link related content
- **Regular Updates**: Keep documentation current

### SEO Optimization
- **Descriptive Titles**: Clear, specific page titles
- **Meta Descriptions**: Concise summaries
- **Keywords**: Include relevant search terms
- **Alt Text**: Describe images for accessibility

### Performance
- **Optimize Images**: Compress images before adding
- **Minimize Plugins**: Only use necessary plugins
- **Build Regularly**: Test builds don't break
- **Monitor Size**: Keep site size reasonable

## Troubleshooting

### Common Issues

#### Site Won't Build
```bash
# Check for YAML syntax errors
python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"

# Validate Markdown files
find docs -name "*.md" -exec markdown-validate {} \;
```

#### Navigation Problems
```bash
# Check YAML indentation
yamllint mkdocs.yml

# Verify file paths exist
ls -la docs/**/*.md
```

#### Search Not Working
```bash
# Clear browser cache
# Check JavaScript console for errors
# Verify search plugin configuration
```

#### Styling Issues
```bash
# Clear MkDocs cache
rm -rf site/
mkdocs build --clean

# Check for CSS conflicts
# Verify theme compatibility
```

### Debug Mode
```bash
# Run with verbose output
mkdocs serve --verbose

# Build with debug info
mkdocs build --strict
```

## Integration with Blender MCP

### Automatic Documentation Updates
- Documentation builds can be part of CI/CD
- Auto-generate API references from code
- Include tool counts and status updates

### Cross-References
- Link from code comments to documentation
- Reference documentation in error messages
- Include links in tool help output

### Version Synchronization
- Keep documentation in sync with releases
- Tag documentation versions
- Maintain changelog integration

## Resources

### Official Documentation
- **MkDocs**: https://mkdocs.org/
- **Material Theme**: https://squidfunk.github.io/mkdocs-material/
- **Plugins**: https://github.com/mkdocs/mkdocs/wiki/MkDocs-Plugins

### Community
- **GitHub Discussions**: https://github.com/squidfunk/mkdocs-material/discussions
- **Discord**: MkDocs community chat
- **Stack Overflow**: #mkdocs tag

### Examples
- **MkDocs Examples**: https://github.com/mkdocs/examples
- **Material Theme Examples**: https://squidfunk.github.io/mkdocs-material/showcase/

---

**🎨 MkDocs provides a beautiful, searchable documentation experience for Blender MCP!**

**🚀 Start the server:** `mkdocs serve -f docs/docsviewer/mkdocs.yml`

**📖 Access at:** http://127.0.0.1:8000 ✨

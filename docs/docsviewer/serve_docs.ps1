# Serve MkDocs Documentation Viewer
# Run this script from the project root to start the documentation server

Write-Host "🚀 Starting Blender MCP MkDocs Documentation Server..." -ForegroundColor Green
Write-Host "📖 Access documentation at: http://127.0.0.1:7333" -ForegroundColor Cyan
Write-Host "📁 Docs location: docs/docsviewer/" -ForegroundColor Yellow
Write-Host ""

# Check if MkDocs is installed
try {
    $mkdocsVersion = & mkdocs --version 2>$null
    Write-Host "✅ MkDocs found: $mkdocsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ MkDocs not found. Install with: pip install mkdocs mkdocs-material" -ForegroundColor Red
    Write-Host "💡 Optional plugins: pip install mkdocs-git-revision-date-localized-plugin mkdocs-git-committers-plugin-2 mkdocs-minify-plugin" -ForegroundColor Yellow
    exit 1
}

# Start MkDocs server
Write-Host "🌐 Starting server..." -ForegroundColor Blue
mkdocs serve -f docs/docsviewer/mkdocs.yml --dev-addr=127.0.0.1:7333

Write-Host "👋 Server stopped." -ForegroundColor Gray

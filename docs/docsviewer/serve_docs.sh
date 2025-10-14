#!/bin/bash

# Serve MkDocs Documentation Viewer
# Run this script from the project root to start the documentation server

echo "🚀 Starting Blender MCP MkDocs Documentation Server..."
echo "📖 Access documentation at: http://127.0.0.1:7333"
echo "📁 Docs location: docs/docsviewer/"
echo ""

# Check if MkDocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo "❌ MkDocs not found. Install with: pip install mkdocs mkdocs-material"
    echo "💡 Optional plugins: pip install mkdocs-git-revision-date-localized-plugin mkdocs-git-committers-plugin-2 mkdocs-minify-plugin"
    exit 1
fi

echo "✅ MkDocs found: $(mkdocs --version)"
echo "🌐 Starting server..."
mkdocs serve -f docs/docsviewer/mkdocs.yml --dev-addr=127.0.0.1:7333

echo "👋 Server stopped."

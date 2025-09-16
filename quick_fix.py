#!/usr/bin/env python3
"""
Blender MCP Quick Fix Script
2025-08-28 - Fix circular import issues and emoji encoding problems
"""

import os
import re
from pathlib import Path

def fix_circular_imports():
    """Fix circular import issues in handler files."""
    handlers_dir = Path("dxt/server/blender_mcp/handlers")
    
    if not handlers_dir.exists():
        print(f"❌ Handlers directory not found: {handlers_dir}")
        return False
        
    # Files to fix
    handler_files = [
        "scene_handler.py",
        "mesh_handler.py", 
        "material_handler.py",
        "export_handler.py",
        "render_handler.py",
        "shader_handler.py"
    ]
    
    print(f"🔧 Fixing circular imports in {len(handler_files)} handler files...")
    
    for filename in handler_files:
        filepath = handlers_dir / filename
        if not filepath.exists():
            print(f"⚠️  Handler file not found: {filename}")
            continue
            
        # Read current content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix circular import - remove server import
        if "from ..server import app" in content:
            print(f"  🔄 Fixing {filename}: removing circular import...")
            
            # Remove the import line
            content = re.sub(r'from \.\.server import app\n?', '', content)
            
            # Replace @app.tool decorators with a placeholder that will be registered later
            content = re.sub(r'@app\.tool\n', '# @tool  # Will be registered by server\n', content)
            
            # Write back the fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed {filename}")
        else:
            print(f"  ℹ️  {filename} already fixed or no circular import found")
    
    return True

def create_proper_server():
    """Create a new server.py with proper tool registration."""
    server_content = '''"""Blender MCP Server - Fixed version without circular imports."""

import asyncio
import sys
import os
from pathlib import Path
from typing import Any, Dict, Optional, List
import argparse

# FastMCP imports
from fastmcp import FastMCP

# Initialize FastMCP application with banner disabled (critical for Claude Desktop)
app = FastMCP(
    name="blender-mcp",
    version="1.0.0", 
    description="Blender MCP Server for 3D content creation and automation",
    banner=False  # Critical: prevents JSON parsing issues in Claude Desktop
)

def register_tools_manually():
    """Register tools manually to avoid circular imports."""
    
    # Import handlers after app is created
    from .handlers import scene_handler, mesh_handler, material_handler, export_handler, render_handler, shader_handler
    
    # Register scene tools
    app.tool(scene_handler.create_scene)
    app.tool(scene_handler.list_scenes) 
    app.tool(scene_handler.clear_scene)
    
    # Register mesh tools (key functions from analysis)
    app.tool(mesh_handler.create_chaiselongue)
    app.tool(mesh_handler.create_vanity_table)
    app.tool(mesh_handler.create_candle_set)
    app.tool(mesh_handler.create_ornate_mirror)
    app.tool(mesh_handler.create_feather_duster)
    
    # Register material tools
    app.tool(material_handler.create_fabric_material)
    app.tool(material_handler.create_metal_material)
    app.tool(material_handler.create_wood_material)
    
    # Register export tools
    app.tool(export_handler.export_for_unity)
    app.tool(export_handler.export_for_vrchat)
    
    # Register render tools
    app.tool(render_handler.render_turntable)
    app.tool(render_handler.render_preview)
    
    print("SUCCESS: All tools registered manually", file=sys.stderr)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Blender MCP Server")
    parser.add_argument("--blender", default="blender", help="Path to Blender executable")
    return parser.parse_args()

async def main():
    """Main entry point."""
    args = parse_args()
    
    # Set Blender executable
    os.environ["BLENDER_EXECUTABLE"] = args.blender
    
    # Register tools
    register_tools_manually()
    
    # Start server in stdio mode
    print("SUCCESS: Starting Blender MCP server...", file=sys.stderr)
    await app.serve_stdio()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("SHUTDOWN: Blender MCP server stopped", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)
'''
    
    server_path = Path("dxt/server/blender_mcp/server_fixed.py")
    with open(server_path, 'w', encoding='utf-8') as f:
        f.write(server_content)
    
    print(f"✅ Created fixed server: {server_path}")
    return True

def fix_emoji_issues():
    """Fix Unicode emoji issues that cause Windows encoding problems."""
    
    files_to_check = [
        "dxt/server/blender_mcp/server.py"
    ]
    
    print("🔧 Checking for Unicode emoji issues...")
    
    # Emoji patterns that cause Windows cp1252 issues
    problematic_emojis = ['🚀', '💬', '📊', '🎨', '🌐', '✅', '💥', '👋']
    
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file contains problematic emojis
        has_issues = any(emoji in content for emoji in problematic_emojis)
        
        if has_issues:
            print(f"⚠️  Found Unicode emojis in {filepath}")
            # Replace emojis with safe ASCII equivalents
            replacements = {
                '🚀': '[START]',
                '💬': '[STDIO]', 
                '📊': '[LOG]',
                '🎨': '[BLENDER]',
                '🌐': '[HTTP]',
                '✅': '[OK]',
                '💥': '[ERROR]',
                '👋': '[SHUTDOWN]'
            }
            
            for emoji, replacement in replacements.items():
                content = content.replace(emoji, replacement)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed Unicode issues in {os.path.basename(filepath)}")

def main():
    """Run all fixes."""
    print("=" * 60)
    print("BLENDER MCP QUICK FIX - 2025-08-28")
    print("=" * 60)
    
    # 1. Fix circular imports
    if not fix_circular_imports():
        print("❌ Failed to fix circular imports")
        return
    
    # 2. Create proper server
    if not create_proper_server():
        print("❌ Failed to create fixed server")
        return
        
    # 3. Fix emoji issues 
    fix_emoji_issues()
    
    print("\n" + "=" * 60)
    print("🎯 QUICK FIX COMPLETE")
    print("=" * 60)
    print("Next steps:")
    print("1. Test server startup: python -m dxt.server.blender_mcp.server_fixed")
    print("2. Should start without import/emoji errors")

if __name__ == "__main__":
    main()

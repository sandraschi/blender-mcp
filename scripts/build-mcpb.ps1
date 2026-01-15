#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Professional MCPB build script for Blender MCP
    Builds, validates, and packages the MCP server for distribution

.DESCRIPTION
    This script provides professional MCPB packaging for the Blender MCP server.
    It handles validation, building, signing, and distribution preparation.

.PARAMETER Clean
    Clean build directory before building

.PARAMETER Validate
    Run MCPB validation checks

.PARAMETER Sign
    Sign the package (requires key file)

.PARAMETER KeyFile
    Path to signing key file

.PARAMETER NoSign
    Explicitly disable signing

.EXAMPLE
    .\build-mcpb.ps1 -Clean -Validate
    .\build-mcpb.ps1 -Sign -KeyFile "my-key.pem"
#>

param(
    [switch]$Clean,
    [switch]$Validate,
    [switch]$Sign,
    [string]$KeyFile,
    [switch]$NoSign
)

$ErrorActionPreference = "Stop"

# Configuration
$PACKAGE_NAME = "blender-mcp"
$VERSION = "1.0.0"
$OUTPUT_DIR = "dist"
$MCPB_DIR = "mcpb"

# Colors for output
$Color_Cyan = "Cyan"
$Color_Green = "Green"
$Color_Red = "Red"
$Color_Yellow = "Yellow"

function Write-Step {
    param([string]$Message)
    Write-Host "🔧 $Message" -ForegroundColor $Color_Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Color_Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Color_Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Color_Red
}

function Exit-WithError {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

# Check prerequisites
function Test-Prerequisites {
    Write-Step "Checking prerequisites..."

    # Check if mcpb is installed
    try {
        $mcpbVersion = & mcpb --version 2>$null
        Write-Success "MCPB CLI found: $mcpbVersion"
    } catch {
        Exit-WithError "MCPB CLI not found. Install with: npm install -g @anthropic-ai/mcpb"
    }

    # Check if we're in the right directory
    if (-not (Test-Path "$MCPB_DIR/manifest.json")) {
        Exit-WithError "Not in correct directory. Missing $MCPB_DIR/manifest.json"
    }

    Write-Success "Prerequisites check passed"
}

# Clean build directory
function Invoke-Clean {
    Write-Step "Cleaning build directory..."
    if (Test-Path $OUTPUT_DIR) {
        Remove-Item -Recurse -Force $OUTPUT_DIR
        Write-Success "Removed existing build directory"
    }

    # Create fresh output directory
    New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null
    Write-Success "Created fresh build directory"
}

# Validate MCPB structure
function Invoke-Validation {
    Write-Step "Validating MCPB structure..."

    Push-Location $MCPB_DIR
    try {
        # Run MCPB validation
        & mcpb validate
        if ($LASTEXITCODE -ne 0) {
            Exit-WithError "MCPB validation failed"
        }
        Write-Success "MCPB validation passed"

        # Additional checks
        if (-not (Test-Path "manifest.json")) {
            Exit-WithError "Missing manifest.json"
        }
        if (-not (Test-Path "mcpb.json")) {
            Exit-WithError "Missing mcpb.json"
        }

        Write-Success "All validation checks passed"

    } catch {
        Exit-WithError "Validation failed: $_"
    } finally {
        Pop-Location
    }
}

# Build MCPB package
function Invoke-Build {
    Write-Step "Building MCPB package..."

    $outputFile = "$OUTPUT_DIR/${PACKAGE_NAME}-${VERSION}.mcpb"

    Push-Location $MCPB_DIR
    try {
        # Build the package
        & mcpb pack . "../$outputFile" --no-sign
        if ($LASTEXITCODE -ne 0) {
            Exit-WithError "MCPB build failed"
        }

        if (-not (Test-Path "../$outputFile")) {
            Exit-WithError "Build completed but output file not found"
        }

        $fileSize = (Get-Item "../$outputFile").Length / 1MB
        Write-Success "MCPB package built successfully"
        Write-Host "📦 Package: $outputFile" -ForegroundColor $Color_Yellow
        Write-Host "📏 Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor $Color_Yellow

    } catch {
        Exit-WithError "Build failed: $_"
    } finally {
        Pop-Location
    }
}

# Sign package
function Invoke-Signing {
    param([string]$KeyPath)

    if (-not $KeyPath) {
        Exit-WithError "KeyFile parameter required for signing"
    }

    if (-not (Test-Path $KeyPath)) {
        Exit-WithError "Signing key file not found: $KeyPath"
    }

    Write-Step "Signing MCPB package..."

    $packageFile = "$OUTPUT_DIR/${PACKAGE_NAME}-${VERSION}.mcpb"

    try {
        & mcpb sign --key $KeyPath $packageFile
        if ($LASTEXITCODE -ne 0) {
            Exit-WithError "Package signing failed"
        }
        Write-Success "Package signed successfully"

    } catch {
        Exit-WithError "Signing failed: $_"
    }
}

# Verify package
function Invoke-Verification {
    Write-Step "Verifying MCPB package..."

    $packageFile = "$OUTPUT_DIR/${PACKAGE_NAME}-${VERSION}.mcpb"

    try {
        # Basic file check
        if (-not (Test-Path $packageFile)) {
            Exit-WithError "Package file not found for verification"
        }

        # MCPB verification
        & mcpb verify $packageFile
        if ($LASTEXITCODE -ne 0) {
            Exit-WithError "Package verification failed"
        }

        Write-Success "Package verification passed"

        # Show package info
        $fileInfo = Get-Item $packageFile
        Write-Host "📋 Package Details:" -ForegroundColor $Color_Cyan
        Write-Host "   Name: $PACKAGE_NAME" -ForegroundColor $Color_Cyan
        Write-Host "   Version: $VERSION" -ForegroundColor $Color_Cyan
        Write-Host "   Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor $Color_Cyan
        Write-Host "   Created: $($fileInfo.CreationTime)" -ForegroundColor $Color_Cyan

    } catch {
        Exit-WithError "Verification failed: $_"
    }
}

# Generate distribution assets
function New-DistributionAssets {
    Write-Step "Generating distribution assets..."

    $packageFile = "$OUTPUT_DIR/${PACKAGE_NAME}-${VERSION}.mcpb"
    $shaFile = "$OUTPUT_DIR/${PACKAGE_NAME}-${VERSION}.sha256"

    try {
        # Generate SHA256 checksum
        $hash = Get-FileHash -Path $packageFile -Algorithm SHA256
        "$($hash.Hash.ToLower())  ${PACKAGE_NAME}-${VERSION}.mcpb" | Out-File -FilePath $shaFile -Encoding UTF8
        Write-Success "SHA256 checksum generated"

        # Create installation script for Windows
        $installScript = @"
# Blender MCP Quick Install Script
# Run this to install Blender MCP automatically

Write-Host "🚀 Installing Blender MCP..." -ForegroundColor Cyan

# Check if MCPB CLI is installed
try {
    `$mcpbVersion = & mcpb --version 2>`$null
    Write-Host "✅ MCPB CLI found: `$mcpbVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ MCPB CLI not found. Install with: npm install -g @anthropic-ai/mcpb" -ForegroundColor Red
    exit 1
}

# Install the package
Write-Host "📦 Installing Blender MCP..." -ForegroundColor Cyan
& mcpb install "$packageFile"

Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host "🔄 Restart Claude Desktop to start using Blender MCP" -ForegroundColor Yellow
"@

        $installScript | Out-File -FilePath "$OUTPUT_DIR/install-windows.ps1" -Encoding UTF8
        Write-Success "Windows install script generated"

        # Create README for releases
        $releaseReadme = @"
# Blender MCP v$VERSION

🚀 **AI-Powered 3D Creation** - Control Blender with natural language!

## Quick Install

**Option 1 - Drag & Drop (Easiest):**
1. Download `${PACKAGE_NAME}-${VERSION}.mcpb`
2. Drag the file into Claude Desktop
3. Done! 🎉

**Option 2 - Command Line:**
```bash
# Install MCPB CLI first
npm install -g @anthropic-ai/mcpb

# Install Blender MCP
mcpb install ${PACKAGE_NAME}-${VERSION}.mcpb
```

## What's New in v$VERSION

- AI-powered 3D scene creation
- Natural language object manipulation
- VRM avatar animation support
- Batch processing capabilities
- Professional MCPB packaging

## Requirements

- Claude Desktop
- Blender 3.0+
- Python 3.8+

## Features

- ⚡ **95% Time Savings** - Hours become minutes
- 🎯 **Zero Learning Curve** - Describe, don't code
- 🔄 **Endless Creativity** - Generate unlimited variations
- 🌐 **Cross-Platform** - Windows, Mac, Linux

## Support

- 📖 [Documentation](https://github.com/sandraschi/blender-mcp)
- 🐛 [Issues](https://github.com/sandraschi/blender-mcp/issues)
- 💬 [Discussions](https://github.com/sandraschi/blender-mcp/discussions)

---

**By FlowEngineer sandraschi** - Pioneering AI-powered creative tools
"@

        $releaseReadme | Out-File -FilePath "$OUTPUT_DIR/RELEASE_README.md" -Encoding UTF8
        Write-Success "Release README generated"

    } catch {
        Write-Warning "Failed to generate some distribution assets: $_"
    }
}

# Main execution
function Invoke-Main {
    Write-Host "🎨 Blender MCP Professional Build System" -ForegroundColor $Color_Cyan
    Write-Host "============================================" -ForegroundColor $Color_Cyan
    Write-Host ""

    Test-Prerequisites

    if ($Clean) {
        Invoke-Clean
    }

    if ($Validate) {
        Invoke-Validation
    }

    Invoke-Build

    if ($Sign -and -not $NoSign) {
        Invoke-Signing -KeyPath $KeyFile
    }

    Invoke-Verification
    New-DistributionAssets

    Write-Host ""
    Write-Success "🎉 MCPB build complete!"
    Write-Host ""
    Write-Host "📦 Ready for distribution:" -ForegroundColor $Color_Yellow
    Write-Host "   • $OUTPUT_DIR/${PACKAGE_NAME}-${VERSION}.mcpb" -ForegroundColor $Color_Yellow
    Write-Host "   • $OUTPUT_DIR/${PACKAGE_NAME}-${VERSION}.sha256" -ForegroundColor $Color_Yellow
    Write-Host "   • $OUTPUT_DIR/install-windows.ps1" -ForegroundColor $Color_Yellow
    Write-Host "   • $OUTPUT_DIR/RELEASE_README.md" -ForegroundColor $Color_Yellow
    Write-Host ""
    Write-Host "🚀 Upload to GitHub Releases!" -ForegroundColor $Color_Green
}

# Run main function
try {
    Invoke-Main
} catch {
    Write-Error "Build failed with error: $_"
    exit 1
}






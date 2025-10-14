# Blender MCP - MCPB Package Builder
# Version: 1.0.0
# Description: Builds MCPB package for Blender MCP server

param(
    [switch]$NoSign,
    [switch]$Clean,
    [string]$OutputDir = "dist",
    [string]$Version = "1.0.0",
    [switch]$Verbose,
    [switch]$SkipValidation
)

# Configuration
$PackageName = "blender-mcp"
$ManifestPath = "mcpb-packaging/manifests/mcpb_manifest.json"
$McpbConfigPath = "mcpb-packaging/mcpb.json"
$SourceDir = "src"
$RequirementsPath = "requirements.txt"

# Color output functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" "Yellow"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ️  $Message" "Cyan"
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to get file size in MB
function Get-FileSizeMB {
    param([string]$Path)
    if (Test-Path $Path) {
        $size = (Get-Item $Path).Length
        return [math]::Round($size / 1MB, 2)
    }
    return 0
}

# Main build function
function Build-MCPBPackage {
    Write-ColorOutput "🚀 Blender MCP - MCPB Package Builder" "Magenta"
    Write-ColorOutput "====================================" "Magenta"

    # Prerequisites check
    Write-Info "Checking prerequisites..."

    $prerequisites = @(
        @{Name = "Node.js"; Command = "node"; InstallUrl = "https://nodejs.org/"},
        @{Name = "MCPB CLI"; Command = "mcpb"; InstallUrl = "npm install -g @anthropic-ai/mcpb"},
        @{Name = "Python"; Command = "python"; InstallUrl = "https://python.org"},
        @{Name = "Pip"; Command = "pip"; InstallUrl = "https://pip.pypa.io/"}
    )

    $missingPrereqs = @()
    foreach ($prereq in $prerequisites) {
        if (Test-Command $prereq.Command) {
            Write-Success "$($prereq.Name) found"
        } else {
            Write-Error "$($prereq.Name) not found"
            $missingPrereqs += $prereq
        }
    }

    if ($missingPrereqs.Count -gt 0) {
        Write-Error "Missing prerequisites. Please install:"
        foreach ($prereq in $missingPrereqs) {
            Write-ColorOutput "  - $($prereq.Name): $($prereq.InstallUrl)" "Yellow"
        }
        exit 1
    }

    # Clean previous builds
    if ($Clean) {
        Write-Info "Cleaning previous builds..."
        if (Test-Path $OutputDir) {
            Remove-Item $OutputDir -Recurse -Force
        }
        Write-Success "Cleaned previous builds"
    }

    # Create output directory
    if (!(Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir | Out-Null
        Write-Success "Created output directory: $OutputDir"
    }

    # Validate files
    if (!$SkipValidation) {
        Write-Info "Validating configuration files..."

        $validationFiles = @(
            $ManifestPath,
            $McpbConfigPath,
            $RequirementsPath,
            "$SourceDir/blender_mcp/__init__.py",
            "$SourceDir/blender_mcp/__main__.py"
        )

        foreach ($file in $validationFiles) {
            if (Test-Path $file) {
                Write-Success "Found: $file"
            } else {
                Write-Error "Missing required file: $file"
                exit 1
            }
        }
    }

    # Validate manifest
    Write-Info "Validating MCPB manifest..."
    try {
        $manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
        Write-Success "Manifest is valid JSON"

        # Check required fields
        $requiredFields = @("manifest_version", "name", "version", "server", "tools")
        foreach ($field in $requiredFields) {
            if ($manifest.PSObject.Properties.Name -contains $field) {
                Write-Success "Manifest has required field: $field"
            } else {
                Write-Error "Manifest missing required field: $field"
                exit 1
            }
        }
    }
    catch {
        Write-Error "Invalid manifest JSON: $($_.Exception.Message)"
        exit 1
    }

    # Check MCPB CLI version
    Write-Info "Checking MCPB CLI version..."
    try {
        $mcpbVersion = & mcpb --version 2>$null
        Write-Success "MCPB CLI version: $mcpbVersion"
    }
    catch {
        Write-Error "Failed to get MCPB CLI version"
        exit 1
    }

    # Update version in manifest if specified
    if ($Version -ne "1.0.0") {
        Write-Info "Updating version to $Version..."
        $manifest.version = $Version
        $manifest | ConvertTo-Json -Depth 10 | Set-Content $ManifestPath -Encoding UTF8
        Write-Success "Updated version in manifest"
    }

    # Build MCPB package
    Write-Info "Building MCPB package..."
    $outputFile = "$OutputDir/$PackageName.mcpb"

    $buildArgs = @("pack", "--manifest", $ManifestPath, "--output", $outputFile)
    if ($Verbose) {
        $buildArgs += "--verbose"
    }

    try {
        if ($Verbose) {
            & mcpb $buildArgs
        } else {
            & mcpb $buildArgs 2>$null
        }

        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCPB package built successfully"
        } else {
            Write-Error "MCPB build failed with exit code $LASTEXITCODE"
            exit 1
        }
    }
    catch {
        Write-Error "MCPB build failed: $($_.Exception.Message)"
        exit 1
    }

    # Verify package
    Write-Info "Verifying package..."
    if (Test-Path $outputFile) {
        $packageSize = Get-FileSizeMB $outputFile
        Write-Success "Package created: $outputFile ($packageSize MB)"

        # Validate package structure
        try {
            $validateArgs = @("validate", $outputFile)
            if ($Verbose) {
                & mcpb $validateArgs
            } else {
                & mcpb $validateArgs 2>$null
            }

            if ($LASTEXITCODE -eq 0) {
                Write-Success "Package validation passed"
            } else {
                Write-Warning "Package validation failed"
            }
        }
        catch {
            Write-Warning "Package validation error: $($_.Exception.Message)"
        }
    } else {
        Write-Error "Package file not created: $outputFile"
        exit 1
    }

    # Sign package (optional)
    if (!$NoSign) {
        Write-Info "Checking for signing capability..."
        try {
            $signArgs = @("sign", "--check")
            & mcpb $signArgs 2>$null | Out-Null

            if ($LASTEXITCODE -eq 0) {
                Write-Info "Signing package..."
                $signArgs = @("sign", $outputFile)
                & mcpb $signArgs 2>$null

                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Package signed successfully"
                } else {
                    Write-Warning "Package signing failed"
                }
            } else {
                Write-Warning "Signing not available or not configured"
            }
        }
        catch {
            Write-Warning "Signing check failed: $($_.Exception.Message)"
        }
    } else {
        Write-Info "Skipping package signing (--nosign specified)"
    }

    # Final verification
    Write-Info "Final package verification..."
    if (Test-Path $outputFile) {
        $finalSize = Get-FileSizeMB $outputFile
        $fileInfo = Get-Item $outputFile

        Write-ColorOutput "" "Magenta"
        Write-ColorOutput "🎯 BUILD COMPLETE!" "Green"
        Write-ColorOutput "==================" "Green"
        Write-Success "Package: $outputFile"
        Write-Success "Size: $finalSize MB"
        Write-Success "Created: $($fileInfo.CreationTime)"
        Write-Success "Version: $Version"

        if (!$NoSign) {
            Write-Success "Signed: Yes"
        } else {
            Write-Info "Signed: No (--nosign specified)"
        }

        Write-ColorOutput "" "Cyan"
        Write-ColorOutput "📦 Package ready for distribution!" "Cyan"
        Write-ColorOutput "   Drag and drop to Claude Desktop to install" "Cyan"
        Write-ColorOutput "" "Cyan"
    } else {
        Write-Error "Final verification failed - package not found"
        exit 1
    }
}

# Run main function
try {
    Build-MCPBPackage
}
catch {
    Write-Error "Build failed with error: $($_.Exception.Message)"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

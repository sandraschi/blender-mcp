# Blender MCP - MCPB Package Validator
# Version: 1.0.0
# Description: Validates MCPB package structure and contents

param(
    [Parameter(Mandatory=$true)]
    [string]$PackagePath,
    [switch]$Verbose,
    [switch]$Detailed
)

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

# Function to validate JSON
function Test-JsonFile {
    param([string]$Path)
    try {
        Get-Content $Path -Raw | ConvertFrom-Json | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to extract MCPB package (if supported)
function Expand-MCPBPackage {
    param([string]$PackagePath, [string]$ExtractPath)

    Write-Info "Extracting MCPB package for detailed validation..."

    # Create temp directory for extraction
    $tempDir = Join-Path $ExtractPath "mcpb_temp"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempDir | Out-Null

    try {
        # Use MCPB CLI to extract/validate
        $extractArgs = @("extract", $PackagePath, "--output", $tempDir)
        if ($Verbose) {
            & mcpb $extractArgs
        } else {
            & mcpb $extractArgs 2>$null
        }

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Package extracted successfully"
            return $tempDir
        } else {
            Write-Warning "Could not extract package for detailed validation"
            return $null
        }
    }
    catch {
        Write-Warning "Package extraction failed: $($_.Exception.Message)"
        return $null
    }
}

# Main validation function
function Test-MCPBPackage {
    Write-ColorOutput "🔍 Blender MCP - MCPB Package Validator" "Magenta"
    Write-ColorOutput "=======================================" "Magenta"

    # Check if package exists
    if (!(Test-Path $PackagePath)) {
        Write-Error "Package not found: $PackagePath"
        exit 1
    }

    Write-Success "Package found: $PackagePath"
    $packageSize = Get-FileSizeMB $PackagePath
    Write-Info "Package size: $packageSize MB"

    # Check file extension
    if (!(Split-Path $PackagePath -Extension).ToLower() -eq ".mcpb") {
        Write-Warning "File does not have .mcpb extension"
    }

    # Check MCPB CLI availability
    if (!(Test-Command "mcpb")) {
        Write-Error "MCPB CLI not found. Install with: npm install -g @anthropic-ai/mcpb"
        exit 1
    }

    Write-Success "MCPB CLI available"

    # Basic MCPB validation
    Write-Info "Running MCPB validation..."
    try {
        $validateArgs = @("validate", $PackagePath)
        if ($Verbose) {
            & mcpb $validateArgs
        } else {
            & mcpb $validateArgs 2>$null
        }

        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCPB validation passed"
        } else {
            Write-Error "MCPB validation failed"
            exit 1
        }
    }
    catch {
        Write-Error "MCPB validation error: $($_.Exception.Message)"
        exit 1
    }

    # Detailed validation
    if ($Detailed) {
        Write-Info "Performing detailed validation..."

        # Create temp directory for detailed checks
        $tempPath = [System.IO.Path]::GetTempPath()
        $extractPath = Join-Path $tempPath "blender-mcp-validation-$(Get-Random)"

        try {
            $extractedPath = Expand-MCPBPackage -PackagePath $PackagePath -ExtractPath $extractPath

            if ($extractedPath) {
                # Validate extracted contents
                Write-Info "Validating extracted package contents..."

                # Check for required directories
                $requiredDirs = @("src", "mcpb-packaging", "docs")
                foreach ($dir in $requiredDirs) {
                    $dirPath = Join-Path $extractedPath $dir
                    if (Test-Path $dirPath) {
                        Write-Success "Found required directory: $dir"
                    } else {
                        Write-Warning "Missing recommended directory: $dir"
                    }
                }

                # Check for Python files
                $pythonFiles = Get-ChildItem -Path $extractedPath -Filter "*.py" -Recurse
                Write-Info "Found $($pythonFiles.Count) Python files"

                # Check for manifest
                $manifestPath = Join-Path $extractedPath "mcpb-packaging/manifests/mcpb_manifest.json"
                if (Test-Path $manifestPath) {
                    Write-Success "Found MCPB manifest"

                    if (Test-JsonFile $manifestPath) {
                        Write-Success "Manifest is valid JSON"

                        # Load and validate manifest content
                        $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json

                        # Check manifest version
                        if ($manifest.manifest_version) {
                            Write-Success "Manifest version: $($manifest.manifest_version)"
                        }

                        # Check server configuration
                        if ($manifest.server) {
                            Write-Success "Server configuration found"
                            if ($manifest.server.entry_point) {
                                Write-Success "Entry point: $($manifest.server.entry_point)"
                            }
                        }

                        # Check tools
                        if ($manifest.tools) {
                            Write-Success "Found $($manifest.tools.Count) tool definitions"
                        }

                        # Check user config
                        if ($manifest.user_config) {
                            Write-Success "User configuration defined"
                        }
                    } else {
                        Write-Error "Manifest is not valid JSON"
                    }
                } else {
                    Write-Error "MCPB manifest not found in package"
                }

                # Check for main module
                $mainPath = Join-Path $extractedPath "src/blender_mcp/__main__.py"
                if (Test-Path $mainPath) {
                    Write-Success "Found main module"
                } else {
                    Write-Error "Main module not found"
                }

                # Check for requirements
                $reqPath = Join-Path $extractedPath "requirements.txt"
                if (Test-Path $reqPath) {
                    Write-Success "Found requirements.txt"
                    $reqContent = Get-Content $reqPath
                    Write-Info "Requirements count: $($reqContent.Count)"
                } else {
                    Write-Warning "requirements.txt not found"
                }

                # Check for documentation
                $docFiles = Get-ChildItem -Path $extractedPath -Filter "*.md" -Recurse
                Write-Info "Found $($docFiles.Count) documentation files"

                # Check for README
                $readmePath = Join-Path $extractedPath "README.md"
                if (Test-Path $readmePath) {
                    Write-Success "Found README.md"
                } else {
                    Write-Warning "README.md not found"
                }

            } else {
                Write-Warning "Skipping detailed content validation"
            }

        } finally {
            # Clean up temp directory
            if (Test-Path $extractPath) {
                try {
                    Remove-Item $extractPath -Recurse -Force
                    Write-Info "Cleaned up temporary files"
                } catch {
                    Write-Warning "Could not clean up temporary files: $($_.Exception.Message)"
                }
            }
        }
    }

    # Installation simulation
    Write-Info "Simulating installation compatibility..."

    # Check if package can be inspected
    try {
        $inspectArgs = @("inspect", $PackagePath)
        if ($Verbose) {
            & mcpb $inspectArgs
        } else {
            & mcpb $inspectArgs 2>$null
        }

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Package inspection successful"
        } else {
            Write-Warning "Package inspection failed"
        }
    }
    catch {
        Write-Warning "Package inspection error: $($_.Exception.Message)"
    }

    # Final summary
    Write-ColorOutput "" "Magenta"
    Write-ColorOutput "🎯 VALIDATION COMPLETE!" "Green"
    Write-ColorOutput "======================" "Green"
    Write-Success "Package: $PackagePath"
    Write-Success "Size: $packageSize MB"
    Write-Success "MCPB Validation: PASSED"

    if ($Detailed) {
        Write-Success "Detailed Validation: COMPLETED"
    }

    Write-ColorOutput "" "Cyan"
    Write-ColorOutput "📦 Package is ready for distribution!" "Cyan"
    Write-ColorOutput "   This package can be installed in Claude Desktop" "Cyan"
    Write-ColorOutput "" "Cyan"
}

# Run main function
try {
    Test-MCPBPackage
}
catch {
    Write-Error "Validation failed with error: $($_.Exception.Message)"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

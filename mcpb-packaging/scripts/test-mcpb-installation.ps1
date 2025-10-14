# Blender MCP - MCPB Installation Tester
# Version: 1.0.0
# Description: Tests MCPB package installation and basic functionality

param(
    [Parameter(Mandatory=$true)]
    [string]$PackagePath,
    [string]$TempDir = "$env:TEMP\blender-mcp-test",
    [switch]$KeepTemp,
    [switch]$Verbose,
    [switch]$SkipCleanup
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

# Function to create test configuration
function New-TestConfig {
    param([string]$InstallPath)

    $config = @{
        blender_executable = "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
        auto_detect_blender = $true
        operation_timeout = 60
        max_parallel_operations = 1
        enable_gpu_rendering = $false
        render_samples = 32
        temp_directory = Join-Path $InstallPath "temp"
        log_level = "INFO"
        enable_performance_monitoring = $false
        backup_blend_files = $false
    }

    return $config
}

# Function to test basic tool functionality
function Test-BasicTools {
    param([string]$InstallPath)

    Write-Info "Testing basic tool functionality..."

    # Test list_scenes (should work without Blender)
    $testScript = @"
import sys
import os
sys.path.insert(0, r'$InstallPath')

try:
    from blender_mcp.app import get_app
    app = get_app()

    # Test tool discovery
    tools = app.get_tools()
    print(f"Found {len(tools)} tools")

    # Test basic scene operations
    from blender_mcp.handlers.scene_handler import create_scene, list_scenes

    # This should work even without Blender running
    result = list_scenes()
    print(f"Scene list result: {result}")

    print("SUCCESS: Basic functionality test passed")
except Exception as e:
    print(f"ERROR: Basic functionality test failed: {e}")
    import traceback
    traceback.print_exc()
"@

    $testFile = Join-Path $env:TEMP "blender_mcp_test.py"
    $testScript | Out-File -FilePath $testFile -Encoding UTF8

    try {
        $result = & python $testFile 2>&1
        Write-Info "Test output: $result"

        if ($result -match "SUCCESS") {
            Write-Success "Basic functionality test passed"
            return $true
        } else {
            Write-Error "Basic functionality test failed"
            return $false
        }
    }
    catch {
        Write-Error "Basic functionality test error: $($_.Exception.Message)"
        return $false
    }
    finally {
        if (Test-Path $testFile) {
            Remove-Item $testFile -Force
        }
    }
}

# Function to test Blender integration
function Test-BlenderIntegration {
    param([string]$InstallPath, [string]$ConfigPath)

    Write-Info "Testing Blender integration..."

    # This test requires Blender to be available
    if (!(Test-Path $ConfigPath)) {
        Write-Warning "Skipping Blender integration test - no config file"
        return $null
    }

    $testScript = @"
import sys
import os
import json
sys.path.insert(0, r'$InstallPath')

# Load config
with open(r'$ConfigPath', 'r') as f:
    config = json.load(f)

try:
    from blender_mcp.config import BLENDER_EXECUTABLE, validate_blender_executable
    from blender_mcp.utils.blender_executor import get_blender_executor

    # Check Blender availability
    if validate_blender_executable():
        print("SUCCESS: Blender executable validated")

        # Test executor creation
        executor = get_blender_executor()
        print("SUCCESS: Blender executor created")

        # Test simple Blender script execution
        test_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
print("SUCCESS: Blender script executed")
'''
        result = executor.execute_script(test_script)
        print(f"Blender execution result: {result}")

    else:
        print("WARNING: Blender not available for testing")

except Exception as e:
    print(f"ERROR: Blender integration test failed: {e}")
    import traceback
    traceback.print_exc()
"@

    $testFile = Join-Path $env:TEMP "blender_integration_test.py"
    $testScript | Out-File -FilePath $testFile -Encoding UTF8

    try {
        $result = & python $testFile 2>&1
        Write-Info "Integration test output: $result"

        if ($result -match "SUCCESS.*Blender") {
            Write-Success "Blender integration test passed"
            return $true
        } elseif ($result -match "WARNING.*Blender not available") {
            Write-Warning "Blender not available for testing"
            return $null
        } else {
            Write-Error "Blender integration test failed"
            return $false
        }
    }
    catch {
        Write-Error "Blender integration test error: $($_.Exception.Message)"
        return $false
    }
    finally {
        if (Test-Path $testFile) {
            Remove-Item $testFile -Force
        }
    }
}

# Main installation test function
function Test-MCPBInstallation {
    Write-ColorOutput "🧪 Blender MCP - MCPB Installation Tester" "Magenta"
    Write-ColorOutput "=========================================" "Magenta"

    # Check prerequisites
    if (!(Test-Command "mcpb")) {
        Write-Error "MCPB CLI not found. Install with: npm install -g @anthropic-ai/mcpb"
        exit 1
    }

    if (!(Test-Command "python")) {
        Write-Error "Python not found"
        exit 1
    }

    # Check if package exists
    if (!(Test-Path $PackagePath)) {
        Write-Error "Package not found: $PackagePath"
        exit 1
    }

    Write-Success "Package found: $PackagePath"

    # Create temp directory for installation
    if (Test-Path $TempDir) {
        Remove-Item $TempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TempDir | Out-Null
    Write-Success "Created test directory: $TempDir"

    try {
        # Simulate installation
        Write-Info "Simulating MCPB package installation..."

        $installArgs = @("install", $PackagePath, "--target", $TempDir)
        if ($Verbose) {
            & mcpb $installArgs
        } else {
            & mcpb $installArgs 2>$null
        }

        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCPB installation simulation successful"
        } else {
            Write-Error "MCPB installation simulation failed"
            exit 1
        }

        # Check installed files
        Write-Info "Checking installed files..."

        $expectedDirs = @("src", "docs", "mcpb-packaging")
        foreach ($dir in $expectedDirs) {
            $dirPath = Join-Path $TempDir $dir
            if (Test-Path $dirPath) {
                Write-Success "Found installed directory: $dir"
            } else {
                Write-Warning "Missing installed directory: $dir"
            }
        }

        # Check main module
        $mainPath = Join-Path $TempDir "src/blender_mcp/__main__.py"
        if (Test-Path $mainPath) {
            Write-Success "Found main module"
        } else {
            Write-Error "Main module not found after installation"
            exit 1
        }

        # Create test configuration
        $configPath = Join-Path $TempDir "config.json"
        $config = New-TestConfig -InstallPath $TempDir
        $config | ConvertTo-Json | Set-Content $configPath -Encoding UTF8
        Write-Success "Created test configuration"

        # Test basic functionality
        $basicTestPassed = Test-BasicTools -InstallPath "$TempDir/src"

        # Test Blender integration (optional)
        $blenderTestPassed = Test-BlenderIntegration -InstallPath "$TempDir/src" -ConfigPath $configPath

        # Run MCPB post-install hooks if they exist
        $hooksPath = Join-Path $TempDir "mcpb-packaging/scripts/post-install.ps1"
        if (Test-Path $hooksPath) {
            Write-Info "Running post-install hooks..."
            try {
                & $hooksPath -InstallPath $TempDir
                Write-Success "Post-install hooks completed"
            }
            catch {
                Write-Warning "Post-install hooks failed: $($_.Exception.Message)"
            }
        }

        # Final results
        Write-ColorOutput "" "Magenta"
        Write-ColorOutput "🎯 INSTALLATION TEST COMPLETE!" "Green"
        Write-ColorOutput "==============================" "Green"

        Write-Success "Package: $PackagePath"
        Write-Success "Installation Directory: $TempDir"
        Write-Success "Basic Functionality Test: $(if ($basicTestPassed) { 'PASSED' } else { 'FAILED' })"

        if ($null -ne $blenderTestPassed) {
            Write-Success "Blender Integration Test: $(if ($blenderTestPassed) { 'PASSED' } else { 'FAILED' })"
        } else {
            Write-Info "Blender Integration Test: SKIPPED (Blender not available)"
        }

        $overallResult = $basicTestPassed -and ($null -eq $blenderTestPassed -or $blenderTestPassed)
        if ($overallResult) {
            Write-ColorOutput "" "Green"
            Write-ColorOutput "🎉 ALL TESTS PASSED!" "Green"
            Write-ColorOutput "   Package is ready for production use" "Green"
            Write-ColorOutput "" "Green"
        } else {
            Write-ColorOutput "" "Red"
            Write-ColorOutput "❌ SOME TESTS FAILED!" "Red"
            Write-ColorOutput "   Package requires fixes before distribution" "Red"
            Write-ColorOutput "" "Red"
            exit 1
        }

    }
    finally {
        # Cleanup
        if (!$KeepTemp -and !$SkipCleanup) {
            Write-Info "Cleaning up test files..."
            try {
                if (Test-Path $TempDir) {
                    Remove-Item $TempDir -Recurse -Force
                }
                Write-Success "Cleanup completed"
            }
            catch {
                Write-Warning "Cleanup failed: $($_.Exception.Message)"
            }
        } elseif ($KeepTemp) {
            Write-Info "Keeping test files (--keeptemp specified)"
            Write-Info "Test directory: $TempDir"
        }
    }
}

# Run main function
try {
    Test-MCPBInstallation
}
catch {
    Write-Error "Installation test failed with error: $($_.Exception.Message)"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

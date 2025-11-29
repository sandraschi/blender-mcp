#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated repository backup using Windows native compression
    
.DESCRIPTION
    Creates a compressed ZIP backup of the repository and saves to:
    1. Desktop\repo backup\
    2. N:\backup\dev\repos\
    
    Excludes:
    - .venv/ (virtual environments)
    - __pycache__/ (Python cache)
    - .ruff_cache/, .mypy_cache/, .pytest_cache/
    - node_modules/ (if any)
    - dist/, build/ (build artifacts)
    - VirtualBox files (*.vdi, *.vmdk, *.vbox)
    - Test artifacts (MagicMock/, sandboxes/, quarantine/)
    - Logs (*.log)
    
.PARAMETER IncludeBuild
    Include dist/ and build/ folders (default: false)
    
.EXAMPLE
    .\scripts\backup-repo.ps1
    # Creates backup in Desktop\repo backup and N:\backup\dev\repos
    
.EXAMPLE
    .\scripts\backup-repo.ps1 -IncludeBuild
    # Creates backup including build artifacts
#>

param(
    [switch]$IncludeBuild = $false
)

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║       📦 Repository Backup (Windows Native ZIP) 📦      ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

# Check if we're in a repo
if (-not (Test-Path "pyproject.toml") -and -not (Test-Path ".git") -and -not (Test-Path "package.json")) {
    Write-Host "❌ Error: Must run from repository root (need pyproject.toml, .git, or package.json)" -ForegroundColor Red
    exit 1
}

# Get repo name and timestamp
$repoName = (Get-Item .).Name
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupName = "${repoName}_backup_${timestamp}.zip"

# Define backup destinations with subdirectories per repo
$desktopBackup = Join-Path (Join-Path ([Environment]::GetFolderPath("Desktop")) "repo backup") $repoName
$nDriveBackup = Join-Path "N:\backup\dev\repos2" $repoName
$oneDriveRoot = Join-Path $env:OneDrive "repo-backups"
$oneDriveBackup = Join-Path $oneDriveRoot $repoName

# Ensure backup directories exist
if (-not (Test-Path $desktopBackup)) {
    New-Item -ItemType Directory -Path $desktopBackup -Force | Out-Null
    Write-Host "✅ Created: $desktopBackup" -ForegroundColor Green
}

if (-not (Test-Path $nDriveBackup)) {
    New-Item -ItemType Directory -Path $nDriveBackup -Force | Out-Null
    Write-Host "✅ Created: $nDriveBackup" -ForegroundColor Green
}

if (-not (Test-Path $oneDriveBackup)) {
    New-Item -ItemType Directory -Path $oneDriveBackup -Force | Out-Null
    Write-Host "✅ Created: $oneDriveBackup" -ForegroundColor Green
}

$backupPath1 = Join-Path $desktopBackup $backupName
$backupPath2 = Join-Path $nDriveBackup $backupName
$backupPath3 = Join-Path $oneDriveBackup $backupName

Write-Host "📋 Backup Configuration:" -ForegroundColor Cyan
Write-Host "  Repository:    $repoName" -ForegroundColor White
Write-Host "  Timestamp:     $timestamp" -ForegroundColor White
Write-Host "  Destination 1: $backupPath1" -ForegroundColor White
Write-Host "  Destination 2: $backupPath2" -ForegroundColor White
Write-Host "  Destination 3: $backupPath3" -ForegroundColor Cyan
Write-Host "  Include build: $(if($IncludeBuild){'Yes'}else{'No'})" -ForegroundColor White
Write-Host "  Method:        .NET ZIP API (folder structure preserved)" -ForegroundColor Green
Write-Host ""

# Define exclusions
$exclusions = @(
    ".venv",
    "venv",
    "env",
    ".env",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "htmlcov",
    "node_modules",
    # ".git",  # INCLUDE .git - contains unpushed commits, local branches, history
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "Thumbs.db",
    ".windsurf",
    ".cursor",
    "*.log",
    ".vbox",
    "*.vdi",
    "*.vmdk",
    "*.vhd",
    "*.vbox",
    "*.vbox-prev",
    "MagicMock",
    "sandboxes",
    "quarantine",
    "analysis",
    "backups",
    "*.dxt"        # Old DXT package format
)

# Large test files that should be excluded (can be regenerated)
# Note: Use forward slashes or double backslashes for regex compatibility
$excludeLargeTestFiles = @(
    "samples/metadata.db",      # Large Calibre test database (3.9 MB)
    "samples/test_library.db",  # Large test libraries  
    "test_data/*.db"            # Test data in any test_data directory
)

# Combine exclusions
$exclusions += $excludeLargeTestFiles

if (-not $IncludeBuild) {
    $exclusions += @("dist", "build", "*.whl", "*.tar.gz")
}

Write-Host "🚫 Excluding:" -ForegroundColor Yellow
foreach ($excl in $exclusions) {
    Write-Host "  - $excl" -ForegroundColor Gray
}
Write-Host ""

# Calculate sizes
Write-Host "📊 Analyzing repository size..." -ForegroundColor Cyan

$allFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue
$totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum / 1MB

# Filter files to backup
$backupFiles = $allFiles | Where-Object {
    $file = $_
    $shouldExclude = $false
    
    # Skip symlinks/ReparsePoints (cause access denied errors)
    if ($file.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        return $false
    }
    
    foreach ($excl in $exclusions) {
        $pattern = $excl -replace '\*', '.*' -replace '\.', '\.'
        if ($file.FullName -match $pattern -or $file.FullName -match [regex]::Escape($excl)) {
            $shouldExclude = $true
            break
        }
    }
    
    -not $shouldExclude
}

$backupSize = ($backupFiles | Measure-Object -Property Length -Sum).Sum / 1MB
$excludedSize = $totalSize - $backupSize

Write-Host "  Total size:    $([math]::Round($totalSize, 2)) MB" -ForegroundColor White
Write-Host "  Excluded:      $([math]::Round($excludedSize, 2)) MB" -ForegroundColor Red
Write-Host "  Backup size:   $([math]::Round($backupSize, 2)) MB" -ForegroundColor Green
Write-Host "  Reduction:     $([math]::Round(($excludedSize / $totalSize) * 100, 1))%`n" -ForegroundColor Cyan

# Create backup
Write-Host "🔄 Creating backups..." -ForegroundColor Cyan

try {
    # CRITICAL FIX: Use .NET ZIP to preserve folder structure
    # Compress-Archive flattens structure when given file list
    
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    
    $repoRoot = (Get-Item .).FullName
    
    # Create backup 1 (Desktop)
    Write-Host "  → Desktop\repo backup..." -ForegroundColor Gray
    if (Test-Path $backupPath1) {
        Remove-Item $backupPath1 -Force
    }
    
    # Create ZIP archive
    $zip1 = [System.IO.Compression.ZipFile]::Open($backupPath1, [System.IO.Compression.ZipArchiveMode]::Create)
    
    foreach ($file in $backupFiles) {
        # Get relative path from repo root
        $relativePath = $file.FullName.Substring($repoRoot.Length + 1)
        # Use forward slashes for ZIP standard
        $zipPath = $relativePath -replace '\\', '/'
        # Add file to archive with full path
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip1, $file.FullName, $zipPath, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
    }
    
    $zip1.Dispose()
    Write-Host "  ✅ Desktop backup complete (folder structure preserved)" -ForegroundColor Green
    
    # Create backup 2 (N: drive)
    Write-Host "  → N:\backup\dev\repos2..." -ForegroundColor Gray
    if (Test-Path $backupPath2) {
        Remove-Item $backupPath2 -Force
    }
    
    # Create ZIP archive
    $zip2 = [System.IO.Compression.ZipFile]::Open($backupPath2, [System.IO.Compression.ZipArchiveMode]::Create)
    
    foreach ($file in $backupFiles) {
        # Get relative path from repo root
        $relativePath = $file.FullName.Substring($repoRoot.Length + 1)
        # Use forward slashes for ZIP standard
        $zipPath = $relativePath -replace '\\', '/'
        # Add file to archive with full path
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip2, $file.FullName, $zipPath, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
    }
    
    $zip2.Dispose()
    Write-Host "  ✅ N: drive backup complete (folder structure preserved)" -ForegroundColor Green
    
    # Create backup 3 (OneDrive)
    Write-Host "  → OneDrive\repo-backups..." -ForegroundColor Gray
    if (Test-Path $backupPath3) {
        Remove-Item $backupPath3 -Force
    }
    
    # Create ZIP archive
    $zip3 = [System.IO.Compression.ZipFile]::Open($backupPath3, [System.IO.Compression.ZipArchiveMode]::Create)
    
    foreach ($file in $backupFiles) {
        # Get relative path from repo root
        $relativePath = $file.FullName.Substring($repoRoot.Length + 1)
        # Use forward slashes for ZIP standard
        $zipPath = $relativePath -replace '\\', '/'
        # Add file to archive with full path
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip3, $file.FullName, $zipPath, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
    }
    
    $zip3.Dispose()
    Write-Host "  ✅ OneDrive backup complete (folder structure preserved)" -ForegroundColor Green
    
    Write-Host "`n✅ All 3 backups created successfully with folder structure!`n" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error creating backup: $_" -ForegroundColor Red
    exit 1
}

# Get final backup file info
if ((Test-Path $backupPath1) -and (Test-Path $backupPath2) -and (Test-Path $backupPath3)) {
    $finalSize = (Get-Item $backupPath1).Length / 1MB
    $compressionRatio = ($finalSize / $backupSize) * 100
    
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║              📦 Backup Complete! 📦                     ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Backup Statistics:" -ForegroundColor Cyan
    Write-Host "  File:           $backupName" -ForegroundColor White
    Write-Host "  Location 1:     $desktopBackup" -ForegroundColor White
    Write-Host "  Location 2:     $nDriveBackup" -ForegroundColor White
    Write-Host "  Location 3:     $oneDriveBackup" -ForegroundColor Cyan
    Write-Host "  Size:           $([math]::Round($finalSize, 2)) MB" -ForegroundColor Cyan
    Write-Host "  Original:       $([math]::Round($backupSize, 2)) MB" -ForegroundColor Gray
    Write-Host "  Compression:    $([math]::Round($compressionRatio, 1))%" -ForegroundColor Green
    Write-Host "  Space saved:    $([math]::Round($totalSize - $finalSize, 2)) MB" -ForegroundColor Green
    Write-Host "  Method:         .NET ZIP API (folder structure preserved)" -ForegroundColor Green
    Write-Host ""
    
    # Restore instructions
    Write-Host "💡 To restore:" -ForegroundColor Cyan
    Write-Host "  Expand-Archive -Path `"$backupPath1`" -DestinationPath `"destination-folder`"" -ForegroundColor Gray
    Write-Host ""
    
} else {
    Write-Host "❌ Error: Some backup files not created" -ForegroundColor Red
    Write-Host "  Path 1: $(Test-Path $backupPath1)" -ForegroundColor Gray
    Write-Host "  Path 2: $(Test-Path $backupPath2)" -ForegroundColor Gray
    Write-Host "  Path 3: $(Test-Path $backupPath3)" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ Done!`n" -ForegroundColor Green

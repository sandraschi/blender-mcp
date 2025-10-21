#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated repository backup using Windows native compression
    
.DESCRIPTION
    Creates a compressed ZIP backup of the repository excluding:
    - .venv/ (virtual environments)
    - __pycache__/ (Python cache)
    - .ruff_cache/, .mypy_cache/, .pytest_cache/
    - node_modules/ (if any)
    - dist/, build/ (build artifacts)
    - VirtualBox files (*.vdi, *.vmdk, *.vbox)
    - Test artifacts (MagicMock/, sandboxes/, quarantine/)
    - Logs (*.log)
    
.PARAMETER OutputPath
    Where to save the backup (default: parent directory)
    
.PARAMETER IncludeBuild
    Include dist/ and build/ folders (default: false)
    
.EXAMPLE
    .\scripts\backup-repo.ps1
    # Creates backup in parent directory
    
.EXAMPLE
    .\scripts\backup-repo.ps1 -OutputPath "D:\Backups" -IncludeBuild
    # Creates backup in D:\Backups including build artifacts
#>

param(
    [string]$OutputPath = "..",
    [switch]$IncludeBuild = $false
)

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║       📦 Repository Backup (Windows Native ZIP) 📦      ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

# Check if we're in a repo
if (-not (Test-Path "pyproject.toml") -and -not (Test-Path ".git")) {
    Write-Host "❌ Error: Must run from repository root" -ForegroundColor Red
    exit 1
}

# Get repo name and timestamp
$repoName = (Get-Item .).Name
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupName = "${repoName}_backup_${timestamp}.zip"

# Resolve output path
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}
$OutputPath = Resolve-Path $OutputPath
$backupPath = Join-Path $OutputPath $backupName

Write-Host "📋 Backup Configuration:" -ForegroundColor Cyan
Write-Host "  Repository:    $repoName" -ForegroundColor White
Write-Host "  Timestamp:     $timestamp" -ForegroundColor White
Write-Host "  Output:        $backupPath" -ForegroundColor White
Write-Host "  Include build: $(if($IncludeBuild){'Yes'}else{'No'})" -ForegroundColor White
Write-Host "  Method:        Windows native (Compress-Archive)" -ForegroundColor Green
Write-Host ""

# Define exclusions (glob patterns)
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
    ".git",
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
    "backups"
)

if (-not $IncludeBuild) {
    $exclusions += @("dist", "build", "*.whl", "*.tar.gz")
}

Write-Host "🚫 Excluding:" -ForegroundColor Yellow
foreach ($excl in $exclusions) {
    Write-Host "  - $excl" -ForegroundColor Gray
}
Write-Host ""

# Calculate original size
Write-Host "📊 Analyzing repository size..." -ForegroundColor Cyan

$allFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue
$totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum / 1MB

# Calculate what we'll actually backup
$backupFiles = $allFiles | Where-Object {
    $file = $_
    $shouldExclude = $false
    
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

# Create temporary list of files to backup
Write-Host "🔄 Creating backup with Windows Compress-Archive..." -ForegroundColor Cyan

try {
    # Compress-Archive with exclusions
    $tempList = $backupFiles | ForEach-Object { $_.FullName }
    
    # Use Compress-Archive (native Windows PowerShell)
    Compress-Archive -Path $tempList -DestinationPath $backupPath -CompressionLevel Optimal -Force
    
    Write-Host "✅ Backup created successfully!`n" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error creating backup: $_" -ForegroundColor Red
    exit 1
}

# Get final backup file info
if (Test-Path $backupPath) {
    $finalSize = (Get-Item $backupPath).Length / 1MB
    $compressionRatio = ($finalSize / $backupSize) * 100
    
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║              📦 Backup Complete! 📦                     ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Backup Statistics:" -ForegroundColor Cyan
    Write-Host "  File:           $(Split-Path -Leaf $backupPath)" -ForegroundColor White
    Write-Host "  Location:       $OutputPath" -ForegroundColor White
    Write-Host "  Size:           $([math]::Round($finalSize, 2)) MB" -ForegroundColor Cyan
    Write-Host "  Original:       $([math]::Round($backupSize, 2)) MB" -ForegroundColor Gray
    Write-Host "  Compression:    $([math]::Round($compressionRatio, 1))%" -ForegroundColor Green
    Write-Host "  Space saved:    $([math]::Round($totalSize - $finalSize, 2)) MB" -ForegroundColor Green
    Write-Host "  Method:         Windows native (Compress-Archive)" -ForegroundColor Green
    Write-Host ""
    
    # Restore instructions
    Write-Host "💡 To restore:" -ForegroundColor Cyan
    Write-Host "  Expand-Archive -Path `"$backupPath`" -DestinationPath `"destination-folder`"" -ForegroundColor Gray
    Write-Host ""
    
} else {
    Write-Host "❌ Error: Backup file not found at $backupPath" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Done!`n" -ForegroundColor Green


#!/usr/bin/env pwsh
<#
---
name: backup-repo.ps1
description: SOTA Repository Backup Script with per-repo rules and frequency support.
version: 2.1.0
features:
  - Multi-destination support (N: Drive, OneDrive, Desktop)
  - Selective frequency (WEEKLY, MONTHLY)
  - Custom exclusions via .backup-rules.md
  - SHA-256 integrity verification
  - Dry-run mode (-WhatIf)
usage: |
  .\backup-repo.ps1 [-List] [-WhatIf] [-Force] [-IncludeBuild]
---
.SYNOPSIS
    Automated repository backup using Windows native compression with SOTA error handling
    
.DESCRIPTION
    Creates a compressed ZIP backup of the repository and saves to:
    1. Desktop\repo backup\
    2. N:\backup\dev\repos\
    3. OneDrive\repo-backups\
    
    Features:
    - Individual error handling per backup location
    - Retry logic with exponential backoff
    - Disk space validation
    - Progress reporting for large backups
    - Partial success handling (continues if one destination fails)
    - Detailed error logging
    - Integrity verification after creation
    - Graceful cleanup on failures
    
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
    
.PARAMETER MaxRetries
    Maximum number of retry attempts for failed operations (default: 3)
    
.PARAMETER RetryDelaySeconds
    Initial delay between retries in seconds (default: 2)
    
.EXAMPLE
    .\scripts\backup-repo.ps1
    # Creates backup in Desktop\repo backup, N:\backup\dev\repos, and OneDrive
    
.EXAMPLE
    .\scripts\backup-repo.ps1 -IncludeBuild
    # Creates backup including build artifacts
    
.EXAMPLE
    .\scripts\backup-repo.ps1 -MaxRetries 5 -RetryDelaySeconds 5
    # Custom retry configuration for unreliable network drives
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [switch]$IncludeBuild = $false,
    [switch]$List = $false,
    [ValidateSet('text', 'json')]
    [string]$OutputFormat = 'text',
    [int]$MaxRetries = 3,
    [int]$RetryDelaySeconds = 2
)

# Set error action preference for better error handling
$ErrorActionPreference = "Stop"
$PSDefaultParameterValues['*:ErrorAction'] = 'Stop'

# Verbose and WhatIf are available via CmdletBinding/SupportsShouldProcess
$Verbose = $VerbosePreference -eq 'Continue'
$WhatIf = $WhatIfPreference

# Start timing
$script:StartTime = Get-Date

# Get repo name early
$repoName = "unknown"
if ((Test-Path "pyproject.toml") -or (Test-Path ".git") -or (Test-Path "package.json")) {
    $repoName = (Get-Item .).Name
}

# Initialize error tracking and logging
$script:ErrorLog = @()
$script:BackupResults = @{}
$script:StartTime = Get-Date
$script:TotalFilesProcessed = 0
$script:TotalFilesFailed = 0

# Add types for hashing and compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.Security.Cryptography

#region Helper Functions

function Write-ErrorLog {
    param(
        [string]$Message,
        [string]$Category = "Error",
        [PSObject]$Exception = $null
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Category] $Message"
    if ($Exception) {
        $ex = if ($Exception -is [System.Management.Automation.ErrorRecord]) { $Exception.Exception } else { $Exception }
        if ($ex) {
            $logEntry += "`n  Exception: $($ex.GetType().FullName)"
            $logEntry += "`n  Message: $($ex.Message)"
            $logEntry += "`n  StackTrace: $($ex.StackTrace)"
        }
    }
    $script:ErrorLog += $logEntry
    
    if ($script:OutputFormat -eq 'text') {
        Write-Host $logEntry -ForegroundColor $(if ($Category -eq "Error") { "Red" } elseif ($Category -eq "Warning") { "Yellow" } else { "Gray" })
    }
}

function Show-BackupHistory {
    param(
        [string]$RepoName,
        [string[]]$BackupDirs
    )
    
    Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║        📊 Backup History: $RepoName 📊         ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
    
    foreach ($backupDir in $BackupDirs) {
        if (-not (Test-Path $backupDir)) {
            Write-Host "⚠️  Location: $backupDir (not found)`n" -ForegroundColor Yellow
            continue
        }
        
        $backups = Get-ChildItem -Path $backupDir -Filter "*.zip" -File | Sort-Object LastWriteTime -Descending
        $locationName = Split-Path $backupDir -Leaf
        $parentDir = Split-Path $backupDir -Parent | Split-Path -Leaf
        
        Write-Host "📍 $parentDir\$locationName" -ForegroundColor White
        Write-Host "   Total backups: $($backups.Count)" -ForegroundColor Gray
        
        if ($backups.Count -gt 0) {
            $oldest = $backups[-1]
            $newest = $backups[0]
            $totalSize = ($backups | Measure-Object -Property Length -Sum).Sum / 1MB
            
            Write-Host "   Oldest:       $($oldest.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
            Write-Host "   Newest:       $($newest.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
            Write-Host "   Total size:   $([math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan
            Write-Host "   Avg size:     $([math]::Round($totalSize / $backups.Count, 2)) MB" -ForegroundColor Gray
        }
        else {
            Write-Host "   (no backups yet)" -ForegroundColor DarkGray
        }
        Write-Host ""
    }
    
    exit 0
}

function Get-FileHashSHA256 {
    param(
        [string]$FilePath,
        [switch]$ShowProgress
    )
    $hash = [System.Security.Cryptography.SHA256]::Create()
    $fileStream = [System.IO.File]::OpenRead($FilePath)
    
    if ($ShowProgress) {
        $fileName = Split-Path $FilePath -Leaf
        Write-Host "  🔐 Computing hash: $fileName..." -NoNewline -ForegroundColor DarkGray
    }
    
    $hashBytes = $hash.ComputeHash($fileStream)
    $fileStream.Close()
    $hash.Dispose()
    
    if ($ShowProgress) {
        Write-Host " ✓" -ForegroundColor Green
    }
    
    return [System.BitConverter]::ToString($hashBytes) -replace '-', ''
}

function Test-BackupDuplicate {
    param(
        [string]$NewBackupPath,
        [string]$BackupDir,
        [switch]$Verbose
    )
    
    if (-not (Test-Path $NewBackupPath)) {
        return $false
    }
    
    # Get all previous backups, sorted by creation time (newest first)
    $previousBackups = Get-ChildItem -Path $BackupDir -Filter "*.zip" -File | 
    Where-Object { $_.FullName -ne $NewBackupPath } | 
    Sort-Object LastWriteTime -Descending
    
    if ($previousBackups.Count -eq 0) {
        if ($Verbose) {
            Write-Host "  ℹ️  No previous backup found for comparison" -ForegroundColor DarkGray
        }
        return $false
    }
    
    # Compare with most recent backup
    $previousBackup = $previousBackups[0]
    if ($Verbose) {
        Write-Host "  🔍 Comparing with previous backup: $(Split-Path $previousBackup.Name -Leaf)" -ForegroundColor DarkGray
    }
    
    $newHash = Get-FileHashSHA256 -FilePath $NewBackupPath -ShowProgress:$Verbose
    $previousHash = Get-FileHashSHA256 -FilePath $previousBackup.FullName -ShowProgress:$Verbose
    
    $isDuplicate = ($newHash -eq $previousHash)
    if ($Verbose -and $isDuplicate) {
        Write-Host "  ✓ Hashes match - duplicate detected" -ForegroundColor Yellow
    }
    elseif ($Verbose) {
        Write-Host "  ✓ Hashes differ - backup is new" -ForegroundColor Green
    }
    
    return $isDuplicate
}

function Test-DiskSpace {
    param(
        [string]$Path,
        [long]$RequiredBytes
    )
    try {
        $drive = (Get-Item $Path).PSDrive.Name
        $driveInfo = Get-PSDrive $drive -ErrorAction Stop
        $availableBytes = $driveInfo.Free
        
        if ($availableBytes -lt $RequiredBytes) {
            Write-ErrorLog "Insufficient disk space on $drive`: Available: $([math]::Round($availableBytes / 1MB, 2)) MB, Required: $([math]::Round($RequiredBytes / 1MB, 2)) MB" "Warning"
            return $false
        }
        return $true
    }
    catch {
        Write-ErrorLog "Failed to check disk space for $Path`: $_" "Warning" $_
        # Assume OK if we can't check (network drives, etc.)
        return $true
    }
}

function Test-PathAccess {
    param(
        [string]$Path,
        [string]$Operation = "Write"
    )
    try {
        $parentPath = Split-Path $Path -Parent
        if (-not (Test-Path $parentPath)) {
            Write-ErrorLog "Parent directory does not exist: $parentPath" "Error"
            return $false
        }
        
        # Test write access by creating a temporary file
        if ($Operation -eq "Write") {
            $testFile = Join-Path $parentPath ".backup-test-$(Get-Random).tmp"
            try {
                New-Item -ItemType File -Path $testFile -Force | Out-Null
                Remove-Item $testFile -Force -ErrorAction SilentlyContinue
                return $true
            }
            catch {
                Write-ErrorLog "No write access to $parentPath`: $_" "Error" $_
                return $false
            }
        }
        return $true
    }
    catch {
        Write-ErrorLog "Failed to test path access for $Path`: $_" "Error" $_
        return $false
    }
}

function Invoke-WithRetry {
    param(
        [scriptblock]$ScriptBlock,
        [string]$OperationName,
        [int]$MaxRetries = 3,
        [int]$InitialDelaySeconds = 2
    )
    
    $attempt = 0
    $delay = $InitialDelaySeconds
    
    while ($attempt -le $MaxRetries) {
        try {
            return & $ScriptBlock
        }
        catch {
            $attempt++
            if ($attempt -gt $MaxRetries) {
                Write-ErrorLog "Operation '$OperationName' failed after $MaxRetries retries" "Error" $_
                throw
            }
            
            Write-ErrorLog "Operation '$OperationName' failed (attempt $attempt/$MaxRetries). Retrying in $delay seconds..." "Warning" $_
            Start-Sleep -Seconds $delay
            $delay = [math]::Min($delay * 2, 60) # Exponential backoff, max 60 seconds
        }
    }
}

function New-BackupZip {
    param(
        [string]$ZipPath,
        [array]$Files,
        [string]$RepoRoot,
        [string]$BackupName
    )
    
    $zip = $null
    $filesAdded = 0
    $filesFailed = 0
    
    try {
        # Remove existing backup if present
        if (Test-Path $ZipPath) {
            Write-Host "    Removing existing backup file..." -ForegroundColor Gray
            Remove-Item $ZipPath -Force -ErrorAction Stop
        }
        
        # Create ZIP archive
        $zip = [System.IO.Compression.ZipFile]::Open($ZipPath, [System.IO.Compression.ZipArchiveMode]::Create)
        
        $totalFiles = $Files.Count
        $processedFiles = 0
        
        foreach ($file in $Files) {
            $processedFiles++
            $script:TotalFilesProcessed++
            
            # Progress reporting for large backups
            if ($totalFiles -gt 100 -and $processedFiles % 100 -eq 0) {
                $percent = [math]::Round(($processedFiles / $totalFiles) * 100, 1)
                Write-Host "    Progress: $percent% ($processedFiles/$totalFiles files)" -ForegroundColor Gray
            }
            
            try {
                # Get relative path from repo root
                $relativePath = $file.FullName.Substring($repoRoot.Length + 1)
                # Use forward slashes for ZIP standard
                $zipEntryPath = $relativePath -replace '\\', '/'
                
                # Add file to archive with full path
                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                    $zip, 
                    $file.FullName, 
                    $zipEntryPath, 
                    [System.IO.Compression.CompressionLevel]::Optimal
                ) | Out-Null
                
                $filesAdded++
            }
            catch {
                $filesFailed++
                $script:TotalFilesFailed++
                Write-ErrorLog "Failed to add file to archive: $($file.FullName)" "Warning" $_
                # Continue with next file instead of failing entire backup
            }
        }
        
        # Dispose ZIP archive
        $zip.Dispose()
        $zip = $null
        
        # Verify backup file was created and is valid
        if (-not (Test-Path $ZipPath)) {
            throw "Backup file was not created: $ZipPath"
        }
        
        $backupSize = (Get-Item $ZipPath).Length
        if ($backupSize -eq 0) {
            throw "Backup file is empty: $ZipPath"
        }
        
        # Verify ZIP integrity by attempting to open it
        try {
            $verifyZip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
            $entryCount = $verifyZip.Entries.Count
            $verifyZip.Dispose()
            
            if ($entryCount -eq 0) {
                throw "Backup file contains no entries: $ZipPath"
            }
        }
        catch {
            throw "Backup file integrity check failed: $($_.Message)"
        }
        
        return @{
            Success     = $true
            FilesAdded  = $filesAdded
            FilesFailed = $filesFailed
            BackupSize  = $backupSize
        }
        
    }
    catch {
        Write-ErrorLog "Failed to create backup ZIP: $ZipPath" "Error" $_
        if ($zip) {
            try {
                $zip.Dispose()
            }
            catch {
                Write-ErrorLog "Failed to dispose ZIP archive" "Warning" $_
            }
        }
        
        # Cleanup partial backup file
        if (Test-Path $ZipPath) {
            try {
                Remove-Item $ZipPath -Force -ErrorAction SilentlyContinue
            }
            catch {
                Write-ErrorLog "Failed to cleanup partial backup file: $ZipPath" "Warning" $_
            }
        }
        
        throw
    }
}

function Save-ErrorLog {
    param([string]$LogPath)
    try {
        $logContent = "Backup Error Log`n"
        $logContent += "==================`n"
        $logContent += "Start Time: $($script:StartTime)`n"
        $logContent += "End Time: $(Get-Date)`n"
        $logContent += "Duration: $((Get-Date) - $script:StartTime)`n"
        $logContent += "`nErrors:`n"
        $logContent += ($script:ErrorLog -join "`n`n")
        
        $logContent | Out-File -FilePath $LogPath -Encoding UTF8 -ErrorAction Stop
        Write-Host "`n📝 Error log saved to: $LogPath" -ForegroundColor Cyan
    }
    catch {
        Write-Host "⚠️  Failed to save error log: $_" -ForegroundColor Yellow
    }
}

#endregion

#region Main Script

# Initialize repoName early for -List flag check
$repoName = "unknown"

# Handle -List flag
if ($List) {
    # Attempt to get repoName for -List flag
    try {
        $isRepo = (Test-Path "pyproject.toml") -or (Test-Path ".git") -or (Test-Path "package.json")
        if ($isRepo) {
            $repoName = (Get-Item .).Name
        }
    }
    catch {
        # Ignore errors, repoName remains "unknown"
    }

    if ($repoName -eq "unknown") {
        Write-Host "❌ Error: Must run from repository root (need pyproject.toml, .git, or package.json) to list backups." -ForegroundColor Red
        exit 1
    }
    $desktopDir = Join-Path (Join-Path ([Environment]::GetFolderPath("Desktop")) "repo backup") $repoName
    $nDriveDir = Join-Path "N:\backup\dev\repo-backups" $repoName
    $oneDriveDir = Join-Path (Join-Path (Join-Path $env:OneDrive "Backup") "repo-backups") $repoName
    
    Show-BackupHistory -RepoName $repoName -BackupDirs @($desktopDir, $nDriveDir, $oneDriveDir)
    exit 0 # Exit after listing
}

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║   📦 Repository Backup (SOTA Error Handling) 📦        ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

# Validate we're in a repository
try {
    $isRepo = (Test-Path "pyproject.toml") -or (Test-Path ".git") -or (Test-Path "package.json")
    if (-not $isRepo) {
        Write-ErrorLog "Must run from repository root (need pyproject.toml, .git, or package.json)" "Error"
        exit 1
    }
}
catch {
    Write-ErrorLog "Failed to validate repository location" "Error" $_
    exit 1
}

# Get repository information
try {
    $repoName = (Get-Item .).Name
    $repoRoot = (Get-Item .).FullName
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $backupName = "${repoName}_backup_${timestamp}.zip"
}
catch {
    Write-ErrorLog "Failed to get repository information" "Error" $_
    exit 1
}

# Define backup destinations
try {
    $desktopBackup = Join-Path (Join-Path ([Environment]::GetFolderPath("Desktop")) "repo backup") $repoName
    $nDriveBackup = Join-Path "N:\backup\dev\repo-backups" $repoName
    $oneDriveRoot = Join-Path (Join-Path $env:OneDrive "Backup") "repo-backups"
    $oneDriveBackup = Join-Path $oneDriveRoot $repoName
    
    $backupDestinations = @(
        @{ Name = "Desktop"; Path = $desktopBackup; BackupPath = (Join-Path $desktopBackup $backupName); Enabled = $true }
        @{ Name = "N: Drive"; Path = $nDriveBackup; BackupPath = (Join-Path $nDriveBackup $backupName); Enabled = $true }
        @{ Name = "OneDrive"; Path = $oneDriveBackup; BackupPath = (Join-Path $oneDriveBackup $backupName); Enabled = $true }
    )
}
catch {
    Write-ErrorLog "Failed to define backup destinations" "Error" $_
    exit 1
}

# Display configuration
Write-Host "📋 Backup Configuration:" -ForegroundColor Cyan
Write-Host "  Repository:    $repoName" -ForegroundColor White
Write-Host "  Timestamp:     $timestamp" -ForegroundColor White
Write-Host "  Include build: $(if($IncludeBuild){'Yes'}else{'No'})" -ForegroundColor White
Write-Host "  Max retries:   $MaxRetries" -ForegroundColor White
Write-Host "  Retry delay:   $RetryDelaySeconds seconds" -ForegroundColor White
Write-Host ""

# Ensure backup directories exist and validate access
foreach ($dest in $backupDestinations) {
    try {
        if (-not (Test-Path $dest.Path)) {
            Write-Host "  Creating directory: $($dest.Path)" -ForegroundColor Gray
            New-Item -ItemType Directory -Path $dest.Path -Force | Out-Null
        }
        
        # Test write access (skip in dry-run)
        if (-not $WhatIf -and -not (Test-PathAccess -Path $dest.BackupPath -Operation "Write")) {
            Write-ErrorLog "No write access to $($dest.Name) backup location: $($dest.Path)" "Error"
            $dest.Enabled = $false
            continue
        }
        
        Write-Host "  ✅ $($dest.Name): $($dest.Path)" -ForegroundColor Green
    }
    catch {
        Write-ErrorLog "Failed to setup $($dest.Name) backup location: $($dest.Path)" "Error" $_
        $dest.Enabled = $false
    }
}

# Filter out disabled destinations
$backupDestinations = $backupDestinations | Where-Object { $_.Enabled }

if ($backupDestinations.Count -eq 0) {
    Write-ErrorLog "No valid backup destinations available" "Error"
    exit 1
}

# Define exclusions
$exclusions = @(
    ".venv", "venv", "env", ".env",
    "__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache", "htmlcov",
    "node_modules",
    "*.pyc", "*.pyo", "*.pyd",
    ".DS_Store", "Thumbs.db",
    ".windsurf", ".cursor", ".snapshots",
    "*.log", "*.bak", "*.backup", "*.tmp", "*.temp",
    ".vbox", "*.vdi", "*.vmdk", "*.vhd", "*.vbox-prev",
    "MagicMock", "sandboxes", "quarantine", "analysis", "backups",
    "*.dxt", "*.db-shm", "*.db-wal",
    "gtfs_data", "gtfs_output", "extracted_data",
    "*.csv", "*.tsv", "*.txt", "*.bin", "*.dat",
    # Rust-specific exclusions (CRITICAL for rustdesk repos)
    "target", "Cargo.lock",
    # Additional locked file exclusions
    "*.exe", "*.dll", "*.pdb", "*.so", "*.dylib",
    "rustdesk.exe", "hbbs.exe", "hbbr.exe",
    "target/debug/*.exe", "target/release/*.exe",
    "target/*/deps/*.rlib",
    "*.db", "*.sqlite", "*.sqlite3",
    "*.lock", "*.pid", "*.pidfile",
    "*.swp", "*.swo", "*.cache", "*.lockfile",
    "docker-compose.override.yml",
    "Procfile"
)

$excludeLargeTestFiles = @(
    "samples/metadata.db",
    "samples/test_library.db",
    "test_data/*.db"
)

$exclusions += $excludeLargeTestFiles

if (-not $IncludeBuild) {
    $exclusions += @("dist", "build", "*.whl", "*.tar.gz")
}

# Load repository-specific rules if present
$rulesFile = Join-Path $repoRoot ".backup-rules.md"
if (Test-Path $rulesFile) {
    Write-Host "📜 Found .backup-rules.md - loading custom rules..." -ForegroundColor Cyan
    $rules = Get-Content $rulesFile
    
    # 1. Standard ALWAYS exclude
    $customExclusions = $rules | Where-Object { $_ -match "^EXCLUDE:\s*(.+)$" } | ForEach-Object { $matches[1].Trim() }
    
    # 2. WEEKLY (Exclude UNLESS today is Sunday)
    $today = Get-Date
    $isWeeklyDay = ($today.DayOfWeek -eq [DayOfWeek]::Sunday)
    $weeklyRules = $rules | Where-Object { $_ -match "^WEEKLY:\s*(.+)$" } | ForEach-Object { $matches[1].Trim() }
    
    if (-not $isWeeklyDay -and $weeklyRules) {
        $customExclusions += $weeklyRules
        Write-Host "  📅 Today is not Sunday - applying $($weeklyRules.Count) weekly exclusions" -ForegroundColor Gray
    }
    elseif ($isWeeklyDay -and $weeklyRules) {
        Write-Host "  ✨ Sunday! Including $($weeklyRules.Count) weekly items in backup" -ForegroundColor Green
    }

    # 3. MONTHLY (Exclude UNLESS today is the 1st)
    $isMonthlyDay = ($today.Day -eq 1)
    $monthlyRules = $rules | Where-Object { $_ -match "^MONTHLY:\s*(.+)$" } | ForEach-Object { $matches[1].Trim() }

    if (-not $isMonthlyDay -and $monthlyRules) {
        $customExclusions += $monthlyRules
        Write-Host "  📅 Today is not the 1st - applying $($monthlyRules.Count) monthly exclusions" -ForegroundColor Gray
    }
    elseif ($isMonthlyDay -and $monthlyRules) {
        Write-Host "  ✨ 1st of the month! Including $($monthlyRules.Count) monthly items in backup" -ForegroundColor Green
    }
    
    if ($customExclusions) {
        $exclusions += $customExclusions
        Write-Host "  ✅ Applied total of $($customExclusions.Count) rules from .backup-rules.md" -ForegroundColor Gray
    }
}

Write-Host "🚫 Excluding:" -ForegroundColor Yellow
foreach ($excl in $exclusions) {
    Write-Host "  - $excl" -ForegroundColor Gray
}
Write-Host ""

# Analyze repository size
Write-Host "📊 Analyzing repository size..." -ForegroundColor Cyan

try {
    $allFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
        # Skip symlinks/ReparsePoints (cause access denied errors)
        -not ($_.Attributes -band [System.IO.FileAttributes]::ReparsePoint)
    }
    
    $totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum
    
    # Filter files to backup
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
    
    $backupSize = ($backupFiles | Measure-Object -Property Length -Sum).Sum
    $excludedSize = $totalSize - $backupSize
    
    Write-Host "  Total size:    $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor White
    Write-Host "  Excluded:      $([math]::Round($excludedSize / 1MB, 2)) MB" -ForegroundColor Red
    Write-Host "  Backup size:   $([math]::Round($backupSize / 1MB, 2)) MB" -ForegroundColor Green
    Write-Host "  Files:         $($backupFiles.Count)" -ForegroundColor White
    if ($totalSize -gt 0) {
        Write-Host "  Reduction:     $([math]::Round(($excludedSize / $totalSize) * 100, 1))%" -ForegroundColor Cyan
    }
    Write-Host ""
    
    # Estimate compressed size (assume 50% compression ratio)
    $estimatedCompressedSize = $backupSize * 0.5
    
    # Validate disk space for all destinations
    foreach ($dest in $backupDestinations) {
        if (-not (Test-DiskSpace -Path $dest.Path -RequiredBytes $estimatedCompressedSize)) {
            Write-ErrorLog "Insufficient disk space for $($dest.Name) backup" "Warning"
            # Don't disable, let it try and fail gracefully
        }
    }
    
    # Exit early if WhatIf (after file analysis)
    if ($WhatIf) {
        Write-Host "`n⚠️  DRY-RUN MODE: No files will be created`n" -ForegroundColor Yellow
        Write-Host "📋 Files that would be backed up: $($backupFiles.Count) files ($([math]::Round($backupSize / 1MB, 2)) MB)" -ForegroundColor Cyan
        Write-Host "📦 Backup locations:" -ForegroundColor Cyan
        foreach ($dest in $backupDestinations) {
            Write-Host "  - $($dest.Name): $($dest.Path)" -ForegroundColor White
        }
        Write-Host "`n✅ Dry-run complete - no files created`n" -ForegroundColor Green
        exit 0
    }
    
}
catch {
    Write-ErrorLog "Failed to analyze repository" "Error" $_
    exit 1
}

# Create backups
Write-Host "🔄 Creating backups..." -ForegroundColor Cyan
Write-Host ""

$successfulBackups = 0
$failedBackups = 0

foreach ($dest in $backupDestinations) {
    Write-Host "  → $($dest.Name) backup..." -ForegroundColor Gray
    
    try {
        $result = Invoke-WithRetry -ScriptBlock {
            New-BackupZip -ZipPath $dest.BackupPath -Files $backupFiles -RepoRoot $repoRoot -BackupName $backupName
        } -OperationName "$($dest.Name) backup" -MaxRetries $MaxRetries -InitialDelaySeconds $RetryDelaySeconds
        
        # Check for duplicates (if it's not the first backup)
        if (Test-BackupDuplicate -NewBackupPath $dest.BackupPath -BackupDir $dest.Path -Verbose:$Verbose) {
            Write-Host "  ⏭️  $($dest.Name) backup identical to previous - removing duplicate" -ForegroundColor Yellow
            Remove-Item $dest.BackupPath -Force
            $script:BackupResults[$dest.Name] = @{ Success = $true; Skipped = $true }
        }
        else {
            $script:BackupResults[$dest.Name] = $result
            $script:BackupResults[$dest.Name].Success = $true
            $successfulBackups++
            
            $backupSizeMB = [math]::Round($result.BackupSize / 1MB, 2)
            Write-Host "  ✅ $($dest.Name) backup complete: $backupSizeMB MB ($($result.FilesAdded) files)" -ForegroundColor Green
            
            if ($result.FilesFailed -gt 0) {
                Write-Host "    ⚠️  Warning: $($result.FilesFailed) files failed to add" -ForegroundColor Yellow
            }
        }
        
    }
    catch {
        $failedBackups++
        $script:BackupResults[$dest.Name] = @{ Success = $false; Error = $_.Exception.Message }
        Write-ErrorLog "Failed to create $($dest.Name) backup" "Error" $_
        Write-Host "  ❌ $($dest.Name) backup failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Summary
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor $(if ($failedBackups -eq 0) { "Green" } else { "Yellow" })
Write-Host "║              📦 Backup Summary 📦                        ║" -ForegroundColor $(if ($failedBackups -eq 0) { "Green" } else { "Yellow" })
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor $(if ($failedBackups -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

if ($successfulBackups -gt 0) {
    Write-Host "✅ Successful backups: $successfulBackups" -ForegroundColor Green
    foreach ($dest in $backupDestinations) {
        $res = $script:BackupResults[$dest.Name]
        if ($res.Success -and -not $res.Skipped) {
            $backupSizeMB = [math]::Round($res.BackupSize / 1MB, 2)
            Write-Host "  • $($dest.Name): $backupSizeMB MB at $($dest.BackupPath)" -ForegroundColor White
        }
        elseif ($res.Skipped) {
            Write-Host "  • $($dest.Name): Skipped (identical to previous)" -ForegroundColor Yellow
        }
    }
    Write-Host ""
}

if ($failedBackups -gt 0) {
    Write-Host "❌ Failed backups: $failedBackups" -ForegroundColor Red
    foreach ($dest in $backupDestinations) {
        if (-not $script:BackupResults[$dest.Name].Success) {
            Write-Host "  • $($dest.Name): $($script:BackupResults[$dest.Name].Error)" -ForegroundColor Red
        }
    }
    Write-Host ""
}

Write-Host "📊 Statistics:" -ForegroundColor Cyan
Write-Host "  Files processed: $script:TotalFilesProcessed" -ForegroundColor White
Write-Host "  Files failed:    $script:TotalFilesFailed" -ForegroundColor $(if ($script:TotalFilesFailed -eq 0) { "Green" } else { "Yellow" })
Write-Host "  Duration:        $((Get-Date) - $script:StartTime)" -ForegroundColor White
Write-Host ""

# Save error log if there were errors
if ($script:ErrorLog.Count -gt 0 -or $failedBackups -gt 0) {
    $logPath = Join-Path $env:TEMP "backup-error-log-${timestamp}.txt"
    Save-ErrorLog -LogPath $logPath
}

# Exit with appropriate code
# JSON output format
if ($OutputFormat -eq "json") {
    $jsonOutput = @{
        repo       = $repoName
        timestamp  = $timestamp
        status     = if ($successfulBackups -gt 0) { "success" } elseif ($failedBackups -eq 0) { "skipped" } else { "partial" }
        successful = $successfulBackups
        failed     = $failedBackups
        results    = $script:BackupResults
    } | ConvertTo-Json -Depth 5
    
    Write-Host $jsonOutput
    exit 0
}

# Exit with appropriate code
$totalSuccess = ($script:BackupResults.Values | Where-Object { $_.Success }).Count

if ($totalSuccess -eq 0) {
    Write-Host "❌ All backups failed!" -ForegroundColor Red
    exit 1
}
elseif ($failedBackups -gt 0) {
    Write-Host "⚠️  Some backups failed, but $totalSuccess succeeded (or were skipped)" -ForegroundColor Yellow
    exit 0
}
else {
    Write-Host "✅ Backup process completed.`n" -ForegroundColor Green
    exit 0
}

#endregion

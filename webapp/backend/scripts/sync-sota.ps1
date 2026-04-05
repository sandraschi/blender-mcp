#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Sync repository scripts with SOTA versions in mcp-central-docs
    
.DESCRIPTION
    Pulls standard SOTA scripts (backup, standards, etc.) from the central 
    mcp-central-docs repository if it exists as a sibling.
    
.EXAMPLE
    .\scripts\sync-sota.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        🔄 SOTA Script Synchronization (Spoke) 🔄        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# 1. Locate the Hub (mcp-central-docs)
$currentRepoRoot = Join-Path $PSScriptRoot ".."
$siblingHubPath = Join-Path $currentRepoRoot "..\mcp-central-docs"

if (-not (Test-Path $siblingHubPath)) {
    Write-Host "❌ Error: Could not find mcp-central-docs sibling directory at:" -ForegroundColor Red
    Write-Host "   $siblingHubPath" -ForegroundColor Gray
    Write-Host "`n   Please ensure mcp-central-docs is cloned in the same parent folder." -ForegroundColor Yellow
    exit 1
}

Write-Host "📍 Found Hub: $siblingHubPath" -ForegroundColor Gray

# 2. Define standard SOTA scripts mapping [Source in Hub -> Target in Spoke]
$sotaMapping = @(
    @{
        Source = Join-Path $siblingHubPath "sota-scripts\backup-system\backup-repo.ps1"
        Target = Join-Path $PSScriptRoot "backup-repo.ps1"
    },
    @{
        Source = Join-Path $siblingHubPath "sota-scripts\repo-standards\check-repo-standards.ps1"
        Target = Join-Path $PSScriptRoot "check-repo-standards.ps1"
    }
)

$updated = 0
$skipped = 0

# 3. Perform Sync
foreach ($mapping in $sotaMapping) {
    if (-not (Test-Path $mapping.Source)) {
        Write-Host "⚠️  Warning: SOTA source not found: $($mapping.Source)" -ForegroundColor Yellow
        continue
    }

    $sourceHash = (Get-FileHash $mapping.Source -Algorithm SHA256).Hash
    
    if (Test-Path $mapping.Target) {
        $targetHash = (Get-FileHash $mapping.Target -Algorithm SHA256).Hash
        
        if ($sourceHash -eq $targetHash) {
            Write-Host "  ⏭️  $(Split-Path $mapping.Target -Leaf) is already up-to-date." -ForegroundColor Gray
            $skipped++
        }
        else {
            Copy-Item $mapping.Source $mapping.Target -Force
            Write-Host "  ✅ Updated $(Split-Path $mapping.Target -Leaf) to latest SOTA." -ForegroundColor Green
            $updated++
        }
    }
    else {
        Copy-Item $mapping.Source $mapping.Target -Force
        Write-Host "  ✨ Installed $(Split-Path $mapping.Target -Leaf) from SOTA." -ForegroundColor Cyan
        $updated++
    }
}

Write-Host "`n📊 Sync Summary: $updated updated, $skipped skipped.`n" -ForegroundColor White

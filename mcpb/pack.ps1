#Requires -Version 7
<#
.SYNOPSIS
Build this repo's .mcpb bundle for Claude Desktop.

Implements the mandatory pipeline from MCPB_PACKAGING_STANDARDS.md section 2.5:
wipe + fresh-copy src -> mcpb/src (never edit the staged copy by hand), ensure
mcpb/.mcpbignore exists (the mcpb CLI reads .mcpbignore from the pack root,
not the repo root), run the required mechanical checks, then pack.

mcpb/src is a build artifact -- regenerated every run, gitignored, never
committed. This script deletes and recreates it each time.

Package name and entry point are read from this repo's own pyproject.toml /
mcpb/manifest.json -- nothing here is hardcoded to a specific repo, so the
same script works unmodified across the fleet.
#>
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$McpbDir = Join-Path $RepoRoot 'mcpb'
$ManifestPath = Join-Path $McpbDir 'manifest.json'
if (-not (Test-Path $ManifestPath)) { throw "No mcpb/manifest.json in $RepoRoot -- cannot pack." }
$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json

function Step($n, $msg) { Write-Host "== $n. $msg ==" -ForegroundColor Cyan }

Step 0 'Detect package name'
$Pkg = $null
$pyprojPath = Join-Path $RepoRoot 'pyproject.toml'
if (Test-Path $pyprojPath) {
    $m = [regex]::Match((Get-Content $pyprojPath -Raw), '(?m)^\s*name\s*=\s*"([^"]+)"')
    if ($m.Success) { $Pkg = $m.Groups[1].Value -replace '-', '_' }
}
if (-not $Pkg) {
    $srcDirs = Get-ChildItem (Join-Path $RepoRoot 'src') -Directory -ErrorAction SilentlyContinue
    if ($srcDirs.Count -eq 1) { $Pkg = $srcDirs[0].Name }
}
if (-not $Pkg) { throw 'Could not detect package name from pyproject.toml or a single src/<pkg>/ directory.' }
Write-Host "  package: $Pkg"

$SrcPkg = Join-Path $RepoRoot "src\$Pkg"
$StageRoot = Join-Path $McpbDir 'src'
$StagePkg = Join-Path $StageRoot $Pkg
$VerifyScript = Join-Path $McpbDir 'verify_pack.py'

# Entry point comes from this repo's own manifest.json -- whatever it already
# declares. Fixing a wrong entry_point is a per-repo judgment call, out of
# scope for this generic template; if it's wrong, the checks below will
# legitimately fail and say so.
$entryPointRel = $manifest.server.entry_point
if (-not $entryPointRel) { throw 'manifest.json has no server.entry_point.' }
$entryFile = Join-Path $RepoRoot $entryPointRel
$entryRelToSrc = [System.IO.Path]::GetRelativePath((Join-Path $RepoRoot 'src'), $entryFile)
$entryModule = ($entryRelToSrc -replace '\.py$', '') -replace '[\\/]', '.'

Step 1 'Wipe + fresh-copy src -> mcpb/src (never a stale/hand-edited stage)'
if (Test-Path $StageRoot) { Remove-Item -Recurse -Force $StageRoot }
if (-not (Test-Path $SrcPkg)) { throw "Copy source missing: $SrcPkg" }
New-Item -ItemType Directory -Force -Path $StageRoot | Out-Null
Copy-Item -Recurse -Force $SrcPkg $StagePkg
Write-Host "  copied $SrcPkg -> $StagePkg"

Step 2 'Strip pollution from the fresh stage'
Get-ChildItem -Recurse -Path $StageRoot -Include '__pycache__' -Directory -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Path $StageRoot -Include '*.pyc', '*.bak', '*.bak.*', '*.bak-*', '*.orig', '*.rej' -File -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue

Step 3 'Sync mcpb/.mcpbignore from repo root (pack root, not repo root, is what mcpb reads)'
$McpbIgnore = Join-Path $McpbDir '.mcpbignore'
$RootIgnore = Join-Path $RepoRoot '.mcpbignore'
if (Test-Path $RootIgnore) {
    Copy-Item $RootIgnore $McpbIgnore -Force
    Write-Host '  synced repo-root .mcpbignore -> mcpb/.mcpbignore'
} elseif (-not (Test-Path $McpbIgnore)) {
    throw 'No .mcpbignore at repo root or mcpb/ -- cannot pack safely.'
}

Step 4 'Required check: import isolation (only mcpb/src on sys.path)'
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --project $RepoRoot python $VerifyScript import $StageRoot $entryModule
if ($LASTEXITCODE -ne 0) { throw 'Import-isolation check failed' }

Step 5 'Required check: AST call-site binding (catches missing imports)'
$stagedEntryFile = Join-Path $StageRoot ($entryRelToSrc)
uv run --project $RepoRoot python $VerifyScript ast $stagedEntryFile
if ($LASTEXITCODE -ne 0) { throw 'AST check failed' }
Remove-Item Env:\PYTHONDONTWRITEBYTECODE -ErrorAction SilentlyContinue

Step 6 'Required check: pollution, run AFTER import (which itself writes bytecode)'
uv run --project $RepoRoot python $VerifyScript pollution $McpbDir
if ($LASTEXITCODE -ne 0) { throw 'Pollution check failed (import step above may have written __pycache__)' }

Step 7 '3-4-100 prompt check (report only -- does not block pack)'
$sysWords = 0; $userWords = 0; $exCount = 0
$sysPath = Join-Path $McpbDir 'assets/prompts/system.md'
$userPath = Join-Path $McpbDir 'assets/prompts/user.md'
$exPath = Join-Path $McpbDir 'assets/prompts/examples.json'
if (Test-Path $sysPath) { $sysWords = ((Get-Content -Raw $sysPath) -split '\s+' | Where-Object { $_ }).Count }
if (Test-Path $userPath) { $userWords = ((Get-Content -Raw $userPath) -split '\s+' | Where-Object { $_ }).Count }
if (Test-Path $exPath) { $exCount = (Get-Content -Raw $exPath | ConvertFrom-Json -ErrorAction SilentlyContinue).Count }
if ($sysWords -lt 3000 -or $userWords -lt 4000 -or $exCount -lt 100) {
    Write-Warning "3-4-100 FAIL (non-blocking): system.md=$sysWords/3000 user.md=$userWords/4000 examples.json=$exCount/100 -- runt package per MCPB_PACKAGING_STANDARDS.md 2.3b"
} else {
    Write-Host "  OK: system.md=$sysWords user.md=$userWords examples.json=$exCount"
}

Step 8 'mcpb pack'
$OutDir = Join-Path $RepoRoot 'dist'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$OutFile = Join-Path $OutDir "$Pkg-v$($manifest.version).mcpb"
if (Test-Path $OutFile) { Remove-Item -Force $OutFile }
bunx @anthropic-ai/mcpb pack $McpbDir $OutFile
if ($LASTEXITCODE -ne 0) { throw 'mcpb pack failed' }

Step 9 'Verify pack output'
if (-not (Test-Path $OutFile)) { throw "Pack did not produce $OutFile" }
$size = (Get-Item $OutFile).Length
Write-Host "  built: $OutFile ($([math]::Round($size / 1kb, 1)) KB)"
bunx @anthropic-ai/mcpb info $OutFile
if ($LASTEXITCODE -ne 0) { throw 'mcpb info failed on the freshly-built bundle' }

Step 10 'Clean up staging copy (derived, regenerable, never committed)'
Remove-Item -Recurse -Force $StageRoot

Write-Host "Done: $OutFile" -ForegroundColor Green

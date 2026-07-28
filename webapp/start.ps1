# Fleet unified launcher - do not edit logic here.
# Change fleet-start.config.ps1 at the repo root instead.
param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser,
    [switch]$ReuseIfRunning
)

$ErrorActionPreference = 'Stop'
$ReposRoot = if ($env:FLEET_REPOS_ROOT) { $env:FLEET_REPOS_ROOT } else { 'D:\Dev\repos' }
$EnginePath = Join-Path $ReposRoot 'mcp-central-docs\scripts\Invoke-FleetWebappStart.ps1'
if (-not (Test-Path -LiteralPath $EnginePath)) {
    Write-Host "ERROR: Missing fleet start engine: $EnginePath" -ForegroundColor Red
    exit 1
}
. $EnginePath

$configCandidates = @(
    (Join-Path $PSScriptRoot 'fleet-start.config.ps1'),
    (Join-Path (Split-Path -Parent $PSScriptRoot) 'fleet-start.config.ps1')
)
$configPath = $null
foreach ($candidate in $configCandidates) {
    if (Test-Path -LiteralPath $candidate) {
        $configPath = $candidate
        break
    }
}
if (-not $configPath) {
    Write-Host 'ERROR: Missing fleet-start.config.ps1 (repo root or beside start.ps1).' -ForegroundColor Red
    exit 1
}

Start-FleetWebapp @PSBoundParameters -ConfigPath $configPath -LauncherRoot $PSScriptRoot


#Requires -Version 5.1
<#
.SYNOPSIS
One-line installer for blender-mcp.

.DESCRIPTION
  irm https://raw.githubusercontent.com/sandraschi/blender-mcp/main/install.ps1 | iex

Thin bootstrap: the logic lives at sandraschi/fleet-install so there is one copy to
maintain instead of one per repo. It detects every AI client (Claude Desktop, Cursor,
Antigravity, Windsurf, OpenCode, Claude Code), backs up each config, merges ONE entry
(never replaces the file), and is idempotent.

The stdio launch command is taken from mcpb/manifest.json (server.mcp_config) and is
PROVEN with a real initialize handshake before it is trusted; a stale manifest falls
back to [project.scripts]. An existing client alias for the repo is reused.

Registering the MCP server only. This does NOT build or serve the webapp (that is
start.ps1) and does NOT download or run a Tauri/NSIS desktop installer.

.PARAMETER Check
Diagnose only - writes nothing.

.PARAMETER DryRun
Show per-client changes without writing.

.PARAMETER Uninstall
Remove only the entry this installer owns.

.EXAMPLE
.\install.ps1 -Check
#>
[CmdletBinding()]
param(
    [switch]$Check,
    [switch]$DryRun,
    [switch]$Uninstall,
    [switch]$List,
    [switch]$Json,
    [switch]$Yes
)
$ErrorActionPreference = 'Stop'

$repoName = 'blender-mcp'
$installerUrl = 'https://raw.githubusercontent.com/sandraschi/fleet-install/main/install-fleet-mcp.ps1'
$writerUrl = 'https://raw.githubusercontent.com/sandraschi/fleet-install/main/install-mcp-clients.ps1'

$pass = @{}
foreach ($flag in 'Check', 'DryRun', 'Uninstall', 'List', 'Json', 'Yes') {
    if ((Get-Variable -Name $flag -ValueOnly)) { $pass[$flag] = $true }
}

# Vendored copy first (offline / installed app), then a local fleet checkout.
$installer = $null
if ($PSScriptRoot) {
    foreach ($candidate in @(
            (Join-Path $PSScriptRoot 'scripts\install-fleet-mcp.ps1'),
            (Join-Path $PSScriptRoot '..\fleet-install\install-fleet-mcp.ps1'),
            (Join-Path $PSScriptRoot '..\mcp-central-docs\scripts\install-fleet-mcp.ps1')
        )) {
        if (Test-Path -LiteralPath $candidate) { $installer = (Resolve-Path -LiteralPath $candidate).Path; break }
    }
}

if (-not $installer) {
    $cache = Join-Path $env:TEMP 'fleet-install'
    New-Item -ItemType Directory -Force -Path $cache | Out-Null
    $installer = Join-Path $cache 'install-fleet-mcp.ps1'
    $writerPath = Join-Path $cache 'install-mcp-clients.ps1'
    Invoke-WebRequest -Uri $installerUrl -OutFile $installer -UseBasicParsing
    Invoke-WebRequest -Uri $writerUrl -OutFile $writerPath -UseBasicParsing
}

& $installer -Repo $repoName @pass

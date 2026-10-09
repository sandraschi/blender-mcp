#Requires -Version 5.1
# Fleet shim - canonical pack logic lives in mcp-central-docs/scripts/fleet-mcpb-pack.ps1.
$ErrorActionPreference = 'Stop'
$ReposRoot = if ($env:FLEET_REPOS_ROOT) { $env:FLEET_REPOS_ROOT } else { 'D:\Dev\repos' }
& (Join-Path $ReposRoot 'mcp-central-docs\scripts\fleet-mcpb-pack.ps1') -RepoRoot (Split-Path -Parent $PSScriptRoot)

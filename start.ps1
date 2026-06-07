
# Fast port helpers (scripts/PortHelpers.ps1)
$__PortHelpers = Join-Path $PSScriptRoot 'scripts\PortHelpers.ps1'
if (Test-Path -LiteralPath $__PortHelpers) { . $__PortHelpers }
Param(     [switch]$Headless,     [switch]$BackendOnly,     [switch]$NoBrowser )  # --- SOTA Headless Standard 2026 --- if ($Headless -and ($Host.Name -ne 'ConsoleHost' -or -not (Get-Variable -Name "NoRelaunch" -ErrorAction SilentlyContinue))) {     $argList = @("-File", $PSCommandPath, "-NoRelaunch")     if ($BackendOnly) { $argList += "-BackendOnly" }     $argList += "-NoBrowser"     Start-Process pwsh.exe -ArgumentList $argList -WindowStyle Hidden     exit } # -----------------------------------  $ErrorActionPreference = "Stop" $RepoRoot = $PSScriptRoot  Write-Host "=== blender-mcp Industrial Startup ===" -ForegroundColor Cyan  # 1. Kill stale $WebPort = 10848 $BackendPort = 10849 foreach ($p in @($WebPort, $BackendPort)) {     $procIds = Get-PortListenerPidsFast -Port $port

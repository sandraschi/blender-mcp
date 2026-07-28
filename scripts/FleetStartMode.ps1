# FleetStartMode.ps1 - shared launch modes for webapp/start.ps1 launchers
# Vendored per-repo under scripts/FleetStartMode.ps1 (no mcp-central-docs runtime path).
# Port clearing uses per-port netstat+findstr (fast); never Get-NetTCPConnection or global python scan.

function Get-FleetStartModeBoundParameters {
    param([hashtable]$BoundParameters)

    $filtered = @{}
    foreach ($key in @('Headless', 'BackendOnly', 'FrontendOnly', 'NoBrowser')) {
        if ($BoundParameters.ContainsKey($key)) {
            $filtered[$key] = $BoundParameters[$key]
        }
    }
    return $filtered
}

function Initialize-FleetStartMode {
    param(
        [switch]$Headless,
        [switch]$BackendOnly,
        [switch]$FrontendOnly,
        [switch]$NoBrowser
    )

    if ($FrontendOnly -and $BackendOnly) {
        Write-Error "Cannot combine -FrontendOnly and -BackendOnly."
        exit 1
    }

    $runBackend = -not $FrontendOnly
    $probeRun = ($env:FLEET_PROBE_RUN -eq '1')
    # Interactive default: run frontend unless -BackendOnly or -Headless (probes may use -Headless + FLEET_PROBE_RUN).
    $runFrontend = (-not $BackendOnly) -and ($FrontendOnly -or (-not $Headless) -or $probeRun)
    # Match legacy start.ps1: only -NoBrowser, -Headless, and -BackendOnly suppress browser open.
    $skipBrowser = $NoBrowser -or $Headless -or $BackendOnly

    return [pscustomobject]@{
        RunBackend  = $runBackend
        RunFrontend = $runFrontend
        SkipBrowser = $skipBrowser
        WindowStyle = if ($Headless) { "Hidden" } else { "Normal" }
    }
}

function Enter-FleetHeadlessConsole {
    param(
        [switch]$Headless,
        [switch]$BackendOnly,
        [switch]$FrontendOnly,
        [string]$StartScriptPath = ''
    )

    if ($env:FLEET_PROBE_RUN -eq '1') { return }
    if (-not $Headless) { return }

    if ($Host.UI.RawUI.WindowTitle -match 'Hidden') { return }

    $scriptPath = $StartScriptPath
    if (-not $scriptPath) {
        Write-Host 'ERROR: Enter-FleetHeadlessConsole requires -StartScriptPath (repo start.ps1).' -ForegroundColor Red
        exit 1
    }
    if (-not (Test-Path -LiteralPath $scriptPath)) {
        Write-Host "ERROR: Headless launcher script not found: $scriptPath" -ForegroundColor Red
        exit 1
    }

    $spawnArgs = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $scriptPath,
        '-Headless'
    )
    if ($FrontendOnly) {
        $spawnArgs += '-FrontendOnly'
    } elseif ($BackendOnly) {
        $spawnArgs += '-BackendOnly'
    }
    Start-Process powershell.exe -ArgumentList $spawnArgs -WindowStyle Hidden
    exit
}

function Get-FleetPortListenerPids {
    param([Parameter(Mandatory)][int]$Port)

    $pids = [System.Collections.Generic.HashSet[int]]::new()
    # Port-scoped findstr: fast, and cmd may return Object[] (one line per element).
    $portNeedle = ":$Port "
    $raw = cmd /c "netstat -ano -p TCP 2>nul | findstr LISTENING | findstr `"$portNeedle`""
    if (-not $raw) { return @() }

    $lines = if ($raw -is [System.Array]) { @($raw) } else { @($raw -split "`r?`n") }
    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $parts = ($line.Trim() -split '\s+')
        if ($parts.Count -lt 5) { continue }
        $localAddr = $parts[1]
        if ($localAddr -notmatch ':(\d+)$') { continue }
        if ([int]$Matches[1] -ne $Port) { continue }
        $procId = 0
        if ([int]::TryParse($parts[-1], [ref]$procId) -and $procId -gt 4) {
            [void]$pids.Add($procId)
        }
    }
    return @($pids)
}

$script:FleetProtectedPidResults = @{}
$script:FleetServiceRootPids = $null
$script:FleetNssmServiceNames = $null

function Clear-FleetProtectedServicePidCache {
    $script:FleetProtectedPidResults = @{}
    $script:FleetServiceRootPids = $null
    $script:FleetNssmServiceNames = $null
}

function Get-FleetServiceRootProcessIds {
    if ($null -eq $script:FleetServiceRootPids) {
        $roots = [System.Collections.Generic.HashSet[int]]::new()
        foreach ($svc in @(Get-CimInstance Win32_Service -ErrorAction SilentlyContinue | Where-Object { $_.ProcessId -gt 4 })) {
            [void]$roots.Add($svc.ProcessId)
        }
        $script:FleetServiceRootPids = $roots
    }
    return $script:FleetServiceRootPids
}

function Get-FleetNssmServiceNames {
    if ($null -eq $script:FleetNssmServiceNames) {
        $script:FleetNssmServiceNames = @(
            Get-CimInstance Win32_Service -ErrorAction SilentlyContinue |
                Where-Object { $_.PathName -match 'nssm' } |
                ForEach-Object { $_.Name }
        )
    }
    return $script:FleetNssmServiceNames
}

function Test-FleetProcessProtectedByService {
    param([Parameter(Mandatory)][int]$ProcessId)

    if ($ProcessId -le 4) { return $false }
    if ($script:FleetProtectedPidResults.ContainsKey($ProcessId)) {
        return [bool]$script:FleetProtectedPidResults[$ProcessId]
    }

    $serviceRoots = Get-FleetServiceRootProcessIds
    $visited = [System.Collections.Generic.HashSet[int]]::new()
    $current = $ProcessId
    $protected = $false

    while ($current -gt 4 -and $visited.Add($current)) {
        if ($serviceRoots.Contains($current)) {
            $protected = $true
            break
        }
        $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$current" -ErrorAction SilentlyContinue
        if (-not $proc -or $proc.ParentProcessId -le 4) { break }
        $current = [int]$proc.ParentProcessId
    }

    $script:FleetProtectedPidResults[$ProcessId] = $protected
    return $protected
}

function Test-FleetPortHeldByService {
    param([Parameter(Mandatory)][int]$Port)

    foreach ($procId in @(Get-FleetPortListenerPids -Port $Port)) {
        if (Test-FleetProcessProtectedByService -ProcessId $procId) {
            return $true
        }
    }
    return $false
}

function Get-FleetPortsStillListening {
    param(
        [Parameter(Mandatory)][int[]]$Ports,
        [switch]$ExcludeProtectedServiceProcesses
    )

    $still = @{}
    foreach ($port in @($Ports | Where-Object { $_ -gt 0 } | Sort-Object -Unique)) {
        $pids = @(Get-FleetPortListenerPids -Port $port)
        if ($ExcludeProtectedServiceProcesses) {
            $pids = @($pids | Where-Object { -not (Test-FleetProcessProtectedByService -ProcessId $_) })
        }
        if ($pids.Count -gt 0) {
            $still[$port] = $pids
        }
    }
    return $still
}

function Get-FleetProcessBrief {
    param([Parameter(Mandatory)][int]$ProcessId)

    $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $proc) { return $null }

    $sessionId = $proc.SessionId
    try {
        $cim = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction SilentlyContinue
        if ($cim -and $null -ne $cim.SessionId) { $sessionId = [int]$cim.SessionId }
    } catch { }

    $parentId = 0
    try { $parentId = $proc.Parent.Id } catch { }

    return [pscustomobject]@{
        Id        = $ProcessId
        Name      = $proc.ProcessName
        SessionId = $sessionId
        ParentId  = $parentId
    }
}

function Test-FleetHttpOk {
    param(
        [Parameter(Mandatory)][string]$Url,
        [int]$TimeoutSec = 3
    )

    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec -ErrorAction Stop
        return ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500)
    } catch {
        return $false
    }
}

function Stop-FleetProcessId {
    param(
        [Parameter(Mandatory)][int]$ProcessId,
        [switch]$Elevated
    )

    if ($ProcessId -le 4 -or $ProcessId -eq $PID) {
        return [pscustomobject]@{ Ok = $true; Skipped = $true }
    }

    $before = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $before) {
        return [pscustomobject]@{ Ok = $true; Gone = $true }
    }

    $mySession = (Get-Process -Id $PID).SessionId
    $targetSession = $before.SessionId
    $killError = $null

    if ($Elevated) {
        $null = Invoke-FleetElevatedTaskKill -ProcessIds @($ProcessId)
    } else {
        $null = Start-Process -FilePath "taskkill.exe" -ArgumentList @("/F", "/T", "/PID", "$ProcessId") `
            -Wait -PassThru -WindowStyle Hidden -ErrorAction SilentlyContinue
        if ($null -and $null.ExitCode -ne 0) {
            try {
                Stop-Process -Id $ProcessId -Force -ErrorAction Stop
            } catch {
                $killError = $_.Exception.Message
            }
        }
    }

    Start-Sleep -Milliseconds 120
    $after = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($after) {
        return [pscustomobject]@{
            Ok           = $false
            Name         = $before.ProcessName
            SessionId    = $targetSession
            MySession    = $mySession
            CrossSession = ($targetSession -ne $mySession)
            Error        = $killError
        }
    }

    return [pscustomobject]@{ Ok = $true }
}

function Invoke-FleetElevatedTaskKill {
    param([Parameter(Mandatory)][int[]]$ProcessIds)

    $unique = @($ProcessIds | Where-Object { $_ -gt 4 } | Sort-Object -Unique)
    if ($unique.Count -eq 0) { return $true }

    $lines = @('$ErrorActionPreference = "SilentlyContinue"')
    foreach ($procId in $unique) {
        $lines += "taskkill /F /T /PID $procId 2>`$null | Out-Null"
    }
    $lines += "Start-Sleep -Milliseconds 400"
    foreach ($procId in $unique) {
        $lines += "if (Get-Process -Id $procId -ErrorAction SilentlyContinue) { exit 1 }"
    }
    $scriptText = ($lines -join "; ")
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($scriptText))

    try {
        $proc = Start-Process -FilePath "powershell.exe" -Verb RunAs -ArgumentList @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-EncodedCommand", $encoded
        ) -Wait -PassThru -WindowStyle Hidden -ErrorAction Stop
        return ($proc.ExitCode -eq 0)
    } catch {
        return $false
    }
}

function Get-FleetPortListenerPidSet {
    param([Parameter(Mandatory)][int[]]$Ports)

    $targetPids = [System.Collections.Generic.HashSet[int]]::new()
    foreach ($port in @($Ports | Where-Object { $_ -gt 0 } | Sort-Object -Unique)) {
        foreach ($procId in @(Get-FleetPortListenerPids -Port $port)) {
            [void]$targetPids.Add($procId)
        }
    }
    return @($targetPids)
}

function Stop-FleetPortSquatters {
    param(
        [Parameter(Mandatory)][int[]]$Ports,
        [string]$Label = "fleet",
        [switch]$ElevatedFallback
    )

    $uniquePorts = @($Ports | Where-Object { $_ -gt 0 } | Sort-Object -Unique)
    if ($uniquePorts.Count -eq 0) { return }

    function Get-FleetKillablePortListenerPids {
        param([int[]]$Ports)
        $targetPids = [System.Collections.Generic.HashSet[int]]::new()
        foreach ($port in @($Ports | Where-Object { $_ -gt 0 } | Sort-Object -Unique)) {
            foreach ($procId in @(Get-FleetPortListenerPids -Port $port)) {
                if (Test-FleetProcessProtectedByService -ProcessId $procId) {
                    $brief = Get-FleetProcessBrief -ProcessId $procId
                    $name = if ($brief) { $brief.Name } else { 'process' }
                    Write-Host "[$Label] skip PID $procId ($name) on port $port - Windows/NSSM service" -ForegroundColor DarkCyan
                    continue
                }
                [void]$targetPids.Add($procId)
            }
        }
        return @($targetPids)
    }

    if ($ElevatedFallback) {
        Write-Host "[$Label] Clearing port listeners on $($uniquePorts -join ', ') ..." -ForegroundColor Yellow
        for ($attempt = 1; $attempt -le 3; $attempt++) {
            $targetPids = @(Get-FleetKillablePortListenerPids -Ports $uniquePorts)
            if ($targetPids.Count -eq 0) { return }

            if ($attempt -gt 1) {
                Write-Host "  retry $attempt PIDs: $($targetPids -join ', ')" -ForegroundColor DarkGray
            }
            foreach ($procId in $targetPids) {
                $result = Stop-FleetProcessId -ProcessId $procId
                if ($result.Ok) {
                    Write-Host "  stop PID $procId" -ForegroundColor DarkGray
                } else {
                    $brief = Get-FleetProcessBrief -ProcessId $procId
                    $name = if ($brief) { $brief.Name } else { 'process' }
                    Write-Host "  could not stop PID $procId ($name)" -ForegroundColor DarkYellow
                }
            }
            Start-Sleep -Milliseconds 300

            $remaining = @(Get-FleetKillablePortListenerPids -Ports $uniquePorts)
            if ($remaining.Count -eq 0) { return }

            Write-Host "  elevated stop PIDs: $($remaining -join ', ')" -ForegroundColor DarkGray
            $null = Invoke-FleetElevatedTaskKill -ProcessIds $remaining
            Start-Sleep -Milliseconds 400
        }
        return
    }

    function Invoke-FleetPortKillPass {
        param([string]$PassLabel)
        $targetPids = @(Get-FleetKillablePortListenerPids -Ports $uniquePorts)
        if ($targetPids.Count -eq 0) { return }

        Write-Host "[$PassLabel] Clearing port listeners on $($uniquePorts -join ', ') ..." -ForegroundColor Yellow
        foreach ($procId in $targetPids) {
            $result = Stop-FleetProcessId -ProcessId $procId
            if ($result.Ok) {
                Write-Host "  stop PID $procId" -ForegroundColor DarkGray
            } else {
                $brief = Get-FleetProcessBrief -ProcessId $procId
                $name = if ($brief) { $brief.Name } else { 'process' }
                $sess = if ($brief) { $brief.SessionId } else { '?' }
                Write-Host "  could not stop PID $procId ($name, session $sess)" -ForegroundColor DarkYellow
            }
        }
    }

    Invoke-FleetPortKillPass -PassLabel $Label
    Start-Sleep -Milliseconds 400
    Invoke-FleetPortKillPass -PassLabel "$Label-retry"
    Start-Sleep -Milliseconds 200
}

function Stop-FleetPortListeners {
    <#
      Hard stop for dev restart/stop.bat. Normal kill then elevated taskkill (UAC) when needed.
    #>
    param(
        [Parameter(Mandatory)][int[]]$Ports,
        [string]$Label = "fleet"
    )

    Stop-FleetPortSquatters -Ports $Ports -Label $Label -ElevatedFallback
    $still = Get-FleetPortsStillListening -Ports $Ports
    if ($still.Count -eq 0) {
        Write-Host "[$Label] Ports clear: $($Ports -join ', ')" -ForegroundColor Green
        return $true
    }

    $details = @()
    foreach ($entry in $still.GetEnumerator()) {
        foreach ($procId in $entry.Value) {
            $brief = Get-FleetProcessBrief -ProcessId $procId
            if ($brief) {
                $details += "port $($entry.Key) $($brief.Name) PID $procId (session $($brief.SessionId))"
            } else {
                $details += "port $($entry.Key) PID $procId"
            }
        }
    }
    Write-Host "[$Label] ERROR: could not free ports: $($details -join '; ')" -ForegroundColor Red
    return $false
}

function Resolve-FleetPortConflict {
    param(
        [Parameter(Mandatory)][int[]]$Ports,
        [string]$Label = "fleet",
        [hashtable]$HealthChecks = @{},
        [switch]$AllowReuse,
        [switch]$ForceRestart
    )

    $hardRestart = $ForceRestart -or (-not $AllowReuse)
    Stop-FleetPortSquatters -Ports $Ports -Label $Label -ElevatedFallback:$hardRestart

    $stillAll = Get-FleetPortsStillListening -Ports $Ports
    $still = Get-FleetPortsStillListening -Ports $Ports -ExcludeProtectedServiceProcesses
    if ($stillAll.Count -eq 0) {
        return [pscustomobject]@{ Action = 'Cleared'; Reuse = $false }
    }

    $blockedPorts = @($stillAll.Keys | Sort-Object)
    $canReuse = ($AllowReuse -or ($still.Count -eq 0 -and $stillAll.Count -gt 0)) -and (-not $ForceRestart) -and ($HealthChecks.Count -gt 0)
    if ($canReuse) {
        foreach ($port in $blockedPorts) {
            $portInt = [int]$port
            if (-not $HealthChecks.ContainsKey($portInt)) {
                $canReuse = $false
                break
            }
            if (-not (Test-FleetHttpOk -Url $HealthChecks[$portInt])) {
                $canReuse = $false
                break
            }
        }
    }

    if ($canReuse) {
        if ($still.Count -eq 0 -and $stillAll.Count -gt 0) {
            Write-Host "[$Label] NSSM/service holds port(s); health OK - reusing (-ReuseIfRunning)." -ForegroundColor Green
        } else {
            Write-Host "[$Label] Ports in use but health checks passed - reusing existing stack (-ReuseIfRunning)." -ForegroundColor Green
        }
        return [pscustomobject]@{ Action = 'ReuseHealthy'; Reuse = $true }
    }

    $liveBlockers = @()
    $ghostBlockers = @()
    foreach ($entry in $still.GetEnumerator()) {
        foreach ($procId in $entry.Value) {
            $brief = Get-FleetProcessBrief -ProcessId $procId
            if ($brief) {
                $liveBlockers += "port $($entry.Key) $($brief.Name) PID $procId (session $($brief.SessionId))"
            } elseif ($null -ne (Get-Process -Id $procId -ErrorAction SilentlyContinue)) {
                $liveBlockers += "port $($entry.Key) PID $procId"
            } else {
                $ghostBlockers += "port $($entry.Key) ghost PID $procId"
            }
        }
    }

    if ($still.Count -eq 0 -and $stillAll.Count -gt 0) {
        $svcBlockers = @()
        foreach ($entry in $stillAll.GetEnumerator()) {
            foreach ($procId in $entry.Value) {
                $brief = Get-FleetProcessBrief -ProcessId $procId
                if ($brief) {
                    $svcBlockers += "port $($entry.Key) $($brief.Name) PID $procId (Windows service)"
                } else {
                    $svcBlockers += "port $($entry.Key) PID $procId (Windows service)"
                }
            }
        }
        Write-Host "[$Label] ERROR: port(s) held by Windows/NSSM service and health check failed: $($svcBlockers -join '; ')" -ForegroundColor Red
        Write-Host "Fix the service (services.msc / nssm restart), do not kill from dev scripts." -ForegroundColor Yellow
        return [pscustomobject]@{ Action = 'Blocked'; Reuse = $false }
    }

    if ($liveBlockers.Count -gt 0) {
        Write-Host "[$Label] ERROR: ports still held: $($liveBlockers -join '; ')" -ForegroundColor Red
        Write-Host "Run stop.bat or restart.bat, then start again." -ForegroundColor Yellow
        return [pscustomobject]@{ Action = 'Blocked'; Reuse = $false }
    }

    if ($ghostBlockers.Count -gt 0) {
        Write-Host "[$Label] WARNING: stale sockets remain ($($ghostBlockers -join '; '))." -ForegroundColor Yellow
        Write-Host "Windows may still block bind until TIME_WAIT clears or after reboot." -ForegroundColor Yellow
    }

    return [pscustomobject]@{ Action = 'Cleared'; Reuse = $false }
}

function Assert-FleetPortsAvailable {
    param(
        [Parameter(Mandatory)][int[]]$Ports,
        [string]$Label = "fleet",
        [hashtable]$HealthChecks = @{},
        [switch]$AllowReuse,
        [switch]$ForceRestart
    )

    if ($HealthChecks.Count -gt 0 -or $AllowReuse -or $ForceRestart) {
        $resolved = Resolve-FleetPortConflict -Ports $Ports -Label $Label -HealthChecks $HealthChecks `
            -AllowReuse:$AllowReuse -ForceRestart:$ForceRestart
        return ($resolved.Action -ne 'Blocked')
    }

    $still = Get-FleetPortsStillListening -Ports $Ports
    if ($still.Count -eq 0) { return $true }

    $liveBlockers = @()
    $ghostBlockers = @()
    foreach ($entry in $still.GetEnumerator()) {
        foreach ($procId in $entry.Value) {
            if ($null -ne (Get-Process -Id $procId -ErrorAction SilentlyContinue)) {
                $liveBlockers += "port $($entry.Key) PID $procId"
            } else {
                $ghostBlockers += "port $($entry.Key) ghost PID $procId"
            }
        }
    }

    if ($liveBlockers.Count -gt 0) {
        Write-Host "[$Label] ERROR: ports still held by live process(es): $($liveBlockers -join '; ')" -ForegroundColor Red
        Write-Host "Close those processes, then re-run start.bat." -ForegroundColor Yellow
        return $false
    }

    if ($ghostBlockers.Count -gt 0) {
        Write-Host "[$Label] WARNING: stale sockets remain ($($ghostBlockers -join '; '))." -ForegroundColor Yellow
        Write-Host "Windows may still block bind until TIME_WAIT clears or after reboot." -ForegroundColor Yellow
    }

    return $true
}

function Start-FleetDetachedShell {
    <#
      Launch a background shell. When FLEET_PROBE_RUN=1, redirect stdout/stderr to
      FLEET_PROBE_LOG_DIR (no visible console; cold-start probe parses logs after teardown).
    #>
    param(
        [Parameter(Mandatory)][string]$Label,
        [Parameter(Mandatory)][string]$Exe,
        [Parameter(Mandatory)][string[]]$Args,
        [string]$WorkingDirectory = "",
        [string]$WindowStyle = "Normal"
    )

    $probeRun = ($env:FLEET_PROBE_RUN -eq '1')
    if ($probeRun) {
        $logDir = if ($env:FLEET_PROBE_LOG_DIR) { $env:FLEET_PROBE_LOG_DIR } else { $env:TEMP }
        if (-not (Test-Path -LiteralPath $logDir)) {
            New-Item -ItemType Directory -Force -Path $logDir | Out-Null
        }
        $outLog = Join-Path $logDir "$Label.stdout.log"
        $errLog = Join-Path $logDir "$Label.stderr.log"
        $psi = @{
            FilePath               = $Exe
            ArgumentList           = $Args
            PassThru               = $true
            NoNewWindow            = $true
            RedirectStandardOutput = $outLog
            RedirectStandardError  = $errLog
        }
        if ($WorkingDirectory) { $psi.WorkingDirectory = $WorkingDirectory }
        return Start-Process @psi
    }

    $normal = @{
        FilePath     = $Exe
        ArgumentList = $Args
        PassThru     = $true
        WindowStyle  = $WindowStyle
    }
    if ($WorkingDirectory) { $normal.WorkingDirectory = $WorkingDirectory }
    return Start-Process @normal
}

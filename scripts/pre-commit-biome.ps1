# Fleet: mcp-central-docs/templates/pre-commit-biome.ps1
# Copy to {repo}/scripts/pre-commit-biome.ps1 — used by .pre-commit-config.yaml local hook.
# Detects webapp/ or web_sota/, ensures node_modules, runs npm run biome:ci.

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

$webRoot = $null
foreach ($candidate in @("webapp", "web_sota", "web-sota", "webapp/frontend", "web")) {
    $path = Join-Path $repoRoot $candidate
    if (Test-Path (Join-Path $path "package.json")) {
        $webRoot = $path
        break
    }
}

if (-not $webRoot) {
    exit 0
}

Push-Location $webRoot
try {
    if (-not (Test-Path "node_modules")) {
        npm ci --silent
        if ($LASTEXITCODE -ne 0) {
            npm install --silent
        }
    }
    npm run biome:ci
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}

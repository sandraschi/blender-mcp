#!/usr/bin/env pwsh
<#
.SYNOPSIS
    MCP Server Repository Standards Checker and Fixer Generator
    
.DESCRIPTION
    Analyzes an MCP server repository for compliance with standards:
    - FastMCP 2.12+ compliance (no description= params)
    - MCPB packaging structure (manifest.json, assets/, etc.)
    - CI/CD workflows (GitHub Actions)
    - Test scaffold (pytest, coverage)
    - Folder structure (docs/, src/, tests/, scripts/)
    - Minimum documentation (README, CONTRIBUTING, etc.)
    - Repo root cleanliness (no unnecessary files)
    - .cursorrules with Rule #1
    
    Generates two outputs:
    1. docs/repository-analysis-{date}.md - Detailed report
    2. scripts/fix-standards.ps1 - Auto-remediation script
    
.PARAMETER GenerateFixScript
    Generate auto-remediation script (default: true)
    
.PARAMETER Verbose
    Show detailed checking progress
    
.EXAMPLE
    .\scripts\check-repo-standards.ps1
    # Analyzes repo, generates report and fix script
    
.EXAMPLE
    .\scripts\check-repo-standards.ps1 -Verbose
    # Shows detailed progress during analysis
#>

param(
    [switch]$GenerateFixScript = $true,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║    🔍 MCP Server Repository Standards Checker 🔍       ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

# Check if we're in a repo
if (-not (Test-Path "pyproject.toml") -and -not (Test-Path ".git")) {
    Write-Host "❌ Error: Must run from repository root" -ForegroundColor Red
    exit 1
}

$repoName = (Get-Item .).Name
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$date = Get-Date -Format "yyyy-MM-dd"

Write-Host "📋 Analyzing Repository: $repoName" -ForegroundColor Cyan
Write-Host "   Timestamp: $timestamp`n" -ForegroundColor Gray

# Initialize results
$results = @{
    RepoName = $repoName
    Timestamp = $timestamp
    Scores = @{}
    Issues = @()
    Fixes = @()
    Summary = @{}
}

# ============================================================================
# SECTION 1: FastMCP 2.12+ Compliance
# ============================================================================

Write-Host "🔍 Checking FastMCP 2.12+ Compliance..." -ForegroundColor Yellow

$fastmcpIssues = @()
$fastmcpScore = 10

# Check for description= parameter in @mcp.tool() decorators
if (Test-Path "src") {
    $toolFiles = Get-ChildItem -Path "src" -Filter "*.py" -Recurse
    foreach ($file in $toolFiles) {
        $content = Get-Content $file.FullName -Raw
        if ($content -match '@mcp\.tool\([^)]*description\s*=') {
            $fastmcpIssues += "Found description= in $($file.Name)"
            $fastmcpScore -= 2
        }
    }
}

if ($fastmcpIssues.Count -eq 0) {
    Write-Host "  ✅ No description= parameters found" -ForegroundColor Green
} else {
    Write-Host "  ❌ Found $($fastmcpIssues.Count) description= parameters" -ForegroundColor Red
    $results.Issues += $fastmcpIssues
    $results.Fixes += "Remove description= parameters from @mcp.tool() decorators"
}

$results.Scores["FastMCP"] = [Math]::Max(0, $fastmcpScore)

# ============================================================================
# SECTION 2: MCPB Packaging
# ============================================================================

Write-Host "🔍 Checking MCPB Packaging..." -ForegroundColor Yellow

$mcpbScore = 10
$mcpbIssues = @()

# Required files
$mcpbRequired = @{
    "manifest.json" = "MCPB manifest"
    "assets/icon.svg" = "Icon asset"
    "assets/prompts/system.md" = "System prompt"
    "requirements.txt" = "Dependencies"
}

foreach ($file in $mcpbRequired.Keys) {
    if (-not (Test-Path $file)) {
        $mcpbIssues += "Missing: $file ($($mcpbRequired[$file]))"
        $mcpbScore -= 2
        $results.Fixes += "Create $file"
    }
}

if ($mcpbIssues.Count -eq 0) {
    Write-Host "  ✅ MCPB structure complete" -ForegroundColor Green
} else {
    Write-Host "  ❌ Missing $($mcpbIssues.Count) MCPB files" -ForegroundColor Red
    $results.Issues += $mcpbIssues
}

$results.Scores["MCPB"] = [Math]::Max(0, $mcpbScore)

# ============================================================================
# SECTION 3: CI/CD Workflows
# ============================================================================

Write-Host "🔍 Checking CI/CD..." -ForegroundColor Yellow

$ciScore = 10
$ciIssues = @()

$ciFiles = @{
    ".github/workflows/ci.yml" = "CI workflow"
    ".github/workflows/release.yml" = "Release workflow"
}

foreach ($file in $ciFiles.Keys) {
    if (-not (Test-Path $file)) {
        $ciIssues += "Missing: $file"
        $ciScore -= 3
        $results.Fixes += "Create $file from central docs template"
    }
}

if ($ciIssues.Count -eq 0) {
    Write-Host "  ✅ CI/CD workflows present" -ForegroundColor Green
} else {
    Write-Host "  ❌ Missing $($ciIssues.Count) CI/CD workflows" -ForegroundColor Red
    $results.Issues += $ciIssues
}

$results.Scores["CICD"] = [Math]::Max(0, $ciScore)

# ============================================================================
# SECTION 4: Test Scaffold
# ============================================================================

Write-Host "🔍 Checking Test Scaffold..." -ForegroundColor Yellow

$testScore = 10
$testIssues = @()

# Check for tests directory
if (-not (Test-Path "tests")) {
    $testIssues += "Missing tests/ directory"
    $testScore -= 5
    $results.Fixes += "Create tests/ directory with __init__.py"
} else {
    # Check for pytest config
    if (-not (Test-Path "pytest.ini") -and -not (Test-Path "pyproject.toml")) {
        $testIssues += "No pytest configuration"
        $testScore -= 2
    }
    
    # Check for test files
    $testFiles = Get-ChildItem -Path "tests" -Filter "test_*.py" -Recurse
    if ($testFiles.Count -eq 0) {
        $testIssues += "No test files found (test_*.py)"
        $testScore -= 3
        $results.Fixes += "Add test files to tests/ directory"
    }
}

if ($testIssues.Count -eq 0) {
    Write-Host "  ✅ Test scaffold complete" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Found $($testIssues.Count) test issues" -ForegroundColor Yellow
    $results.Issues += $testIssues
}

$results.Scores["Tests"] = [Math]::Max(0, $testScore)

# ============================================================================
# SECTION 5: Folder Structure
# ============================================================================

Write-Host "🔍 Checking Folder Structure..." -ForegroundColor Yellow

$structureScore = 10
$structureIssues = @()

$requiredDirs = @{
    "src" = "Source code"
    "docs" = "Documentation"
    "tests" = "Test suite"
    "scripts" = "Utility scripts"
}

foreach ($dir in $requiredDirs.Keys) {
    if (-not (Test-Path $dir)) {
        $structureIssues += "Missing directory: $dir/"
        $structureScore -= 2
        $results.Fixes += "Create $dir/ directory"
    }
}

if ($structureIssues.Count -eq 0) {
    Write-Host "  ✅ Folder structure complete" -ForegroundColor Green
} else {
    Write-Host "  ❌ Missing $($structureIssues.Count) required directories" -ForegroundColor Red
    $results.Issues += $structureIssues
}

$results.Scores["Structure"] = [Math]::Max(0, $structureScore)

# ============================================================================
# SECTION 6: Minimum Documentation
# ============================================================================

Write-Host "🔍 Checking Documentation..." -ForegroundColor Yellow

$docsScore = 10
$docsIssues = @()

$requiredDocs = @{
    "README.md" = "Project README"
    "CONTRIBUTING.md" = "Contribution guide"
    "CHANGELOG.md" = "Version history"
    ".cursorrules" = "Cursor IDE rules"
}

foreach ($doc in $requiredDocs.Keys) {
    if (-not (Test-Path $doc)) {
        $docsIssues += "Missing: $doc"
        $docsScore -= 2
        $results.Fixes += "Create $doc from central docs template"
    }
}

# Check if .cursorrules has Rule #1
if (Test-Path ".cursorrules") {
    $cursorrules = Get-Content ".cursorrules" -Raw
    if ($cursorrules -notmatch "RULE #1|Check Central Documentation|central.*docs") {
        $docsIssues += ".cursorrules missing Rule #1 (central docs reference)"
        $docsScore -= 1
        $results.Fixes += "Add Rule #1 to .cursorrules"
    }
}

if ($docsIssues.Count -eq 0) {
    Write-Host "  ✅ Documentation complete" -ForegroundColor Green
} else {
    Write-Host "  ❌ Missing $($docsIssues.Count) documentation files" -ForegroundColor Red
    $results.Issues += $docsIssues
}

$results.Scores["Documentation"] = [Math]::Max(0, $docsScore)

# ============================================================================
# SECTION 7: Repo Root Cleanliness
# ============================================================================

Write-Host "🔍 Checking Repo Root Cleanliness..." -ForegroundColor Yellow

$cleanScore = 10
$rubbishFiles = @()

# Common rubbish patterns
$rubbishPatterns = @(
    "*.dxt",
    "*.old",
    "*.bak",
    "*.tmp",
    "*.temp",
    "*_backup.*",
    "*_old.*",
    "test_*.py",  # Test files in root
    "*.log",
    "error.log",
    "debug.log"
)

$rootFiles = Get-ChildItem -File
foreach ($file in $rootFiles) {
    foreach ($pattern in $rubbishPatterns) {
        if ($file.Name -like $pattern) {
            $rubbishFiles += $file.Name
            $cleanScore -= 1
            $results.Fixes += "Delete or move: $($file.Name)"
            break
        }
    }
}

# Check for specific known rubbish
$knownRubbish = @("extract_tools.py", "minimal_test.py", "run_server.py")
foreach ($file in $knownRubbish) {
    if (Test-Path $file) {
        $rubbishFiles += "$file (should be in scripts/)"
        $cleanScore -= 1
        $results.Fixes += "Move $file to scripts/"
    }
}

if ($rubbishFiles.Count -eq 0) {
    Write-Host "  ✅ Repo root clean" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Found $($rubbishFiles.Count) unnecessary root files" -ForegroundColor Yellow
    $results.Issues += $rubbishFiles
}

$results.Scores["Cleanliness"] = [Math]::Max(0, $cleanScore)

# ============================================================================
# SECTION 8: Modern Python Tooling
# ============================================================================

Write-Host "🔍 Checking Modern Python Tooling..." -ForegroundColor Yellow

$toolingScore = 10
$toolingIssues = @()

# Check pyproject.toml
if (-not (Test-Path "pyproject.toml")) {
    $toolingIssues += "Missing pyproject.toml"
    $toolingScore -= 5
    $results.Fixes += "Create pyproject.toml"
} else {
    $pyproject = Get-Content "pyproject.toml" -Raw
    
    # Check for ruff
    if ($pyproject -notmatch 'ruff') {
        $toolingIssues += "No ruff configuration"
        $toolingScore -= 2
        $results.Fixes += "Add ruff configuration to pyproject.toml"
    }
    
    # Check for uv.lock
    if (-not (Test-Path "uv.lock")) {
        $toolingIssues += "Missing uv.lock (not using uv package manager)"
        $toolingScore -= 1
    }
}

if ($toolingIssues.Count -eq 0) {
    Write-Host "  ✅ Modern tooling configured" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  $($toolingIssues.Count) tooling improvements available" -ForegroundColor Yellow
    $results.Issues += $toolingIssues
}

$results.Scores["Tooling"] = [Math]::Max(0, $toolingScore)

# ============================================================================
# Calculate Overall Score
# ============================================================================

$overallScore = ($results.Scores.Values | Measure-Object -Average).Average
$results.Summary["OverallScore"] = [Math]::Round($overallScore, 1)
$results.Summary["TotalIssues"] = $results.Issues.Count
$results.Summary["TotalFixes"] = $results.Fixes.Count

# Determine grade
$grade = switch ($overallScore) {
    {$_ -ge 9.0} { "🏆 EXCELLENT"; break }
    {$_ -ge 8.0} { "✅ GOOD"; break }
    {$_ -ge 7.0} { "⚠️  NEEDS WORK"; break }
    {$_ -ge 6.0} { "❌ POOR"; break }
    default { "🔥 CRITICAL"; break }
}

$results.Summary["Grade"] = $grade

# ============================================================================
# Generate Report
# ============================================================================

Write-Host "`n📊 Generating Report..." -ForegroundColor Cyan

$reportPath = "docs/repository-analysis-$date.md"
if (-not (Test-Path "docs")) {
    New-Item -ItemType Directory -Path "docs" -Force | Out-Null
}

$report = @"
# Repository Standards Analysis - $repoName

**Date:** $timestamp  
**Overall Score:** $($results.Summary.OverallScore)/10  
**Grade:** $grade

---

## 📊 Scores by Category

| Category | Score | Status |
|----------|-------|--------|
| FastMCP 2.12+ | $($results.Scores.FastMCP)/10 | $(if($results.Scores.FastMCP -ge 8){"✅"}else{"❌"}) |
| MCPB Packaging | $($results.Scores.MCPB)/10 | $(if($results.Scores.MCPB -ge 8){"✅"}else{"❌"}) |
| CI/CD | $($results.Scores.CICD)/10 | $(if($results.Scores.CICD -ge 7){"✅"}else{"❌"}) |
| Test Scaffold | $($results.Scores.Tests)/10 | $(if($results.Scores.Tests -ge 7){"✅"}else{"❌"}) |
| Folder Structure | $($results.Scores.Structure)/10 | $(if($results.Scores.Structure -ge 8){"✅"}else{"❌"}) |
| Documentation | $($results.Scores.Documentation)/10 | $(if($results.Scores.Documentation -ge 8){"✅"}else{"❌"}) |
| Repo Cleanliness | $($results.Scores.Cleanliness)/10 | $(if($results.Scores.Cleanliness -ge 8){"✅"}else{"❌"}) |
| Modern Tooling | $($results.Scores.Tooling)/10 | $(if($results.Scores.Tooling -ge 8){"✅"}else{"❌"}) |

---

## ❌ Issues Found ($($results.Issues.Count))

$(if($results.Issues.Count -eq 0){"✅ No issues found! Repository is in excellent condition."}else{$results.Issues | ForEach-Object { "- $_" } | Out-String})

---

## 🔧 Recommended Fixes ($($results.Fixes.Count))

$(if($results.Fixes.Count -eq 0){"✅ No fixes needed!"}else{($results.Fixes | Sort-Object -Unique | ForEach-Object { "- $_" }) -join "`n"})

---

## 📋 Detailed Findings

### FastMCP 2.12+ Compliance
**Score:** $($results.Scores.FastMCP)/10  
$(if($results.Scores.FastMCP -ge 9){"✅ Fully compliant with FastMCP 2.12+ standards"}else{"⚠️ Review tool decorators for description= parameters"})

### MCPB Packaging  
**Score:** $($results.Scores.MCPB)/10  
$(if($results.Scores.MCPB -ge 9){"✅ Complete MCPB package structure"}else{"⚠️ Missing some MCPB required files"})

### CI/CD Workflows
**Score:** $($results.Scores.CICD)/10  
$(if($results.Scores.CICD -ge 8){"✅ GitHub Actions configured"}else{"⚠️ Missing CI/CD workflows"})

### Test Coverage
**Score:** $($results.Scores.Tests)/10  
$(if($results.Scores.Tests -ge 8){"✅ Test infrastructure in place"}else{"⚠️ Improve test coverage"})

### Documentation
**Score:** $($results.Scores.Documentation)/10  
$(if($results.Scores.Documentation -ge 8){"✅ Minimum documentation present"}else{"⚠️ Missing key documentation files"})

### Repository Cleanliness
**Score:** $($results.Scores.Cleanliness)/10  
$(if($results.Scores.Cleanliness -ge 9){"✅ Clean repository root"}else{"⚠️ Clean up unnecessary root files"})

---

## 🎯 Priority Actions

### High Priority (Critical for Production)
$(($results.Fixes | Where-Object { $_ -match "manifest|README|CI/CD" } | ForEach-Object { "- $_" }) -join "`n")

### Medium Priority (Quality Improvements)
$(($results.Fixes | Where-Object { $_ -match "test|docs|CONTRIBUTING" } | ForEach-Object { "- $_" }) -join "`n")

### Low Priority (Cleanup)
$(($results.Fixes | Where-Object { $_ -match "Delete|Move|Clean" } | ForEach-Object { "- $_" }) -join "`n")

---

## 📚 References

- **Central Docs:** D:\Dev\repos\mcp-central-docs\
- **Standards:** mcp-central-docs/STANDARDS.md
- **FastMCP Guide:** mcp-central-docs/FASTMCP_2.12_MIGRATION.md
- **MCPB Packaging:** mcp-central-docs/MCPB_PACKAGING_STANDARDS.md
- **Templates:** mcp-central-docs/templates/

---

**Generated by:** check-repo-standards.ps1  
**Report saved to:** $reportPath  
$(if($GenerateFixScript){"**Fix script:** scripts/fix-standards.ps1"}else{""})
"@

Set-Content -Path $reportPath -Value $report -Encoding UTF8
Write-Host "  ✅ Report saved: $reportPath" -ForegroundColor Green

# ============================================================================
# Generate Fix Script
# ============================================================================

if ($GenerateFixScript -and $results.Fixes.Count -gt 0) {
    Write-Host "🔧 Generating Fix Script..." -ForegroundColor Cyan
    
    $fixScriptPath = "scripts/fix-standards.ps1"
    if (-not (Test-Path "scripts")) {
        New-Item -ItemType Directory -Path "scripts" -Force | Out-Null
    }
    
    # Build fix script content
    $fixScriptContent = @()
    $fixScriptContent += "#!/usr/bin/env pwsh"
    $fixScriptContent += "# Auto-generated fix script for $repoName"
    $fixScriptContent += "# Generated: $timestamp"
    $fixScriptContent += "# Issues to fix: $($results.Fixes.Count)"
    $fixScriptContent += ""
    $fixScriptContent += "param([switch]`$DryRun = `$false)"
    $fixScriptContent += ""
    $fixScriptContent += "Write-Host '🔧 Fixing Repository Standards...' -ForegroundColor Cyan"
    $fixScriptContent += "if (`$DryRun) { Write-Host '🔍 DRY RUN MODE' -ForegroundColor Yellow }"
    $fixScriptContent += ""
    $fixScriptContent += "`$centralDocs = 'D:\Dev\repos\mcp-central-docs'"
    $fixScriptContent += ""
    
    # Add fixes
    foreach ($fix in $results.Fixes) {
        $fixScriptContent += "# Fix: $fix"
        
        if ($fix -match "Create (.*?) directory") {
            $dir = $matches[1] -replace "/$", ""
            $fixScriptContent += "if (-not (Test-Path '$dir')) {"
            $fixScriptContent += "    New-Item -ItemType Directory -Path '$dir' -Force | Out-Null"
            $fixScriptContent += "    Write-Host '  ✅ Created: $dir/' -ForegroundColor Green"
            $fixScriptContent += "}"
        }
        elseif ($fix -match "Create (.*?) from") {
            $file = $matches[1]
            $fixScriptContent += "if (-not (Test-Path '$file')) {"
            $fixScriptContent += "    if (Test-Path `"`$centralDocs/templates/$file`") {"
            $fixScriptContent += "        Copy-Item `"`$centralDocs/templates/$file`" '$file' -Force"
            $fixScriptContent += "        Write-Host '  ✅ Copied: $file' -ForegroundColor Green"
            $fixScriptContent += "    }"
            $fixScriptContent += "}"
        }
        elseif ($fix -match "Delete.*?:\s*(.+)") {
            $file = $matches[1] -replace "\s*\(.*", ""
            $fixScriptContent += "if (Test-Path '$file') {"
            $fixScriptContent += "    Remove-Item '$file' -Force -ErrorAction SilentlyContinue"
            $fixScriptContent += "    Write-Host '  ✅ Deleted: $file' -ForegroundColor Green"
            $fixScriptContent += "}"
        }
        elseif ($fix -match "Move.*?:\s*(.+)") {
            $file = $matches[1] -replace "\s*\(.*", ""
            $fixScriptContent += "if (Test-Path '$file') {"
            $fixScriptContent += "    if (-not (Test-Path 'scripts')) { New-Item -ItemType Directory -Path 'scripts' -Force | Out-Null }"
            $fixScriptContent += "    Move-Item '$file' 'scripts/' -Force -ErrorAction SilentlyContinue"
            $fixScriptContent += "    Write-Host '  ✅ Moved: $file' -ForegroundColor Green"
            $fixScriptContent += "}"
        }
        
        $fixScriptContent += ""
    }
    
    $fixScriptContent += "Write-Host '✅ Fix script complete!' -ForegroundColor Green"
    
    Set-Content -Path $fixScriptPath -Value ($fixScriptContent -join "`n") -Encoding UTF8
    Write-Host "  ✅ Fix script saved: $fixScriptPath" -ForegroundColor Green
}

# ============================================================================
# Display Summary
# ============================================================================

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║              📊 Analysis Complete! 📊                  ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

Write-Host "🎯 Overall Score: $($results.Summary.OverallScore)/10 - $grade" -ForegroundColor $(if($overallScore -ge 8){"Green"}else{"Yellow"})
Write-Host ""
Write-Host "📊 Category Scores:" -ForegroundColor White
foreach ($category in $results.Scores.Keys | Sort-Object) {
    $score = $results.Scores[$category]
    $color = if ($score -ge 8) { "Green" } elseif ($score -ge 6) { "Yellow" } else { "Red" }
    Write-Host ("  {0,-20} {1}/10" -f $category, $score) -ForegroundColor $color
}

Write-Host ""
Write-Host "📋 Issues: $($results.Issues.Count)" -ForegroundColor $(if($results.Issues.Count -eq 0){"Green"}else{"Yellow"})
Write-Host "🔧 Fixes available: $($results.Fixes.Count)" -ForegroundColor Cyan
Write-Host ""

Write-Host "📄 Report: $reportPath" -ForegroundColor White
if ($GenerateFixScript -and $results.Fixes.Count -gt 0) {
    Write-Host "🔧 Fix script: scripts/fix-standards.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 To apply fixes:" -ForegroundColor Yellow
    Write-Host "   .\scripts\fix-standards.ps1 -DryRun  # Preview" -ForegroundColor Gray
    Write-Host "   .\scripts\fix-standards.ps1          # Apply" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ Done!" -ForegroundColor Green


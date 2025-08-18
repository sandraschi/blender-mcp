# Fix-BpyImports.ps1 - Remove problematic bpy imports from blender-mcp handlers
# This fixes the "ModuleNotFoundError: No module named 'bpy'" issue

$repoPath = "D:\Dev\repos\blender-mcp\src\blender_mcp\handlers"
$backupPath = "D:\Dev\repos\blender-mcp\backup_handlers_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "🔧 Fixing bpy imports in blender-mcp handlers..." -ForegroundColor Cyan

# Create backup
Write-Host "📁 Creating backup at: $backupPath" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
Copy-Item "$repoPath\*" $backupPath -Recurse -Force

# Get all Python files in handlers directory
$handlerFiles = Get-ChildItem $repoPath -Filter "*.py" -File

Write-Host "🔍 Found $($handlerFiles.Count) handler files to process" -ForegroundColor Green

$fixedFiles = @()
$errorFiles = @()

foreach ($file in $handlerFiles) {
    try {
        Write-Host "  Processing: $($file.Name)" -ForegroundColor Gray
        
        # Read content
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        $originalContent = $content
        
        # Remove standalone bpy imports at module level
        # This regex matches lines that are just "import bpy" or "import bpy " followed by whitespace/newline
        $content = $content -replace '(?m)^import bpy\s*$', ''
        
        # Remove empty lines that result from the removal (but keep intentional spacing)
        $lines = $content -split "`n"
        $cleanLines = @()
        $previousWasEmpty = $false
        
        foreach ($line in $lines) {
            $isEmptyOrWhitespace = [string]::IsNullOrWhiteSpace($line)
            
            # Keep the line if:
            # - It's not empty/whitespace, OR
            # - It's empty but the previous line wasn't empty (preserve single empty lines)
            if (-not $isEmptyOrWhitespace -or -not $previousWasEmpty) {
                $cleanLines += $line
            }
            
            $previousWasEmpty = $isEmptyOrWhitespace
        }
        
        $content = $cleanLines -join "`n"
        
        # Only write if content changed
        if ($content -ne $originalContent) {
            Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
            $fixedFiles += $file.Name
            Write-Host "    ✅ Fixed bpy imports" -ForegroundColor Green
        } else {
            Write-Host "    ✨ No changes needed" -ForegroundColor DarkGreen
        }
        
    } catch {
        $errorFiles += @{
            File = $file.Name
            Error = $_.Exception.Message
        }
        Write-Host "    ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "  📁 Backup created: $backupPath" -ForegroundColor Yellow
Write-Host "  ✅ Files fixed: $($fixedFiles.Count)" -ForegroundColor Green
Write-Host "  ❌ Files with errors: $($errorFiles.Count)" -ForegroundColor Red

if ($fixedFiles.Count -gt 0) {
    Write-Host "`n🔧 Fixed files:" -ForegroundColor Green
    $fixedFiles | ForEach-Object { Write-Host "    - $_" -ForegroundColor Gray }
}

if ($errorFiles.Count -gt 0) {
    Write-Host "`n❌ Files with errors:" -ForegroundColor Red
    $errorFiles | ForEach-Object { Write-Host "    - $($_.File): $($_.Error)" -ForegroundColor Gray }
}

Write-Host "`n🎯 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Test the blender-mcp server: python -m blender_mcp" -ForegroundColor Gray
Write-Host "  2. Restart Claude Desktop to reconnect" -ForegroundColor Gray
Write-Host "  3. If issues persist, check the backup at: $backupPath" -ForegroundColor Gray

Write-Host "`n✨ Done! The bpy import issue should now be resolved." -ForegroundColor Green
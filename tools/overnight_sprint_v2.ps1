# Overnight Sprint v2 - Windows PowerShell Wrapper
# Cross-platform compatibility wrapper for PowerShell 7+ and Windows PowerShell

param(
    [string]$RepoRoot = $PWD,
    [switch]$Force = $false,
    [switch]$Verbose = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"
if ($Verbose) {
    $VerbosePreference = "Continue"
}

Write-Host "🚀 Overnight Sprint v2 - Windows PowerShell Execution" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check PowerShell version
$psVersion = $PSVersionTable.PSVersion
Write-Host "PowerShell Version: $psVersion" -ForegroundColor Yellow

if ($psVersion.Major -lt 5) {
    Write-Host "❌ PowerShell 5.0 or higher required" -ForegroundColor Red
    exit 1
}

# Check if we're in PowerShell 7+
$isPowerShell7Plus = $psVersion.Major -ge 7
if ($isPowerShell7Plus) {
    Write-Host "✅ PowerShell 7+ detected - Full compatibility mode" -ForegroundColor Green
} else {
    Write-Host "⚠️ Windows PowerShell detected - Limited compatibility mode" -ForegroundColor Yellow
}

# Validate repository root
$repoPath = Resolve-Path $RepoRoot -ErrorAction SilentlyContinue
if (-not $repoPath) {
    Write-Host "❌ Invalid repository path: $RepoRoot" -ForegroundColor Red
    exit 1
}

Set-Location $repoPath
Write-Host "📁 Repository: $repoPath" -ForegroundColor Green

# Check for Python
$pythonCmd = $null
$pythonVersions = @("python", "python3", "py")

foreach ($pyCmd in $pythonVersions) {
    try {
        $pythonVersion = & $pyCmd --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $pyCmd
            Write-Host "🐍 Python found: $pythonVersion ($pyCmd)" -ForegroundColor Green
            break
        }
    }
    catch {
        # Continue to next python command
    }
}

if (-not $pythonCmd) {
    Write-Host "❌ Python not found. Please install Python 3.11+ and ensure it's in PATH" -ForegroundColor Red
    exit 1
}

# Check for the overnight sprint script
$sprintScript = Join-Path $repoPath "tools/overnight_sprint_v2.py"
if (-not (Test-Path $sprintScript)) {
    Write-Host "❌ Overnight sprint script not found: $sprintScript" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Sprint script found: $sprintScript" -ForegroundColor Green

# Check virtual environment
$venvPath = Join-Path $repoPath ".venv-ci"
$venvExists = Test-Path $venvPath

if ($venvExists) {
    Write-Host "✅ Virtual environment found: $venvPath" -ForegroundColor Green
} else {
    Write-Host "⚠️ Virtual environment not found, will be created" -ForegroundColor Yellow
}

# Prepare execution
Write-Host "`n🔧 Preparing to execute overnight sprint..." -ForegroundColor Cyan

$arguments = @(
    $sprintScript,
    "--repo-root", $repoPath
)

if ($Verbose) {
    Write-Host "Command: $pythonCmd $($arguments -join ' ')" -ForegroundColor Gray
}

# Execute the sprint
Write-Host "`n⚡ Starting Overnight Sprint v2..." -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

try {
    $startTime = Get-Date
    
    if ($isPowerShell7Plus) {
        # PowerShell 7+ has better subprocess handling
        $process = Start-Process -FilePath $pythonCmd -ArgumentList $arguments -NoNewWindow -Wait -PassThru
        $exitCode = $process.ExitCode
    } else {
        # Windows PowerShell fallback
        & $pythonCmd @arguments
        $exitCode = $LASTEXITCODE
    }
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host "`n" + "=" * 60 -ForegroundColor Green
    Write-Host "⏱️ Execution completed in: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Yellow
    
    if ($exitCode -eq 0) {
        Write-Host "✅ Overnight Sprint v2 completed successfully!" -ForegroundColor Green
        
        # Show output summary
        $logsDir = Join-Path $repoPath "logs/nightly"
        if (Test-Path $logsDir) {
            Write-Host "`n📋 Generated files:" -ForegroundColor Cyan
            Get-ChildItem $logsDir -File | Sort-Object LastWriteTime -Descending | Select-Object -First 10 | ForEach-Object {
                $size = [math]::Round($_.Length / 1KB, 2)
                Write-Host "  📄 $($_.Name) ($size KB)" -ForegroundColor White
            }
            
            # Show summary if available
            $summaryFiles = Get-ChildItem $logsDir -Filter "*summary*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($summaryFiles) {
                Write-Host "`n📊 Latest summary: $($summaryFiles.Name)" -ForegroundColor Cyan
            }
        }
        
        Write-Host "`n🎉 Ready for PR creation and coverage review!" -ForegroundColor Green
        
    } else {
        Write-Host "❌ Overnight Sprint v2 failed with exit code: $exitCode" -ForegroundColor Red
        
        # Try to show recent log entries
        $logFiles = Get-ChildItem (Join-Path $repoPath "logs/nightly") -Filter "*.log" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($logFiles) {
            Write-Host "`n📋 Recent log entries from $($logFiles.Name):" -ForegroundColor Yellow
            Get-Content $logFiles.FullName -Tail 10 | ForEach-Object {
                Write-Host "  $_" -ForegroundColor Gray
            }
        }
        
        exit $exitCode
    }
    
} catch {
    Write-Host "`n❌ PowerShell execution error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Gray
    exit 1
}

# PowerShell 7 specific enhancements
if ($isPowerShell7Plus) {
    Write-Host "`n🔧 PowerShell 7+ Enhancements Available:" -ForegroundColor Cyan
    Write-Host "  - Enhanced subprocess handling ✅" -ForegroundColor Green
    Write-Host "  - Better error reporting ✅" -ForegroundColor Green
    Write-Host "  - Cross-platform compatibility ✅" -ForegroundColor Green
    
    # Check for Windows-specific features that might need attention
    if ($env:OS -eq "Windows_NT") {
        Write-Host "`n💡 Windows-specific considerations:" -ForegroundColor Yellow
        Write-Host "  - Pre-commit hooks: May need cache clearing if permission issues occur" -ForegroundColor Gray
        Write-Host "  - Path handling: Using Windows-native path resolution" -ForegroundColor Gray
        Write-Host "  - Virtual environment: Using Scripts/ instead of bin/" -ForegroundColor Gray
    }
}

Write-Host "`n✨ Overnight Sprint v2 execution complete!" -ForegroundColor Cyan
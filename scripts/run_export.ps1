# bar-directory-recon Export Wrapper (PowerShell)
# Purpose: Validate environment, run health check, execute export, log results
# Usage: .\run_export.ps1 -CsvPath "data.csv" -SheetId "abc123" [-Mode "append"] [-Worksheet "leads"]

param(
    [Parameter(Mandatory=$true)]
    [string]$CsvPath,
    
    [Parameter(Mandatory=$true)]
    [string]$SheetId,
    
    [string]$Mode = "append",
    
    [string]$Worksheet = "leads"
)

$ErrorActionPreference = "Stop"

# Setup logging (create directory and transcript)
$logsDir = "logs/exports"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}
$timestamp = (Get-Date -Format "yyyyMMdd_HHmmss")
$logFile = "$logsDir/$timestamp.log"

try {
    # Start transcript (captured in finally block)
    Start-Transcript -Path $logFile -Append -ErrorAction SilentlyContinue | Out-Null
    
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "bdr Export Wrapper (v0.1.10)" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Log file: $logFile"
    Write-Host "CSV: $CsvPath"
    Write-Host "Sheet ID: $SheetId"
    Write-Host "Mode: $Mode"
    Write-Host "Worksheet: $Worksheet"
    Write-Host ""
    
    # [1/6] Preflight: Ensure bdr command exists
    Write-Host "[1/6] Checking bdr installation..." -ForegroundColor Yellow
    try {
        Get-Command bdr -ErrorAction Stop | Out-Null
        Write-Host "✅ bdr command found" -ForegroundColor Green
    } catch {
        Write-Host "❌ bdr command not found. Ensure bar-directory-recon is installed." -ForegroundColor Red
        throw "bdr command not available"
    }
    Write-Host ""
    
    # [2/6] Preflight: Ensure GOOGLE_SHEETS_CREDENTIALS_PATH is set and readable
    Write-Host "[2/6] Checking credentials environment variable..." -ForegroundColor Yellow
    if (-not $env:GOOGLE_SHEETS_CREDENTIALS_PATH) {
        Write-Host "❌ GOOGLE_SHEETS_CREDENTIALS_PATH is not set" -ForegroundColor Red
        throw "GOOGLE_SHEETS_CREDENTIALS_PATH is not set"
    }
    if (-not (Test-Path $env:GOOGLE_SHEETS_CREDENTIALS_PATH)) {
        Write-Host "❌ Credentials file not found at: $($env:GOOGLE_SHEETS_CREDENTIALS_PATH)" -ForegroundColor Red
        throw "Credentials file not found at GOOGLE_SHEETS_CREDENTIALS_PATH"
    }
    Write-Host "✅ Credentials file accessible at $($env:GOOGLE_SHEETS_CREDENTIALS_PATH)" -ForegroundColor Green
    Write-Host ""
    
    # [3/6] Verify Python version 3.11+
    Write-Host "[3/6] Checking Python version..." -ForegroundColor Yellow
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
                Write-Host "❌ Python 3.11+ required (found: $pythonVersion)" -ForegroundColor Red
                throw "Python version check failed: $pythonVersion"
            }
            Write-Host "✅ Python $major.$minor (3.11+ required)" -ForegroundColor Green
        } else {
            throw "Could not parse Python version: $pythonVersion"
        }
    } catch {
        Write-Host "❌ Python version check failed: $_" -ForegroundColor Red
        throw $_
    }
    Write-Host ""
    
    # [4/6] Run bdr doctor (exit code check)
    Write-Host "[4/6] Running bdr doctor --no-exec..." -ForegroundColor Yellow
    try {
        & bdr doctor --no-exec
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ bdr doctor failed. Fix environment/config before export." -ForegroundColor Red
            throw "bdr doctor exited with code $LASTEXITCODE"
        }
        Write-Host "✅ Health check passed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Health check failed: $_" -ForegroundColor Red
        throw $_
    }
    Write-Host ""
    
    # [5/6] Validate CSV exists and count rows (streaming approach)
    Write-Host "[5/6] Validating CSV and counting rows..." -ForegroundColor Yellow
    if (-not (Test-Path $CsvPath)) {
        Write-Host "❌ CSV file not found: $CsvPath" -ForegroundColor Red
        throw "CSV file not found at $CsvPath"
    }
    try {
        $rowCount = (Get-Content -Path $CsvPath -ReadCount 0 | Measure-Object -Line).Lines
        Write-Host "✅ CSV loaded ($rowCount rows)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to read CSV: $_" -ForegroundColor Red
        throw $_
    }
    Write-Host ""
    
    # [6/6] Execute export command
    Write-Host "[6/6] Running export command..." -ForegroundColor Yellow
    Write-Host "Command: bdr export csv-to-sheets $CsvPath --sheet-id $SheetId --worksheet $Worksheet --mode $Mode" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        & bdr export csv-to-sheets $CsvPath --sheet-id $SheetId --worksheet $Worksheet --mode $Mode
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "==========================================" -ForegroundColor Green
            Write-Host "✅ Export completed successfully!" -ForegroundColor Green
            Write-Host "==========================================" -ForegroundColor Green
            Write-Host "Log file: $logFile"
        } else {
            Write-Host ""
            Write-Host "==========================================" -ForegroundColor Red
            Write-Host "❌ Export failed with exit code $LASTEXITCODE" -ForegroundColor Red
            Write-Host "==========================================" -ForegroundColor Red
            throw "Export command exited with code $LASTEXITCODE"
        }
    } catch {
        Write-Host "❌ Export failed: $_" -ForegroundColor Red
        throw $_
    }
    
} finally {
    # Always stop transcript, even on error
    Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    if (-not $?) {
        Write-Host "Note: Transcript may not have been fully captured." -ForegroundColor Yellow
    }
}

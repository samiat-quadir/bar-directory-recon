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

# Setup logging
$logsDir = "logs/exports"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}
$timestamp = (Get-Date -Format "yyyyMMdd_HHmmss")
$logFile = "$logsDir/$timestamp.log"

# Start transcript (will be stopped in finally block at end)
Start-Transcript -Path $logFile -Append -ErrorAction SilentlyContinue | Out-Null

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "bdr Export Wrapper (v0.1.9)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Log file: $logFile"
Write-Host "CSV: $CsvPath"
Write-Host "Sheet ID: $SheetId"
Write-Host "Mode: $Mode"
Write-Host "Worksheet: $Worksheet"
Write-Host ""

# 0. Preflight: Ensure bdr command exists
Write-Host "[0/5] Checking bdr installation..." -ForegroundColor Yellow
try {
    Get-Command bdr -ErrorAction Stop | Out-Null
    Write-Host "✅ bdr command found" -ForegroundColor Green
} catch {
    Write-Host "❌ bdr command not found. Ensure bar-directory-recon is installed." -ForegroundColor Red
    throw "bdr command not available"
}
Write-Host ""

# 0b. Preflight: Ensure GOOGLE_SHEETS_CREDENTIALS_PATH is set and readable
Write-Host "[0b/5] Checking credentials environment variable..." -ForegroundColor Yellow
if (-not $env:GOOGLE_SHEETS_CREDENTIALS_PATH) {
    Write-Host "❌ GOOGLE_SHEETS_CREDENTIALS_PATH is not set" -ForegroundColor Red
    throw "GOOGLE_SHEETS_CREDENTIALS_PATH is not set"
}
if (-not (Test-Path $env:GOOGLE_SHEETS_CREDENTIALS_PATH)) {
    Write-Host "❌ Credentials file not found at: $($env:GOOGLE_SHEETS_CREDENTIALS_PATH)" -ForegroundColor Red
    throw "Credentials file not found at GOOGLE_SHEETS_CREDENTIALS_PATH: $($env:GOOGLE_SHEETS_CREDENTIALS_PATH)"
} (using exit code)
Write-Host "[2/5] Running bdr doctor --no-exec..." -ForegroundColor Yellow
try {
    & bdr doctor --no-exec
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ bdr doctor failed. Fix environment/config before export." -ForegroundColor Red
        throw "bdr doctor exited with code $LASTEXITCODE"
    }
    Write-Host "✅ Health check passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
    throw $_ ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Host "❌ Python 3.11+ required (found: $pythonVersion)" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Python $($matches[0])" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Python not found or version check failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Run health check
Write-Host "[2/4] Running bdr doctor --no-exec..." -ForegroundColor Yellow
try {
    $doctorOutput = & bdr doctor --no-exec 2>&1
    if ($doctorOutput -match "Overall: PASS") {
        Write-Host "✅ Health check passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Doctor output shows failures:" -ForegroundColor Red
        Write-Host $doctorOutput
        exit 1
    }
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. Validate CSV exists
Write-Host "[3/4] Validating CSV..." -ForegroundColor Yellow
if (!(Test-Path $CsvPath)) {
    Write-Host 5] Validating CSV..." -ForegroundColor Yellow
if (!(Test-Path $CsvPath)) {
    Write-Host "❌ CSV file not found: $CsvPath" -ForegroundColor Red
    throw "CSV file not found at: $CsvPath"
}

$csvFile = Get-Item $CsvPath
# Use streaming approach to avoid loading entire file into memory
$rowCount = (Get-Content -Path $CsvPath -ReadCount 0 | Measure-Object -Line).Lines

# 4. Run export
Write-Host "[4/4] Running export..." -ForegroundColor Yellow
Write-Host "Com5] Running export..." -ForegroundColor Yellow
Write-Host "Command: bdr export csv-to-sheets `"$CsvPath`" --sheet-id `"$SheetId`" --worksheet `"$Worksheet`" --mode `"$Mode`"" -ForegroundColor Cyan
Write-Host ""

try {
    & bdr export csv-to-sheets "$CsvPath" `
        --sheet-id "$SheetId" `
        --worksheet "$Worksheet" `
        --mode "$Mode"
    
    # Check if export succeeded
    if ($LASTEXITCODE -ne 0) {
        throw "bdr export exited with code $LASTEXITCODE"
    }
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✅ Export completed successfully" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Rows exported: $rowCount"
    Write-Host "Destination: https://docs.google.com/spreadsheets/d/$SheetId"
    Write-Host "Worksheet: $Worksheet"
    Write-Host "Log file: $logFile"
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "❌ Export failed" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Log file: $logFile" -ForegroundColor Red
    Write-Host ""
    throw $_
} finally {
    # Always stop transcript
    try {
        Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    } catch {
        # Ignore errors stopping transcript
    }

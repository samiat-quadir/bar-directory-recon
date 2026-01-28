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

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "bdr Export Wrapper (v0.1.9)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "CSV: $CsvPath"
Write-Host "Sheet ID: $SheetId"
Write-Host "Mode: $Mode"
Write-Host "Worksheet: $Worksheet"
Write-Host ""

# 1. Validate Python 3.11+
Write-Host "[1/4] Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    $versionMatch = $pythonVersion -match '(\d+)\.(\d+)'
    if ($matches) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
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
    Write-Host "❌ CSV file not found: $CsvPath" -ForegroundColor Red
    exit 1
}

$csvFile = Get-Item $CsvPath
$rowCount = @(Get-Content $CsvPath).Count
Write-Host "✅ CSV found: $rowCount rows ($([Math]::Round($csvFile.Length / 1MB, 2)) MB)" -ForegroundColor Green
Write-Host ""

# 4. Run export
Write-Host "[4/4] Running export..." -ForegroundColor Yellow
Write-Host "Command: bdr export csv-to-sheets `"$CsvPath`" --sheet-id `"$SheetId`" --worksheet `"$Worksheet`" --mode `"$Mode`"" -ForegroundColor Cyan
Write-Host ""

try {
    & bdr export csv-to-sheets "$CsvPath" `
        --sheet-id "$SheetId" `
        --worksheet "$Worksheet" `
        --mode "$Mode"
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✅ Export completed successfully" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Rows exported: $rowCount"
    Write-Host "Destination: https://docs.google.com/spreadsheets/d/$SheetId"
    Write-Host "Worksheet: $Worksheet"
    Write-Host ""
    exit 0
} catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "❌ Export failed" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

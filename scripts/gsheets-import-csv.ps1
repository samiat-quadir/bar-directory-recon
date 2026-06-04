<#
.SYNOPSIS
    One-command CSV import to Google Sheets.

.DESCRIPTION
    This script:
    1. Changes to the repository root
    2. Activates the .venv virtual environment (or warns if not found)
    3. Loads environment variables from .env.local
    4. Imports a CSV file to Google Sheets using the gsheets_exporter CLI

.PARAMETER CsvPath
    Path to the CSV file to import. If omitted, auto-discovers sample CSV from:
    1) .\client_export_kit\examples\sample_leads.csv
    2) .\examples\sample_leads.csv

.PARAMETER Worksheet
    Target worksheet name (default: "leads")

.PARAMETER DedupeKey
    Column name to deduplicate by (default: "email")

.PARAMETER Mode
    Import mode: "append" or "replace" (default: "append")

.PARAMETER DryRun
    If specified, runs in dry-run mode (no network calls)

.EXAMPLE
    .\scripts\gsheets-import-csv.ps1 -CsvPath .\leads.csv
    Imports leads.csv to worksheet "leads", deduping by email.

.EXAMPLE
    .\scripts\gsheets-import-csv.ps1 -CsvPath .\data.csv -Worksheet "Sheet1" -Mode replace
    Replaces all data in "Sheet1" with contents of data.csv.

.EXAMPLE
    .\scripts\gsheets-import-csv.ps1 -CsvPath .\leads.csv -DedupeKey name
    Imports leads.csv, removing duplicates by name column.

.EXAMPLE
    .\scripts\gsheets-import-csv.ps1 -CsvPath .\leads.csv -DryRun
    Preview import without actually writing to Google Sheets.
#>
[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [string]$CsvPath,

    [string]$Worksheet = "leads",

    [string]$DedupeKey = "email",

    [ValidateSet("append", "replace")]
    [string]$Mode = "append",

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────────────────────────────────────
# 1. Navigate to repository root
# ─────────────────────────────────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Google Sheets CSV Import" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Repo:      $RepoRoot"
Write-Host "  CSV:       $CsvPath"
Write-Host "  Worksheet: $Worksheet"
Write-Host "  Mode:      $Mode"
Write-Host "  Dedupe:    $DedupeKey"
if ($DryRun) {
    Write-Host "  Dry Run:   Yes" -ForegroundColor Yellow
}
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# 2. Auto-discover or validate CSV file
# ─────────────────────────────────────────────────────────────────────────────
$SamplePaths = @(
    (Join-Path $RepoRoot "client_export_kit\examples\sample_leads.csv"),
    (Join-Path $RepoRoot "examples\sample_leads.csv")
)

if (-not $CsvPath) {
    # Auto-discover sample CSV
    $FoundSample = $null
    foreach ($sp in $SamplePaths) {
        if (Test-Path $sp) {
            $FoundSample = $sp
            break
        }
    }
    if ($FoundSample) {
        $CsvPath = $FoundSample
        Write-Host "  Auto-discovered: $CsvPath" -ForegroundColor DarkGray
    } else {
        Write-Host ""
        Write-Error "No CSV file specified and no sample found."
        Write-Host ""
        Write-Host "Usage:" -ForegroundColor Yellow
        Write-Host "  .\scripts\gsheets-import-csv.ps1 -CsvPath .\your-leads.csv" -ForegroundColor White
        Write-Host ""
        Write-Host "Sample locations (none found):" -ForegroundColor Yellow
        foreach ($sp in $SamplePaths) {
            Write-Host "  • $sp" -ForegroundColor DarkGray
        }
        Write-Host ""
        exit 1
    }
}

if (-not (Test-Path $CsvPath)) {
    Write-Host ""
    Write-Error "CSV file not found: $CsvPath"
    Write-Host ""
    Write-Host "Did you mean one of these?" -ForegroundColor Yellow
    foreach ($sp in $SamplePaths) {
        if (Test-Path $sp) {
            Write-Host "  ✓ $sp" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $sp" -ForegroundColor DarkGray
        }
    }
    Write-Host ""
    exit 1
}

# Resolve to absolute path
$CsvPath = (Resolve-Path $CsvPath).Path

# ─────────────────────────────────────────────────────────────────────────────
# 3. Verify virtual environment Python
# ─────────────────────────────────────────────────────────────────────────────
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (Test-Path $VenvPython) {
    Write-Host "[1/3] Using .venv Python..." -ForegroundColor Yellow
    Write-Host "      Python: $VenvPython" -ForegroundColor DarkGray
} else {
    Write-Host ""
    Write-Error ".venv not found at $RepoRoot\.venv"
    Write-Host ""
    Write-Host "To create the virtual environment, run:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor White
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  pip install -e .[gsheets]" -ForegroundColor White
    Write-Host ""
    exit 1
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. Load environment variables from .env.local
# ─────────────────────────────────────────────────────────────────────────────
$LoadEnvScript = Join-Path $ScriptDir "load-env.ps1"

Write-Host "[2/3] Loading .env.local..." -ForegroundColor Yellow
& $LoadEnvScript -ShowLoaded

# ─────────────────────────────────────────────────────────────────────────────
# 5. Run CSV import
# ─────────────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[3/3] Importing CSV to Google Sheets..." -ForegroundColor Yellow

$PythonArgs = @(
    "-m", "tools.gsheets_exporter",
    "--csv", $CsvPath,
    "--worksheet", $Worksheet,
    "--dedupe-key", $DedupeKey,
    "--mode", $Mode
)

if ($DryRun) {
    $PythonArgs += "--dry-run"
}

& $VenvPython @PythonArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  ✅ OK: CSV imported to worksheet '$Worksheet'" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host "  ❌ FAILED: Could not import CSV" -ForegroundColor Red
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host ""
    exit 1
}

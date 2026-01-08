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
    Path to the CSV file to import (required)

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
    [Parameter(Mandatory=$true, Position=0)]
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
# 2. Validate CSV file exists (with repo-root fallbacks)
# ─────────────────────────────────────────────────────────────────────────────
if (-not (Test-Path $CsvPath)) {
    # Try resolving the path relative to the repository root
    $Candidate = Join-Path $RepoRoot $CsvPath
    if (Test-Path $Candidate) {
        $CsvPath = (Resolve-Path $Candidate).Path
    } else {
        # Try using only the file name relative to repo root (handles .\prefix)
        $Leaf = Split-Path $CsvPath -Leaf
        $Candidate2 = Join-Path $RepoRoot $Leaf
        if (Test-Path $Candidate2) {
            $CsvPath = (Resolve-Path $Candidate2).Path
        } else {
            Write-Error "CSV file not found: $CsvPath"
            Write-Error "Try providing an absolute path or a repo-relative path, e.g. docs/examples/sample_leads.csv"
            exit 1
        }
    }
} else {
    # Resolve to absolute path
    $CsvPath = (Resolve-Path $CsvPath).Path
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. Activate virtual environment
# ─────────────────────────────────────────────────────────────────────────────
$VenvActivate = Join-Path $RepoRoot ".venv\Scripts\Activate.ps1"

if (Test-Path $VenvActivate) {
    Write-Host "[1/3] Activating .venv..." -ForegroundColor Yellow
    & $VenvActivate
} else {
    Write-Warning "[1/3] .venv not found at $VenvActivate — using system Python"
    Write-Warning "      Consider running: python -m venv .venv && .\.venv\Scripts\Activate.ps1 && pip install -e .[gsheets]"
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

$Args = @(
    "-m", "tools.gsheets_exporter",
    "--csv", $CsvPath,
    "--worksheet", $Worksheet,
    "--dedupe-key", $DedupeKey,
    "--mode", $Mode
)

if ($DryRun) {
    $Args += "--dry-run"
}

python @Args

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

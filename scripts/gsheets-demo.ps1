<#
.SYNOPSIS
    One-command Google Sheets demo: check dependencies, list worksheets, export demo row.

.DESCRIPTION
    This script:
    1. Changes to the repository root
    2. Activates the .venv virtual environment (or warns if not found)
    3. Loads environment variables from .env.local
    4. Runs the Google Sheets exporter CLI to:
       - Check if dependencies are installed
       - List available worksheets
       - Export a demo row to the "changelog" worksheet (system/run logs)

.PARAMETER Worksheet
    Target worksheet name (default: "changelog")

.PARAMETER DryRun
    If specified, runs demo in dry-run mode (no network calls)

.EXAMPLE
    .\scripts\gsheets-demo.ps1
    Runs the full demo against worksheet "changelog".

.EXAMPLE
    .\scripts\gsheets-demo.ps1 -Worksheet "Sheet1"
    Runs the demo against worksheet "Sheet1".

.EXAMPLE
    .\scripts\gsheets-demo.ps1 -DryRun
    Runs the demo in dry-run mode (no actual export).
#>
[CmdletBinding()]
param(
    [string]$Worksheet = "changelog",
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
Write-Host "  Google Sheets Demo" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Repo:      $RepoRoot"
Write-Host "  Worksheet: $Worksheet"
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# 2. Verify virtual environment Python
# ─────────────────────────────────────────────────────────────────────────────
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (Test-Path $VenvPython) {
    Write-Host "[1/4] Using .venv Python..." -ForegroundColor Yellow
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
# 3. Load environment variables from .env.local
# ─────────────────────────────────────────────────────────────────────────────
$LoadEnvScript = Join-Path $ScriptDir "load-env.ps1"

Write-Host "[2/4] Loading .env.local..." -ForegroundColor Yellow
& $LoadEnvScript -ShowLoaded

# ─────────────────────────────────────────────────────────────────────────────
# 4. Run gsheets exporter commands
# ─────────────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[3/4] Checking Google Sheets dependencies..." -ForegroundColor Yellow
& $VenvPython -m tools.gsheets_exporter --check
if ($LASTEXITCODE -ne 0) {
    Write-Error "Google Sheets dependencies not installed. Run: pip install .[gsheets]"
    exit 1
}

Write-Host ""
Write-Host "[3/4] Listing available worksheets..." -ForegroundColor Yellow
& $VenvPython -m tools.gsheets_exporter --list-worksheets
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Could not list worksheets (check credentials/spreadsheet ID)"
}

Write-Host ""
Write-Host "[4/4] Exporting demo row to worksheet '$Worksheet'..." -ForegroundColor Yellow

if ($DryRun) {
    & $VenvPython -m tools.gsheets_exporter --demo --worksheet $Worksheet --dry-run
} else {
    & $VenvPython -m tools.gsheets_exporter --demo --worksheet $Worksheet
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  ✅ OK: Demo row exported to worksheet '$Worksheet'" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host "  ❌ FAILED: Could not export demo row" -ForegroundColor Red
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host ""
    exit 1
}

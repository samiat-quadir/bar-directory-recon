<#
.SYNOPSIS
    One-command CSV import to Google Sheets.

.DESCRIPTION
    Wrapper script that loads environment and imports a CSV to Google Sheets.
    This is the client-facing entry point for the export kit.

.PARAMETER CsvPath
    Path to the CSV file to import. If omitted, uses examples\sample_leads.csv

.PARAMETER Worksheet
    Target worksheet name (default: "leads")

.PARAMETER Mode
    Import mode: "append" or "replace" (default: "append")

.PARAMETER DryRun
    If specified, runs in dry-run mode (no network calls)

.EXAMPLE
    .\Run-Import.ps1 -CsvPath .\leads.csv

.EXAMPLE
    .\Run-Import.ps1 -CsvPath .\leads.csv -Mode replace

.EXAMPLE
    .\Run-Import.ps1 -CsvPath .\leads.csv -DryRun
#>
[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [string]$CsvPath,

    [string]$Worksheet = "leads",

    [ValidateSet("append", "replace")]
    [string]$Mode = "append",

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Navigate to repository root (parent of client_export_kit)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Client Export Kit — CSV Import" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Delegate to the main import script
$ImportScript = Join-Path $RepoRoot "scripts\gsheets-import-csv.ps1"

if (-not (Test-Path $ImportScript)) {
    Write-Error "Import script not found: $ImportScript"
    exit 1
}

$ImportArgs = @{
    Worksheet = $Worksheet
    Mode = $Mode
}

# Only pass CsvPath if specified (let import script auto-discover if not)
if ($CsvPath) {
    $ImportArgs.CsvPath = $CsvPath
}

if ($DryRun) {
    & $ImportScript @ImportArgs -DryRun
} else {
    & $ImportScript @ImportArgs
}

exit $LASTEXITCODE

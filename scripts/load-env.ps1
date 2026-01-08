<#
.SYNOPSIS
    Load environment variables from .env.local into the current PowerShell session.

.DESCRIPTION
    Reads .env.local from the repository root and sets each KEY=VALUE pair
    as an environment variable. Skips comments and blank lines.

.PARAMETER Verbose
    Print each loaded variable name (not the value, for security).

.EXAMPLE
    . .\scripts\load-env.ps1
    Loads .env.local silently.

.EXAMPLE
    . .\scripts\load-env.ps1 -Verbose
    Loads .env.local and prints each variable name.
#>
[CmdletBinding()]
param(
    [switch]$ShowLoaded
)

# Determine repo root (parent of scripts folder)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$EnvFile = Join-Path $RepoRoot ".env.local"

if (-not (Test-Path $EnvFile)) {
    Write-Error "ERROR: .env.local not found at: $EnvFile"
    Write-Error "Create .env.local with:"
    Write-Error "  GOOGLE_SHEETS_CREDENTIALS_PATH=C:\path\to\service-account.json"
    Write-Error "  GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id"
    exit 1
}

$LoadedCount = 0

Get-Content $EnvFile | ForEach-Object {
    $line = $_.Trim()
    
    # Skip empty lines and comments
    if ($line -eq "" -or $line.StartsWith("#")) {
        return
    }
    
    # Parse KEY=VALUE
    $eqIndex = $line.IndexOf("=")
    if ($eqIndex -gt 0) {
        $key = $line.Substring(0, $eqIndex).Trim()
        $value = $line.Substring($eqIndex + 1).Trim()
        
        # Remove surrounding quotes if present
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        
        # Set environment variable
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
        $LoadedCount++
        
        if ($ShowLoaded) {
            Write-Host "  Loaded: $key" -ForegroundColor DarkGray
        }
    }
}

if ($ShowLoaded) {
    Write-Host "Loaded $LoadedCount environment variables from .env.local" -ForegroundColor Green
}

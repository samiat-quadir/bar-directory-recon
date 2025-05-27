<#
.SYNOPSIS
Enhanced Cross-Device Compatibility Checker with Graceful Fallback.

.DESCRIPTION
Checks critical configurations and paths for seamless multi-device syncing. Logs all outcomes clearly.
#>

$logFile = ".\logs\cross_device_sync.log"

function Log {
    param([string]$message, [string]$tag = "INFO")
    $timestamp = (Get-Date).ToString("o")
    Add-Content -Path $logFile -Value "$timestamp [$tag] $message"
    Write-Host "[$tag] $message"
}

Log "Starting compatibility check."

# Check virtual environment
if (Test-Path ".\.venv\Scripts\activate.ps1") {
    Log ".venv environment detected." "SUCCESS"
}
else {
    Log ".venv environment missing." "ERROR"
    exit 1
}

# Check .vscode settings
$vscodeSettings = ".\.vscode\settings.json"
if (Test-Path $vscodeSettings) {
    Log ".vscode/settings.json found." "SUCCESS"
}
else {
    Log ".vscode/settings.json missing - creating from template." "WARNING"
    Copy-Item ".\.vscode\settings_template.json" $vscodeSettings -ErrorAction SilentlyContinue
}

# Verify Git upstream configuration
$gitConfig = ".\.git\config"
if ((Test-Path $gitConfig) -and (Select-String -Path $gitConfig -Pattern "url = .*github\.com.*" -Quiet)) {
    Log "Git remote configured correctly." "SUCCESS"
}
else {
    Log "Git remote misconfigured or missing." "ERROR"
}

# Check device profile JSON
$deviceProfile = ".\config\device_profile_$env:COMPUTERNAME.json"
if (Test-Path $deviceProfile) {
    Log "Device profile $deviceProfile exists." "SUCCESS"
}
else {
    Log "Device profile $deviceProfile missing." "ERROR"
}

Log "Compatibility check completed."
exit 0

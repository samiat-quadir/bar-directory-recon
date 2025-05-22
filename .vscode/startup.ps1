# VS Code Workspace Startup Script
$logPath = Join-Path $PSScriptRoot "..\logs\cross_device_sync.log"
$timestamp = (Get-Date).ToString("o")

function Log {
    param([string]$message, [string]$tag = "INFO")
    $logEntry = "$timestamp [$tag] $message"
    Add-Content -Path $logPath -Value $logEntry
    Write-Host $logEntry
}

# Activate Virtual Environment
try {
    & "$PSScriptRoot\..\..\.venv\Scripts\activate.ps1"
    Log ".venv environment activated." "SUCCESS"
}
catch {
    Log "Failed to activate .venv environment. Error: $_" "ERROR"
}

# Load Copilot-specific profile (if exists)
$copilotProfilePath = Join-Path $PSScriptRoot "copilot_profile.ps1"
if (Test-Path $copilotProfilePath) {
    try {
        . $copilotProfilePath
        Log "copilot_profile.ps1 loaded successfully." "SUCCESS"
    }
    catch {
        Log "Failed to load copilot_profile.ps1. Error: $_" "ERROR"
    }
}
else {
    Log "copilot_profile.ps1 not found. Continuing without it." "WARNING"
}

Log "Workspace startup script executed successfully."

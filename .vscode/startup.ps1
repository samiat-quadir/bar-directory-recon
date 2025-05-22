# Corrected .vscode/startup.ps1
$logPath = Join-Path $PSScriptRoot "..\logs\cross_device_sync.log"
$timestamp = (Get-Date).ToString("o")

function Log {
    param([string]$message, [string]$tag = "INFO")
    $logEntry = "$timestamp [$tag] $message"
    Add-Content -Path $logPath -Value $logEntry
    Write-Host $logEntry
}

# Activate Virtual Environment (fixed path)
$activateScript = Join-Path $PSScriptRoot "..\.venv\Scripts\activate.ps1"
if (Test-Path $activateScript) {
    try {
        & $activateScript
        Log ".venv environment activated." "SUCCESS"
    }
    catch {
        Log "Failed to activate .venv environment. Error: $_" "ERROR"
    }
}
else {
    Log ".venv activation script not found at $activateScript" "ERROR"
}

# Load Copilot-specific PowerShell profile (optional)
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

# Verify Copilot Agent runtime setup
$copilotContext = Join-Path $PSScriptRoot "copilot_context.json"
if (Test-Path $copilotContext) {
    try {
        $contextContent = Get-Content $copilotContext -Raw | ConvertFrom-Json
        Log "copilot_context.json loaded successfully. Agent context: $($contextContent | ConvertTo-Json -Compress)" "SUCCESS"
    }
    catch {
        Log "copilot_context.json exists but failed to parse. Error: $_" "ERROR"
    }
}
else {
    Log "copilot_context.json not found. Copilot Agent runtime context missing." "ERROR"
}

# Check for required environment variables (example: AGENT_ENV_READY)
if ($env:AGENT_ENV_READY -eq '1') {
    Log "Copilot Agent environment ready (AGENT_ENV_READY=1)." "SUCCESS"
}
else {
    Log "Copilot Agent environment not ready. AGENT_ENV_READY is not set to '1'." "ERROR"
}

Log "Workspace startup script executed successfully."

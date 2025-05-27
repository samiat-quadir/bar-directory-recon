<<<<<<< HEAD
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
=======
# VS Code startup script for cross-device compatibility
# This script is automatically run when VS Code's terminal starts

# Get current directory and workspace folder
$workspaceFolder = Split-Path -Parent $PSScriptRoot

# Display startup banner
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Cross-Device Development Environment Setup        " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Load path resolver if exists
$pathResolverScript = Join-Path -Path $workspaceFolder -ChildPath "tools\DevicePathResolver.ps1"
if (Test-Path $pathResolverScript) {
    try {
        . $pathResolverScript
        $deviceInfo = Get-DeviceInfo
        if ($deviceInfo) {
            $username = $deviceInfo.Username
            $deviceType = $deviceInfo.DeviceType
            Write-Host "Device detected: $deviceType ($username)" -ForegroundColor Green
        }
        else {
            Write-Host "Running on: $env:COMPUTERNAME ($env:USERNAME)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Error loading device path resolver: $_" -ForegroundColor Red
    }
}

# Try using cross-device activation script first
$crossDeviceActivate = Join-Path -Path $workspaceFolder -ChildPath ".venv\Scripts\activate_cross_device.ps1"
$regularActivate = Join-Path -Path $workspaceFolder -ChildPath ".venv\Scripts\activate.ps1"

if (Test-Path $crossDeviceActivate) {
    try {
        . $crossDeviceActivate
        Write-Host "Cross-device Python virtual environment activated." -ForegroundColor Green
    }
    catch {
        Write-Host "Error activating cross-device environment: $_" -ForegroundColor Red

        # Fall back to regular activation script
        if (Test-Path $regularActivate) {
            try {
                . $regularActivate
                Write-Host "Standard virtual environment activated." -ForegroundColor Green
            }
            catch {
                Write-Host "Failed to activate virtual environment: $_" -ForegroundColor Yellow
                Write-Host "Run .\Fix-VenvPath.bat to repair the virtual environment." -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "Virtual environment not found. Run 'python -m venv .venv' to create one." -ForegroundColor Yellow
        }
    }
}
elseif (Test-Path $regularActivate) {
    try {
        . $regularActivate
        Write-Host "Standard virtual environment activated." -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to activate virtual environment: $_" -ForegroundColor Yellow
        Write-Host "Run .\Fix-VenvPath.bat to repair the virtual environment." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Virtual environment not found. Run 'python -m venv .venv' to create one." -ForegroundColor Yellow
}

# Check for cross-device configuration
$configPath = Join-Path -Path $workspaceFolder -ChildPath "config\device_config.json"
if (-not (Test-Path $configPath)) {
    Write-Host "Cross-device configuration not found. Consider running:" -ForegroundColor Yellow
    Write-Host "  .\SwitchToDevice.bat" -ForegroundColor Yellow
}

# Set up alias for common cross-device commands
function Fix-Paths { & "$workspaceFolder\Fix-VenvPath.bat" }
function Scan-Paths { & "$workspaceFolder\ScanPaths.bat" }
function Switch-DeviceContext { & "$workspaceFolder\SwitchToDevice.bat" }

# Show available cross-device commands
Write-Host ""
Write-Host "Cross-device commands available:" -ForegroundColor Cyan
Write-Host "  Fix-Paths            - Fix virtual environment paths" -ForegroundColor White
Write-Host "  Scan-Paths           - Scan for problematic hardcoded paths" -ForegroundColor White
Write-Host "  Switch-DeviceContext - Switch to another device configuration" -ForegroundColor White
Write-Host ""
>>>>>>> origin/main

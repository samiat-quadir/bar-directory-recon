# VS Code startup script for bar-directory-recon project
# Automatically runs when VS Code terminal starts

try {
    # Define the logs directory (update to correct path)
    $logsDir = "C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon\logs"
    if (!(Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }

    # Get current device info
    $device = $env:COMPUTERNAME
    $username = $env:USERNAME
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    # Log startup
    $logEntry = "$timestamp - INFO: VS Code startup script executed on device $device ($username)"
    $logFile = Join-Path $logsDir "startup_script_log.txt"
    Add-Content -Path $logFile -Value $logEntry

    # Load path resolver if it exists
    $pathResolverScript = "C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon\tools\DevicePathResolver.ps1"
    if (Test-Path $pathResolverScript) {
        . $pathResolverScript
        $deviceInfo = Get-DeviceInfo
        if ($deviceInfo) {
            Write-Host "Device detected: $($deviceInfo.DeviceType) ($($deviceInfo.Username))" -ForegroundColor Green
            $logEntry = "$timestamp - INFO: Device detected as $($deviceInfo.DeviceType) ($($deviceInfo.Username))"
            Add-Content -Path $logFile -Value $logEntry
        }
        else {
            $logEntry = "$timestamp - INFO: Device detection returned no results."
            Add-Content -Path $logFile -Value $logEntry
        }
    }
    else {
        $logEntry = "$timestamp - WARNING: DevicePathResolver.ps1 not found at $pathResolverScript"
        Add-Content -Path $logFile -Value $logEntry
    }

    # Load Copilot Agent helper profile
    $copilotProfile = "C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon\.vscode\copilot_profile.ps1"
    if (Test-Path $copilotProfile) {
        . $copilotProfile
        $logEntry = "$timestamp - INFO: Copilot Agent helper profile loaded successfully."
        Add-Content -Path $logFile -Value $logEntry
    }
    else {
        $logEntry = "$timestamp - ERROR: Copilot Agent helper profile not found at $copilotProfile"
        Add-Content -Path $logFile -Value $logEntry
    }

    # Activate virtual environment if not already active
    if (-not $env:VIRTUAL_ENV) {
        $activateScript = "C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon\.venv\Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            . $activateScript
            $logEntry = "$timestamp - INFO: Virtual environment activated automatically."
            Add-Content -Path $logFile -Value $logEntry
        }
        else {
            $logEntry = "$timestamp - WARNING: Virtual environment activation script not found at $activateScript"
            Add-Content -Path $logFile -Value $logEntry
        }
    }

    Write-Host "✅ VS Code startup.ps1 executed successfully." -ForegroundColor Green
}
catch {
    $ErrorMessage = $_.Exception.Message
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - ERROR: $ErrorMessage"

    # Ensure logs directory exists
    $logsDir = "C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon\logs"
    if (!(Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }

    # Append error to log file
    $logFile = Join-Path $logsDir "startup_script_log.txt"
    Add-Content -Path $logFile -Value $logEntry

    Write-Host "❌ Error in startup.ps1. See logs/startup_script_log.txt for details." -ForegroundColor Red
}

# AutoDeviceDetectionTask.ps1
# This script is executed automatically when the VS Code workspace opens
# It detects the current device and sets up the appropriate profile

<#
.SYNOPSIS
    Automatically detects and configures the current device when VS Code opens.

.DESCRIPTION
    This script runs when the workspace is opened in VS Code. It:
    1. Detects the current device (SALESREP or ROG-LUCCI)
    2. Links the appropriate device profile
    3. Logs the device transition
    4. Updates configurations as needed
#>

# Set error action preference
$ErrorActionPreference = "Continue"
$VerbosePreference = "SilentlyContinue"

# Get script location and project root
$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
$projectRoot = (Split-Path -Parent $scriptDir)

# Setup logging
$logDir = Join-Path -Path $projectRoot -ChildPath "logs"
if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory -Force | Out-Null
}
$logFile = Join-Path -Path $logDir -ChildPath "device_transition_setup.log"

function Write-Log {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message,
        
        [Parameter(Mandatory = $false)]
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Write to log file
    Add-Content -Path $logFile -Value $logEntry
}

# Main execution - keep this very simple to avoid errors
try {
    # Log startup
    Write-Log "AutoDeviceDetectionTask starting" "INFO"
    Write-Log "Device: $env:COMPUTERNAME | User: $env:USERNAME" "INFO"
    
    # Try to run the Python resolver first if it exists
    $pythonResolver = Join-Path -Path $projectRoot -ChildPath "tools\resolve_device_profile.py"
    if (Test-Path $pythonResolver) {
        # Try to find Python
        $pythonExe = $null
        $venvPython = Join-Path -Path $projectRoot -ChildPath ".venv\Scripts\python.exe"
        
        if (Test-Path $venvPython) {
            $pythonExe = $venvPython
        }
        else {
            # Try system Python
            $pythonExe = "python"
        }
        
        try {
            Write-Log "Running Python resolver: $pythonResolver" "INFO"
            Start-Process -FilePath $pythonExe -ArgumentList "`"$pythonResolver`"" -NoNewWindow -Wait
            Write-Log "Python resolver completed" "SUCCESS"
        }
        catch {
            Write-Log "Error running Python resolver: $_" "ERROR"
        }
    }
    else {
        Write-Log "Python resolver not found: $pythonResolver" "WARNING"
    }
    
    # Run the PowerShell device detection script as a backup
    $deviceSetupScript = Join-Path -Path $projectRoot -ChildPath "tools\AutoDeviceSetup.ps1"
    if (Test-Path $deviceSetupScript) {
        try {
            Write-Log "Running device setup script: $deviceSetupScript" "INFO"
            & $deviceSetupScript
            Write-Log "Device setup script completed" "SUCCESS"
        }
        catch {
            Write-Log "Error running device setup script: $_" "ERROR"
        }
    }
    else {
        Write-Log "Device setup script not found: $deviceSetupScript" "ERROR"
    }
    
    # Log completion
    Write-Log "AutoDeviceDetectionTask completed" "INFO"
}
catch {
    Write-Log "Unhandled error in AutoDeviceDetectionTask: $_" "ERROR"
}

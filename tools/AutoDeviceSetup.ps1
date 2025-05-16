# AutoDeviceSetup.ps1
# This script automatically detects and configures the current device when VS Code opens the project
# It ensures that device-specific paths are correctly handled and virtual environments are set up

<#
.SYNOPSIS
    Automatically configures the development environment for the current device.

.DESCRIPTION
    This script detects the current device, ensures it's registered, validates the OneDrive path,
    and sets up the virtual environment for cross-device compatibility. It's designed to run
    when VS Code opens the workspace, providing a seamless experience across different devices.

.NOTES
    Created by GitHub Copilot - May 15, 2025
#>

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Configuring Device..."

function Write-StatusMessage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $false)]
        [string]$Color = "White"
    )

    Write-Host "[SETUP] $Message" -ForegroundColor $Color
}

function Initialize-DeviceConfig {
    # Determine script location and project root
    $scriptPath = $MyInvocation.MyCommand.Path
    $scriptDir = Split-Path -Parent $scriptPath
    $projectRoot = (Split-Path -Parent $scriptDir)

    Write-StatusMessage "Project Root: $projectRoot" "Cyan"

    # Ensure we have the device path resolver
    $pathResolverScript = Join-Path -Path $projectRoot -ChildPath "tools\DevicePathResolver.ps1"
    if (-not (Test-Path $pathResolverScript)) {
        Write-StatusMessage "ERROR: DevicePathResolver.ps1 not found at expected location." "Red"
        Write-StatusMessage "Expected at: $pathResolverScript" "Red"
        exit 1
    }

    # Import the device path resolver
    try {
        . $pathResolverScript
        Write-StatusMessage "Device path resolver loaded." "Green"
    }
    catch {
        Write-StatusMessage "ERROR: Failed to load DevicePathResolver.ps1" "Red"
        Write-StatusMessage "Error: $_" "Red"
        exit 1
    }

    # Detect and register the current device
    try {
        $deviceId = $env:COMPUTERNAME
        $configFile = Join-Path -Path $projectRoot -ChildPath "config\device_config.json"

        if (-not (Test-Path $configFile)) {
            Write-StatusMessage "Device not registered. Registering now..." "Yellow"
            Register-CurrentDevice
        }
        else {
            $config = Get-Content -Path $configFile -Raw | ConvertFrom-Json

            if ($config.DeviceId -ne $deviceId) {
                Write-StatusMessage "Device mismatch detected. Current device is $deviceId but config is for $($config.DeviceId)" "Yellow"
                Write-StatusMessage "Re-registering device..." "Yellow"
                Register-CurrentDevice -Force
            }
            else {
                Write-StatusMessage "Device already registered as: $($config.DeviceId)" "Green"
            }
        }

        # Verify OneDrive path
        $onedrivePath = Get-OneDrivePath
        Write-StatusMessage "OneDrive path: $onedrivePath" "Green"

        if (-not (Test-Path $onedrivePath)) {
            Write-StatusMessage "WARNING: OneDrive path does not exist: $onedrivePath" "Yellow"
        }
    }
    catch {
        Write-StatusMessage "ERROR during device registration: $_" "Red"
    }

    # Check virtual environment status
    try {
        $venvPath = Join-Path -Path $projectRoot -ChildPath ".venv"

        if (-not (Test-Path $venvPath)) {
            Write-StatusMessage "Virtual environment not found. Skipping venv setup." "Yellow"
        }
        else {
            # Check if cross-device activation scripts exist
            $crossDeviceActivate = Join-Path -Path $venvPath -ChildPath "Scripts\activate_cross_device.bat"

            if (-not (Test-Path $crossDeviceActivate)) {
                Write-StatusMessage "Updating virtual environment for cross-device compatibility..." "Yellow"

                # Run the cross-device update script
                $updateScript = Join-Path -Path $projectRoot -ChildPath "UpdateVenvCrossDevice.bat"
                if (Test-Path $updateScript) {
                    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$updateScript`"" -NoNewWindow -Wait
                    Write-StatusMessage "Virtual environment updated for cross-device use." "Green"
                }
                else {
                    Write-StatusMessage "WARNING: UpdateVenvCrossDevice.bat not found." "Yellow"
                }
            }
            else {
                Write-StatusMessage "Cross-device virtual environment already set up." "Green"
            }
        }
    }
    catch {
        Write-StatusMessage "ERROR during virtual environment check: $_" "Red"
    }

    # Final validation
    try {
        # Run a quick path validation
        $projectRootPath = Get-ProjectRootPath

        if ($projectRootPath -ne $projectRoot) {
            Write-StatusMessage "WARNING: Project root path mismatch" "Yellow"
            Write-StatusMessage "  Expected: $projectRoot" "Yellow"
            Write-StatusMessage "  Detected: $projectRootPath" "Yellow"
        }
        else {
            Write-StatusMessage "Project root path validation successful." "Green"
        }
    }
    catch {
        Write-StatusMessage "ERROR during path validation: $_" "Red"
    }

    Write-StatusMessage "Device setup complete." "Cyan"
}

# Run the initialization
Initialize-DeviceConfig

# Test-CrossDevicePaths.ps1
# A simple utility script to test cross-device path resolution

param (
    [switch]$Verbose,
    [switch]$RegisterDevice,
    [switch]$Force
)

# Determine script location and project root
$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
$projectRoot = (Resolve-Path $scriptDir).Path

# Output basic system information
Write-Host "Cross-Device Path Resolution Test" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host "Date and Time: $(Get-Date)" -ForegroundColor White
Write-Host "Computer Name: $env:COMPUTERNAME" -ForegroundColor White
Write-Host "Username: $env:USERNAME" -ForegroundColor White
Write-Host "PowerShell Version: $($PSVersionTable.PSVersion)" -ForegroundColor White
Write-Host "Script Location: $scriptPath" -ForegroundColor White
Write-Host "Project Root: $projectRoot" -ForegroundColor White
Write-Host ""

# Load the device path resolver
$pathResolverScript = Join-Path -Path $projectRoot -ChildPath "tools\DevicePathResolver.ps1"
if (Test-Path $pathResolverScript) {
    Write-Host "Loading DevicePathResolver.ps1..." -ForegroundColor Green
    . $pathResolverScript
}
else {
    Write-Host "ERROR: Could not find DevicePathResolver.ps1" -ForegroundColor Red
    Write-Host "Expected location: $pathResolverScript" -ForegroundColor Red
    exit 1
}

# Test OneDrive path detection
Write-Host "OneDrive Path Detection:" -ForegroundColor Yellow
$onedrivePath = Get-OneDrivePath
Write-Host "Detected OneDrive path: $onedrivePath" -ForegroundColor Green
if (-not (Test-Path $onedrivePath)) {
    Write-Host "WARNING: OneDrive path does not exist" -ForegroundColor Red
}

# Test project root path detection
Write-Host "`nProject Path Detection:" -ForegroundColor Yellow
$detectedProjectRoot = Get-ProjectRootPath
Write-Host "Detected project root: $detectedProjectRoot" -ForegroundColor Green
if ($detectedProjectRoot -ne $projectRoot) {
    Write-Host "WARNING: Detected project root does not match actual script location" -ForegroundColor Yellow
    Write-Host "  Actual: $projectRoot" -ForegroundColor Yellow
    Write-Host "  Detected: $detectedProjectRoot" -ForegroundColor Yellow
}

# Test device detection
Write-Host "`nDevice Detection:" -ForegroundColor Yellow
$device = Get-CurrentDevice
if ($device) {
    Write-Host "Detected as device: $device" -ForegroundColor Green
    if ($DEVICE_CONFIGS.ContainsKey($device)) {
        $deviceConfig = $DEVICE_CONFIGS[$device]
        Write-Host "  Username: $($deviceConfig.Username)" -ForegroundColor White
        Write-Host "  OneDrive Folder: $($deviceConfig.OneDriveFolder)" -ForegroundColor White
    }
    else {
        Write-Host "WARNING: Device detected but not in configuration" -ForegroundColor Yellow
    }
}
else {
    Write-Host "No specific device detected, using generic methods" -ForegroundColor Yellow
}

# Test device configuration
Write-Host "`nDevice Configuration:" -ForegroundColor Yellow
$configFile = Join-Path -Path $projectRoot -ChildPath "config\device_config.json"
if (Test-Path $configFile) {
    $config = Get-Content -Path $configFile -Raw | ConvertFrom-Json
    Write-Host "Device registered as: $($config.DeviceId)" -ForegroundColor Green
    Write-Host "Registration date: $($config.FirstRegistered)" -ForegroundColor White
    Write-Host "Last updated: $($config.LastUpdated)" -ForegroundColor White

    if ($Verbose) {
        Write-Host "`nConfiguration details:" -ForegroundColor White
        $config | Format-List | Out-String | Write-Host
    }
}
else {
    Write-Host "No device configuration found" -ForegroundColor Yellow
    if ($RegisterDevice) {
        Write-Host "Registering device..." -ForegroundColor Green
        $newConfig = Register-CurrentDevice -Force:$Force
        Write-Host "Device registered successfully" -ForegroundColor Green
    }
    else {
        Write-Host "Run with -RegisterDevice to create configuration" -ForegroundColor White
    }
}

# Test virtual environment detection
Write-Host "`nVirtual Environment:" -ForegroundColor Yellow
$venvPath = Join-Path -Path $projectRoot -ChildPath ".venv"
if (Test-Path $venvPath) {
    Write-Host "Virtual environment found at: $venvPath" -ForegroundColor Green
    $activatePath = Join-Path -Path $venvPath -ChildPath "Scripts\activate.bat"
    $psActivatePath = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"

    if (Test-Path $activatePath) {
        Write-Host "  CMD activation script: Found" -ForegroundColor Green
    }
    else {
        Write-Host "  CMD activation script: Missing" -ForegroundColor Red
        Write-Host "  Run UpdateVenvCrossDevice.bat to fix" -ForegroundColor Yellow
    }

    if (Test-Path $psActivatePath) {
        Write-Host "  PowerShell activation script: Found" -ForegroundColor Green
    }
    else {
        Write-Host "  PowerShell activation script: Missing" -ForegroundColor Red
        Write-Host "  Run UpdateVenvCrossDevice.bat to fix" -ForegroundColor Yellow
    }
}
else {
    Write-Host "Virtual environment not found" -ForegroundColor Yellow
    Write-Host "Run RunDevelopment.bat to create" -ForegroundColor White
}

# Test virtual environment paths
Write-Host "`nVirtual Environment Test:" -ForegroundColor Yellow
$venvPath = Join-Path -Path $projectRoot -ChildPath ".venv"
$venvScriptsPath = Join-Path -Path $venvPath -ChildPath "Scripts"
$venvActivatePath = Join-Path -Path $venvScriptsPath -ChildPath "activate.ps1"
$venvCrossDeviceActivatePath = Join-Path -Path $venvScriptsPath -ChildPath "activate_cross_device.ps1"
$venvPythonPath = Join-Path -Path $venvScriptsPath -ChildPath "python.exe"

if (Test-Path $venvPath) {
    Write-Host "Virtual environment found at: $venvPath" -ForegroundColor Green

    if (Test-Path $venvScriptsPath) {
        Write-Host "Scripts directory found at: $venvScriptsPath" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING: Scripts directory not found at: $venvScriptsPath" -ForegroundColor Red
    }

    if (Test-Path $venvActivatePath) {
        Write-Host "Activation script found at: $venvActivatePath" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING: Activation script not found at: $venvActivatePath" -ForegroundColor Red
    }

    if (Test-Path $venvCrossDeviceActivatePath) {
        Write-Host "Cross-device activation script found at: $venvCrossDeviceActivatePath" -ForegroundColor Green
    }
    else {
        Write-Host "INFO: Cross-device activation script not found. Consider creating it." -ForegroundColor Yellow
    }

    if (Test-Path $venvPythonPath) {
        Write-Host "Python executable found at: $venvPythonPath" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING: Python executable not found at: $venvPythonPath" -ForegroundColor Red
    }
}
else {
    Write-Host "WARNING: Virtual environment not found at: $venvPath" -ForegroundColor Red
}

# Check VS Code configuration
Write-Host "`nVS Code Configuration Test:" -ForegroundColor Yellow
$vscodeDir = Join-Path -Path $projectRoot -ChildPath ".vscode"
$settingsPath = Join-Path -Path $vscodeDir -ChildPath "settings.json"
$tasksPath = Join-Path -Path $vscodeDir -ChildPath "tasks.json"
$startupPath = Join-Path -Path $vscodeDir -ChildPath "startup.ps1"

if (Test-Path $vscodeDir) {
    Write-Host "VS Code directory found at: $vscodeDir" -ForegroundColor Green

    if (Test-Path $settingsPath) {
        Write-Host "Settings file found at: $settingsPath" -ForegroundColor Green

        # Check the content for proper paths
        $settings = Get-Content -Path $settingsPath -Raw | ConvertFrom-Json
        if ($settings.'python.defaultInterpreterPath') {
            Write-Host "Python interpreter path in settings: $($settings.'python.defaultInterpreterPath')" -ForegroundColor Green

            # Check if the path is device-agnostic (uses ${workspaceFolder})
            if ($settings.'python.defaultInterpreterPath' -like "*`${workspaceFolder}*") {
                Write-Host "Python interpreter path uses workspace folder variable (good)" -ForegroundColor Green
            }
            else {
                Write-Host "WARNING: Python interpreter path may be hardcoded" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "WARNING: Python interpreter path not set in settings.json" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "WARNING: Settings file not found at: $settingsPath" -ForegroundColor Yellow
    }

    if (Test-Path $tasksPath) {
        Write-Host "Tasks file found at: $tasksPath" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING: Tasks file not found at: $tasksPath" -ForegroundColor Yellow
    }

    if (Test-Path $startupPath) {
        Write-Host "Startup script found at: $startupPath" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING: Startup script not found at: $startupPath" -ForegroundColor Yellow
    }
}
else {
    Write-Host "WARNING: VS Code directory not found at: $vscodeDir" -ForegroundColor Yellow
}

# Test device registration
Write-Host "`nDevice Registration Test:" -ForegroundColor Yellow
$configDir = Join-Path -Path $projectRoot -ChildPath "config"
$deviceConfigPath = Join-Path -Path $configDir -ChildPath "device_config.json"

if (Test-Path $deviceConfigPath) {
    Write-Host "Device configuration found at: $deviceConfigPath" -ForegroundColor Green

    try {
        $deviceConfig = Get-Content -Path $deviceConfigPath -Raw | ConvertFrom-Json
        Write-Host "Registered device: $($deviceConfig.DeviceId)" -ForegroundColor Green

        if ($deviceConfig.DeviceId -eq $env:COMPUTERNAME) {
            Write-Host "Device ID matches current computer (good)" -ForegroundColor Green
        }
        else {
            Write-Host "WARNING: Device ID doesn't match current computer" -ForegroundColor Yellow
            Write-Host "Current: $env:COMPUTERNAME, Registered: $($deviceConfig.DeviceId)" -ForegroundColor Yellow

            if ($RegisterDevice -or $Force) {
                Write-Host "Re-registering device..." -ForegroundColor Yellow
                Register-CurrentDevice -Force:$Force
            }
            else {
                Write-Host "Run with -RegisterDevice to register current device" -ForegroundColor Yellow
            }
        }
    }
    catch {
        Write-Host "ERROR reading device configuration: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "Device configuration not found at: $deviceConfigPath" -ForegroundColor Yellow

    if ($RegisterDevice -or $Force) {
        Write-Host "Registering current device..." -ForegroundColor Yellow
        Register-CurrentDevice -Force:$Force
    }
    else {
        Write-Host "Run with -RegisterDevice to register current device" -ForegroundColor Yellow
    }
}

Write-Host "`nCross-device path test completed" -ForegroundColor Cyan
Write-Host "For detailed instructions, see CROSS_DEVICE_GUIDE.md" -ForegroundColor White

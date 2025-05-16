# ActivateVenv.ps1
# PowerShell script to activate the virtual environment and provide a development shell

param (
    [switch]$Force,
    [switch]$Install
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = (Resolve-Path "$scriptDir").Path

# Load device path resolver if exists
$pathResolverScript = Join-Path -Path $projectRoot -ChildPath "tools\DevicePathResolver.ps1"
if (Test-Path $pathResolverScript) {
    . $pathResolverScript
    Write-Host "Device path resolver loaded." -ForegroundColor Green

    # Check if device is registered and register if needed
    $configFile = Join-Path -Path $projectRoot -ChildPath "config\device_config.json"
    if (-not (Test-Path $configFile) -or $Force) {
        Write-Host "Device not registered or Force parameter used. Registering device..." -ForegroundColor Yellow
        Register-CurrentDevice -Force:$Force
    }

    # Verify OneDrive path
    $oneDrivePath = Get-OneDrivePath
    Write-Host "Using OneDrive path: $oneDrivePath" -ForegroundColor DarkCyan
}
else {
    Write-Host "Warning: DevicePathResolver.ps1 not found. Cross-device compatibility may be limited." -ForegroundColor Yellow
}

# Import the VirtualEnvHelper module
$helperScript = Join-Path $projectRoot "tools\VirtualEnvHelper.ps1"
if (Test-Path $helperScript) {
    . $helperScript
}
else {
    Write-Host "VirtualEnvHelper.ps1 not found at: $helperScript" -ForegroundColor Red
    exit 1
}

# Ensure we have a virtual environment
if ($Force -or $Install) {
    Update-VirtualEnvironment -VenvPath "$projectRoot\.venv" -ForceRecreate:$Force
}
else {
    if (-not (Test-Path "$projectRoot\.venv")) {
        Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
        Update-VirtualEnvironment -VenvPath "$projectRoot\.venv"
    }
    else {
        Enter-VirtualEnvironment -VenvPath "$projectRoot\.venv"
    }
}

# Set up the development environment
function prompt {
    $projectName = Split-Path $projectRoot -Leaf
    Write-Host "[$projectName]" -NoNewline -ForegroundColor Cyan
    Write-Host " (venv) " -NoNewline -ForegroundColor Green
    Write-Host "$(Get-Location)>" -NoNewline
    return " "
}

# Show available commands
Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "  OneDrive Automation Project Environment" -ForegroundColor Cyan
Write-Host "==================================================`n" -ForegroundColor Cyan

Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  Run-OneDriveAutomation - Run the main automation script"
Write-Host "  Run-OneDriveCleanup    - Run the cleanup script"
Write-Host "  Run-Tests              - Run all project tests"
Write-Host "  Run-GitCleanup         - Run Git repository cleanup"
Write-Host "  Run-SecretsScanner     - Scan for secrets in the codebase"
Write-Host "`nType 'Show-Commands' to see this list again`n" -ForegroundColor Yellow

# Define helper functions
function Run-OneDriveAutomation {
    & python "$projectRoot\OneDriveAutomation.ps1" @args
}

function Run-OneDriveCleanup {
    & python "$projectRoot\OneDriveCleanup.ps1" @args
}

function Run-Tests {
    & pytest "$projectRoot"
}

function Run-GitCleanup {
    & python "$projectRoot\tools\git_repo_cleanup.ps1" @args
}

function Run-SecretsScanner {
    & python "$projectRoot\tools\secrets_scan.py" @args
}

function Show-Commands {
    Write-Host "`nAvailable commands:" -ForegroundColor Yellow
    Write-Host "  Run-OneDriveAutomation - Run the main automation script"
    Write-Host "  Run-OneDriveCleanup    - Run the cleanup script"
    Write-Host "  Run-Tests              - Run all project tests"
    Write-Host "  Run-GitCleanup         - Run Git repository cleanup"
    Write-Host "  Run-SecretsScanner     - Scan for secrets in the codebase"
    Write-Host "`n"
}

# Export functions
Export-ModuleMember -Function Run-OneDriveAutomation, Run-OneDriveCleanup, Run-Tests, Run-GitCleanup, Run-SecretsScanner, Show-Commands

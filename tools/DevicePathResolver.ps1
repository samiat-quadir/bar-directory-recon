# PowerShell script to manage cross-device paths for OneDrive
# DevicePathResolver.ps1

<#
.SYNOPSIS
    Provides device-agnostic path resolution for OneDrive paths across multiple devices.

.DESCRIPTION
    This script detects the current device and provides the correct paths for OneDrive
    and project directories. It handles different username scenarios (samq vs samqu) and
    can be dot-sourced from other scripts to provide consistent paths.

.EXAMPLE
    . .\tools\DevicePathResolver.ps1
    $onedrivePath = Get-OneDrivePath
    Write-Host "Current OneDrive path: $onedrivePath"
#>

# Known device configurations
$DEVICE_CONFIGS = @{
    "DESKTOP-ACER" = @{
        Username       = "samq"
        OneDriveFolder = "OneDrive - Digital Age Marketing Group"
    }
    "LAPTOP-ASUS"  = @{
        Username       = "samqu"
        OneDriveFolder = "OneDrive - Digital Age Marketing Group"
    }
}

# Function to detect current device
function Get-CurrentDevice {
    $computerName = $env:COMPUTERNAME
    $username = $env:USERNAME

    # First try to match by computer name
    foreach ($device in $DEVICE_CONFIGS.Keys) {
        if ($computerName -like "*$device*") {
            return $device
        }
    }

    # If no match by computer name, try by username
    foreach ($device in $DEVICE_CONFIGS.Keys) {
        if ($DEVICE_CONFIGS[$device].Username -eq $username) {
            return $device
        }
    }

    # If no match, check if this device is registered in the config
    try {
        $configFile = Join-Path -Path (Get-ProjectRootPath -DefaultPath (Get-Location).Path) -ChildPath "config\device_config.json"
        if (Test-Path $configFile) {
            $config = Get-Content -Path $configFile -Raw | ConvertFrom-Json
            if ($config.DeviceId -eq $computerName) {
                return $computerName
            }
        }
    }
    catch {
        # Silently handle errors during auto-detection
    }

    # If no match, return a default key (or you could return $null)
    return $null
}

# Function to get the correct OneDrive path for the current device
function Get-OneDrivePath {
    # Try to detect automatically first
    $device = Get-CurrentDevice

    if ($device -and $DEVICE_CONFIGS.ContainsKey($device)) {
        $username = $DEVICE_CONFIGS[$device].Username
        $oneDriveFolder = $DEVICE_CONFIGS[$device].OneDriveFolder
        $path = "C:\Users\$username\$oneDriveFolder"

        if (Test-Path $path) {
            return $path
        }
    }

    # If automatic detection fails, try common locations
    $possiblePaths = @(
        "C:\Users\samq\OneDrive - Digital Age Marketing Group"
        "C:\Users\samqu\OneDrive - Digital Age Marketing Group"
        "C:\Users\$env:USERNAME\OneDrive - Digital Age Marketing Group"
    )

    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            return $path
        }
    }

    # If still no match, look for OneDrive folders
    $userFolder = "C:\Users\$env:USERNAME"
    if (Test-Path $userFolder) {
        $oneDriveFolders = Get-ChildItem -Path $userFolder -Directory | Where-Object { $_.Name -like "OneDrive*" }
        if ($oneDriveFolders.Count -gt 0) {
            return $oneDriveFolders[0].FullName
        }
    }

    # If all else fails, return the current directory
    Write-Warning "Could not determine OneDrive path. Using current directory."
    return (Get-Location).Path
}

# Function to get the project root path
function Get-ProjectRootPath {
    param (
        [string]$OneDrivePath = (Get-OneDrivePath),
        [string]$ProjectName = "bar-directory-recon",
        [string]$SubPath = "Desktop\Local Py\Work Projects"
    )

    # First try the expected path within OneDrive
    $projectPath = Join-Path -Path $OneDrivePath -ChildPath "$SubPath\$ProjectName"

    if (Test-Path $projectPath) {
        return $projectPath
    }

    # If not found, try to locate it anywhere within OneDrive
    $foundPaths = Get-ChildItem -Path $OneDrivePath -Recurse -Directory -Filter $ProjectName -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName

    if ($foundPaths) {
        return $foundPaths
    }

    # If still not found, check if we're already in the project directory
    $currentDir = (Get-Location).Path
    if ((Split-Path -Leaf $currentDir) -eq $ProjectName) {
        return $currentDir
    }

    # If all else fails, return $null
    Write-Warning "Could not find project path for '$ProjectName'. Please specify the path manually."
    return $null
}

# Function to convert a path to be relative to the project root
function ConvertTo-ProjectRelativePath {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [string]$ProjectRoot = (Get-ProjectRootPath)
    )

    if (-not $ProjectRoot) {
        return $Path
    }

    # Ensure both paths are absolute
    $absolutePath = [System.IO.Path]::GetFullPath($Path)
    $absoluteRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

    # Check if the path is within the project root
    if ($absolutePath.StartsWith($absoluteRoot)) {
        $relativePath = $absolutePath.Substring($absoluteRoot.Length)
        if ($relativePath.StartsWith("\")) {
            $relativePath = $relativePath.Substring(1)
        }
        return $relativePath
    }

    # If not within the project, return the original path
    return $Path
}

# Function to convert a relative path to absolute path based on project root
function ConvertTo-ProjectAbsolutePath {
    param (
        [Parameter(Mandatory = $true)]
        [string]$RelativePath,

        [string]$ProjectRoot = (Get-ProjectRootPath)
    )

    if (-not $ProjectRoot) {
        return $RelativePath
    }

    # If already absolute, return as is
    if ([System.IO.Path]::IsPathRooted($RelativePath)) {
        return $RelativePath
    }

    # Join with project root to make absolute
    return Join-Path -Path $ProjectRoot -ChildPath $RelativePath
}

# Function to store device-specific configuration
function Set-DeviceConfig {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Key,

        [Parameter(Mandatory = $true)]
        [string]$Value,

        [string]$DeviceId = $env:COMPUTERNAME
    )

    $configDir = Join-Path -Path (Get-ProjectRootPath) -ChildPath "config"
    if (-not (Test-Path $configDir)) {
        New-Item -Path $configDir -ItemType Directory -Force | Out-Null
    }

    $configFile = Join-Path -Path $configDir -ChildPath "device_config.json"

    # Load existing config or create new
    if (Test-Path $configFile) {
        $config = Get-Content -Path $configFile -Raw | ConvertFrom-Json
    }
    else {
        $config = [PSCustomObject]@{
            DeviceId    = $DeviceId
            Settings    = @{}
            Paths       = @{}
            LastUpdated = (Get-Date).ToString("o")
        }
    }

    # Update with new value
    if (-not $config.Settings) {
        Add-Member -InputObject $config -MemberType NoteProperty -Name "Settings" -Value @{}
    }

    $config.Settings.$Key = $Value
    $config.LastUpdated = (Get-Date).ToString("o")

    # Save config
    $config | ConvertTo-Json -Depth 10 | Set-Content -Path $configFile

    return $config
}

# Function to get device-specific configuration
function Get-DeviceConfig {
    param (
        [Parameter(Mandatory = $false)]
        [string]$Key,

        [string]$DefaultValue = $null,

        [string]$DeviceId = $env:COMPUTERNAME
    )

    $configFile = Join-Path -Path (Get-ProjectRootPath) -ChildPath "config\device_config.json"

    # Check if config file exists
    if (-not (Test-Path $configFile)) {
        return $DefaultValue
    }

    # Load config
    $config = Get-Content -Path $configFile -Raw | ConvertFrom-Json

    # If no key specified, return the entire config
    if (-not $Key) {
        return $config
    }

    # Return the specific key value
    if ($config.Settings -and $config.Settings.PSObject.Properties.Name -contains $Key) {
        return $config.Settings.$Key
    }

    return $DefaultValue
}

# Function to detect and register the current device
function Register-CurrentDevice {
    param (
        [switch]$Force
    )

    $configDir = Join-Path -Path (Get-ProjectRootPath) -ChildPath "config"
    $configFile = Join-Path -Path $configDir -ChildPath "device_config.json"

    # Check if device is already registered
    if ((Test-Path $configFile) -and -not $Force) {
        $config = Get-Content -Path $configFile -Raw | ConvertFrom-Json
        if ($config.DeviceId -eq $env:COMPUTERNAME) {
            Write-Host "Device already registered as: $($config.DeviceId)" -ForegroundColor Green
            return $config
        }
    }

    # Ensure config directory exists
    if (-not (Test-Path $configDir)) {
        New-Item -Path $configDir -ItemType Directory -Force | Out-Null
    }

    # Create new device config
    $oneDrivePath = Get-OneDrivePath
    $projectRoot = Get-ProjectRootPath -OneDrivePath $oneDrivePath

    $config = [PSCustomObject]@{
        DeviceId        = $env:COMPUTERNAME
        Username        = $env:USERNAME
        Settings        = @{
            DefaultEditor = "code"
        }
        Paths           = @{
            OneDrive    = $oneDrivePath
            ProjectRoot = $projectRoot
        }
        FirstRegistered = (Get-Date).ToString("o")
        LastUpdated     = (Get-Date).ToString("o")
    }

    # Save config
    $config | ConvertTo-Json -Depth 10 | Set-Content -Path $configFile

    Write-Host "Device registered as: $($config.DeviceId)" -ForegroundColor Green
    Write-Host "OneDrive path: $($config.Paths.OneDrive)" -ForegroundColor Green
    Write-Host "Project root: $($config.Paths.ProjectRoot)" -ForegroundColor Green

    return $config
}

# Export functions for use in other scripts
# Note: Originally had Export-ModuleMember here, but it's unnecessary for dot-sourcing
# and causes warnings when the script is run directly

# If this script is run directly (not dot-sourced), display information
if ($MyInvocation.InvocationName -eq $MyInvocation.MyCommand.Name) {
    Write-Host "Device Path Resolver Information:" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "Detected OneDrive Path: $(Get-OneDrivePath)" -ForegroundColor Green
    Write-Host "Detected Project Root: $(Get-ProjectRootPath)" -ForegroundColor Green
    Write-Host ""
    Write-Host "To use this module in your scripts:" -ForegroundColor Yellow
    Write-Host '. $PSScriptRoot\tools\DevicePathResolver.ps1' -ForegroundColor Yellow
    Write-Host '$oneDrivePath = Get-OneDrivePath' -ForegroundColor Yellow
    Write-Host '$projectRoot = Get-ProjectRootPath' -ForegroundColor Yellow
}

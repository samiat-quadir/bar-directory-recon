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

# --- PATCH: Robust root path and fallback logging, device_profile.json only, no $DEVICE_CONFIGS ---

$LogFile = Join-Path -Path (Join-Path $PSScriptRoot '..' | Resolve-Path -Relative) -ChildPath 'logs/device_path_resolver.log'

function Write-PathResolverLog {
    param(
        [string]$Message,
        [string]$Level = 'INFO'
    )
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logLine = "[$timestamp][$Level] $Message"
    Add-Content -Path $LogFile -Value $logLine
}

function Get-DeviceProfile {
    $profilePath = Join-Path -Path (Join-Path $PSScriptRoot '..' | Resolve-Path -Relative) -ChildPath 'config/device_profile.json'
    if (Test-Path $profilePath) {
        try {
            $profile = Get-Content -Path $profilePath -Raw | ConvertFrom-Json
            Write-PathResolverLog "Loaded device profile from $profilePath"
            return $profile
        } catch {
            Write-PathResolverLog "Failed to parse device_profile.json: $_" 'ERROR'
            return $null
        }
    } else {
        Write-PathResolverLog "device_profile.json not found at $profilePath" 'ERROR'
        return $null
    }
}

function Get-CurrentDevice {
    $profile = Get-DeviceProfile
    if ($profile -and $profile.device_id) {
        Write-PathResolverLog "Detected device_id: $($profile.device_id) from device_profile.json"
        return $profile.device_id
    } else {
        Write-PathResolverLog "Could not detect device_id from device_profile.json, falling back to COMPUTERNAME: $env:COMPUTERNAME" 'WARN'
        return $env:COMPUTERNAME
    }
}

function Get-OneDrivePath {
    $profile = Get-DeviceProfile
    if ($profile -and $profile.onedrive_path) {
        if (Test-Path $profile.onedrive_path) {
            Write-PathResolverLog "Resolved OneDrive path from device_profile.json: $($profile.onedrive_path)"
            return $profile.onedrive_path
        } else {
            Write-PathResolverLog "OneDrive path in device_profile.json does not exist: $($profile.onedrive_path)" 'WARN'
        }
    }
    # Fallback: try environment or default locations
    $fallbacks = @(
        "C:\\Users\\$env:USERNAME\\OneDrive - Digital Age Marketing Group"
    )
    foreach ($path in $fallbacks) {
        if (Test-Path $path) {
            Write-PathResolverLog "Fallback: Found OneDrive path at $path"
            return $path
        }
    }
    Write-PathResolverLog "Failed to resolve OneDrive path, using current directory as fallback" 'ERROR'
    return (Get-Location).Path
}

function Get-ProjectRootPath {
    $profile = Get-DeviceProfile
    if ($profile -and $profile.project_root) {
        if (Test-Path $profile.project_root) {
            Write-PathResolverLog "Resolved project root from device_profile.json: $($profile.project_root)"
            return $profile.project_root
        } else {
            Write-PathResolverLog "Project root in device_profile.json does not exist: $($profile.project_root)" 'WARN'
        }
    }
    # Fallback: try to find project root in OneDrive
    $oneDrivePath = Get-OneDrivePath
    $projectName = 'bar-directory-recon'
    $possible = Join-Path $oneDrivePath "Desktop\Local Py\Work Projects\$projectName"
    if (Test-Path $possible) {
        Write-PathResolverLog "Fallback: Found project root at $possible"
        return $possible
    }
    Write-PathResolverLog "Failed to resolve project root, using current directory as fallback" 'ERROR'
    return (Get-Location).Path
}

function Get-WindowsRootPath {
    $root = [System.Environment]::GetFolderPath('SystemDrive')
    Write-PathResolverLog "Detected Windows root: $root"
    return $root
}

function ConvertTo-ProjectRelativePath {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [string]$ProjectRoot = (Get-ProjectRootPath)
    )
    if (-not $ProjectRoot) {
        Write-PathResolverLog "Project root not found for relative conversion. Returning original: $Path" 'WARN'
        return $Path
    }
    $absolutePath = [System.IO.Path]::GetFullPath($Path)
    $absoluteRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
    if ($absolutePath.StartsWith($absoluteRoot)) {
        $relativePath = $absolutePath.Substring($absoluteRoot.Length)
        if ($relativePath.StartsWith("\")) {
            $relativePath = $relativePath.Substring(1)
        }
        Write-PathResolverLog "Converted $Path to project-relative: $relativePath"
        return $relativePath
    }
    Write-PathResolverLog "Path $Path is not within project root $ProjectRoot. Returning original." 'WARN'
    return $Path
}

function ConvertTo-ProjectAbsolutePath {
    param (
        [Parameter(Mandatory = $true)]
        [string]$RelativePath,
        [string]$ProjectRoot = (Get-ProjectRootPath)
    )
    if (-not $ProjectRoot) {
        Write-PathResolverLog "Project root not found for absolute conversion. Returning original: $RelativePath" 'WARN'
        return $RelativePath
    }
    if ([System.IO.Path]::IsPathRooted($RelativePath)) {
        Write-PathResolverLog "Path $RelativePath is already absolute."
        return $RelativePath
    }
    $abs = Join-Path -Path $ProjectRoot -ChildPath $RelativePath
    Write-PathResolverLog "Converted $RelativePath to absolute: $abs"
    return $abs
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

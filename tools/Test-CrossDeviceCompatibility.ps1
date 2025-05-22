# Test-CrossDeviceCompatibility.ps1
# Script to test cross-device compatibility of the repository

<#
.SYNOPSIS
    Tests cross-device compatibility of the repository.

.DESCRIPTION
    This script performs comprehensive tests to ensure the repository
    is correctly configured for cross-device compatibility. It verifies
    device profile detection, path resolution, and environment setup.

.NOTES
    Created by GitHub Copilot - May 20, 2025
#>

param (
    [switch]$Verbose,
    [switch]$SkipVenvCheck
)

# Set error action preference
$ErrorActionPreference = "Stop"
if ($Verbose) {
    $VerbosePreference = "Continue"
}

# Get script location and project root
$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath # e.g., C:\\...\\project\\tools
$projectRoot = Split-Path -Parent $scriptDir # e.g., C:\\...\\project. This is the corrected line.

# Test imports
function Import-RequiredModules {
    $moduleImported = $false
    
    # Try to import DevicePathResolver
    $devicePathResolverScript = Join-Path -Path $projectRoot -ChildPath "tools\DevicePathResolver.ps1"
    if (Test-Path $devicePathResolverScript) {
        try {
            . $devicePathResolverScript
            Write-Host "✅ Successfully imported DevicePathResolver.ps1" -ForegroundColor Green
            $moduleImported = $true
        }
        catch {
            Write-Host "❌ Failed to import DevicePathResolver.ps1: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "❌ DevicePathResolver.ps1 not found at: $devicePathResolverScript" -ForegroundColor Red
    }
    
    # Try to import DevicePathHelper
    $devicePathHelperScript = Join-Path -Path $projectRoot -ChildPath "tools\DevicePathHelper.ps1"
    if (Test-Path $devicePathHelperScript) {
        try {
            . $devicePathHelperScript
            Write-Host "✅ Successfully imported DevicePathHelper.ps1" -ForegroundColor Green
            $moduleImported = $true
        }
        catch {
            Write-Host "❌ Failed to import DevicePathHelper.ps1: $_" -ForegroundColor Red
        }
    }
    
    return $moduleImported
}

function Test-DeviceProfiles {
    $configDir = Join-Path -Path $projectRoot -ChildPath "config"
    
    # Check if config directory exists
    if (-not (Test-Path $configDir)) {
        Write-Host "❌ Config directory not found at: $configDir" -ForegroundColor Red
        return $false
    }
    
    # Check device profiles
    $salesrepProfile = Join-Path -Path $configDir -ChildPath "device_profile_SALESREP.json"
    $rogLucciProfile = Join-Path -Path $configDir -ChildPath "device_profile_ROG-LUCCI.json"
    $deviceProfile = Join-Path -Path $configDir -ChildPath "device_profile.json"
    $deviceConfig = Join-Path -Path $configDir -ChildPath "device_config.json"
    
    $allFound = $true
    
    if (-not (Test-Path $salesrepProfile)) {
        Write-Host "❌ SALESREP profile not found at: $salesrepProfile" -ForegroundColor Red
        $allFound = $false
    }
    else {
        Write-Host "✅ SALESREP profile found" -ForegroundColor Green
        try {
            $profile = Get-Content -Path $salesrepProfile -Raw | ConvertFrom-Json
            $keys = $profile.PSObject.Properties.Name
            $requiredKeys = @("device_id", "username", "onedrive_path", "project_root", "python_path")
            $missingKeys = $requiredKeys | Where-Object { $_ -notin $keys }
            
            if ($missingKeys.Count -gt 0) {
                Write-Host "⚠️ SALESREP profile is missing required keys: $($missingKeys -join ', ')" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "❌ Error parsing SALESREP profile: $_" -ForegroundColor Red
        }
    }
    
    if (-not (Test-Path $rogLucciProfile)) {
        Write-Host "❌ ROG-LUCCI profile not found at: $rogLucciProfile" -ForegroundColor Red
        $allFound = $false
    }
    else {
        Write-Host "✅ ROG-LUCCI profile found" -ForegroundColor Green
        try {
            $profile = Get-Content -Path $rogLucciProfile -Raw | ConvertFrom-Json
            $keys = $profile.PSObject.Properties.Name
            $requiredKeys = @("device_id", "username", "onedrive_path", "project_root", "python_path")
            $missingKeys = $requiredKeys | Where-Object { $_ -notin $keys }
            
            if ($missingKeys.Count -gt 0) {
                Write-Host "⚠️ ROG-LUCCI profile is missing required keys: $($missingKeys -join ', ')" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "❌ Error parsing ROG-LUCCI profile: $_" -ForegroundColor Red
        }
    }
    
    if (-not (Test-Path $deviceProfile)) {
        Write-Host "❌ Active device profile not found at: $deviceProfile" -ForegroundColor Red
        $allFound = $false
    }
    else {
        Write-Host "✅ Active device profile found" -ForegroundColor Green
        try {
            $profile = Get-Content -Path $deviceProfile -Raw | ConvertFrom-Json
            Write-Host "   Current device: $($profile.device_id)" -ForegroundColor Cyan
        }
        catch {
            Write-Host "❌ Error parsing active device profile: $_" -ForegroundColor Red
        }
    }
    
    if (-not (Test-Path $deviceConfig)) {
        Write-Host "❌ Device config not found at: $deviceConfig" -ForegroundColor Red
        $allFound = $false
    }
    else {
        Write-Host "✅ Device config found" -ForegroundColor Green
    }
    
    return $allFound
}

function Test-PythonResolver {
    $pythonResolverScript = Join-Path -Path $projectRoot -ChildPath "tools\resolve_device_profile.py"
    
    if (-not (Test-Path $pythonResolverScript)) {
        Write-Host "❌ Python resolver not found at: $pythonResolverScript" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ Python resolver found" -ForegroundColor Green
    
    # Try to run the Python resolver if Python is available
    if (-not $SkipVenvCheck) {
        $venvPython = Join-Path -Path $projectRoot -ChildPath ".venv\Scripts\python.exe"
        
        if (Test-Path $venvPython) {
            try {
                Write-Host "Running Python resolver test..." -ForegroundColor Cyan
                $output = & $venvPython $pythonResolverScript
                Write-Host "✅ Python resolver executed successfully" -ForegroundColor Green
                return $true
            }
            catch {
                Write-Host "⚠️ Error running Python resolver: $_" -ForegroundColor Yellow
                return $false
            }
        }
        else {
            Write-Host "⚠️ Virtual environment Python not found, skipping resolver test" -ForegroundColor Yellow
        }
    }
    
    return $true
}

function Test-VSCodeIntegration {
    $vscodeDir = Join-Path -Path $projectRoot -ChildPath ".vscode"
    
    if (-not (Test-Path $vscodeDir)) {
        Write-Host "❌ .vscode directory not found at: $vscodeDir" -ForegroundColor Red
        return $false
    }
    
    # Check settings.json
    $settingsFile = Join-Path -Path $vscodeDir -ChildPath "settings.json"
    $settingsValid = $false
    
    if (Test-Path $settingsFile) {
        Write-Host "✅ settings.json found" -ForegroundColor Green
        try {
            $settings = Get-Content -Path $settingsFile -Raw | ConvertFrom-Json
            
            # Check if cross-device settings are present
            if ($settings.PSObject.Properties.Name -contains "crossDevice.enabled") {
                Write-Host "✅ Cross-device settings found in settings.json" -ForegroundColor Green
                $settingsValid = $true
            }
            else {
                Write-Host "❌ Cross-device settings not found in settings.json" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "❌ Error parsing settings.json: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "❌ settings.json not found at: $settingsFile" -ForegroundColor Red
    }
    
    # Check tasks.json
    $tasksFile = Join-Path -Path $vscodeDir -ChildPath "tasks.json"
    $tasksValid = $false
    
    if (Test-Path $tasksFile) {
        Write-Host "✅ tasks.json found" -ForegroundColor Green
        try {
            $tasks = Get-Content -Path $tasksFile -Raw | ConvertFrom-Json
            
            # Check if cross-device tasks are present
            $deviceTasks = $tasks.tasks | Where-Object { $_.label -like "*Device*" }
            
            if ($deviceTasks.Count -gt 0) {
                Write-Host "✅ Device-related tasks found in tasks.json: $($deviceTasks.Count) tasks" -ForegroundColor Green
                $tasksValid = $true
            }
            else {
                Write-Host "❌ No device-related tasks found in tasks.json" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "❌ Error parsing tasks.json: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "❌ tasks.json not found at: $tasksFile" -ForegroundColor Red
    }
    
    return $settingsValid -and $tasksValid
}

function Test-PathResolution {
    # Only test path resolution if we can import the required modules
    if (-not (Import-RequiredModules)) {
        Write-Host "⚠️ Skipping path resolution tests due to missing modules" -ForegroundColor Yellow
        return $false
    }
    
    $success = $true
    
    # Test OneDrive path resolution
    try {
        $onedrivePath = Get-OneDrivePath
        
        if ($onedrivePath -and (Test-Path $onedrivePath)) {
            Write-Host "✅ OneDrive path resolved: $onedrivePath" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Failed to resolve OneDrive path" -ForegroundColor Red
            $success = $false
        }
    }
    catch {
        Write-Host "❌ Error in OneDrive path resolution: $_" -ForegroundColor Red
        $success = $false
    }
    
    # Test project root resolution
    try {
        $projectRootPath = Get-ProjectRootPath
        
        if ($projectRootPath -and (Test-Path $projectRootPath)) {
            Write-Host "✅ Project root resolved: $projectRootPath" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Failed to resolve project root path" -ForegroundColor Red
            $success = $false
        }
    }
    catch {
        Write-Host "❌ Error in project root resolution: $_" -ForegroundColor Red
        $success = $false
    }
    
    # Test current device detection
    try {
        $device = Get-CurrentDevice
        
        if ($device) {
            Write-Host "✅ Current device detected: $device" -ForegroundColor Green
            
            # Check if device matches the current computer name
            if ($device -eq $env:COMPUTERNAME -or $env:COMPUTERNAME -like "*$device*") {
                Write-Host "✅ Device name matches computer name" -ForegroundColor Green
            }
            else {
                Write-Host "⚠️ Device name ($device) doesn't match computer name ($env:COMPUTERNAME)" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "❌ Failed to detect current device" -ForegroundColor Red
            $success = $false
        }
    }
    catch {
        Write-Host "❌ Error in device detection: $_" -ForegroundColor Red
        $success = $false
    }
    
    return $success
}

# Main test execution
Write-Host "======================================================" -ForegroundColor Green
Write-Host "      CROSS-DEVICE COMPATIBILITY TEST                  " -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host "Device: $env:COMPUTERNAME | User: $env:USERNAME | Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "------------------------------------------------------" -ForegroundColor Green

Write-Host "`nTEST 1: Device Profiles" -ForegroundColor Cyan
$profilesTest = Test-DeviceProfiles
Write-Host "------------------------------------------------------" -ForegroundColor Green

Write-Host "`nTEST 2: Python Resolver" -ForegroundColor Cyan
$pythonTest = Test-PythonResolver
Write-Host "------------------------------------------------------" -ForegroundColor Green

Write-Host "`nTEST 3: VS Code Integration" -ForegroundColor Cyan
$vscodeTest = Test-VSCodeIntegration
Write-Host "------------------------------------------------------" -ForegroundColor Green

Write-Host "`nTEST 4: Path Resolution" -ForegroundColor Cyan
$pathTest = Test-PathResolution
Write-Host "------------------------------------------------------" -ForegroundColor Green

# Summary
Write-Host "`nTEST SUMMARY:" -ForegroundColor Cyan
if ($profilesTest) {
    Write-Host "Device Profiles:     ✅ PASSED" -ForegroundColor Green
}
else {
    Write-Host "Device Profiles:     ❌ FAILED" -ForegroundColor Red
}

if ($pythonTest) {
    Write-Host "Python Resolver:     ✅ PASSED" -ForegroundColor Green
}
else {
    Write-Host "Python Resolver:     ❌ FAILED" -ForegroundColor Red
}

if ($vscodeTest) {
    Write-Host "VS Code Integration: ✅ PASSED" -ForegroundColor Green
}
else {
    Write-Host "VS Code Integration: ❌ FAILED" -ForegroundColor Red
}

if ($pathTest) {
    Write-Host "Path Resolution:     ✅ PASSED" -ForegroundColor Green
}
else {
    Write-Host "Path Resolution:     ❌ FAILED" -ForegroundColor Red
}

$overallResult = $profilesTest -and $pythonTest -and $vscodeTest -and $pathTest
if ($overallResult) {
    Write-Host "`nOVERALL RESULT: PASSED ✅" -ForegroundColor Green
}
else {
    Write-Host "`nOVERALL RESULT: FAILED ❌" -ForegroundColor Red
}

if (-not $overallResult) {
    Write-Host "`nRecommendations:" -ForegroundColor Yellow
    
    if (-not $profilesTest) {
        Write-Host "- Run 'Set Up Cross-Device Environment' task to set up device profiles" -ForegroundColor Yellow
    }
    
    if (-not $pythonTest) {
        Write-Host "- Check Python installation and virtual environment" -ForegroundColor Yellow
    }
    
    if (-not $vscodeTest) {
        Write-Host "- Run 'Update VS Code for Cross-Device' task to configure VS Code" -ForegroundColor Yellow
    }
    
    if (-not $pathTest) {
        Write-Host "- Check DevicePathResolver.ps1 and ensure device detection works" -ForegroundColor Yellow
        Write-Host "- Run 'Detect and Configure Device' task" -ForegroundColor Yellow
    }
}

# Export results to log file
$logDir = Join-Path -Path $projectRoot -ChildPath "logs"
if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory -Force | Out-Null
}

$logFile = Join-Path -Path $logDir -ChildPath "device_compatibility_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Patch: Use if/else instead of unsupported ternary operator
if ($profilesTest) { $profilesResult = 'PASSED' } else { $profilesResult = 'FAILED' }
if ($pythonTest) { $pythonResult = 'PASSED' } else { $pythonResult = 'FAILED' }
if ($vscodeTest) { $vscodeResult = 'PASSED' } else { $vscodeResult = 'FAILED' }
if ($pathTest) { $pathResult = 'PASSED' } else { $pathResult = 'FAILED' }
if ($overallResult) { $overallResultStr = 'PASSED' } else { $overallResultStr = 'FAILED' }

$logContent = @"
CROSS-DEVICE COMPATIBILITY TEST RESULTS
=======================================
Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Device: $env:COMPUTERNAME
User: $env:USERNAME

TEST RESULTS:
------------
Device Profiles:     $profilesResult
Python Resolver:     $pythonResult
VS Code Integration: $vscodeResult
Path Resolution:     $pathResult

OVERALL RESULT: $overallResultStr
"@

$logContent | Out-File -FilePath $logFile
Write-Host "`nTest results saved to: $logFile" -ForegroundColor Cyan

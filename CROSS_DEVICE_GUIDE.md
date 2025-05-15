# Cross-Device OneDrive Automation

This document explains how to use the OneDrive automation tools across multiple devices.

## Overview

This project now includes a comprehensive cross-device path resolution system that automatically detects which device you're using and uses the correct paths. This enables seamless transitions between your work desktop (username: samq) and laptop (username: samqu).

## Device Configuration

The following devices are currently configured:

| Device ID | Username | OneDrive Path |
|-----------|----------|---------------|
| DESKTOP-ACER | samq | C:\Users\samq\OneDrive - Digital Age Marketing Group |
| LAPTOP-ASUS | samqu | C:\Users\samqu\OneDrive - Digital Age Marketing Group |

## Getting Started on a New Device

1. First, clone or sync the repository to your device
2. Run `CrossDeviceLauncher.bat` to automatically detect your device
3. Select option 7 to register your device
4. From the menu, select options as needed

## How It Works

### Automatic Path Resolution

The system includes two key components:

1. **PowerShell Path Resolver**: `tools\DevicePathResolver.ps1`
   - Used by PowerShell scripts to automatically detect the correct OneDrive path
   - Can be dot-sourced from any PowerShell script

2. **Python Path Resolver**: `tools\device_path_resolver.py`
   - Used by Python scripts to automatically detect the correct OneDrive path
   - Can be imported from any Python script

### OneDrive Path Detection Logic

The path resolvers use the following methods to determine the correct OneDrive path:

1. First, detect the device by computer name or username
2. Look up the device-specific OneDrive path
3. If device is unknown, try common OneDrive paths
4. If all else fails, use the current directory

### Cross-Device Virtual Environment

When working with Python virtual environments across devices:

1. Run `UpdateVenvCrossDevice.bat` to create device-agnostic activation scripts
2. Use `CrossDeviceLauncher.bat` to activate the virtual environment
3. The activation scripts use relative paths instead of absolute paths

## Sample Usage

### PowerShell Example

```powershell
# Load the device path resolver
. $PSScriptRoot\tools\DevicePathResolver.ps1

# Get the correct OneDrive path for this device
$onedrivePath = Get-OneDrivePath
Write-Host "OneDrive path: $onedrivePath"

# Get the project root path
$projectRoot = Get-ProjectRootPath
Write-Host "Project root: $projectRoot"
```

### Python Example

```python
# Import the device path resolver
from tools.device_path_resolver import get_onedrive_path, get_project_root_path

# Get the correct OneDrive path for this device
onedrive_path = get_onedrive_path()
print(f"OneDrive path: {onedrive_path}")

# Get the project root path
project_root = get_project_root_path()
print(f"Project root: {project_root}")
```

## Adding a New Device

To add a new device to the configuration:

1. Open `tools\DevicePathResolver.ps1` and add your device to the `$DEVICE_CONFIGS` hashtable
2. Open `tools\device_path_resolver.py` and add your device to the `DEVICE_CONFIGS` dictionary
3. Run `CrossDeviceLauncher.bat` and select option 7 to register your device

## Troubleshooting

If you encounter any issues with path resolution:

1. Run `CrossDeviceLauncher.bat` and check the detected OneDrive path
2. If incorrect, register your device using option 7
3. If still incorrect, manually add your device configuration to the path resolvers

For virtual environment issues:
1. Run `UpdateVenvCrossDevice.bat` to recreate the activation scripts
2. Use `fix_venv_activation.bat` to regenerate the virtual environment files

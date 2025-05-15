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

## VS Code Integration

This project includes automated VS Code integration for seamless cross-device development:

1. **Automatic Device Detection**: When opening the project in VS Code, it automatically detects and configures for the current device
2. **Path Resolution**: All VS Code tasks use device-agnostic paths
3. **Cross-Device Terminal**: The integrated terminal is configured with proper path resolution

### VS Code Tasks

Open the Command Palette (`Ctrl+Shift+P`) and type "Tasks: Run Task" to see the available tasks:

| Task | Description |
|------|-------------|
| Detect and Configure Device | Automatically runs when VS Code opens |
| Start Development Environment | Opens a new PowerShell terminal with the environment activated |
| Run OneDrive Automation | Runs the automation script |
| Test Cross-Device Compatibility | Tests path resolution |
| Update Virtual Environment for Cross-Device | Updates virtual env scripts for cross-device compatibility |
| Scan for Hardcoded Paths | Scans for hardcoded device-specific paths |
| Fix Hardcoded Paths | Automatically fixes hardcoded paths |

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

### Hardcoded Path Detection and Fixing

The project includes tools to scan for and fix hardcoded paths:

1. **Path Scanning**: Tools to scan for hardcoded user paths that could break cross-device compatibility
2. **Automatic Fixing**: Tools to automatically convert hardcoded paths to device-agnostic paths
3. **Pre-commit Hook**: Optional Git hook to prevent committing hardcoded paths

Available path scanning tools:

1. **PowerShell Scanner**: `tools\Scan_For_Hardcoded_Paths.ps1`
   - Scans PowerShell, batch, and text files
   - Use with `-Fix` parameter to automatically fix issues

2. **Python Scanner**: `tools\scan_hardcoded_paths.py`
   - Scans Python and other text files
   - Use with `--fix` parameter to automatically fix issues

3. **Combined Scanner**: `ScanPaths.bat`
   - Runs both scanners for comprehensive scanning
   - Use with `--fix` parameter to automatically fix issues

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

## Cross-Device Best Practices

1. **Use Path Resolver Functions**: Never hardcode user paths

   ```powershell
   # PowerShell - Good
   $projectRoot = Get-ProjectRootPath
   $filePath = Join-Path -Path $projectRoot -ChildPath "data\output.json"

   # PowerShell - Bad
   $filePath = "C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon\data\output.json"
   ```

   ```python
   # Python - Good
   from tools.device_path_resolver import get_project_root_path
   import os

   project_root = get_project_root_path()
   file_path = os.path.join(project_root, "data/output.json")

   # Python - Bad
   file_path = "C:/Users/samq/OneDrive - Digital Age Marketing Group/Desktop/Local Py/Work Projects/bar-directory-recon/data/output.json"
   ```

2. **Use the Virtual Environment**: Always activate the cross-device virtual environment

3. **Scan for Hardcoded Paths**: Use the provided scanning tools regularly
   - Before committing code
   - After merging changes
   - When moving to a new device

4. **Pre-commit Hook**: Consider enabling the pre-commit hook to prevent committing hardcoded paths

   ```bash
   # Copy the hook to Git hooks directory
   copy pre-commit-hooks\check_hardcoded_paths.py .git\hooks\pre-commit
   ```

## Using the New CrossDeviceManager.bat

We've now added a comprehensive management tool that consolidates all cross-device functionality into a single interface:

```batch
CrossDeviceManager.bat
```

This new tool provides a menu-driven interface to:

1. **Check device compatibility status**: Runs a full diagnostic test of your environment
2. **Fix virtual environment paths**: Ensures Python virtual environment works across devices
3. **Scan for hardcoded paths**: Identifies paths that might cause cross-device issues
4. **Fix hardcoded paths**: Automatically fixes detected path issues
5. **Switch to another device**: Guides you through transitioning to another device
6. **Run full system check**: Performs comprehensive system verification
7. **Update VS Code configuration**: Ensures VS Code is properly configured
8. **Run OneDrive automation**: Executes the main OneDrive automation script

### Usage

Simply run `CrossDeviceManager.bat` and follow the menu prompts. This provides a more streamlined experience compared to using individual scripts.

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

For hardcoded path issues:

1. Run `ScanPaths.bat` to identify hardcoded paths
2. Run `ScanPaths.bat --fix` to automatically fix detected issues
3. For paths that can't be automatically fixed, follow the Cross-Device Best Practices section

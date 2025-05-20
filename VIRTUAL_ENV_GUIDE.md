# Virtual Environment Setup & Troubleshooting

This document provides instructions on how to set up and use the Python virtual environment for the OneDrive Automation project.

## 1. Virtual Environment Files

The project includes several scripts to help manage the virtual environment:

- **activate_venv.bat**: Simple batch file to activate the virtual environment in CMD
- **fix_venv_activation.bat**: Repairs broken activation scripts in the virtual environment
- **InstallDependencies.bat**: Installs required Python packages in the virtual environment
- **RunDevelopment.bat**: Provides a menu-driven interface with the virtual environment activated
- **StartDevPowerShell.bat**: Launches a PowerShell session with the virtual environment activated
- **ActivateVenv.ps1**: PowerShell script with development utilities
- **tools/VirtualEnvHelper.ps1**: PowerShell library for virtual environment management

## 2. Common Issues

### 2.1. "Virtual environment cannot be activated"

This usually happens because the activation scripts are missing or corrupted. To fix:

1. Run `fix_venv_activation.bat` to regenerate the activation scripts
2. If that doesn't work, run `UpdateVenvScripts.bat` to update all virtual environment scripts

### 2.2. "Missing dependencies"

If the application shows errors about missing modules:

1. Run `InstallDependencies.bat` to install all required packages
2. Activate the virtual environment first, then run `pip install -r requirements.txt`

### 2.3. "Running scripts with incorrect Python version"

Make sure you're using the virtual environment's Python:

1. Activate the virtual environment using one of the methods below
2. Verify the Python path with `where python` (CMD) or `Get-Command python` (PowerShell)

### 2.4. "Cross-device path issues"

If you're working on both your desktop (samq) and laptop (samqu), you may encounter path issues:

1. Run `CrossDeviceLauncher.bat` to use a device-agnostic launcher
2. Run `UpdateVenvCrossDevice.bat` to update your virtual environment scripts for cross-device compatibility
3. See `CROSS_DEVICE_GUIDE.md` for complete details on cross-device usage

## 3. Activating the Virtual Environment

### 3.1. Using CMD/Command Prompt

```bat
# Simple activation
activate_venv.bat

# Full development environment with menu
RunDevelopment.bat
```

### 3.2. Using PowerShell

```powershell
# Start a development PowerShell session
.\StartDevPowerShell.bat

# Or from an existing PowerShell window
.\ActivateVenv.ps1
```

## 4. Virtual Environment Commands

When using the PowerShell development environment (via `StartDevPowerShell.bat` or `ActivateVenv.ps1`),
the following commands are available:

```powershell
# Run the main automation script
Run-OneDriveAutomation

# Run the cleanup script
Run-OneDriveCleanup

# Run all project tests
Run-Tests

# Run Git repository cleanup
Run-GitCleanup

# Scan for secrets in the codebase
Run-SecretsScanner

# Show all available commands
Show-Commands
```

## 5. Advanced: Recreating the Virtual Environment

If you need to completely recreate the virtual environment:

1. Delete the `.venv` folder
2. Run `UpdateVenvScripts.bat` to create a new virtual environment
3. Run `InstallDependencies.bat` to install all required packages

## 6. Troubleshooting PowerShell Execution Policy

If you encounter execution policy errors in PowerShell:

```powershell
# Check the current execution policy
Get-ExecutionPolicy

# Set a more permissive policy (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 7. Cross-Device Virtual Environment

When working across multiple devices (desktop/laptop), special tools are provided:

### 7.1. Using CrossDeviceLauncher.bat

```bat
# Run the launcher
CrossDeviceLauncher.bat

# From the menu, select:
# - Option 3: Activate Python Virtual Environment
# - Option 4: Start PowerShell Development Environment
# - Option 7: Register This Device (first time only)
```

### 7.2. Updating for Cross-Device Compatibility

```bat
# Updates virtual environment scripts to work on any device
UpdateVenvCrossDevice.bat

# Validates cross-device setup
ValidateCrossDeviceSetup.bat
```

### 7.3. Understanding Device-Specific Configuration

The system creates a configuration file at `config\device_config.json` that stores device-specific settings. This is managed automatically, but you can view it to troubleshoot cross-device issues.

See the `CROSS_DEVICE_GUIDE.md` file for complete details on cross-device compatibility.

Or run scripts with the bypass flag:

```powershell
powershell -ExecutionPolicy Bypass -File .\ActivateVenv.ps1
```

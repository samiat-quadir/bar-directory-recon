# OneDrive Automation Solution

A comprehensive PowerShell automation solution for managing OneDrive-based development environments.

## Overview

This automation solution addresses common challenges with using OneDrive for development:

1. 🔍 **Path Resolution**: Correctly identifies and resolves OneDrive paths across different devices
2. 📁 **Folder Standardization**: Creates and maintains a consistent folder structure
3. 🔄 **Cross-Device Synchronization**: Ensures environment parity (Python packages, VS Code extensions, etc.)
4. 🐙 **Git Repository Management**: Detects and resolves Git repository conflicts
5. 🔒 **Secrets Scanning**: Identifies sensitive information in files
6. ⏰ **Scheduled Tasks**: Automates maintenance operations

## Requirements

- Windows 10/11 with PowerShell 5.1 or higher
- OneDrive installed and configured
- Python 3.11+ (for Python automation and scripts)
- Administrator rights (for scheduled tasks)

## Getting Started

### Virtual Environment Setup

This project uses a Python virtual environment to manage dependencies. You have several ways to activate it:

#### For CMD/Command Prompt Users

```bat
# One-time activation
activate_venv.bat

# For a full development environment with a menu
RunDevelopment.bat
```

#### For PowerShell Users

```powershell
# Start a development PowerShell session with virtual environment
.\StartDevPowerShell.bat

# Or from an existing PowerShell window
.\ActivateVenv.ps1
```

#### First-Time Setup

If you need to recreate or fix the virtual environment:

```bat
# Fix activation scripts
fix_venv_activation.bat

# Install all dependencies
InstallDependencies.bat
```

### Quick Start

1. Run `RunOneDriveAutomation.bat` and select an option from the menu
2. For first-time setup, choose option 7 "Run in preview mode" to see what changes would be made
3. Then run option 1 "Run all tasks" to apply all changes

### Command-Line Usage

The main script can be run directly from PowerShell:

```powershell
# Run all tasks
.\OneDriveAutomation.ps1 -Tasks All

# Run specific task with preview (no changes)
.\OneDriveAutomation.ps1 -Tasks StandardizeFolders -WhatIf

# Specify custom OneDrive path
.\OneDriveAutomation.ps1 -OneDrivePath "D:\Custom OneDrive Path"
```

## Available Tasks

| Task | Description |
|------|-------------|
| `ResolvePath` | Detects and validates OneDrive path |
| `StandardizeFolders` | Creates standard folder structure and organizes files |
| `SyncEnvironment` | Synchronizes development environments across devices |
| `GitCleanup` | Manages Git repositories and resolves conflicts |
| `ScanSecrets` | Scans for sensitive information in files |
| `ScheduleTasks` | Sets up scheduled automation tasks |
| `All` | Runs all tasks in sequence |

## Configuration

The scripts use default values that can be overridden:

- OneDrive path: `C:\Users\samq\OneDrive - Digital Age Marketing Group`
- Primary repo path: `C:\bar-directory-recon`
- Device ID: Uses computer name by default

## Utility Tools

The solution includes several utility scripts in the `tools` folder:

- `consolidate_env_files.ps1`: Merges .env files from different devices
- `git_repo_cleanup.ps1`: Manages Git repositories in OneDrive
- `secrets_scan.py`: Python-based scanner for sensitive information
- `VirtualEnvHelper.ps1`: Manages Python virtual environments

## Troubleshooting

- **Path Issues**: Use the `ResolvePath` task to verify OneDrive path detection
- **Permission Errors**: Run as Administrator for tasks that require elevated privileges
- **Synchronization Conflicts**: Run `GitCleanup` to resolve Git-related issues
- **Log Files**: Check the `Logs` folder for detailed execution logs
- **Virtual Environment Issues**: Use `fix_venv_activation.bat` to repair activation scripts

## License

MIT

## Author

Created with GitHub Copilot

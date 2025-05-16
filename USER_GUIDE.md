# OneDrive Automation - User Guide

## Initial Setup

The OneDrive Automation tool needs to be configured with the correct paths for your environment. Follow these steps to get started:

1. Run the `SetupOneDriveAutomation.bat` script to configure your paths
2. Verify the configuration by running the tool in preview mode
3. Run the full automation to organize your OneDrive folders

### Step 1: Configuration

1. Double-click `SetupOneDriveAutomation.bat`
2. Enter your OneDrive path or press Enter to accept the default
3. Enter your primary repository path or press Enter to use the current directory
4. The script will verify the paths and update your configuration

### Step 2: Run the Automation

After setup, you can use the `RunOneDriveAutomation.bat` launcher to perform automation tasks:

1. Double-click `RunOneDriveAutomation.bat`
2. Choose from the available options:
   - Option 1: Run all tasks
   - Option 2: Fix folder structure only
   - Option 3: Sync environment between devices
   - Option 4: Cleanup Git repositories
   - Option 5: Scan for secrets
   - Option 6: Setup scheduled tasks
   - Option 7: Run in preview mode (no changes)

## Common Tasks

### Standardizing Folder Structure

The tool creates and maintains a standard folder structure in your OneDrive:

- **Scripts**: PowerShell, Python, and other script files
- **Logs**: Log files and output records
- **Configs**: Configuration files, including .env files
- **Docs**: Documentation, spreadsheets, and text-based documents
- **Projects**: Project-related files
- **Images**: Image files
- **Archives**: Archived files and backups
- **Other**: Files that don't fit elsewhere

Files in the root of your OneDrive will be automatically organized into these folders based on their file extension.

### Environment Synchronization

Running the environment sync task will:

1. Export your installed Python packages to a requirements file
2. Export your VS Code extensions to a list
3. Consolidate .env files from different devices
4. Compare your environment with other devices
5. Generate reports of any differences

Running this on multiple devices helps keep your development environments in sync.

### Git Repository Management

The Git repository management function will:

1. Detect and archive any Git repositories stored in OneDrive
2. Verify your primary Git repository
3. Fetch and pull updates from remote repositories
4. Push any local changes to remote repositories

This helps prevent Git-related issues that can occur when repositories are synchronized by OneDrive.

### Secrets Scanning

The secrets scanner checks for sensitive information in your OneDrive files:

1. Passwords and credentials
2. API keys and tokens
3. Connection strings
4. Private keys and secrets

Results are logged and reported, allowing you to secure sensitive information before it's accidentally shared.

### Scheduled Tasks

Setting up scheduled tasks (requires administrator rights) will:

1. Create a daily task for Git operations
2. Ensure OneDrive is regularly organized
3. Maintain environment synchronization

## Troubleshooting

### Common Issues

1. **Path Not Found**: Make sure your OneDrive path is correctly specified in the configuration
2. **Administrator Privileges**: Run as administrator when setting up scheduled tasks
3. **Git Not Found**: Ensure Git is installed and in your PATH environment variable
4. **Python Not Found**: Make sure Python is installed and in your PATH environment variable

### Log Files

The tool generates detailed log files in the same directory as the script:

- `OneDriveAutomation_YYYYMMDD_HHMMSS.log`: Complete execution log
- `OneDriveAutomation_YYYYMMDD_HHMMSS_errors.log`: Errors-only log

These logs can help diagnose issues with the automation.

## Advanced Usage

### Command-Line Parameters

The main script can be run directly with custom parameters:

```powershell
.\OneDriveAutomation.ps1 -Tasks All,ResolvePath,StandardizeFolders -OneDrivePath "D:\Custom Path" -PrimaryRepoPath "C:\Git\MyRepo" -DeviceId "WorkPC" -WhatIf
```

Available parameters:

- `-Tasks`: Comma-separated list of tasks to run
- `-OneDrivePath`: Path to your OneDrive folder
- `-PrimaryRepoPath`: Path to your primary Git repository
- `-DeviceId`: Identifier for the current device
- `-WhatIf`: Run in preview mode without making changes

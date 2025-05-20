# Device Transition Guide

This document provides step-by-step instructions for switching between devices while working on this project.

## When Moving from Work Desktop to Laptop

1. **Commit and Push Your Changes**

   ```powershell
   git add .
   git commit -m "Work desktop checkpoint before device transition"
   git push
   ```

2. **On Your Laptop**
   - Pull the latest changes:

   ```powershell
   git pull
   ```

   - Run the device detection:

   ```powershell
   .\CrossDeviceLauncher.bat
   ```

   - Or open VS Code which will auto-detect:

   ```powershell
   .\OpenInVSCode.bat
   ```

3. **Verify Virtual Environment**
   - Update the virtual environment for cross-device compatibility:

   ```powershell
   .\UpdateVenvCrossDevice.bat
   ```

4. **Scan for Hardcoded Paths**
   - Check for any paths that might cause issues:

   ```powershell
   .\ScanPaths.bat
   ```

   - Fix any detected issues:

   ```powershell
   .\ScanPaths.bat --fix
   ```

## When Moving from Laptop to Work Desktop

1. **Commit and Push Your Changes**

   ```powershell
   git add .
   git commit -m "Laptop checkpoint before device transition"
   git push
   ```

2. **On Your Work Desktop**
   - Pull the latest changes:

   ```powershell
   git pull
   ```

   - Run the device detection:

   ```powershell
   .\CrossDeviceLauncher.bat
   ```

   - Or open VS Code which will auto-detect:

   ```powershell
   .\OpenInVSCode.bat
   ```

3. **Verify Virtual Environment**
   - Update the virtual environment for cross-device compatibility:

   ```powershell
   .\UpdateVenvCrossDevice.bat
   ```

4. **Scan for Hardcoded Paths**
   - Check for any paths that might cause issues:

   ```powershell
   .\ScanPaths.bat
   ```

   - Fix any detected issues:

   ```powershell
   .\ScanPaths.bat --fix
   ```

## Troubleshooting Device Transition Issues

### Path Resolution Issues

If you're experiencing path-related errors after switching devices:

1. **Run the Path Test Tool**

   ```powershell
   .\Test-CrossDevicePaths.ps1 -Verbose
   ```

2. **Register Your Device**
   - Run `CrossDeviceLauncher.bat` and select option 7 to register your device

3. **Check for Hardcoded Paths**
   - Run `ScanPaths.bat` to find and fix hardcoded paths

### Virtual Environment Issues

If your virtual environment isn't working correctly:

1. **Update Activation Scripts**

   ```powershell
   .\UpdateVenvCrossDevice.bat
   ```

2. **Recreate if Necessary**

   ```powershell
   .\fix_venv_activation.bat
   ```

### Git Issues

If you're having Git-related issues during device transition:

1. **Configure Git for Cross-Device Work**

   ```powershell
   git config --local core.autocrlf input
   git config --local merge.ours.driver true
   ```

2. **Install Git Hooks**

   ```powershell
   .\install-git-hooks.bat
   ```

## Best Practices for Cross-Device Development

1. **Always Use Path Resolver Functions**
   - Never hardcode user-specific paths
   - Use `Get-ProjectRootPath` or `get_project_root_path()` to get the correct base path

2. **Regular Scanning**
   - Run `ScanPaths.bat` regularly to check for hardcoded paths
   - Use VS Code tasks for automatic checks

3. **Use VS Code for Consistent Editor Experience**
   - VS Code has been configured for cross-device compatibility
   - Tasks will run automatically when opening the project

4. **Update Both Path Resolvers**
   - When adding a new device, update both PowerShell and Python resolvers
   - Keep them in sync for consistent behavior

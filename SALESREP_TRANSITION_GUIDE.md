# SALESREP Device Transition Guide

**Date:** May 19, 2025
**Author:** GitHub Copilot
**Topic:** Instructions for continuing work on SALESREP device with Copilot Agent

## Overview

This guide provides detailed instructions for transitioning from your ROG-LUCCI laptop to the SALESREP device while maintaining seamless GitHub Copilot Agent integration in VS Code.

## Before Leaving ROG-LUCCI

1. **Commit and Push All Changes**

   ```powershell
   # Open the CrossDeviceManager for safe commits
   .\CrossDeviceManager.bat
   # Select option 9 for "Safe commit and push"
   ```

   Alternatively, use the safe commit script directly:

   ```powershell
   .\safe_commit_push.bat
   ```

2. **Create a Transition Checkpoint**

   Add a descriptive commit message that indicates you're transitioning:

   ```powershell
   git add .
   git commit -m "ROG-LUCCI checkpoint before transition to SALESREP"
   git push
   ```

## On SALESREP Device

### Initial Setup

1. **Clone or Pull the Repository**

   If not already cloned:

   ```powershell
   git clone <your-repository-url> bar-directory-recon
   cd bar-directory-recon
   ```

   If already cloned:

   ```powershell
   cd path\to\bar-directory-recon
   git pull
   ```

2. **Run the Cross-Device Launcher**

   ```powershell
   .\CrossDeviceLauncher.bat
   ```

   This will detect your device and set up the appropriate environment.

3. **Fix Device Path Resolver**

   The `device_path_resolver.py` file contains some syntax errors that need to be fixed. First:

   ```powershell
   # Run the scanner to identify issues
   .\ScanPaths.bat

   # Then run the auto-fix
   .\ScanPaths.bat --fix
   ```

   If the auto-fix doesn't resolve all issues, you'll need to manually edit the file:

   ```powershell
   code tools\device_path_resolver.py
   ```

   Fix the following specific issues:
   - Update the code to properly add "SALESREP" to the DEVICE_CONFIGS dictionary
   - Fix the get_onedrive_path function which appears to be corrupted with nested function calls
   - Update any references to get_onedrive_path that have similar issues

4. **Verify Device Configuration**

   ```powershell
   # Option 1 in CrossDeviceManager.bat
   # Or manually:
   powershell -ExecutionPolicy Bypass -NoProfile -File ".\Test-CrossDevicePaths.ps1" -Verbose
   ```

5. **Update Virtual Environment for Cross-Device Compatibility**

   ```powershell
   .\Fix-VenvPath.bat
   ```

   This updates the virtual environment activation scripts to work on SALESREP.

6. **Register SALESREP Device Profile**

   ```powershell
   python tools\create_device_profile.py --device SALESREP
   ```

### VS Code and GitHub Copilot Agent Setup

1. **Open VS Code on SALESREP**

   ```powershell
   .\OpenInVSCode.bat
   ```

   This will open VS Code with the correct environment settings.

2. **Verify GitHub Copilot Extension**

   - Ensure the GitHub Copilot extension is installed and signed in
   - Check for GitHub Copilot Chat extension as well

3. **Create a Device Transition Message for Copilot**

   When starting a new Copilot Chat conversation, include this context:

   ```
   I've transitioned from my ROG-LUCCI device to SALESREP.
   I'm continuing work on the bar-directory-recon project.
   The project uses a cross-device compatibility system for handling paths.
   My username on this device is "samq" (instead of "samqu" on ROG-LUCCI).
   The project uses a device_path_resolver.py file for path resolution.
   ```

4. **Use VS Code Tasks**

   VS Code tasks are already configured for cross-device compatibility:
   - `Detect and Configure Device` - Run automatically when opening the folder
   - `Start Development Environment` - Opens a terminal with proper environment
   - `Test Cross-Device Compatibility` - Verifies path resolution
   - `Scan for Hardcoded Paths` - Scans for path issues
   - `Fix Hardcoded Paths` - Automatically fixes path issues

## Continuing Your Work

1. **Use CrossDeviceManager.bat**

   This central interface provides all the tools you need for cross-device operations:

   ```powershell
   .\CrossDeviceManager.bat
   ```

   Key options:
   - Option 1: Check device compatibility status
   - Option 2: Fix virtual environment paths
   - Option 3/4: Scan/fix hardcoded paths
   - Option 6: Run full system check
   - Option 9: Safe commit and push

2. **Work with Copilot Agent**

   When asking Copilot to generate code:

   - Specify that you're on the "SALESREP" device
   - Mention the username is "samq"
   - Request device-agnostic paths using functions from device_path_resolver.py
   - Use the following pattern for Python code:

   ```python
   from tools.device_path_resolver import get_project_root_path

   # Use device-agnostic path
   project_path = get_project_root_path()
   data_path = os.path.join(project_path, "data")
   ```

3. **Periodically Run Compatibility Checks**

   ```powershell
   .\Test-CrossDevicePaths.ps1 -Verbose
   ```

   Or use VS Code Task "Test Cross-Device Compatibility"

4. **When Finishing Work**

   Use the safe commit process to ensure no device-specific paths are committed:

   ```powershell
   .\safe_commit_push.bat
   ```

   Or use option 9 in CrossDeviceManager.bat

## Debugging Path Issues

If you encounter path-related problems:

1. **Check Device Detection**

   ```powershell
   python tools\device_path_resolver.py
   ```

   Ensure the output shows "SALESREP" or your computer name.

2. **Update Device Config**

   If SALESREP is not being detected:

   ```powershell
   python tools\device_path_resolver.py --register --force
   ```

3. **Fix Common OneDrive Path Issues**

   If you encounter errors in the get_onedrive_path function, edit the device_path_resolver.py file to repair the function:

   ```python
   def get_onedrive_path() -> str:
       """
       Get the correct OneDrive path for the current device.

       Returns:
           str: The detected OneDrive path
       """
       # Try to detect automatically first
       device = get_current_device()

       if device and device in DEVICE_CONFIGS:
           username = DEVICE_CONFIGS[device]["username"]
           onedrive_folder = DEVICE_CONFIGS[device]["onedrive_folder"]
           path = os.path.join("C:\\", "Users", username, onedrive_folder)

           if os.path.exists(path):
               return path

       # If automatic detection fails, try common locations
       possible_paths = [
           os.path.join("C:\\", "Users", "samq", "OneDrive - Digital Age Marketing Group"),
           os.path.join("C:\\", "Users", "samqu", "OneDrive - Digital Age Marketing Group"),
           os.path.join("C:\\", "Users", os.getlogin(), "OneDrive - Digital Age Marketing Group")
       ]

       for path in possible_paths:
           if os.path.exists(path):
               return path

       # Final fallback
       return os.getcwd()
   ```

---

## Copilot Agent Best Practices

When working with Copilot Agent on the SALESREP device:

1. **Start Each Session with Context**:

   Begin with:

   ```
   I'm working on the bar-directory-recon project on the SALESREP device.
   Username: samq
   The project uses device_path_resolver.py for cross-device compatibility.
   ```

2. **Ask for Device-Agnostic Code**:

   When requesting code, specifically ask for:

   ```
   Please generate code that uses device_path_resolver functions
   for cross-device compatibility.
   ```

3. **For Path Operations**:

   Ask Copilot to:

   ```
   Use get_project_root_path() instead of hardcoded paths.
   ```

4. **When Debugging Path Issues**:

   Tell Copilot:

   ```
   I'm on the SALESREP device (username: samq) and need to
   debug path resolution issues.
   ```

By following these instructions, you'll be able to seamlessly continue your work on the SALESREP device with full GitHub Copilot Agent integration.

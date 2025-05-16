# Cross-Device Development Checklist

Use this checklist to ensure your code is compatible with both work desktop (samq) and laptop (samqu) environments.

## Before Committing Code

- [ ] Run `ScanPaths.bat` to check for hardcoded paths
- [ ] If issues found, run `ScanPaths.bat --fix` to fix them
- [ ] Test code on current device using `Test-CrossDevicePaths.ps1`
- [ ] Ensure virtual environment is cross-device compatible with `UpdateVenvCrossDevice.bat`
- [ ] Verify no device-specific absolute paths are used in your code

## New Files and Scripts

When creating new files, ensure they follow these guidelines:

- [ ] Use path resolver functions instead of hardcoded paths
  - PowerShell: `Get-ProjectRootPath`, `Get-OneDrivePath`
  - Python: `get_project_root_path()`, `get_onedrive_path() <!-- TODO: Use device-agnostic path --> <!-- TODO: Use device-agnostic path --> <!-- TODO: Use device-agnostic path --> <!-- TODO: Use device-agnostic path -->`
- [ ] If the file needs device detection, import the appropriate resolver
  - PowerShell: `. $PSScriptRoot\tools\DevicePathResolver.ps1`
  - Python: `from tools.device_path_resolver import ...`
- [ ] Test the file on your current device
- [ ] Add appropriate entries to `.gitignore` if the file generates device-specific output

## Before Switching Devices

- [ ] Commit and push all changes
- [ ] Run `ValidateCrossDeviceSetup.bat` to ensure everything is properly configured
- [ ] Document any device-specific workarounds in `device_notes.md`

## After Switching Devices

- [ ] Pull the latest changes
- [ ] Run `CrossDeviceLauncher.bat` to detect the new device
- [ ] Run `Test-CrossDevicePaths.ps1` to validate path resolution
- [ ] Check for any hardcoded paths with `ScanPaths.bat`
- [ ] Update virtual environment if needed with `UpdateVenvCrossDevice.bat`

## New Device Setup

If setting up a new device (neither samq nor samqu):

- [ ] Add device configuration to `tools\DevicePathResolver.ps1`
- [ ] Add device configuration to `tools\device_path_resolver.py`
- [ ] Run `CrossDeviceLauncher.bat` and select option 7 to register the device
- [ ] Validate with `Test-CrossDevicePaths.ps1`
- [ ] Document the new device in `docs\cross_device_implementation_summary.yaml`

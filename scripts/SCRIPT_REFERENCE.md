# Script Reference Guide
# Generated: 2025-07-14 12:36:07

This file provides a reference for script locations after reorganization.

## Moved Scripts:
- activate_venv.bat
- AutoTransitionToSALESREP.bat
- CommitRemainingChanges.bat
- CrossDeviceLauncher.bat
- CrossDeviceManager.bat
- cross_device_bootstrap.bat
- Fix-VenvPath.bat
- Fix-VirtualEnvPath.bat
- fix_venv_activation.bat
- FixGitRepository.bat
- FixPathResolverForSALESREP.bat
- install-git-hooks.bat
- InstallDependencies.bat
- OpenInVSCode.bat
- RecreateVenv.bat
- RunAutomation.bat
- RunDevelopment.bat
- RunListDiscovery.bat
- RunOneDriveAdmin.bat
- RunOneDriveAutomation.bat
- safe_commit_push.bat
- ScanPaths.bat
- SetupOneDriveAutomation.bat
- StartDevPowerShell.bat
- SwitchToDevice.bat
- UpdateVenvCrossDevice.bat
- UpdateVenvScripts.bat
- ValidateCrossDeviceSetup.bat
- ActivateVenv.ps1
- AutomationHotkeys.ps1
- OneDriveAutomation.ps1
- OneDriveCleanup.ps1
- onedrive_audit.ps1
- Test-CrossDevicePaths.ps1


## Consolidated Scripts:
- Fix-VenvPath.bat, Fix-VirtualEnvPath.bat, fix_venv_activation.bat â†’ scripts/consolidated_venv_fix.bat

## Script Directory Structure:
All utility scripts are now located in the scripts/ directory with standardized naming:
- snake_case naming convention
- Descriptive names
- Grouped by functionality

To update any references to these scripts in your code or documentation,
use the new paths listed above.

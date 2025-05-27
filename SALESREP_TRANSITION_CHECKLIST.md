# SALESREP Device Transition Checklist

## Before Leaving ROG-LUCCI

- [ ] Commit all changes using safe_commit_push.bat
- [ ] Push changes to remote repository
- [ ] Create a transition checkpoint commit

## Initial Setup on SALESREP

- [ ] Pull latest changes from repository
- [ ] Run FixPathResolverForSALESREP.bat to fix and update device_path_resolver.py
- [ ] Verify path resolution with Test-CrossDevicePaths.ps1
- [ ] Run ScanPaths.bat --fix to correct any hardcoded paths
- [ ] Update virtual environment with Fix-VenvPath.bat
- [ ] Register SALESREP device profile with python tools\create_device_profile.py --device SALESREP
- [ ] Verify device profile creation in config directory

## VS Code and GitHub Copilot Setup

- [ ] Open project with OpenInVSCode.bat
- [ ] Verify GitHub Copilot extension is active
- [ ] Run "Detect and Configure Device" VS Code task
- [ ] Create new Copilot chat with device transition context

## Verify Cross-Device Compatibility

- [ ] Run full system check (option 6 in CrossDeviceManager.bat)
- [ ] Verify OneDrive path resolution
- [ ] Test virtual environment activation
- [ ] Run a sample task to confirm everything works

## Continue Development

- [ ] Use CrossDeviceManager.bat for all cross-device operations
- [ ] Include device context in Copilot prompts
- [ ] Use device-agnostic path functions in all new code
- [ ] Periodically run ScanPaths.bat to catch any hardcoded paths

## When Finished

- [ ] Use safe_commit_push.bat for all commits
- [ ] Create a transition report if needed
- [ ] Document any issues encountered for future reference

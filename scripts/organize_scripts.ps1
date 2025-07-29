# Script Organization and Consolidation
# Moves all batch and PowerShell scripts to scripts/ directory
# Consolidates duplicate functionality

Write-Host "Starting script organization..." -ForegroundColor Green

$rootPath = Split-Path -Parent $PSScriptRoot
$scriptsPath = Join-Path $rootPath "scripts"

# Ensure scripts directory exists
if (-not (Test-Path $scriptsPath)) {
    New-Item -ItemType Directory -Path $scriptsPath -Force
    Write-Host "Created scripts directory" -ForegroundColor Green
}

# Define scripts to move and consolidate
$scriptActions = @(
    # Batch files to move
    @{ Source = "activate_venv.bat"; Target = "scripts/activate_venv.bat"; Action = "MOVE" },
    @{ Source = "AutoTransitionToSALESREP.bat"; Target = "scripts/auto_transition_salesrep.bat"; Action = "MOVE" },
    @{ Source = "CommitRemainingChanges.bat"; Target = "scripts/commit_remaining_changes.bat"; Action = "MOVE" },
    @{ Source = "CrossDeviceLauncher.bat"; Target = "scripts/cross_device_launcher.bat"; Action = "MOVE" },
    @{ Source = "CrossDeviceManager.bat"; Target = "scripts/cross_device_manager.bat"; Action = "MOVE" },
    @{ Source = "cross_device_bootstrap.bat"; Target = "scripts/cross_device_bootstrap.bat"; Action = "MOVE" },
    @{ Source = "Fix-VenvPath.bat"; Target = "scripts/consolidated_venv_fix.bat"; Action = "CONSOLIDATE" },
    @{ Source = "Fix-VirtualEnvPath.bat"; Target = "scripts/consolidated_venv_fix.bat"; Action = "CONSOLIDATE" },
    @{ Source = "fix_venv_activation.bat"; Target = "scripts/consolidated_venv_fix.bat"; Action = "CONSOLIDATE" },
    @{ Source = "FixGitRepository.bat"; Target = "scripts/fix_git_repository.bat"; Action = "MOVE" },
    @{ Source = "FixPathResolverForSALESREP.bat"; Target = "scripts/fix_path_resolver_salesrep.bat"; Action = "MOVE" },
    @{ Source = "install-git-hooks.bat"; Target = "scripts/install_git_hooks.bat"; Action = "MOVE" },
    @{ Source = "InstallDependencies.bat"; Target = "scripts/install_dependencies.bat"; Action = "MOVE" },
    @{ Source = "OpenInVSCode.bat"; Target = "scripts/open_in_vscode.bat"; Action = "MOVE" },
    @{ Source = "RecreateVenv.bat"; Target = "scripts/recreate_venv.bat"; Action = "MOVE" },
    @{ Source = "RunAutomation.bat"; Target = "scripts/run_automation.bat"; Action = "MOVE" },
    @{ Source = "RunDevelopment.bat"; Target = "scripts/run_development.bat"; Action = "MOVE" },
    @{ Source = "RunListDiscovery.bat"; Target = "scripts/run_list_discovery.bat"; Action = "MOVE" },
    @{ Source = "RunOneDriveAdmin.bat"; Target = "scripts/run_onedrive_admin.bat"; Action = "MOVE" },
    @{ Source = "RunOneDriveAutomation.bat"; Target = "scripts/run_onedrive_automation.bat"; Action = "MOVE" },
    @{ Source = "safe_commit_push.bat"; Target = "scripts/safe_commit_push.bat"; Action = "MOVE" },
    @{ Source = "ScanPaths.bat"; Target = "scripts/scan_paths.bat"; Action = "MOVE" },
    @{ Source = "SetupOneDriveAutomation.bat"; Target = "scripts/setup_onedrive_automation.bat"; Action = "MOVE" },
    @{ Source = "StartDevPowerShell.bat"; Target = "scripts/start_dev_powershell.bat"; Action = "MOVE" },
    @{ Source = "SwitchToDevice.bat"; Target = "scripts/switch_to_device.bat"; Action = "MOVE" },
    @{ Source = "UpdateVenvCrossDevice.bat"; Target = "scripts/update_venv_cross_device.bat"; Action = "MOVE" },
    @{ Source = "UpdateVenvScripts.bat"; Target = "scripts/update_venv_scripts.bat"; Action = "MOVE" },
    @{ Source = "ValidateCrossDeviceSetup.bat"; Target = "scripts/validate_cross_device_setup.bat"; Action = "MOVE" },

    # PowerShell files to move
    @{ Source = "ActivateVenv.ps1"; Target = "scripts/activate_venv.ps1"; Action = "MOVE" },
    @{ Source = "AutomationHotkeys.ps1"; Target = "scripts/automation_hotkeys.ps1"; Action = "MOVE" },
    @{ Source = "OneDriveAutomation.ps1"; Target = "scripts/onedrive_automation.ps1"; Action = "MOVE" },
    @{ Source = "OneDriveCleanup.ps1"; Target = "scripts/onedrive_cleanup.ps1"; Action = "MOVE" },
    @{ Source = "onedrive_audit.ps1"; Target = "scripts/onedrive_audit.ps1"; Action = "MOVE" },
    @{ Source = "Test-CrossDevicePaths.ps1"; Target = "scripts/test_cross_device_paths.ps1"; Action = "MOVE" }
)

$consolidatedVenvContent = @"
@echo off
REM Consolidated Virtual Environment Fix Script
REM Combines functionality from Fix-VenvPath.bat, Fix-VirtualEnvPath.bat, and fix_venv_activation.bat

echo Starting virtual environment fix process...

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found. Creating new one...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    exit /b 1
)

REM Update pip and install requirements
python -m pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Warning: Some packages failed to install
    )
)

REM Fix common path issues for cross-device compatibility
python -c "
import sys
import os
from pathlib import Path

# Fix pyvenv.cfg for cross-device compatibility
venv_path = Path('.venv')
pyvenv_cfg = venv_path / 'pyvenv.cfg'

if pyvenv_cfg.exists():
    print('Updating pyvenv.cfg for cross-device compatibility...')
    with open(pyvenv_cfg, 'r') as f:
        content = f.read()

    # Update home path to current Python installation
    import sys
    python_home = str(Path(sys.executable).parent)

    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('home = '):
            lines[i] = f'home = {python_home}'
            break

    with open(pyvenv_cfg, 'w') as f:
        f.write('\n'.join(lines))

    print('pyvenv.cfg updated successfully')
"

echo Virtual environment fix completed successfully!
echo Virtual environment is now activated and ready to use.
"@

# Execute script actions
$processedFiles = @()
foreach ($action in $scriptActions) {
    $sourcePath = Join-Path $rootPath $action.Source
    $targetPath = Join-Path $rootPath $action.Target

    if (Test-Path $sourcePath) {
        Write-Host "Processing: $($action.Source)" -ForegroundColor Yellow

        try {
            switch ($action.Action) {
                "MOVE" {
                    # Ensure target directory exists
                    $targetDir = Split-Path $targetPath -Parent
                    if (-not (Test-Path $targetDir)) {
                        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
                    }

                    Move-Item $sourcePath $targetPath -Force
                    Write-Host "  Moved to: $($action.Target)" -ForegroundColor Green
                    $processedFiles += $action.Source
                }
                "CONSOLIDATE" {
                    if ($action.Target -eq "scripts/consolidated_venv_fix.bat") {
                        # Create consolidated venv fix script
                        if (-not (Test-Path $targetPath)) {
                            $consolidatedVenvContent | Out-File -FilePath $targetPath -Encoding ASCII
                            Write-Host "  Created consolidated script: $($action.Target)" -ForegroundColor Green
                        }
                        # Remove the original file
                        Remove-Item $sourcePath -Force
                        Write-Host "  Consolidated into: $($action.Target)" -ForegroundColor Green
                        $processedFiles += $action.Source
                    }
                }
            }
        }
        catch {
            Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "File not found: $($action.Source)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Script organization completed!" -ForegroundColor Green
Write-Host "Processed $($processedFiles.Count) files" -ForegroundColor Cyan

# Create a reference file for script locations
$referenceContent = @"
# Script Reference Guide
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

This file provides a reference for script locations after reorganization.

## Moved Scripts:
$($processedFiles | ForEach-Object { "- $_" } | Out-String)

## Consolidated Scripts:
- Fix-VenvPath.bat, Fix-VirtualEnvPath.bat, fix_venv_activation.bat → scripts/consolidated_venv_fix.bat

## Script Directory Structure:
All utility scripts are now located in the scripts/ directory with standardized naming:
- snake_case naming convention
- Descriptive names
- Grouped by functionality

To update any references to these scripts in your code or documentation,
use the new paths listed above.
"@

$referenceContent | Out-File -FilePath (Join-Path $scriptsPath "SCRIPT_REFERENCE.md") -Encoding UTF8
Write-Host "Created script reference guide: scripts/SCRIPT_REFERENCE.md" -ForegroundColor Green

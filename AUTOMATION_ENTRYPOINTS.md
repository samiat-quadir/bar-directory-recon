# Automation Entry Points

This document lists the canonical scripts and commands for day-to-day operations.

## GA / Release validation

- PowerShell (Windows): `scripts/ops_ga_011_execution.ps1` (if present in repo)
- CLI: `bdr --version` and `bdr doctor --no-exec`

## Cross-device automation

- Python: `automation/ops_queue.py`
- Python: `automation/run_cross_device_task.py`

## Bootstrap / environment setup

- PowerShell: `bootstrap_alienware.ps1`
- PowerShell: `setup_windows_dev_environment.ps1`
- PowerShell: `setup_windows_dev_simple.ps1`

## Maintenance / repair scripts

- PowerShell: `fix_precommit.ps1`
- PowerShell: `fix_precommit_cache.ps1`
- PowerShell: `fix_precommit_comprehensive.ps1`
- PowerShell: `fix_asus_parity.ps1`
- PowerShell: `fix_asus_parity_clean.ps1`
- PowerShell: `fix_stray_files.ps1`

## Notes

- Scripts under `archive/legacy_scripts/` and `archive/legacy_modules/` are historical or experimental.
- If a script is not listed here and lives at repo root, treat it as non-canonical unless explicitly referenced by docs.

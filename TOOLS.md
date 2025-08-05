# Essential Tools Documentation

This directory contains streamlined, essential utilities for the Bar Directory Reconnaissance project. Each tool has a specific purpose and is actively maintained.

## 🛠️ Core Development Tools

### Security & Secrets Management
- **`secrets_scan.py`** - Comprehensive secrets scanner for the entire repository
  - Usage: `python secrets_scan.py --path . --report-path security_report.json`
  - Finds API keys, passwords, and other sensitive information
  - Generates detailed JSON reports with remediation suggestions

### Environment & Configuration
- **`validate_requirements.py`** - Validates Python dependencies and environment setup
  - Usage: `python validate_requirements.py`
  - Checks for missing packages and version conflicts
  - Validates virtual environment configuration

- **`validate_rog_lucci_env.py`** - ROG-Lucci specific environment validation
  - Usage: `python validate_rog_lucci_env.py`
  - Device-specific configuration verification
  - Cross-environment compatibility checks

### Path & Repository Management
- **`device_path_resolver.py`** - Cross-device path resolution utility
  - Usage: `python device_path_resolver.py --check-paths`
  - Resolves hardcoded paths across different development environments
  - Maintains path compatibility between devices

- **`fix_hardcoded_paths.py`** - Automated hardcoded path fixing
  - Usage: `python fix_hardcoded_paths.py --scan-directory ./src`
  - Identifies and replaces hardcoded paths with environment variables
  - Supports bulk fixing across multiple files

- **`scan_hardcoded_paths.py`** - Hardcoded path detection scanner
  - Usage: `python scan_hardcoded_paths.py --path . --report-path paths_report.json`
  - Comprehensive scanning for hardcoded file and directory paths
  - Generates reports for manual or automated fixing

### Git & Repository Operations
- **`auto_conflict_resolver.py`** - Automated Git conflict resolution
  - Usage: `python auto_conflict_resolver.py --resolve-simple`
  - Handles common merge conflicts automatically
  - Preserves manual review for complex conflicts

- **`safe_commit_push.py`** - Safe Git operations with validation
  - Usage: `python safe_commit_push.py --message "commit message"`
  - Pre-commit validation and safety checks
  - Automated testing before pushing changes

### Code Quality & Linting
- **`run_linters.py`** - Centralized code quality checking
  - Usage: `python run_linters.py --all`
  - Runs flake8, black, isort, and mypy
  - Generates unified code quality reports

- **`fix_whitespace.py`** - Automated whitespace and formatting fixes
  - Usage: `python fix_whitespace.py --fix-all`
  - Standardizes line endings and whitespace
  - Consistent code formatting across the project

### Device Profile Management
- **`create_device_profile.py`** - Device-specific configuration creation
  - Usage: `python create_device_profile.py --device-name "MyDevice"`
  - Creates standardized device profiles
  - Ensures consistent environment setup across devices

- **`resolve_device_profile.py`** - Device profile resolution and validation
  - Usage: `python resolve_device_profile.py --validate`
  - Resolves device-specific configuration issues
  - Validates profile compatibility and settings

## 📁 PowerShell Tools (Windows-Specific)

### Environment Setup
- **`consolidate_env_files.ps1`** - Environment file consolidation
- **`git_repo_cleanup.ps1`** - Repository cleanup and optimization
- **`windows_dev_tweaks.ps1`** - Windows development environment optimization

### Device Management
- **`AutoDeviceSetup.ps1`** - Automated device setup and configuration
- **`DevicePathResolver.ps1`** - PowerShell path resolution utilities
- **`VirtualEnvHelper.ps1`** - Python virtual environment management

### Cross-Device Compatibility
- **`Test-CrossDeviceCompatibility-SalesRep.ps1`** - Cross-device testing utilities
- **`Test-CrossDevicePaths.ps1`** - Path compatibility validation

## 🚀 Quick Start Commands

### Daily Development Workflow
```bash
# Security scan before committing
python tools/secrets_scan.py --path . --report-path /tmp/security_check.json

# Code quality check
python tools/run_linters.py --all

# Environment validation
python tools/validate_requirements.py

# Safe commit and push
python tools/safe_commit_push.py --message "Feature implementation"
```

### Environment Setup (New Device)
```bash
# Create device profile
python tools/create_device_profile.py --device-name "$(hostname)"

# Validate environment
python tools/validate_rog_lucci_env.py

# Resolve any path issues
python tools/device_path_resolver.py --check-paths
```

### Repository Maintenance
```bash
# Scan for hardcoded paths
python tools/scan_hardcoded_paths.py --path . --report-path paths_audit.json

# Fix whitespace issues
python tools/fix_whitespace.py --fix-all

# Automated conflict resolution
python tools/auto_conflict_resolver.py --resolve-simple
```

## 📝 Tool Development Guidelines

### Adding New Tools
1. **Single Purpose**: Each tool should have one clear, specific purpose
2. **Documentation**: Include usage examples and parameter descriptions
3. **Error Handling**: Robust error handling with informative messages
4. **Testing**: Include basic tests for critical functionality
5. **Cross-Platform**: Consider Windows/Linux compatibility where possible

### Maintenance Standards
- **Keep tools under 300 lines** for maintainability
- **Use consistent command-line interfaces** (argparse for Python)
- **Include verbose and quiet modes** for different use cases
- **Generate machine-readable output** (JSON) when appropriate
- **Follow existing code style** and formatting standards

## 📊 Tool Categories Summary

| Category | Tool Count | Primary Purpose |
|----------|------------|-----------------|
| Security & Scanning | 3 | Secrets detection, path scanning, security auditing |
| Environment Setup | 4 | Configuration validation, device profiles |
| Code Quality | 2 | Linting, formatting, standards compliance |
| Git Operations | 2 | Safe commits, conflict resolution |
| Windows Utilities | 8 | PowerShell-based Windows environment tools |
| **Total Essential Tools** | **19** | **Focused, maintainable toolset** |

---

## 🎯 Achievement: Streamlined from 54+ tools to 19 essential utilities

**Removed**: 12 empty files, 3 duplicate files
**Archived**: Legacy and device-specific variations
**Result**: Clean, focused toolset with clear documentation and purpose
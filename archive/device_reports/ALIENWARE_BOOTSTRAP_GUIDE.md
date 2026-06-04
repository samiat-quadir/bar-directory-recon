# Alienware Device Bootstrap Documentation

## Overview

This documentation provides a comprehensive guide for bootstrapping an Alienware device to achieve exact parity with the ASUS "golden image" environment for the `bar-directory-recon` project.

## Prerequisites

### System Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Operating System** | Windows 10/11, macOS 12+, or Ubuntu 20.04+ | Tested on multiple platforms |
| **Python Version** | Python 3.13.x | Required for compatibility |
| **Git** | Latest version | For repository cloning |
| **Disk Space** | Minimum 5GB free | For project files and dependencies |
| **Memory** | 8GB RAM recommended | For development and automation |
| **Administrator Access** | Required on Windows | For system-level installations |

### Required System Packages

#### Windows
```powershell
# These should be installed before running the bootstrap:
# - Python 3.13 (from python.org or Microsoft Store)
# - Git for Windows
# - Google Chrome (for web automation)
# - PowerShell 5.1+ (comes with Windows)
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y python3.13 python3.13-venv python3.13-dev
sudo apt-get install -y git curl wget build-essential
sudo apt-get install -y google-chrome-stable  # For web automation
```

#### macOS
```bash
# Install via Homebrew
brew install python@3.13 git
brew install --cask google-chrome
```

## Bootstrap Scripts

### PowerShell Script (Windows)

**File**: `bootstrap_alienware.ps1`

**Usage**:
```powershell
# Basic usage (installs to C:\Code)
.\bootstrap_alienware.ps1

# Custom workspace location
.\bootstrap_alienware.ps1 -WorkspaceRoot "D:\Development"

# Skip validation step
.\bootstrap_alienware.ps1 -SkipValidation
```

**Features**:
- ✅ Administrator privilege checking
- ✅ Prerequisites validation
- ✅ Repository cloning at tag v2.0
- ✅ Python 3.13 virtual environment setup
- ✅ Dependencies installation (core + optional)
- ✅ Device-specific configuration generation
- ✅ Required directory structure creation
- ✅ External tools installation
- ✅ Comprehensive validation reporting

### Bash Script (Linux/macOS)

**File**: `bootstrap_alienware.sh`

**Usage**:
```bash
# Make executable
chmod +x bootstrap_alienware.sh

# Basic usage (installs to ~/Code)
./bootstrap_alienware.sh

# Custom workspace location
./bootstrap_alienware.sh /opt/development

# Skip validation step
./bootstrap_alienware.sh ~/Code --skip-validation
```

**Features**:
- ✅ Cross-platform compatibility (Linux/macOS)
- ✅ Automatic system detection
- ✅ All Windows script features adapted for Unix

## GitHub Actions Workflow

**File**: `.github/workflows/bootstrap-alienware.yml`

**Triggers**:
- Manual dispatch (`workflow_dispatch`)
- Pushes to `bootstrap-alienware` branch
- Pull requests affecting bootstrap files

**Test Matrix**:
- Ubuntu Latest
- Windows Latest
- macOS Latest

**Artifacts Generated**:
- Validation reports for each platform
- Environment configuration files
- Device profile configurations
- Consolidated summary report

## Dependencies Management

### Core Dependencies (`requirements-core.txt`)

Essential packages required for basic functionality:

```
pydantic[email]>=2.0.0      # Configuration validation
python-dotenv>=1.0.0        # Environment variable management
pyyaml>=6.0                 # YAML configuration files
jinja2>=3.1.0               # Template engine
requests>=2.31.0            # HTTP requests
aiohttp>=3.9.0              # Async HTTP
aiofiles>=23.2.1            # Async file operations
pandas>=2.1.0               # Data processing
numpy>=1.25.0               # Numerical computing
beautifulsoup4>=4.12.0      # HTML parsing
loguru>=0.7.2               # Logging
typer>=0.9.0                # CLI support
schedule>=1.2.0             # Task scheduling
watchdog>=3.0.0             # File system monitoring
```

### Optional Dependencies (`requirements-optional.txt`)

Advanced features and integrations:

```
selenium>=4.15.0            # Web automation
webdriver-manager>=4.0.0    # Driver management
playwright>=1.40.0          # Modern web automation
openpyxl>=3.1.2             # Excel file handling
lxml>=4.9.0                 # XML/HTML processing
pillow>=10.0.0              # Image processing
sqlalchemy>=2.0.0           # Database ORM
fastapi>=0.104.0            # Web framework
uvicorn>=0.23.2             # ASGI server
prefect>=2.13.0             # Workflow management
azure-storage-blob>=12.17.0 # Azure integration
PyPDF2>=3.0.0               # PDF processing
pdfplumber>=0.9.0           # PDF text extraction
```

## Configuration Files

### Environment Configuration (`.env`)

Generated from `.env.template` with device-specific values:

```bash
# Device identification
DEVICE_NAME=ALIENWARE
DEVICE_TYPE=development

# Paths (auto-configured)
PROJECT_ROOT=/path/to/project
WORKSPACE_ROOT=/path/to/workspace

# API Keys (user must configure)
OPENAI_API_KEY=your_key_here
GOOGLE_SHEETS_CREDENTIALS_PATH=config/credentials.json

# Feature flags
DEBUG=true
ENABLE_ADVANCED_FEATURES=true
```

### Device Profile (`config/device_profile-{hostname}.json`)

Auto-generated device-specific configuration:

```json
{
    "device": "ALIENWARE-PC",
    "username": "user",
    "user_home": "/home/user",
    "timestamp": "2025-07-25T19:15:00.000000-04:00",
    "python_path": "/usr/bin/python3.13",
    "onedrive_path": "/home/user/OneDrive",
    "project_root": "/home/user/Code/bar-directory-recon",
    "virtual_env": "/home/user/Code/bar-directory-recon/.venv"
}
```

## Directory Structure

The bootstrap process creates the following directory structure:

```
bar-directory-recon/
├── .venv/                          # Python virtual environment
├── config/                         # Configuration files
│   ├── device_profile-{device}.json
│   └── *.json
├── logs/                           # Log files
│   ├── automation/
│   └── device_logs/
├── input/                          # Input data files
├── output/                         # Generated output files
├── automation/                     # Automation scripts
├── tools/                          # Utility tools
├── scripts/                        # Deployment scripts
├── .env                           # Environment variables
├── requirements-core.txt           # Core dependencies
├── requirements-optional.txt       # Optional dependencies
└── validate_env_state.py          # Environment validation
```

## Validation Process

### Validation Script (`validate_env_state.py`)

The validation script checks:

1. **Python Packages**: Verifies all required packages are installed
2. **Configuration Files**: Ensures all config files exist
3. **Directory Structure**: Validates required directories
4. **External Tools**: Checks for Git, Chrome, pre-commit
5. **Environment Variables**: Validates important env vars

### Validation Report (`alienware_validation_report.md`)

Generated after bootstrap completion:

```markdown
# Alienware Device Bootstrap Validation Report

**Generated**: 2025-07-25 19:15:00
**Device**: ALIENWARE-PC
**User**: username
**Bootstrap Script**: bootstrap_alienware.ps1

## Validation Output
[Detailed validation results...]

## Bootstrap Summary
- ✅ Repository cloned at tag v2.0
- ✅ Python 3.13 virtual environment created
- ✅ Dependencies installed
- ✅ Configuration files created
```

## Missing Dependencies by Device

### ROG-LUCCI (ASUS - Reference Device)

**Status**: ✅ **FULLY CONFIGURED** (Golden Image)

All 45 packages installed, all configurations present.

### ALIENWARE (Target Device)

**Expected Missing Items** (to be resolved by bootstrap):

**Missing Packages** (will be installed):
- All packages from `requirements-core.txt`
- All packages from `requirements-optional.txt`
- Device-specific dependencies

**Missing Configuration** (will be created):
- `config/device_profile-{alienware-hostname}.json`
- `.env` file with device-specific paths
- Required directory structure

## Post-Bootstrap Configuration

### 1. Update Environment Variables

Edit the `.env` file to add your API keys and secrets:

```bash
# Required for full functionality
OPENAI_API_KEY=your_actual_openai_key
GOOGLE_SHEETS_CREDENTIALS_PATH=config/your_credentials.json

# Optional but recommended
DATABASE_URL=your_database_connection_string
AZURE_STORAGE_CONNECTION_STRING=your_azure_connection
```

### 2. Verify Installation

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\Activate.ps1  # Windows

# Run tests
python -m pytest -v

# Check environment
python validate_env_state.py
```

### 3. Test Core Functionality

```bash
# Test basic imports
python -c "import requests, pandas, beautifulsoup4; print('✅ Core packages work')"

# Test automation features (if Chrome is installed)
python -c "from selenium import webdriver; print('✅ Web automation ready')"

# Test configuration loading
python -c "from dotenv import load_dotenv; load_dotenv(); print('✅ Environment loaded')"
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Python 3.13 not found** | Install Python 3.13 from python.org |
| **Permission denied** | Run as Administrator (Windows) or use sudo (Linux) |
| **Git not found** | Install Git and add to PATH |
| **Virtual environment fails** | Check Python installation and permissions |
| **Package installation fails** | Update pip: `python -m pip install --upgrade pip` |
| **Chrome not detected** | Install Google Chrome for automation features |

### Platform-Specific Issues

#### Windows
- Ensure PowerShell execution policy allows scripts: `Set-ExecutionPolicy RemoteSigned`
- Run PowerShell as Administrator
- Check Windows Defender isn't blocking script execution

#### Linux
- Install development packages: `sudo apt-get install python3.13-dev build-essential`
- Ensure user has permissions for workspace directory
- Check Python 3.13 is properly linked

#### macOS
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew for package management
- Check Python path with `which python3.13`

## Advanced Configuration

### Device-Specific Profiles

Create additional device profiles for different environments:

```json
{
    "device": "ALIENWARE-LAPTOP",
    "device_type": "portable",
    "performance_mode": "battery_optimized",
    "automation_settings": {
        "headless": true,
        "timeout": 60,
        "max_workers": 2
    }
}
```

### Cross-Device Synchronization

Enable automatic synchronization across devices:

```bash
# Set up OneDrive sync
ONEDRIVE_PATH=/home/user/OneDrive
SYNC_ENABLED=true
BACKUP_ENABLED=true
```

### Custom Automation Workflows

Configure device-specific automation schedules:

```yaml
# automation/alienware_schedule.yaml
schedules:
  daily_sync:
    time: "09:00"
    timezone: "America/New_York"
    enabled: true
  weekly_cleanup:
    day: "sunday"
    time: "02:00"
    enabled: true
```

## Security Considerations

### Secrets Management

- Never commit `.env` files to version control
- Use Azure Key Vault or similar for production secrets
- Rotate API keys regularly
- Use environment-specific configurations

### Access Control

- Limit repository access to authorized devices
- Use SSH keys for Git authentication
- Enable two-factor authentication on all accounts
- Regular security audits of dependencies

## Maintenance

### Regular Updates

```bash
# Update Python packages
pip-review --auto

# Update system packages
sudo apt update && sudo apt upgrade  # Linux
brew update && brew upgrade          # macOS

# Re-run validation
python validate_env_state.py
```

### Health Checks

Schedule regular health checks:

```bash
# Add to crontab (Linux/macOS)
0 9 * * * cd /path/to/project && python validate_env_state.py

# Add to Task Scheduler (Windows)
# Run bootstrap validation weekly
```

---

## Support

For issues with the bootstrap process:

1. Check the validation report for specific errors
2. Review the troubleshooting section above
3. Verify all prerequisites are met
4. Check GitHub Actions logs for workflow issues
5. Create an issue with detailed error logs

**Generated by**: Bootstrap Documentation Generator v1.0
**Last Updated**: July 25, 2025

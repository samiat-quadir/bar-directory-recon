# Bar Directory Recon - Complete Documentation
*Generated on 2025-07-14 14:07:02*

This document consolidates all project documentation from multiple README files.

# Table of Contents

## General Documentation
- [Universal Recon - Bar Directory Reconnaissance Tool](#universal-recon-bar-directory-reconnaissance-tool)
  - File: `README.md`
  - Date: unknown
- [🚀 AI & Automation Project Guide](#-ai-automation-project-guide)
  - File: `README_AUTOMATION.md`
  - Date: unknown
- [README_DEV_SETUP](#readme_dev_setup)
  - File: `README_DEV_SETUP.md`
  - Date: unknown
- [🚀 AI & Automation Project Guide](#-ai-automation-project-guide)
  - File: `README_AUTOMATION.md`
  - Date: unknown
- [README_DEV_SETUP](#readme_dev_setup)
  - File: `README_DEV_SETUP.md`
  - Date: unknown

## Phase 3
- [🔍 Universal Project Runner - Phase 3 Automation Initiative](#-universal-project-runner-phase-3-automation-initiative)
  - File: `README_PHASE3_AUTOMATION.md`
  - Date: unknown
- [🔍 Universal Project Runner - Phase 3 Automation Initiative](#-universal-project-runner-phase-3-automation-initiative)
  - File: `README_PHASE3_AUTOMATION.md`
  - Date: unknown

---

## Universal Recon - Bar Directory Reconnaissance Tool
*Source: `README.md` | Phase: 0 | Date: unknown*

## Universal Recon - Bar Directory Reconnaissance Tool

[![PyPI version](https://img.shields.io/pypi/v/bar-directory-recon.svg)](https://pypi.org/project/bar-directory-recon/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-33%20passed-green.svg)](https://github.com/samiat-quadir/bar-directory-recon/actions)

### Overview

Universal Recon is a comprehensive bar directory reconnaissance and automation tool designed for legal professional data extraction. It provides a modular plugin system for extracting, validating, and analyzing data from legal bar directories and professional websites.

---

### Key Features

- **Plugin-Based Architecture**: Modular system with specialized extractors for different data types
- **Social Media Detection**: Automated discovery of LinkedIn, Twitter, Facebook, and Instagram profiles
- **Firm Data Extraction**: Intelligent parsing of law firm information and contact details
- **ML-Powered Classification**: Machine learning-based content labeling and categorization
- **Validation Framework**: Comprehensive data validation and quality assessment tools
- **Analytics Suite**: Risk assessment, trend analysis, and reporting capabilities
- **Cross-Platform Support**: Works on Windows and Linux with automated environment detection

---

### Getting Started

#### Requirements

- Windows 10/11, PowerShell 5.1+
- OneDrive installed and configured
- Python 3.11+
- Admin rights for scheduled tasks

#### Virtual Environment Setup

- Use `activate_venv.bat` (CMD) or `ActivateVenv.ps1` (PowerShell) to activate the Python environment.
- For full dev setup: `RunDevelopment.bat` or `StartDevPowerShell.bat`.
- To validate or recreate the venv: `python validate_env_state.py` and `tools\VirtualEnvHelper.ps1`.

#### Environment Variables

- `.env.work` and `.env.asus` are used for device-specific configs.
- `env_loader.py` auto-detects and loads the correct file.
- Only one `.env` is loaded per execution.

#### First-Time Setup

1. Activate the venv and install dependencies.
2. Run `RunOneDriveAutomation.bat` and follow the menu.
3. For preview, use option 7; for full automation, use option 1.

---

### Automation Scripts

- **OneDriveAutomation.ps1**: Main entry for all tasks.
- **auto_git_commit.py**: Auto-commits and pushes to GitHub.
- **git_commit_and_notify.py**: Commits, pushes, and sends notifications.
- **notifier.py**: Handles all email notifications (HTML supported).
- **motion_task_creator.py**: Local integration with Motion App via Flask API.
- **health_check.py**: Verifies environment and variables.
- **log_rotator.py**: Archives old logs.

---

### Best Practices

- Always use `env_loader.py` for environment detection.
- Maintain only one version of each core script.
- Keep `.env` files in the project root.
- Log all actions for traceability.
- Deprecated: `.env` (generic), `token.pickle`, device-specific notifier scripts.

---

### Project Roadmap (Excerpt)

- [x] Unified .env management and loader
- [x] Centralized logging
- [x] AI-powered task automation (Motion App integration)
- [x] Git automation and notification
- [ ] Optional: Further AI enhancements and advanced analytics

---

### Contributors & Contact

- For setup help, see the archived Setup Instructions and Roadmap in `docs/archive/`.
- For issues, open a ticket or contact the maintainer.

---

*This README consolidates all previous documentation, setup guides, and roadmaps. For historical docs, see `docs/archive/`.*


---

## 🚀 AI & Automation Project Guide
*Source: `README_AUTOMATION.md` | Phase: 0 | Date: unknown*

## 🚀 AI & Automation Project Guide

### 📁 Project Structure

- `src/`: All Python automation scripts categorized by purpose.
- `config/`: Device-specific profiles dynamically loaded.
- `tools/`: Cross-device validation and bootstrap scripts.
- `.vscode/`: VS Code workspace configurations and automation setups.

### ⚙️ Essential Setup

- Always use project-level `.venv`:

```powershell
.\.venv\Scripts\activate.ps1
pip install -r requirements.txt


---

## README_DEV_SETUP
*Source: `README_DEV_SETUP.md` | Phase: 0 | Date: unknown*



---

## 🚀 AI & Automation Project Guide
*Source: `README_AUTOMATION.md` | Phase: 0 | Date: unknown*

## 🚀 AI & Automation Project Guide

### 📁 Project Structure

- `src/`: All Python automation scripts categorized by purpose.
- `config/`: Device-specific profiles dynamically loaded.
- `tools/`: Cross-device validation and bootstrap scripts.
- `.vscode/`: VS Code workspace configurations and automation setups.

### ⚙️ Essential Setup

- Always use project-level `.venv`:

```powershell
.\.venv\Scripts\activate.ps1
pip install -r requirements.txt


---

## README_DEV_SETUP
*Source: `README_DEV_SETUP.md` | Phase: 0 | Date: unknown*



---

## 🔍 Universal Project Runner - Phase 3 Automation Initiative
*Source: `README_PHASE3_AUTOMATION.md` | Phase: 3 | Date: unknown*

## 🔍 Universal Project Runner - Phase 3 Automation Initiative

### ✨ Quick Start

**Run the demo:**
```batch
python automation_demo.py
```

**Start automating:**
```batch
RunAutomation.bat setup
RunAutomation.bat dashboard
```

### 🚀 What's New

#### Universal Project Runner
- **Scheduled Operations**: Daily scraping, weekly exports, hourly status updates
- **Input Monitoring**: Auto-process new files dropped in `input/` directory
- **Smart Notifications**: Discord webhooks + HTML email alerts
- **Live Dashboard**: Real-time status with auto-refresh
- **CLI Shortcuts**: Batch scripts, PowerShell hotkeys, Python APIs

#### Key Features

| Feature | Description | Command |
|---------|-------------|---------|
| 🔄 **Auto Pipeline** | Runs full pipeline for all sites | `RunAutomation.bat full` |
| ⚡ **Quick Run** | Single site processing | `RunAutomation.bat quick site.com` |
| 👀 **Input Monitor** | Watch for new data files | `RunAutomation.bat monitor` |
| ⏰ **Scheduler** | Daily/weekly automation | `RunAutomation.bat schedule` |
| 📊 **Dashboard** | Live status & statistics | `RunAutomation.bat dashboard` |
| 📧 **Notifications** | Discord/Email alerts | `RunAutomation.bat test` |

### 🛠️ Components

#### Core Automation (`automation/`)
- `universal_runner.py` - Main orchestration engine
- `notifier.py` - Discord/Email notification system
- `dashboard.py` - Status dashboard generator
- `pipeline_executor.py` - Pipeline execution with retry logic
- `cli_shortcuts.py` - Command-line interface
- `config.yaml` - Configuration file

#### User Interfaces
- `RunAutomation.bat` - Windows batch interface
- `AutomationHotkeys.ps1` - PowerShell shortcuts
- `automation_demo.py` - Live demonstration
- VS Code Tasks - Integrated task runner

### ⚙️ Configuration

Edit `automation/config.yaml`:

```yaml
## Add your sites
pipeline:
  sites:
    - "your-target-site.com"

## Setup notifications
notifications:
  discord_webhook: "https://discord.com/api/webhooks/..."
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    username: "your-email@gmail.com"
    recipients: ["admin@company.com"]

## Schedule automation
schedules:
  scraping:
    frequency: daily
    time: "02:00"
```

### 🎯 Use Cases

#### Daily Operations
- **02:00** - Automated scraping for all sites
- **06:00** - Validation and health checks
- **Hourly** - Dashboard updates
- **Continuous** - Input file monitoring

#### On-Demand Tasks
- Process urgent site updates
- Generate instant status reports
- Test notification systems
- Validate pipeline health

#### Development Workflow
- Monitor for new data files
- Automatic processing and validation
- Real-time status tracking
- Error notifications

### 🔧 PowerShell Hotkeys

Load shortcuts: `. .\AutomationHotkeys.ps1`

```powershell
ur-quick site.com    # Quick pipeline run
ur-full             # Full pipeline
ur-dashboard        # Generate dashboard
ur-status          # Show status
ur-monitor         # Start monitoring
ur-help            # Show help
```

### 📊 Dashboard Features

The live dashboard (`output/dashboard.html`) shows:
- ✅ Success/failure statistics
- 📈 Success rate trending
- 🌐 Individual site status
- 📋 Recent activity log
- 🔄 Auto-refresh every 5 minutes

### 📧 Notification System

#### Discord Integration
- Rich embed messages with color coding
- Error details and stack traces
- Mobile push notifications
- Instant delivery

#### Email Integration
- HTML formatted messages
- Professional styling
- Error logs attached
- Multiple recipients

### 🗂️ File Organization

```
bar-directory-recon-1/
├── automation/           # 🤖 Automation engine
├── input/               # 📥 Drop files here for auto-processing
├── output/              # 📤 Generated reports and dashboard
├── logs/automation/     # 📝 Automation logs
├── RunAutomation.bat    # 🚀 Main launcher
└── automation_demo.py   # 🎬 Live demo
```

### 🚨 Error Handling

- **Automatic Retry**: 3 attempts with exponential backoff
- **Timeout Protection**: 1-hour max per operation
- **Detailed Logging**: Full error traces and context
- **Instant Alerts**: Immediate notification on failures
- **Graceful Degradation**: Continue processing other sites

### 🔮 Advanced Features

#### Headless Operation
- Runs completely unattended
- Comprehensive logging for debugging
- Background process support
- Resource management

#### Cross-Device Compatibility
- Works on any Windows machine
- Portable configuration
- Device-specific optimizations
- Cloud synchronization ready

### 📋 Next Steps

1. **Setup**: Run `RunAutomation.bat setup`
2. **Configure**: Edit `automation/config.yaml`
3. **Test**: Run `RunAutomation.bat test`
4. **Demo**: Run `python automation_demo.py`
5. **Deploy**: Run `RunAutomation.bat schedule`

### 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Module errors | `RunAutomation.bat install` |
| Config errors | `RunAutomation.bat setup` |
| Pipeline fails | `RunAutomation.bat validate` |
| No notifications | `RunAutomation.bat test` |

---

**Phase 3 Automation Initiative**
*Intelligent, scalable, hands-free bar directory reconnaissance*

🔗 **Documentation**: See `PHASE3_AUTOMATION_DOCS.md` for complete details
🎬 **Demo**: Run `python automation_demo.py` for live demonstration
⚙️ **Configuration**: Edit `automation/config.yaml` to customize


---

## 🔍 Universal Project Runner - Phase 3 Automation Initiative
*Source: `README_PHASE3_AUTOMATION.md` | Phase: 3 | Date: unknown*

## 🔍 Universal Project Runner - Phase 3 Automation Initiative

### ✨ Quick Start

**Run the demo:**
```batch
python automation_demo.py
```

**Start automating:**
```batch
RunAutomation.bat setup
RunAutomation.bat dashboard
```

### 🚀 What's New

#### Universal Project Runner
- **Scheduled Operations**: Daily scraping, weekly exports, hourly status updates
- **Input Monitoring**: Auto-process new files dropped in `input/` directory
- **Smart Notifications**: Discord webhooks + HTML email alerts
- **Live Dashboard**: Real-time status with auto-refresh
- **CLI Shortcuts**: Batch scripts, PowerShell hotkeys, Python APIs

#### Key Features

| Feature | Description | Command |
|---------|-------------|---------|
| 🔄 **Auto Pipeline** | Runs full pipeline for all sites | `RunAutomation.bat full` |
| ⚡ **Quick Run** | Single site processing | `RunAutomation.bat quick site.com` |
| 👀 **Input Monitor** | Watch for new data files | `RunAutomation.bat monitor` |
| ⏰ **Scheduler** | Daily/weekly automation | `RunAutomation.bat schedule` |
| 📊 **Dashboard** | Live status & statistics | `RunAutomation.bat dashboard` |
| 📧 **Notifications** | Discord/Email alerts | `RunAutomation.bat test` |

### 🛠️ Components

#### Core Automation (`automation/`)
- `universal_runner.py` - Main orchestration engine
- `notifier.py` - Discord/Email notification system
- `dashboard.py` - Status dashboard generator
- `pipeline_executor.py` - Pipeline execution with retry logic
- `cli_shortcuts.py` - Command-line interface
- `config.yaml` - Configuration file

#### User Interfaces
- `RunAutomation.bat` - Windows batch interface
- `AutomationHotkeys.ps1` - PowerShell shortcuts
- `automation_demo.py` - Live demonstration
- VS Code Tasks - Integrated task runner

### ⚙️ Configuration

Edit `automation/config.yaml`:

```yaml
## Add your sites
pipeline:
  sites:
    - "your-target-site.com"

## Setup notifications
notifications:
  discord_webhook: "https://discord.com/api/webhooks/..."
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    username: "your-email@gmail.com"
    recipients: ["admin@company.com"]

## Schedule automation
schedules:
  scraping:
    frequency: daily
    time: "02:00"
```

### 🎯 Use Cases

#### Daily Operations
- **02:00** - Automated scraping for all sites
- **06:00** - Validation and health checks
- **Hourly** - Dashboard updates
- **Continuous** - Input file monitoring

#### On-Demand Tasks
- Process urgent site updates
- Generate instant status reports
- Test notification systems
- Validate pipeline health

#### Development Workflow
- Monitor for new data files
- Automatic processing and validation
- Real-time status tracking
- Error notifications

### 🔧 PowerShell Hotkeys

Load shortcuts: `. .\AutomationHotkeys.ps1`

```powershell
ur-quick site.com    # Quick pipeline run
ur-full             # Full pipeline
ur-dashboard        # Generate dashboard
ur-status          # Show status
ur-monitor         # Start monitoring
ur-help            # Show help
```

### 📊 Dashboard Features

The live dashboard (`output/dashboard.html`) shows:
- ✅ Success/failure statistics
- 📈 Success rate trending
- 🌐 Individual site status
- 📋 Recent activity log
- 🔄 Auto-refresh every 5 minutes

### 📧 Notification System

#### Discord Integration
- Rich embed messages with color coding
- Error details and stack traces
- Mobile push notifications
- Instant delivery

#### Email Integration
- HTML formatted messages
- Professional styling
- Error logs attached
- Multiple recipients

### 🗂️ File Organization

```
bar-directory-recon-1/
├── automation/           # 🤖 Automation engine
├── input/               # 📥 Drop files here for auto-processing
├── output/              # 📤 Generated reports and dashboard
├── logs/automation/     # 📝 Automation logs
├── RunAutomation.bat    # 🚀 Main launcher
└── automation_demo.py   # 🎬 Live demo
```

### 🚨 Error Handling

- **Automatic Retry**: 3 attempts with exponential backoff
- **Timeout Protection**: 1-hour max per operation
- **Detailed Logging**: Full error traces and context
- **Instant Alerts**: Immediate notification on failures
- **Graceful Degradation**: Continue processing other sites

### 🔮 Advanced Features

#### Headless Operation
- Runs completely unattended
- Comprehensive logging for debugging
- Background process support
- Resource management

#### Cross-Device Compatibility
- Works on any Windows machine
- Portable configuration
- Device-specific optimizations
- Cloud synchronization ready

### 📋 Next Steps

1. **Setup**: Run `RunAutomation.bat setup`
2. **Configure**: Edit `automation/config.yaml`
3. **Test**: Run `RunAutomation.bat test`
4. **Demo**: Run `python automation_demo.py`
5. **Deploy**: Run `RunAutomation.bat schedule`

### 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Module errors | `RunAutomation.bat install` |
| Config errors | `RunAutomation.bat setup` |
| Pipeline fails | `RunAutomation.bat validate` |
| No notifications | `RunAutomation.bat test` |

---

**Phase 3 Automation Initiative**
*Intelligent, scalable, hands-free bar directory reconnaissance*

🔗 **Documentation**: See `PHASE3_AUTOMATION_DOCS.md` for complete details
🎬 **Demo**: Run `python automation_demo.py` for live demonstration
⚙️ **Configuration**: Edit `automation/config.yaml` to customize


---

## Document Information
- **Generated**: 2025-07-14 14:07:02
- **Source Files**: 7 README files
- **Project**: Bar Directory Recon
- **Repository**: [bar-directory-recon](https://github.com/samiat-quadir/bar-directory-recon)

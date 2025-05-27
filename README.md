# OneDrive Automation & AI Integration Project

## Overview

This project provides a unified automation and AI integration solution for managing OneDrive-based development environments across multiple devices (e.g., ASUS laptop and Work Desktop). It includes robust environment detection, cross-device sync, Git automation, secrets scanning, and AI-powered task automation.

---

## Key Features

- **Path Resolution & Folder Standardization**: Ensures consistent folder structure and path resolution across devices.
- **Cross-Device Synchronization**: Syncs Python environments, VS Code extensions, and device-specific configs using `.env.work` and `.env.asus` files, auto-loaded by `env_loader.py`.
- **Git Automation**: Auto-commit, push, and notification scripts (`auto_git_commit.py`, `git_commit_and_notify.py`).
- **Secrets Scanning**: Identifies sensitive info in files.
- **Central Logging**: All logs are UTF-8 and stored in the synced OneDrive project folder for easy access.
- **AI & Motion App Integration**: Local Flask API and Motion App API for automated task creation, replacing Zapier.
- **Health Checks & Maintenance**: Includes health check scripts, log rotation, and scheduled tasks.

---

## Getting Started

### Requirements

- Windows 10/11, PowerShell 5.1+
- OneDrive installed and configured
- Python 3.11+
- Admin rights for scheduled tasks

### Virtual Environment Setup

- Use `activate_venv.bat` (CMD) or `ActivateVenv.ps1` (PowerShell) to activate the Python environment.
- For full dev setup: `RunDevelopment.bat` or `StartDevPowerShell.bat`.
- To fix or recreate the venv: `fix_venv_activation.bat` and `InstallDependencies.bat`.

### Environment Variables

- `.env.work` and `.env.asus` are used for device-specific configs.
- `env_loader.py` auto-detects and loads the correct file.
- Only one `.env` is loaded per execution.

### First-Time Setup

1. Activate the venv and install dependencies.
2. Run `RunOneDriveAutomation.bat` and follow the menu.
3. For preview, use option 7; for full automation, use option 1.

---

## Automation Scripts

- **OneDriveAutomation.ps1**: Main entry for all tasks.
- **auto_git_commit.py**: Auto-commits and pushes to GitHub.
- **git_commit_and_notify.py**: Commits, pushes, and sends notifications.
- **notifier.py**: Handles all email notifications (HTML supported).
- **motion_task_creator.py**: Local integration with Motion App via Flask API.
- **health_check.py**: Verifies environment and variables.
- **log_rotator.py**: Archives old logs.

---

## Best Practices

- Always use `env_loader.py` for environment detection.
- Maintain only one version of each core script.
- Keep `.env` files in the project root.
- Log all actions for traceability.
- Deprecated: `.env` (generic), `token.pickle`, device-specific notifier scripts.

---

## Project Roadmap (Excerpt)

- [x] Unified .env management and loader
- [x] Centralized logging
- [x] AI-powered task automation (Motion App integration)
- [x] Git automation and notification
- [ ] Optional: Further AI enhancements and advanced analytics

---

## Contributors & Contact

- For setup help, see the archived Setup Instructions and Roadmap in `docs/archive/`.
- For issues, open a ticket or contact the maintainer.

---

*This README consolidates all previous documentation, setup guides, and roadmaps. For historical docs, see `docs/archive/`.*

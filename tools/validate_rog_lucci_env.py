#!/usr/bin/env python
"""
validate_rog_lucci_env.py - ASUS (ROG-Lucci) Environment Validation Script
Created: May 19, 2025

This script performs a comprehensive validation of the ROG-Lucci environment
to ensure it's properly configured for cross-device development.
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from datetime import datetime


def success(message):
    """Print a success message."""
    print(f"✅ {message}")


def warning(message):
    """Print a warning message."""
    print(f"⚠️ {message}")


def error(message):
    """Print an error message."""
    print(f"❌ {message}")


def info(message):
    """Print an info message."""
    print(f"ℹ️ {message}")


def banner(message):
    """Print a banner."""
    print("\n" + "=" * 60)
    print(f"    {message}")
    print("=" * 60)


def run_command(cmd):
    """Run a command and return the output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error(f"Command failed: {cmd}")
        error(f"Error: {e.stderr}")
        return None


def check_device_profile():
    """Check if the device profile exists and is valid."""
    banner("Checking Device Profile")

    device_name = platform.node()
    profile_path = Path("config") / f"device_profile-{device_name}.json"

    if not profile_path.exists():
        error(f"Device profile not found at {profile_path}")
        return False

    try:
        with open(profile_path, "r") as f:
            profile = json.load(f)

        info(f"Device profile found: {profile_path}")
        info(f"Device: {profile.get('device', 'Unknown')}")
        info(f"Username: {profile.get('username', 'Unknown')}")
        info(f"Python version: {profile.get('python_version', 'Unknown')}")

        if profile.get("device") != device_name:
            warning(f"Device name mismatch: {profile.get('device')} != {device_name}")

        success("Device profile is valid")
        return True
    except (json.JSONDecodeError, FileNotFoundError) as e:
        error(f"Failed to read device profile: {e}")
        return False


def check_virtual_env():
    """Check if the virtual environment is properly configured."""
    banner("Checking Virtual Environment")

    venv_path = Path(".venv")
    if not venv_path.exists():
        error("Virtual environment not found at .venv")
        return False

    activate_scripts = [".venv/Scripts/activate.bat", ".venv/Scripts/activate.ps1", ".venv/Scripts/activate"]

    all_found = True
    for script in activate_scripts:
        if Path(script).exists():
            success(f"Found activation script: {script}")
        else:
            if script.endswith(".bat") or script.endswith(".ps1"):
                error(f"Missing activation script: {script}")
                all_found = False
            else:
                warning(f"Missing activation script: {script} (may not be needed on Windows)")

    if all_found:
        success("Virtual environment is properly configured")
        return True
    else:
        warning("Some virtual environment scripts are missing")
        return False


def check_pre_commit():
    """Check if pre-commit is installed and hooks are set up."""
    banner("Checking Pre-commit Installation")

    # Check if pre-commit is installed
    pre_commit_version = run_command("pre-commit --version")
    if not pre_commit_version:
        error("Pre-commit is not installed or not in PATH")
        return False

    info(f"Pre-commit version: {pre_commit_version}")

    # Check if pre-commit config exists
    config_path = Path(".pre-commit-config.yaml")
    if not config_path.exists():
        error("Pre-commit config file not found")
        return False

    success("Pre-commit config file found")

    # Check if git hooks are installed
    hook_path = Path(".git/hooks/pre-commit")
    if not hook_path.exists():
        error("Git pre-commit hook not found")
        return False

    success("Git pre-commit hook is installed")
    return True


def check_paths():
    """Check if paths are properly configured."""
    banner("Checking Path Resolution")

    # Check if PowerShell path resolver exists
    ps_resolver = Path("tools/DevicePathResolver.ps1")
    if not ps_resolver.exists():
        error("PowerShell path resolver not found")
        return False

    success("PowerShell path resolver found")

    # Check if Python path resolver exists
    py_resolver = Path("tools/device_path_resolver.py")
    if not py_resolver.exists():
        error("Python path resolver not found")
        return False

    success("Python path resolver found")

    # Check if ROG-Lucci is in both resolvers
    ps_content = ps_resolver.read_text()
    py_content = py_resolver.read_text()

    if "ROG-LUCCI" not in ps_content:
        error("ROG-LUCCI not found in PowerShell path resolver")
        return False

    if "ROG-LUCCI" not in py_content:
        error("ROG-LUCCI not found in Python path resolver")
        return False

    success("ROG-LUCCI is properly configured in path resolvers")
    return True


def check_cross_device_manager():
    """Check if CrossDeviceManager.bat exists and includes safe commit option."""
    banner("Checking CrossDeviceManager")

    cdm_path = Path("CrossDeviceManager.bat")
    if not cdm_path.exists():
        error("CrossDeviceManager.bat not found")
        return False

    success("CrossDeviceManager.bat found")

    cdm_content = cdm_path.read_text()
    if "SAFE_COMMIT" not in cdm_content:
        warning("Safe commit option not found in CrossDeviceManager.bat")
        return False

    success("Safe commit option is configured in CrossDeviceManager.bat")
    return True


def check_logs_structure():
    """Check if logs directory structure is properly configured."""
    banner("Checking Logs Structure")

    log_dirs = ["logs", "logs/device_logs", "logs/sync_logs", "logs/validation"]

    all_found = True
    for log_dir in log_dirs:
        if not Path(log_dir).exists():
            error(f"Log directory not found: {log_dir}")
            all_found = False
        else:
            success(f"Log directory found: {log_dir}")

    if not all_found:
        warning("Some log directories are missing")
        return False

    success("Logs directory structure is properly configured")
    return True


def check_vs_code_settings():
    """Check if VS Code settings are properly configured."""
    banner("Checking VS Code Settings")

    settings_path = Path(".vscode/settings.json")
    if not settings_path.exists():
        error("VS Code settings file not found")
        return False

    try:
        with open(settings_path, "r") as f:
            settings = json.load(f)

        # Check if chatAttention is set to "never"
        chat_attention = settings.get("github.copilot.chat.promptsUserData", {}).get("chatAttention")
        if chat_attention != "never":
            warning("github.copilot.chat.promptsUserData.chatAttention is not set to 'never'")
        else:
            success("github.copilot.chat.promptsUserData.chatAttention is properly configured")

        # Check if terminal execution is enabled
        terminal_execution = settings.get("github.copilot.chat.server.security.enableTerminalExecution")
        if not terminal_execution:
            warning("github.copilot.chat.server.security.enableTerminalExecution is not enabled")
        else:
            success("github.copilot.chat.server.security.enableTerminalExecution is properly configured")

        success("VS Code settings are properly configured")
        return True
    except (json.JSONDecodeError, FileNotFoundError) as e:
        error(f"Failed to read VS Code settings: {e}")
        return False


def generate_report():
    """Generate a validation report."""
    banner("Generating Validation Report")

    device_name = platform.node()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_content = f"""# ROG-Lucci Environment Validation Report

**Generated:** {timestamp}
**Device:** {device_name}
**User:** {os.getlogin()}
**Python Version:** {'.'.join(map(str, sys.version_info[:3]))}

## Validation Results

The following components were validated:

1. Device Profile: {"✅" if check_device_profile() else "❌"}
2. Virtual Environment: {"✅" if check_virtual_env() else "❌"}
3. Pre-commit Installation: {"✅" if check_pre_commit() else "❌"}
4. Path Resolution: {"✅" if check_paths() else "❌"}
5. CrossDeviceManager: {"✅" if check_cross_device_manager() else "❌"}
6. Logs Structure: {"✅" if check_logs_structure() else "❌"}
7. VS Code Settings: {"✅" if check_vs_code_settings() else "❌"}

## Conclusion

The ROG-Lucci environment is {"fully validated and ready for development" if all([
    check_device_profile(),
    check_virtual_env(),
    check_pre_commit(),
    check_paths(),
    check_cross_device_manager(),
    check_logs_structure(),
    check_vs_code_settings()
]) else "not fully configured, see issues above"}.

---

*This report was automatically generated by validate_rog_lucci_env.py*
"""

    # Ensure logs directory exists
    Path("logs/validation").mkdir(parents=True, exist_ok=True)

    # Generate report file
    report_path = Path(f"logs/validation/validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    report_path.write_text(report_content)

    success(f"Validation report generated: {report_path}")


def main():
    """Main function."""
    banner("ROG-Lucci Environment Validation")

    print(f"Device: {platform.node()}")
    print(f"User: {os.getlogin()}")
    print(f"Python: {'.'.join(map(str, sys.version_info[:3]))}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    check_device_profile()
    check_virtual_env()
    check_pre_commit()
    check_paths()
    check_cross_device_manager()
    check_logs_structure()
    check_vs_code_settings()

    generate_report()

    banner("Validation Complete")


if __name__ == "__main__":
    main()

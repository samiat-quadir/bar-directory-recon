#!/usr/bin/env python
"""
Environment file synchronization tool.

This script syncs the appropriate environment file (.env.work or .env.asus)
to the main .env file based on the current hostname/OS.
"""
import os
import platform
import shutil
import socket
import sys
from datetime import datetime
from pathlib import Path


def get_timestamp():
    """Return formatted timestamp for logs."""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def log_message(message):
    """Print a message with timestamp."""
    print(f"{get_timestamp()} {message}")


def get_project_root():
    """Get the project root directory."""
    # Start with the current script's directory
    current_dir = Path(__file__).resolve().parent
    # Navigate up to the project root (parent of 'tools')
    return current_dir.parent


def create_env_file_if_missing(env_path, template_path=None):
    """
    Create an environment file from template if it doesn't exist.

    Args:
        env_path (Path): Path to environment file to create
        template_path (Path, optional): Path to template file

    Returns:
        bool: True if file existed or was created, False otherwise
    """
    if env_path.exists():
        return True

    if template_path is None:
        template_path = get_project_root() / ".env.template"

    if not template_path.exists():
        log_message(f"[WARNING] Neither {env_path} nor template {template_path} found!")
        return False

    try:
        shutil.copy2(template_path, env_path)
        log_message(f"[INFO] Created new {env_path.name} from template")
        return True
    except Exception as e:
        log_message(f"[ERROR] Failed to create {env_path}: {e}")
        return False


def sync_env_file():
    """
    Sync the appropriate .env file based on hostname.

    - If hostname contains 'ASUS' or 'ROG', use .env.asus
    - Otherwise use .env.work

    Returns:
        bool: True if successful, False otherwise
    """
    root_dir = get_project_root()
    hostname = socket.gethostname().upper()
    os_type = platform.system()

    log_message(f"[INFO] Detected system: {os_type} - {hostname}")

    # Determine which env file to use
    if "ASUS" in hostname or "ROG" in hostname:
        source_env = root_dir / ".env.asus"
        env_type = "ASUS"
    else:
        source_env = root_dir / ".env.work"
        env_type = "WORK"

    target_env = root_dir / ".env"
    template_path = root_dir / ".env.template"

    # Create source env file from template if it doesn't exist
    if not source_env.exists():
        log_message(f"[WARNING] Source environment file {source_env} not found!")
        if not create_env_file_if_missing(source_env, template_path):
            log_message(f"[ERROR] Failed to create {source_env.name} from template")
            log_message(f"Please create {source_env.name} manually and run this script again")
            return False

    # Ensure target directory exists
    os.makedirs(target_env.parent, exist_ok=True)

    # Copy the file
    try:
        shutil.copy2(source_env, target_env)
        log_message(f"[SUCCESS] Environment synchronized: {env_type} -> .env")
        log_message(f"Source: {source_env}")
        log_message(f"Target: {target_env}")
        return True
    except Exception as e:
        log_message(f"[ERROR] Failed to sync environment files: {e}")
        return False


if __name__ == "__main__":
    # Create logs directory
    logs_dir = get_project_root() / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_message(f"[INFO] Starting environment sync")
    success = sync_env_file()

    if success:
        log_message("[INFO] Environment sync completed successfully")
    else:
        log_message("[ERROR] Environment sync failed")

    sys.exit(0 if success else 1)

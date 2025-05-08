#!/usr/bin/env python
"""
Environment file synchronization tool.

This script syncs the appropriate environment file (.env.work or .env.asus)
to the main .env file based on the current hostname/OS.
"""
import argparse
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


def log_message(message, verbose=False, log_file=None):
    """
    Print a message with timestamp and optionally write to log file.

    Args:
        message: The message to log
        verbose: Whether to print the message (only when verbose mode is on)
        log_file: Optional file path to write the log message to
    """
    timestamped_message = f"{get_timestamp()} {message}"

    # Always print non-verbose messages or if verbose mode is on
    if not message.startswith("[VERBOSE]") or verbose:
        print(timestamped_message)

    # Write to log file if provided
    if log_file:
        with open(log_file, "a") as f:
            f.write(timestamped_message + "\n")


def get_project_root():
    """Get the project root directory."""
    # Start with the current script's directory
    current_dir = Path(__file__).resolve().parent
    # Navigate up to the project root (parent of 'tools')
    return current_dir.parent


def setup_logging():
    """Set up logging directories and return log file paths."""
    root_dir = get_project_root()
    logs_dir = root_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Create Phase 28 specific log directory
    phase28_log_dir = logs_dir / "phase_28"
    phase28_log_dir.mkdir(exist_ok=True)

    return phase28_log_dir / "env_sync.log"


def create_env_file_if_missing(env_path, template_path=None, verbose=False, log_file=None):
    """
    Create an environment file from template if it doesn't exist.

    Args:
        env_path (Path): Path to environment file to create
        template_path (Path, optional): Path to template file
        verbose (bool): Whether to print verbose messages
        log_file (Path): Path to log file

    Returns:
        bool: True if file existed or was created, False otherwise
    """
    if env_path.exists():
        log_message(f"[VERBOSE] {env_path.name} already exists", verbose, log_file)
        return True

    if template_path is None:
        template_path = get_project_root() / ".env.template"

    if not template_path.exists():
        log_message(
            f"[WARNING] Neither {env_path} nor template {template_path} found!", verbose=True, log_file=log_file
        )
        return False

    try:
        shutil.copy2(template_path, env_path)
        log_message(f"[INFO] Created new {env_path.name} from template", verbose=True, log_file=log_file)
        return True
    except Exception as e:
        log_message(f"[ERROR] Failed to create {env_path}: {e}", verbose=True, log_file=log_file)
        return False


def sync_env_file(dry_run=False, verbose=False):
    """
    Sync the appropriate .env file based on hostname.

    - If hostname contains 'ASUS' or 'ROG', use .env.asus
    - Otherwise use .env.work

    Args:
        dry_run (bool): If True, only simulate the operation
        verbose (bool): If True, print verbose output

    Returns:
        bool: True if successful, False otherwise
    """
    root_dir = get_project_root()
    hostname = socket.gethostname().upper()
    os_type = platform.system()
    log_file = setup_logging()

    log_message(f"[INFO] Starting environment sync (dry-run: {dry_run})", verbose=True, log_file=log_file)
    log_message(f"[INFO] Detected system: {os_type} - {hostname}", verbose=True, log_file=log_file)

    # Determine which env file to use
    if "ASUS" in hostname or "ROG" in hostname:
        source_env = root_dir / ".env.asus"
        env_type = "ASUS"
    else:
        source_env = root_dir / ".env.work"
        env_type = "WORK"

    target_env = root_dir / ".env"
    template_path = root_dir / ".env.template"

    log_message(f"[VERBOSE] Using environment type: {env_type}", verbose, log_file)
    log_message(f"[VERBOSE] Source env path: {source_env}", verbose, log_file)
    log_message(f"[VERBOSE] Target env path: {target_env}", verbose, log_file)

    # Create source env file from template if it doesn't exist
    if not source_env.exists():
        log_message(f"[WARNING] Source environment file {source_env} not found!", verbose=True, log_file=log_file)
        if not create_env_file_if_missing(source_env, template_path, verbose, log_file):
            log_message(f"[ERROR] Failed to create {source_env.name} from template", verbose=True, log_file=log_file)
            log_message(
                f"Please create {source_env.name} manually and run this script again", verbose=True, log_file=log_file
            )
            return False

    # Ensure target directory exists
    os.makedirs(target_env.parent, exist_ok=True)

    # Copy the file
    try:
        if dry_run:
            log_message(f"[DRY-RUN] Would copy: {source_env} -> {target_env}", verbose=True, log_file=log_file)
            log_message(f"[SUCCESS] Dry run completed successfully", verbose=True, log_file=log_file)
            return True
        else:
            shutil.copy2(source_env, target_env)
            log_message(f"[SUCCESS] Environment synchronized: {env_type} -> .env", verbose=True, log_file=log_file)
            log_message(f"[INFO] Source: {source_env}", verbose=True, log_file=log_file)
            log_message(f"[INFO] Target: {target_env}", verbose=True, log_file=log_file)
            return True
    except Exception as e:
        log_message(f"[ERROR] Failed to sync environment files: {e}", verbose=True, log_file=log_file)
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Sync environment files based on detected device.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the operation without making changes")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Create logs directory
    logs_dir = get_project_root() / "logs"
    logs_dir.mkdir(exist_ok=True)

    success = sync_env_file(dry_run=args.dry_run, verbose=args.verbose)

    if success:
        log_message("[INFO] Environment sync completed successfully", verbose=True)
    else:
        log_message("[ERROR] Environment sync failed", verbose=True)

    sys.exit(0 if success else 1)

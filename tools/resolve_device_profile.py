#!/usr/bin/env python3
"""
resolve_device_profile.py

This script automatically detects the current device and generates or links
the appropriate device_profile.json based on the hostname.

It creates a symlink or copy from the appropriate device-specific profile
(device_profile_HOSTNAME.json) to the generic device_profile.json that will
be used by all scripts.
"""

import json
import logging
import os
import platform
import shutil
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Set up logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "device_transition_setup.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("DeviceProfileResolver")


def get_project_root():
    """Get the project root directory based on this script's location."""
    return Path(__file__).parent.parent.resolve()


def get_device_name():
    """Get the current device hostname."""
    return socket.gethostname()


def get_device_info():
    """Get detailed information about the current device."""
    device_name = get_device_name()
    username = os.getlogin()
    system_info = {
        "hostname": device_name,
        "username": username,
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
        "timestamp": datetime.now().isoformat(),
    }

    # Try to detect OneDrive path
    onedrive_path = detect_onedrive_path(username)
    if onedrive_path:
        system_info["onedrive_path"] = str(onedrive_path)

    return system_info


def detect_onedrive_path(username):
    """Detect the OneDrive path based on username."""
    possible_paths = [
        Path(f"C:/Users/{username}/OneDrive - Digital Age Marketing Group"),
        Path(f"C:/Users/{username}/OneDrive"),
    ]

    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path

    return None


def load_device_config():
    """Load the device_config.json file."""
    config_path = get_project_root() / "config" / "device_config.json"
    if not config_path.exists():
        logger.error(f"device_config.json not found at {config_path}")
        return None

    try:
        with open(config_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing device_config.json: {e}")
        return None


def update_device_config(device_name):
    """Update the device_config.json with the current device."""
    config_path = get_project_root() / "config" / "device_config.json"

    try:
        # Read the existing config
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
        else:
            logger.warning("No device_config.json found. Creating a new one.")
            config = {
                "DeviceId": device_name,
                "Username": os.getlogin(),
                "Settings": {},
                "Paths": {},
                "FirstRegistered": datetime.now().isoformat(),
                "LastUpdated": datetime.now().isoformat(),
            }

        # Update the current device
        config["DeviceId"] = device_name
        config["LastUpdated"] = datetime.now().isoformat()

        # Write the updated config
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

        logger.info(f"Updated device_config.json with device: {device_name}")
        return True
    except Exception as e:
        logger.error(f"Error updating device_config.json: {e}")
        return False


def link_device_profile(device_name):
    """Link or copy the appropriate device profile to device_profile.json."""
    config_dir = get_project_root() / "config"
    source_profile = config_dir / f"device_profile_{device_name}.json"
    target_profile = config_dir / "device_profile.json"

    if not source_profile.exists():
        logger.error(f"Source profile not found: {source_profile}")
        return False

    try:
        # If the target already exists, backup first
        if target_profile.exists():
            backup_file = (
                config_dir / f"device_profile.json.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.copy2(target_profile, backup_file)
            logger.info(f"Backed up existing device_profile.json to {backup_file.name}")
            target_profile.unlink()

        # Try to create symlink first (on Windows, requires admin or developer mode)
        try:
            if platform.system() == "Windows":
                # Use subprocess for Windows symlink creation
                result = subprocess.run(
                    f"powershell -Command \"New-Item -ItemType SymbolicLink -Path '{target_profile}' -Target '{source_profile}'\"",
                    capture_output=True,
                    text=True,
                    shell=True,
                , timeout=60)
                if result.returncode != 0:
                    raise Exception(f"Failed to create symlink: {result.stderr}")
            else:
                # Unix-style symlink
                os.symlink(source_profile, target_profile)
            logger.info(f"Created symlink from {source_profile.name} to {target_profile.name}")
        except Exception as e:
            # If symlink fails, fall back to copy
            logger.warning(f"Symlink creation failed: {e}")
            logger.warning("Falling back to file copy method.")
            shutil.copy2(source_profile, target_profile)
            logger.info(f"Copied {source_profile.name} to {target_profile.name}")

        return True
    except Exception as e:
        logger.error(f"Error linking device profile: {e}")
        return False


def main():
    """Main entry point for device profile resolution."""
    logger.info("Starting Device Profile Resolution")

    # Get device information
    device_name = get_device_name()
    device_info = get_device_info()
    logger.info(f"Detected device: {device_name}")

    # Load and update device config
    update_device_config(device_name)

    # Link the appropriate device profile
    success = link_device_profile(device_name)
    if success:
        logger.info(f"Successfully linked device profile for {device_name}")
    else:
        logger.error(f"Failed to link device profile for {device_name}")

    # Write device info to log
    logger.info(f"Device information: {json.dumps(device_info, indent=2)}")
    logger.info("Device Profile Resolution complete")


if __name__ == "__main__":
    main()


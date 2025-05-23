"""
Cross-device path resolver for the bar-directory-recon repository
"""

import os
import sys
import json
import platform
from pathlib import Path

def get_device_name():
    """Detect the current device based on hostname"""
    hostname = platform.node().upper()
    if "ROG" in hostname or "LUCCI" in hostname:
        return "ROG-LUCCI"
    elif "SALESREP" in hostname:
        return "SALESREP"
    else:
        # Default to current username
        return f"Unknown ({os.getlogin()})"

def get_config_path():
    """Get the path to device_config.json"""
    script_dir = Path(__file__).parent.absolute()
    root_dir = script_dir.parent
    config_path = root_dir / "config" / "device_config.json"

    if config_path.exists():
        return config_path
    return None

def get_onedrive_path():
    """Get the path to OneDrive based on current device"""
    # Try to load config
    config_path = get_config_path()
    if config_path:
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            device = get_device_name()

            if device in config["devices"]:
                return config["devices"][device]["onedrive_path"]
        except Exception as e:
            print(f"Error loading config: {e}")

    # Fallback methods
    username = os.getlogin()

    # Check common OneDrive paths
    potential_paths = [
        f"C:\\Users\\{username}\\OneDrive - Digital Age Marketing Group",
        f"C:\\Users\\{username}\\OneDrive"
    ]

    for path in potential_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return path

    return None

def get_project_path():
    """Get the path to the project directory"""
    onedrive = get_onedrive_path()
    if not onedrive:
        return None

    # Try to find the project path based on device
    device = get_device_name()
    config_path = get_config_path()

    if config_path:
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            if device in config["devices"]:
                return config["devices"][device]["project_path"]
        except Exception as e:
            print(f"Error loading config: {e}")

    # Fallback to common locations
    potential_paths = [
        os.path.join(onedrive, "Desktop", "Local Py", "Work Projects", "bar-directory-recon"),
        os.path.join(onedrive, "Documents", "Projects", "bar-directory-recon")
    ]

    for path in potential_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return path

    return None

def resolve_path(path):
    """Resolve a path to be compatible with the current device"""
    if not path:
        return None

    onedrive_path = get_onedrive_path()
    project_path = get_project_path()

    if not onedrive_path or not project_path:
        return path

    # Replace OneDrive path
    if "OneDrive" in path:
        return path.replace(os.path.dirname(os.path.dirname(onedrive_path)), onedrive_path)

    # Replace project path
    if "bar-directory-recon" in path:
        parts = path.split("bar-directory-recon")
        if len(parts) > 1:
            return os.path.join(project_path, parts[1].lstrip("\\/"))

    return path

if __name__ == "__main__":
    print(f"Current device: {get_device_name()}")
    print(f"OneDrive path: {get_onedrive_path()}")
    print(f"Project path: {get_project_path()}")

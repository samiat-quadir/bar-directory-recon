#!/usr/bin/env python3
"""
Device Path Resolver

This module resolves device-specific paths and settings to ensure
cross-device consistency in development. It's used by Git hooks and
other automation tools to maintain a consistent environment.
"""

import os
import json
import platform
import sys
from pathlib import Path
from typing import Dict, Optional, Union, List, Any

# Known device configurations
DEVICE_CONFIGS = {
    "DESKTOP-ACER": {
        "username": "samq",
        "onedrive_folder": "OneDrive - Digital Age Marketing Group"
    },
    "LAPTOP-ASUS": {
        "username": "samqu",
        "onedrive_folder": "OneDrive - Digital Age Marketing Group"
    }
}

def get_python_interpreter():
    """
    Returns the appropriate Python interpreter path for the current device.

    This function handles differences between Windows and Unix-based systems,
    and provides device-specific Python paths if needed.

    Returns:
        str: Path to the Python interpreter
    """
    # Get current Python interpreter by default
    current_python = sys.executable

    # Use system-specific logic to determine the right interpreter
    system = platform.system().lower()

    # Device-specific overrides (customize based on your environment)
    device_name = os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME', '').lower()

    # Dict of device-specific Python paths (add your devices here)
    device_paths = {
        # Example mappings - replace with your actual device names and paths
        'salesrep': {
            'windows': r'C:\Python312\python.exe',
            'linux': '/usr/bin/python3',
            'darwin': '/usr/local/bin/python3'
        },
        'workstation': {
            'windows': r'C:\Python312\python.exe',
            'linux': '/usr/bin/python3',
            'darwin': '/usr/local/bin/python3'
        }
    }    # Check for device-specific settings
    if device_name and device_name.lower() in device_paths:
        if system in device_paths[device_name.lower()]:
            return device_paths[device_name.lower()][system]

    # Default fallback paths by system
    default_paths = {
        'windows': r'python.exe',  # Use system PATH
        'linux': '/usr/bin/python3',
        'darwin': '/usr/bin/python3'
    }

    # Use system default path if no specific match
    if system in default_paths:
        return default_paths[system]

    # Final fallback is the current Python executable
    return current_python


def get_current_device() -> Optional[str]:
    """
    Detect the current device based on computer name and username.

    Returns:
        str: Device identifier from DEVICE_CONFIGS, or None if not found
    """
    computer_name = platform.node()
    username = os.getlogin()

    # First try to match by computer name
    for device in DEVICE_CONFIGS:
        if device in computer_name:
            return device

    # If no match by computer name, try by username
    for device, config in DEVICE_CONFIGS.items():
        if config["username"] == username:
            return device

    return None


def get_onedrive_path() -> str:
    """
    Get the correct OneDrive path for the current device.

    Returns:
        str: The detected OneDrive path
    """
    # Try to detect automatically first
    device = get_current_device()

    if device and device in DEVICE_CONFIGS:
        username = DEVICE_CONFIGS[device]["username"]
        onedrive_folder = DEVICE_CONFIGS[device]["onedrive_folder"]
        path = os.path.join("C:\\", "Users", username, onedrive_folder)

        if os.path.exists(path):
            return path

    # If automatic detection fails, try common locations
    possible_paths = [
        os.path.join("C:\\", "Users", "samq", "OneDrive - Digital Age Marketing Group"),
        os.path.join("C:\\", "Users", "samqu", "OneDrive - Digital Age Marketing Group"),
        os.path.join("C:\\", "Users", os.getlogin(), "OneDrive - Digital Age Marketing Group")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # If still no match, look for OneDrive folders
    user_folder = os.path.join("C:\\", "Users", os.getlogin())
    if os.path.exists(user_folder):
        onedrive_folders = [f for f in os.listdir(user_folder)
                          if os.path.isdir(os.path.join(user_folder, f)) and f.startswith("OneDrive")]
        if onedrive_folders:
            return os.path.join(user_folder, onedrive_folders[0])

    # If all else fails, return the current directory
    print("Warning: Could not determine OneDrive path. Using current directory.")
    return os.getcwd()


def get_project_root_path(onedrive_path: Optional[str] = None,
                         project_name: str = "bar-directory-recon",
                         sub_path: str = "Desktop\\Local Py\\Work Projects") -> Optional[str]:
    """
    Get the project root path.

    Args:
        onedrive_path: Path to OneDrive folder (will auto-detect if None)
        project_name: Name of the project folder
        sub_path: Path within OneDrive where the project is located

    Returns:
        str: Path to the project root, or None if not found
    """
    if onedrive_path is None:
        onedrive_path = get_onedrive_path()

    # First try the expected path within OneDrive
    project_path = os.path.join(onedrive_path, sub_path, project_name)

    if os.path.exists(project_path):
        return project_path

    # If not found, check if we're already in the project directory
    current_dir = os.getcwd()
    if os.path.basename(current_dir) == project_name:
        return current_dir

    # Also try the repository root method as a backup
    repo_root = get_repository_root()
    if os.path.basename(repo_root) == project_name:
        return repo_root

    # If all else fails, return None
    print(f"Warning: Could not find project path for '{project_name}'. Please specify the path manually.")
    return None


def to_project_relative_path(path: str, project_root: Optional[str] = None) -> str:
    """
    Convert an absolute path to a path relative to the project root.

    Args:
        path: The path to convert
        project_root: Path to the project root (will auto-detect if None)

    Returns:
        str: Relative path, or original path if not within project
    """
    if project_root is None:
        project_root = get_project_root_path()
        if project_root is None:
            return path

    # Ensure both paths are absolute
    abs_path = os.path.abspath(path)
    abs_root = os.path.abspath(project_root)

    # Check if the path is within the project root
    if abs_path.startswith(abs_root):
        rel_path = abs_path[len(abs_root):]
        if rel_path.startswith(os.sep):
            rel_path = rel_path[1:]
        return rel_path

    # If not within the project, return the original path
    return path


def get_repository_root() -> str:
    """
    Get the Git repository root directory by traversing up from current dir.

    Returns:
        str: The repository root path, or current directory if not in a repo
    """
    current_dir = os.path.abspath(os.getcwd())

    # Try to find .git directory by walking up from current directory
    path = Path(current_dir)
    for _ in range(10):  # Limit search depth to 10 levels
        if (path / '.git').exists() and (path / '.git').is_dir():
            return str(path)

        parent = path.parent
        if parent == path:  # Reached root directory
            break
        path = parent

    # If not found, fall back to project root
    project_root = get_project_root_path()
    if project_root is not None:
        return project_root

    # Final fallback to current directory
    return current_dir


def get_data_directory() -> str:
    """
    Get the data directory for the project.

    Returns:
        str: Path to the data directory
    """
    project_root = get_project_root_path()
    if project_root is None:
        # Fallback to a subdirectory of the current directory
        return os.path.join(os.getcwd(), "data")

    # Check common data directory locations
    possible_paths = [
        os.path.join(project_root, "data"),
        os.path.join(project_root, "database"),
        os.path.join(project_root, "datasets")
    ]

    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return path

    # Default to data subdirectory of project root
    data_dir = os.path.join(project_root, "data")

    # Create it if it doesn't exist
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
        except Exception as e:
            print(f"Warning: Could not create data directory: {e}")

    return data_dir


def set_device_config(key: str, value: Any, device_id: Optional[str] = None) -> Dict:
    """
    Set device-specific configuration.

    Args:
        key: Configuration key to set
        value: Value to store
        device_id: Device identifier (defaults to current computer name)

    Returns:
        dict: Updated configuration
    """
    if device_id is None:
        device_id = platform.node()

    project_root = get_project_root_path()
    if project_root is None:
        raise ValueError("Could not determine project root path")

    config_dir = os.path.join(project_root, "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    config_file = os.path.join(config_dir, "device_config.json")

    # Load existing config or create new
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        from datetime import datetime
        config = {
            "DeviceId": device_id,
            "Settings": {},
            "Paths": {},
            "LastUpdated": datetime.now().isoformat()
        }

    # Update with new value
    if "Settings" not in config:
        config["Settings"] = {}

    config["Settings"][key] = value

    # Update timestamp
    from datetime import datetime
    config["LastUpdated"] = datetime.now().isoformat()

    # Save config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

    return config


def register_current_device(force: bool = False) -> Dict:
    """
    Register the current device in the configuration.

    Args:
        force: If True, re-register even if already registered

    Returns:
        dict: The updated device configuration
    """
    project_root = get_project_root_path()
    if project_root is None:
        raise ValueError("Could not determine project root path")

    config_dir = os.path.join(project_root, "config")
    config_file = os.path.join(config_dir, "device_config.json")

    # Check if device is already registered
    if os.path.exists(config_file) and not force:
        with open(config_file, 'r') as f:
            config = json.load(f)

        if config.get("DeviceId") == platform.node():
            print(f"Device already registered as: {config['DeviceId']}")
            return config

    # Ensure config directory exists
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Create new device config
    onedrive_path = get_onedrive_path()

    from datetime import datetime
    now = datetime.now().isoformat()

    config = {
        "DeviceId": platform.node(),
        "Username": os.getlogin(),
        "Settings": {
            "DefaultEditor": "code"
        },
        "Paths": {
            "OneDrive": onedrive_path,
            "ProjectRoot": project_root,
            "DataDirectory": get_data_directory(),
            "RepoRoot": get_repository_root()
        },
        "FirstRegistered": now,
        "LastUpdated": now
    }

    # Save config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"Device registered as: {config['DeviceId']}")
    print(f"OneDrive path: {config['Paths']['OneDrive']}")
    print(f"Project root: {config['Paths']['ProjectRoot']}")

    return config


if __name__ == "__main__":
    # When run directly, output useful diagnostics
    import argparse

    parser = argparse.ArgumentParser(description="Device path resolver utility")
    parser.add_argument("--onedrive", action="store_true", help="Output only the OneDrive path")
    parser.add_argument("--project", action="store_true", help="Output only the project root path")
    parser.add_argument("--python", action="store_true", help="Output only the Python interpreter path")
    parser.add_argument("--register", action="store_true", help="Register the current device")
    parser.add_argument("--force", action="store_true", help="Force registration even if already registered")
    parser.add_argument("--config", nargs="*", help="Get or set configuration")
    args = parser.parse_args()
      # Handle specific output requests
    if args.onedrive:
        print(get_onedrive_path())
    elif args.project:
        print(get_project_root_path() or "")
    elif args.python:
        print(get_python_interpreter())
    elif args.register:
        # Register the current device
        try:
            register_current_device(force=args.force)
        except Exception as e:
            print(f"Error registering device: {e}")
            sys.exit(1)
    elif args.config is not None:
        # Handle config operations
        if len(args.config) == 0:
            # Print all config
            print("\nDevice Configuration:")
            config = get_device_config()
            if config:
                import pprint
                pprint.pprint(config)
            else:
                print("No device configuration found.")
        elif len(args.config) == 1:
            # Get specific config
            key = args.config[0]
            value = get_device_config(key)
            print(f"\nConfig[{key}] = {value}")
        elif len(args.config) == 2:
            # Set specific config
            key, value = args.config
            try:
                set_device_config(key, value)
                print(f"Set Config[{key}] = {value}")
            except Exception as e:
                print(f"Error setting configuration: {e}")
                sys.exit(1)
        else:
            print("Usage: --config [key [value]]")
    else:
        # Print full diagnostics by default
        print(f"Device Path Resolver Information:")
        print(f"=================================")
        print(f"Current device: {platform.node()}")
        try:
            print(f"Current user: {os.getlogin()}")
        except:
            print(f"Current user: {os.environ.get('USERNAME') or os.environ.get('USER', 'Unknown')}")
        print(f"Detected device config: {get_current_device() or 'Unknown'}")
        print(f"Python interpreter: {get_python_interpreter()}")
        print(f"OneDrive path: {get_onedrive_path()}")
        print(f"Project root: {get_project_root_path() or 'Unknown'}")
        print(f"Repository root: {get_repository_root()}")
        print(f"Data directory: {get_data_directory()}")

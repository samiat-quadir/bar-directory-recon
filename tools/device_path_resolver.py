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
<<<<<<< HEAD
from typing import Dict, Optional, Any, cast
import getpass

# Known device configurations
DEVICE_CONFIGS = {
    "DESKTOP-ACER": {"username": "samq", "onedrive_folder": "OneDrive - Digital Age Marketing Group"},
    "LAPTOP-ASUS": {"username": "samqu", "onedrive_folder": "OneDrive - Digital Age Marketing Group"},
    "ROG-LUCCI": {"username": "samqu", "onedrive_folder": "OneDrive - Digital Age Marketing Group"},
    "SALESREP": {"username": "samq", "onedrive_folder": "OneDrive - Digital Age Marketing Group"},
}


def get_python_interpreter() -> str:
=======
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
>>>>>>> origin/main
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
<<<<<<< HEAD
    device_name = os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME", "").lower()
=======
    device_name = os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME', '').lower()
>>>>>>> origin/main

    # Dict of device-specific Python paths (add your devices here)
    device_paths = {
        # Example mappings - replace with your actual device names and paths
<<<<<<< HEAD
        "salesrep": {
            "windows": r"C:\Python312\python.exe",
            "linux": "/usr/bin/python3",
            "darwin": "/usr/local/bin/python3",
        },
        "workstation": {
            "windows": r"C:\Python312\python.exe",
            "linux": "/usr/bin/python3",
            "darwin": "/usr/local/bin/python3",
        },
    }

    # Check for device-specific settings
=======
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
>>>>>>> origin/main
    if device_name and device_name.lower() in device_paths:
        if system in device_paths[device_name.lower()]:
            return device_paths[device_name.lower()][system]

    # Default fallback paths by system
    default_paths = {
<<<<<<< HEAD
        "windows": r"python.exe",  # Use system PATH
        "linux": "/usr/bin/python3",
        "darwin": "/usr/bin/python3",
=======
        'windows': r'python.exe',  # Use system PATH
        'linux': '/usr/bin/python3',
        'darwin': '/usr/bin/python3'
>>>>>>> origin/main
    }

    # Use system default path if no specific match
    if system in default_paths:
        return default_paths[system]

    # Final fallback is the current Python executable
    return current_python

<<<<<<< HEAD
=======

>>>>>>> origin/main
def get_current_device() -> Optional[str]:
    """
    Detect the current device based on computer name and username.

    Returns:
        str: Device identifier from DEVICE_CONFIGS, or None if not found
    """
    computer_name = platform.node()
<<<<<<< HEAD
    username = getpass.getuser()
=======
>>>>>>> origin/main
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

<<<<<<< HEAD
    possible_paths = [
        os.path.join("C:\\", "Users", "samq", "OneDrive - Digital Age Marketing Group"),
        os.path.join("C:\\", "Users", "samqu", "OneDrive - Digital Age Marketing Group"),
        os.path.join("C:\\", "Users", getpass.getuser(), "OneDrive - Digital Age Marketing Group"),
=======
    # If automatic detection fails, try common locations
    possible_paths = [
        os.path.join("C:\\", "Users", "samq", "OneDrive - Digital Age Marketing Group"),
        os.path.join("C:\\", "Users", "samqu", "OneDrive - Digital Age Marketing Group"),
        os.path.join("C:\\", "Users", os.getlogin(), "OneDrive - Digital Age Marketing Group")
>>>>>>> origin/main
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

<<<<<<< HEAD
    user_folder = os.path.join("C:\\", "Users", getpass.getuser())
    user_folder = os.path.join("C:\\", "Users", os.getlogin())
    if os.path.exists(user_folder):
        onedrive_folders = [
            f
            for f in os.listdir(user_folder)
            if os.path.isdir(os.path.join(user_folder, f)) and f.startswith("OneDrive")
        ]
=======
    # If still no match, look for OneDrive folders
    user_folder = os.path.join("C:\\", "Users", os.getlogin())
    if os.path.exists(user_folder):
        onedrive_folders = [f for f in os.listdir(user_folder)
                          if os.path.isdir(os.path.join(user_folder, f)) and f.startswith("OneDrive")]
>>>>>>> origin/main
        if onedrive_folders:
            return os.path.join(user_folder, onedrive_folders[0])

    # If all else fails, return the current directory
    print("Warning: Could not determine OneDrive path. Using current directory.")
    return os.getcwd()


<<<<<<< HEAD
def get_project_root_path(
    onedrive_path: Optional[str] = None,
    project_name: str = "bar-directory-recon-new",
    sub_path: str = "Desktop\\Local Py\\Work Projects",
) -> Optional[str]:
    """
    Get the correct project root path for the current device.

    Args:
        onedrive_path: Override the OneDrive path detection (optional)
        project_name: Name of the project folder
        sub_path: Subfolder path under OneDrive

    Returns:
        str: The detected project root path, or None if not found
    """
    # Use provided OneDrive path or detect it
    if onedrive_path is None:
        onedrive_path = get_onedrive_path()

    # Try with provided project name
    project_path = os.path.join(onedrive_path, sub_path, project_name)
    if os.path.exists(project_path):
        return project_path

    # Try with original project name (without -new suffix)
    if "new" in project_name:
        original_name = project_name.replace("-new", "")
        project_path = os.path.join(onedrive_path, sub_path, original_name)
        if os.path.exists(project_path):
            return project_path

    # If project name is already without -new, try with -new added
    else:
        new_name = f"{project_name}-new"
        project_path = os.path.join(onedrive_path, sub_path, new_name)
        if os.path.exists(project_path):
            return project_path

    # Try searching for any folder that starts with the project name
    base_path = os.path.join(onedrive_path, sub_path)
    if os.path.exists(base_path):
        for folder in os.listdir(base_path):
            if folder.startswith(project_name.split("-")[0]) and os.path.isdir(os.path.join(base_path, folder)):
                return os.path.join(base_path, folder)

    # As a last resort, try current directory or its parent
=======
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
>>>>>>> origin/main
    current_dir = os.getcwd()
    if os.path.basename(current_dir) == project_name:
        return current_dir

<<<<<<< HEAD
    parent_dir = os.path.dirname(current_dir)
    if os.path.basename(parent_dir) == project_name:
        return parent_dir

    # If all else fails, return None
    print(f"Warning: Could not determine project root path for {project_name}.")
=======
    # Also try the repository root method as a backup
    repo_root = get_repository_root()
    if os.path.basename(repo_root) == project_name:
        return repo_root

    # If all else fails, return None
    print(f"Warning: Could not find project path for '{project_name}'. Please specify the path manually.")
>>>>>>> origin/main
    return None


def to_project_relative_path(path: str, project_root: Optional[str] = None) -> str:
    """
<<<<<<< HEAD
    Convert an absolute path to a project-relative path.

    Args:
        path: The absolute path to convert
        project_root: The project root path (optional, will be detected if not provided)

    Returns:
        str: The project-relative path
    """
    if project_root is None:
        project_root = get_project_root_path()

    if project_root is None:
        # If we can't determine project root, return the original path
        return path

    # Convert both to Path objects for easier manipulation
    try:
        path_obj = Path(path)
        root_obj = Path(project_root)

        # Try to make the path relative to project root
        try:
            relative = path_obj.relative_to(root_obj)
            return str(relative)
        except ValueError:
            # If path is not under project root, return the original path
            return path
    except Exception:
        # If any other error occurs, return the original path
        return path
=======
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
>>>>>>> origin/main


def get_repository_root() -> str:
    """
<<<<<<< HEAD
    Get the Git repository root for the current project.

    Returns:
        str: Path to the repository root
    """
    # Start from project root
    project_root = get_project_root_path()
    if not project_root:
        return os.getcwd()

    # Check if project root is a git repo
    git_dir = os.path.join(project_root, ".git")
    if os.path.exists(git_dir) and os.path.isdir(git_dir):
        return project_root

    # Check parent directories
    current_dir = project_root
    while current_dir and current_dir != os.path.dirname(current_dir):
        git_dir = os.path.join(current_dir, ".git")
        if os.path.exists(git_dir) and os.path.isdir(git_dir):
            return current_dir
        current_dir = os.path.dirname(current_dir)

    # If no git repository found, return project root
    return project_root
=======
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
>>>>>>> origin/main


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
<<<<<<< HEAD
        os.path.join(project_root, "datasets"),
=======
        os.path.join(project_root, "datasets")
>>>>>>> origin/main
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


<<<<<<< HEAD
def get_device_config(
    key: Optional[str] = None, default_value: Any = None, device_id: Optional[str] = None
) -> Any:
    """
    Get device-specific configuration.

    Args:
        key: Configuration key to retrieve (None to get entire config)
        default_value: Default value to return if key is not found
        device_id: Device identifier (defaults to current computer name)

    Returns:
        Union[Dict, Any]: The config dict or specific value
    """
    if device_id is None:
        device_id = platform.node()

    project_root = get_project_root_path()
    if project_root is None:
        return default_value

    config_file = os.path.join(project_root, "config", "device_config.json")

    # Check if config file exists
    if not os.path.exists(config_file):
        return default_value

    # Load config
    with open(config_file, "r") as f:
        config = json.load(f)

    # If no key specified, return the entire config
    if key is None:
        return cast(Dict[str, Any], config)

    # Return the specific key value
    if "Settings" in config and key in config["Settings"]:
        return config["Settings"][key]

    return default_value


=======
>>>>>>> origin/main
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
<<<<<<< HEAD
        with open(config_file, "r") as f:
            config = json.load(f)
    else:
        from datetime import datetime

        config = {"DeviceId": device_id, "Settings": {}, "Paths": {}, "LastUpdated": datetime.now().isoformat()}
=======
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
>>>>>>> origin/main

    # Update with new value
    if "Settings" not in config:
        config["Settings"] = {}

    config["Settings"][key] = value

    # Update timestamp
    from datetime import datetime
<<<<<<< HEAD

    config["LastUpdated"] = datetime.now().isoformat()

    # Save config
    with open(config_file, "w") as f:
=======
    config["LastUpdated"] = datetime.now().isoformat()

    # Save config
    with open(config_file, 'w') as f:
>>>>>>> origin/main
        json.dump(config, f, indent=4)

    return config


<<<<<<< HEAD
def register_current_device(force: bool = False) -> Dict[str, Any]:
=======
def register_current_device(force: bool = False) -> Dict:
>>>>>>> origin/main
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
<<<<<<< HEAD
        with open(config_file, "r") as f:
=======
        with open(config_file, 'r') as f:
>>>>>>> origin/main
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
<<<<<<< HEAD

    now = datetime.now().isoformat()
    config = {
        "DeviceId": platform.node(),
        "Username": getpass.getuser(),
        "Settings": {"DefaultEditor": "code"},
=======
    now = datetime.now().isoformat()

    config = {
        "DeviceId": platform.node(),
        "Username": os.getlogin(),
        "Settings": {
            "DefaultEditor": "code"
        },
>>>>>>> origin/main
        "Paths": {
            "OneDrive": onedrive_path,
            "ProjectRoot": project_root,
            "DataDirectory": get_data_directory(),
<<<<<<< HEAD
            "RepoRoot": get_repository_root(),
        },
        "FirstRegistered": now,
        "LastUpdated": now,
    }

    # Save config
    with open(config_file, "w") as f:
=======
            "RepoRoot": get_repository_root()
        },
        "FirstRegistered": now,
        "LastUpdated": now
    }

    # Save config
    with open(config_file, 'w') as f:
>>>>>>> origin/main
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
<<<<<<< HEAD

    # Handle specific output requests
=======
      # Handle specific output requests
>>>>>>> origin/main
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
<<<<<<< HEAD

=======
>>>>>>> origin/main
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
<<<<<<< HEAD
        print("Device Path Resolver Information:")
        print("=================================")
        try:
            print(f"Current user: {getpass.getuser()}")
        except Exception:
            print(f"Current user: {os.environ.get('USERNAME') or os.environ.get('USER', 'Unknown')}")
=======
        print(f"Device Path Resolver Information:")
        print(f"=================================")
        print(f"Current device: {platform.node()}")
        try:
            print(f"Current user: {os.getlogin()}")
        except:
>>>>>>> origin/main
            print(f"Current user: {os.environ.get('USERNAME') or os.environ.get('USER', 'Unknown')}")
        print(f"Detected device config: {get_current_device() or 'Unknown'}")
        print(f"Python interpreter: {get_python_interpreter()}")
        print(f"OneDrive path: {get_onedrive_path()}")
        print(f"Project root: {get_project_root_path() or 'Unknown'}")
        print(f"Repository root: {get_repository_root()}")
        print(f"Data directory: {get_data_directory()}")

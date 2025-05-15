#!/usr/bin/env python3
"""
Device Path Resolver

This module resolves device-specific paths and settings to ensure
cross-device consistency in development. It's used by Git hooks and
other automation tools to maintain a consistent environment.
"""

import os
import platform
import sys


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
    }

    # Check for device-specific settings
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


def get_repository_root():
    """
    Returns the repository root directory path.

    This is useful for scripts that need to operate at the repo level,
    regardless of where they are called from.

    Returns:
        str: Absolute path to the repository root
    """
    # This assumes this script is in the tools directory at the repo root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, os.pardir))
    return repo_root


def get_data_directory():
    """
    Returns the path to the data directory for the current device.

    This helps manage different data locations across development devices.

    Returns:
        str: Path to the data directory
    """
    repo_root = get_repository_root()
    # Default location in the repository
    default_data_dir = os.path.join(repo_root, 'data')

    # Device-specific overrides
    device_name = os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME', '').lower()

    # Define device-specific data directories here
    device_data_dirs = {
        # Example - replace with your actual paths
        'salesrep': r'C:\Users\samq\OneDrive - Digital Age Marketing Group\Data',
        'workstation': r'/home/user/data'
    }

    if device_name and device_name.lower() in device_data_dirs:
        return device_data_dirs[device_name.lower()]

    # Fallback to default
    return default_data_dir


if __name__ == "__main__":
    # When run directly, print paths for debugging
    print(f"Python interpreter: {get_python_interpreter()}")
    print(f"Repository root: {get_repository_root()}")
    print(f"Data directory: {get_data_directory()}")

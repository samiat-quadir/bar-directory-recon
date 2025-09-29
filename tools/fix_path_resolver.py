#!/usr/bin/env python3
"""
Device Path Resolver Fix

This script repairs the get_onedrive_path function in the device_path_resolver.py file,
which appears to have some corrupted nested function calls. Run this script to automatically
fix the device_path_resolver.py file.
"""

import os
import re
import sys


def find_device_path_resolver():
    """Find the device_path_resolver.py file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Try in the current directory
    if os.path.exists(os.path.join(script_dir, "device_path_resolver.py")):
        return os.path.join(script_dir, "device_path_resolver.py")

    # Try in the tools directory
    if os.path.exists(os.path.join(script_dir, "tools", "device_path_resolver.py")):
        return os.path.join(script_dir, "tools", "device_path_resolver.py")

    # Try in the parent directory's tools
    parent_dir = os.path.dirname(script_dir)
    if os.path.exists(os.path.join(parent_dir, "tools", "device_path_resolver.py")):
        return os.path.join(parent_dir, "tools", "device_path_resolver.py")

    return None


def fix_device_path_resolver():
    """Fix the device_path_resolver.py file"""
    resolver_path = find_device_path_resolver()
    if not resolver_path:
        print("Error: Could not find device_path_resolver.py")
        return False

    print(f"Found device_path_resolver.py at: {resolver_path}")

    # Read the file content
    with open(resolver_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Create a backup
    backup_path = resolver_path + ".bak"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created backup at: {backup_path}")

    # Fix the get_onedrive_path function
    pattern = r"def os\.path\.join\(get_project_root_path\(\), 'os\.path\.join.*?\(\)"
    replacement = """def get_onedrive_path() -> str:
    \"\"\"
    Get the correct OneDrive path for the current device.

    Returns:
        str: The detected OneDrive path
    \"\"\"
    # Try to detect automatically first
    device = get_current_device()

    if device and device in DEVICE_CONFIGS:
        username = DEVICE_CONFIGS[device]["username"]
        onedrive_folder = DEVICE_CONFIGS[device]["onedrive_folder"]
        path = os.path.join("C:\\\\", "Users", username, onedrive_folder)

        if os.path.exists(path):
            return path

    # If automatic detection fails, try common locations
    possible_paths = [
        os.path.join("C:\\\\", "Users", "samq", "OneDrive - Digital Age Marketing Group"),
        os.path.join("C:\\\\", "Users", "samqu", "OneDrive - Digital Age Marketing Group"),
        os.path.join("C:\\\\", "Users", os.getlogin(), "OneDrive - Digital Age Marketing Group")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # If still no match, look for OneDrive folders
    user_folder = os.path.join("C:\\\\", "Users", os.getlogin())
    if os.path.exists(user_folder):
        onedrive_folders = [f for f in os.listdir(user_folder)
                         if os.path.isdir(os.path.join(user_folder, f)) and f.startswith("OneDrive")]
        if onedrive_folders:
            return os.path.join(user_folder, onedrive_folders[0])

    # If all else fails, return the current directory
    print("Warning: Could not determine OneDrive path. Using current directory.")
    return os.getcwd()"""

    # Replace the corrupted function
    new_content = re.sub(pattern, replacement, content)

    # Fix reference to get_onedrive_path in get_project_root_path
    get_project_root_pattern = r"onedrive_path = os\.path\.join\(get_project_root_path\(\), 'os\.path\.join.*?\(\)"
    get_project_root_replacement = "onedrive_path = get_onedrive_path()"
    new_content = re.sub(
        get_project_root_pattern, get_project_root_replacement, new_content
    )

    # Fix reference to get_onedrive_path in register_current_device
    register_current_device_pattern = r"onedrive_path = os\.path\.join\(get_project_root_path\(\), 'os\.path\.join.*?\(\)"
    register_current_device_replacement = "onedrive_path = get_onedrive_path()"
    new_content = re.sub(
        register_current_device_pattern,
        register_current_device_replacement,
        new_content,
    )

    # Fix any args.onedrive path references
    args_onedrive_pattern = (
        r"print\(os\.path\.join\(get_project_root_path\(\), 'os\.path\.join.*?\(\)\)"
    )
    args_onedrive_replacement = "print(get_onedrive_path())"
    new_content = re.sub(args_onedrive_pattern, args_onedrive_replacement, new_content)

    # Fix references in diagnostic output
    diagnostics_pattern = r"print\(f\"OneDrive path: \{os\.path\.join\(get_project_root_path\(\), 'os\.path\.join.*?\(\)\}\"\)"
    diagnostics_replacement = 'print(f"OneDrive path: {get_onedrive_path()}")'
    new_content = re.sub(diagnostics_pattern, diagnostics_replacement, new_content)

    # Write the fixed content back to the file
    with open(resolver_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Successfully fixed device_path_resolver.py")

    # Ensure SALESREP is in DEVICE_CONFIGS
    if "SALESREP" not in new_content:
        print("Adding SALESREP to DEVICE_CONFIGS...")
        # Read the file again to ensure we have the latest content
        with open(resolver_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Add SALESREP to DEVICE_CONFIGS
        device_configs_pattern = r'(DEVICE_CONFIGS = \{.*?"ROG-LUCCI": \{.*?"onedrive_folder": "OneDrive - Digital Age Marketing Group"\s+\})'
        device_configs_replacement = r'\1,\n    "SALESREP": {\n        "username": "samq",\n        "onedrive_folder": "OneDrive - Digital Age Marketing Group"\n    }'
        new_content = re.sub(
            device_configs_pattern, device_configs_replacement, content, flags=re.DOTALL
        )

        # Write the updated content back to the file
        with open(resolver_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print("Successfully added SALESREP to DEVICE_CONFIGS")

    return True


if __name__ == "__main__":
    print("Running device_path_resolver fix script...")
    success = fix_device_path_resolver()
    if success:
        print("Finished fixing device_path_resolver.py")
        print(
            "You can now run python tools/device_path_resolver.py to verify it works correctly"
        )
    else:
        print("Failed to fix device_path_resolver.py")
        sys.exit(1)

import json
import os
from pathlib import Path

PROFILE_FILE = "config/device_profile.json"


def get_device_profile():
    """
    Load the device profile information from the JSON file.
    If the file doesn't exist, returns None.
    """
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_device_type():
    """
    Get the device type from the profile file or environment.
    Returns "unknown" if not available.
    """
    # First try to get from environment
    device_type = os.environ.get("MACHINE_TYPE")
    if device_type:
        return device_type

    # Then try to get from profile file
    profile = get_device_profile()
    if profile and "device" in profile:
        return profile["device"].lower().replace(" ", "_")

    return "unknown"


def get_user_home():
    """
    Get the user's home directory from the profile or system.
    """
    profile = get_device_profile()
    if profile and "user_home" in profile:
        return profile["user_home"]

    return str(Path.home())


def get_python_path():
    """
    Get the Python executable path from the profile or system.
    """
    profile = get_device_profile()
    if profile and "python_path" in profile:
        return profile["python_path"]

    import sys

    return sys.executable


def resolve_path(path):
    """
    Resolve a path with potential user folder references to the correct path for the current device.

    Examples:
        resolve_path("C:/Users/samq/...") on ASUS machine will return "C:/Users/samqu/..."
        resolve_path("C:/Users/samqu/...") on Work Desktop will return "C:/Users/samq/..."
    """
    if not path:
        return path

    path_str = str(path)
    home_dir = get_user_home()
    device_type = get_device_type()

    # Replace specific user paths based on device
    if "samq" in path_str and "samqu" not in path_str and device_type == "asus":
        return path_str.replace("/samq/", "/samqu/").replace("\\samq\\", "\\samqu\\")
    elif "samqu" in path_str and device_type == "work_desktop":
        return path_str.replace("/samqu/", "/samq/").replace("\\samqu\\", "\\samq\\")

    # Try to use Path.home() substitution for more general cases
    if "C:/Users/samq" in path_str and device_type == "asus":
        return path_str.replace("C:/Users/samq", home_dir)
    elif "C:\\Users\\samq" in path_str and device_type == "asus":
        return path_str.replace("C:\\Users\\samq", home_dir)
    elif "C:/Users/samqu" in path_str and device_type == "work_desktop":
        return path_str.replace("C:/Users/samqu", home_dir)
    elif "C:\\Users\\samqu" in path_str and device_type == "work_desktop":
        return path_str.replace("C:\\Users\\samqu", home_dir)

    return path_str

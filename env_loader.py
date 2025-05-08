import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add tools directory to system path if not already there
tools_dir = Path(__file__).resolve().parent / "tools"
if str(tools_dir) not in sys.path:
    sys.path.append(str(tools_dir))

# Import device profile utils
try:
    from tools.device_profile_utils import get_device_type, resolve_path
except ImportError:
    # Fallback if device_profile_utils is not available
    def get_device_type():
        """Fallback function if device_profile_utils is not available."""
        return os.getenv("MACHINE_TYPE", "work").strip('"').strip("'").lower()

    def resolve_path(path):
        """Fallback function that returns the path unchanged."""
        return path


def load_environment():
    """
    Load environment variables based on device profile.
    Looks for .env.<device_type> in this script's folder; if missing,
    falls back to .env. Raises an error listing available .env* files if none found.
    """
    project_root = Path(__file__).resolve().parent

    # Get device type from profile or environment variable
    machine_type = get_device_type()

    # If machine_type is not set, try to detect it
    if not machine_type or machine_type == "unknown":
        # Try to run the device profile script to detect the machine type
        try:
            profile_script = project_root / "tools" / "resolve_device_profile.py"
            if profile_script.exists():
                print(f"Running device profile detection script: {profile_script}")
                # Get the script's directory into the path
                script_dir = profile_script.parent
                if str(script_dir) not in sys.path:
                    sys.path.append(str(script_dir))

                # Import and run the script
                from tools.resolve_device_profile import apply_profile

                device = apply_profile()
                machine_type = device.lower().replace(" ", "_")
                print(f"Detected machine type: {machine_type}")
            else:
                # Fallback to default
                machine_type = "work"
                print(f"Device profile script not found, defaulting to: {machine_type}")
        except Exception as e:
            print(f"Warning: Failed to run device profile detection: {e}")
            machine_type = "work"  # Default fallback

    # Use the detected or provided machine type
    print(f"Using machine type: {machine_type}")

    # Determine file paths
    env_specific = project_root / f".env.{machine_type}"
    env_default = project_root / ".env"

    # Choose the file
    if env_specific.exists():
        env_file = env_specific
    elif env_default.exists():
        env_file = env_default
        print(f"WARNING: {env_specific.name} not found; using fallback {env_file.name}")
    else:
        available = [p.name for p in project_root.glob(".env*")]
        raise FileNotFoundError(
            "No .env file found!\n" f"Tried: {env_specific.name} and {env_default.name}\n" f"Available: {available}"
        )

    # Load and report
    load_dotenv(env_file)
    print(f"Loaded environment from {env_file.name}")

    # Process environment variables with path resolution
    for key, value in os.environ.items():
        if any(
            path_indicator in key.lower()
            for path_indicator in ["_PATH", "_DIR", "PATH_", "DIR_", "FOLDER", "DIRECTORY"]
        ):
            resolved_path = resolve_path(value)
            if resolved_path != value:
                os.environ[key] = resolved_path
                print(f"Resolved path for {key}: {value} -> {resolved_path}")


if __name__ == "__main__":
    load_environment()

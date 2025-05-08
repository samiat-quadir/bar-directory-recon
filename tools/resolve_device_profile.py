import os
import platform
import getpass
import sys
from datetime import datetime
import subprocess

LOG_FILE = "logs/setup_log.txt"

def detect_device():
    """
    Detects the device profile based on the current user's username.
    Handles the specific case of samq vs samqu usernames.
    """
    username = getpass.getuser().lower()
    if "samqu" in username:
        return "ASUS"
    elif "samq" in username and "samqu" not in username:
        return "Work Desktop"
    else:
        return "Unknown"

def log(message):
    """Log a message to both the console and log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def check_python_version(expected_major):
    """Check if the Python version matches the expected major version."""
    actual_version = sys.version_info
    return actual_version.major == expected_major

def get_python_executable():
    """Get the current Python executable path safely."""
    return sys.executable

if __name__ == "__main__":
    try:
        device = detect_device()
        python_path = get_python_executable()
        
        log(f"🖥️  Detected device profile: {device}")
        log(f"🐍 Python executable: {python_path}")
        
        if check_python_version(3):
            log(f"✅ Python major version is correct (3.x)")
        else:
            log(f"⚠️ WARNING: Python version mismatch (expected 3.x, got {sys.version})")
    except Exception as e:
        log(f"❌ Error: {str(e)}")

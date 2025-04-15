import os
import sys
import socket
import shutil
import platform
import subprocess
from datetime import datetime
from env_loader import load_environment

# Load environment and project path
load_environment()

REPORT_PATH = "system_report.log"


def get_disk_usage(path="/"):
    total, used, free = shutil.disk_usage(path)
    return {
        "Total": f"{total // (2**30)} GB",
        "Used": f"{used // (2**30)} GB",
        "Free": f"{free // (2**30)} GB"
    }

def get_git_status():
    try:
        output = subprocess.check_output(["git", "status"], stderr=subprocess.DEVNULL)
        return output.decode("utf-8")
    except Exception as e:
        return f"Git status unavailable: {e}"

def check_env_vars(required_vars):
    status = {}
    for var in required_vars:
        value = os.getenv(var)
        status[var] = "✅ Found" if value else "❌ Missing"
    return status

def collect_system_info():
    return {
        "DateTime": datetime.now().isoformat(),
        "Computer Name": socket.gethostname(),
        "Platform": platform.system(),
        "OS Version": platform.version(),
        "Python Executable": sys.executable,
        "Python Version": platform.python_version(),
        "Current Working Dir": os.getcwd(),
        "Disk Usage": get_disk_usage("C:/"),
        "Git Status": get_git_status(),
        "Environment Variables": check_env_vars([
            "GMAIL_USER", "TO_EMAILS", "GMAIL_TOKEN_PATH",
            "LOCAL_GIT_REPO", "MOTION_API_KEY", "NGROK_AUTH_TOKEN",
            "MOTION_WORKSPACE_ID", "MOTION_PROJECT_ID", "GIT_EXECUTABLE_PATH"
        ])
    }

def write_report(info, path=REPORT_PATH):
    with open(path, "w", encoding="utf-8") as f:
        for key, value in info.items():
            f.write(f"\n[{key}]\n")
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    f.write(f"  {subkey}: {subvalue}\n")
            else:
                f.write(f"{value}\n")

if __name__ == "__main__":
    report_info = collect_system_info()
    write_report(report_info)
    print("System report generated to:", REPORT_PATH)

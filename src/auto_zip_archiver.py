import os
import subprocess
from datetime import datetime

LOG_FILE = "automation_run.log"


def log(message):
    """TODO: Add docstring."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")


def run_script(script_path):
    """TODO: Add docstring."""
    try:
        result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
        log(f"Running: {script_path}")
        log(result.stdout)
        if result.stderr:
            log(f"ERROR: {result.stderr}")
    except subprocess.CalledProcessError as e:
        log(f"FAILED: {script_path}")
        log(e.stderr)


scripts_to_run = [
    "env_loader.py",
    "project_path.py",
    os.path.join("src", "health_check.py"),
    "git_commit_and_notify.py",
    os.path.join("src", "log_rotator.py"),
    "generate_readme.py",
    os.path.join("src", "motion_task_via_email.py"),
    os.path.join("src", "log_summary.py"),
    os.path.join("src", "backup_manager.py"),
    os.path.join("src", "cleanup_old_files.py"),
]
if __name__ == "__main__":
    log("=== DAILY AUTOMATION START ===")
    for script in scripts_to_run:
        run_script(script)
    log("=== DAILY AUTOMATION COMPLETE ===\n")

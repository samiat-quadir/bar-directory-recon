import os
import subprocess
from datetime import datetime

# === Logging ===
LOG_FILE = "automation_run.log"


def log(message):
    """TODO: Add docstring."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")


def run_script(script_path):
    """Run the specified script and log the output."""
    try:
        log(f"Running: {script_path}")
        result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
        log(result.stdout)
        if result.stderr:
            log(f"ERROR: {result.stderr}")
    except subprocess.CalledProcessError as e:
        log(f"FAILED: {script_path}")
        log(e.stderr)


# === Define script paths ===
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
]

# === Main Execution ===
if __name__ == "__main__":
    log("=== DAILY AUTOMATION START ===")
    for script in scripts_to_run:
        run_script(script)

    # Step 7: Cleanup old logs and backups
    log("Running: cleanup_old_files.py")
    try:
        pass
    except Exception as e:
        log(f"ERROR running cleanup_old_files.py: {e}")

    log("=== DAILY AUTOMATION COMPLETE ===\n")

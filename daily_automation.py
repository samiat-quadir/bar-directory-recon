import os
import subprocess
from datetime import datetime

# === Logging ===
LOG_FILE = "automation_run.log"


def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}\n"
    print(full_message.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message)


def run_script(script_path):
    try:
        log(f"Running: {script_path}")
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        log(f"Error running {script_path}: {e}")
    except Exception as e:
        log(f"Unexpected error running {script_path}: {e}")


# === Define script paths ===
scripts_to_run = [
    "env_loader.py",
    "project_path.py",
    os.path.join("src", "health_check.py"),
    "git_commit_and_notify.py",
    os.path.join("src", "cleanup_manager.py"),  # Updated to use consolidated cleanup
    "generate_readme.py",
    os.path.join("src", "motion_task_via_email.py"),
    os.path.join("src", "log_summary.py"),
    os.path.join("src", "backup_manager.py"),
    os.path.join("src", "email_summary_report.py"),
]

# === Main Execution ===
if __name__ == "__main__":
    log("=== DAILY AUTOMATION START ===")
    for script in scripts_to_run:
        run_script(script)
    log("=== DAILY AUTOMATION COMPLETE ===\n")

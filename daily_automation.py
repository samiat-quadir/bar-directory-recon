import os
import subprocess
from datetime import datetime

# Set working directory to project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
LOG_FILE = os.path.join(PROJECT_ROOT, "automation_run.log")

# Helper function to log actions
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {message}"
    print(full_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(full_msg + "\n")

def run_script(script_path):
    try:
        log(f"Running: {script_path}")
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        log(result.stdout.strip())
        if result.stderr:
            log(f"ERROR: {result.stderr.strip()}")
    except Exception as e:
        log(f"Exception while running {script_path}: {str(e)}")

def main():
    log("=== DAILY AUTOMATION START ===")

    # Step 1: Set env and path
    run_script("env_loader.py")
    run_script("project_path.py")

    # Step 2: Core scripts
    run_script(os.path.join(SRC_DIR, "health_check.py"))
    run_script("git_commit_and_notify.py")
    run_script(os.path.join(SRC_DIR, "log_rotator.py"))
    run_script("generate_readme.py")

    # Step 3: Optional fallback Motion Task via Email (in case API fails)
    run_script(os.path.join(SRC_DIR, "motion_task_via_email.py"))

    log("=== DAILY AUTOMATION COMPLETE ===\n")

if __name__ == "__main__":
    main()

import os
import subprocess
import logging
from datetime import datetime
from env_loader import load_environment

# === Setup ===
load_environment()
logging.basicConfig(
    filename="git_commit_notify.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# === Pre-commit safety check ===
def run_pre_commit_validator():
    result = subprocess.run(
        ["python", "pre_commit_validator.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        logging.error("Pre-commit validation failed.")
        logging.error(result.stdout + result.stderr)
        print("ERROR: Pre-commit validation failed.")
        return False
    return True

# === Git Commit Logic ===
def run_git_command(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)

def git_commit_only():
    if not run_pre_commit_validator():
        print("Aborting: pre-commit validation failed.")
        return

    try:
        # Stage all changes
        run_git_command(["git", "add", "."])

        # Check if anything to commit
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        ).stdout
        if not status.strip():
            logging.info("No changes to commit.")
            print("No changes to commit.")
            return

        # Commit with timestamp
        commit_msg = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        run_git_command(["git", "commit", "-m", commit_msg])
        logging.info("Local git commit created.")
        print("Changes committed locally.")

    except subprocess.CalledProcessError as e:
        logging.error("Git command failed: " + e.stderr)
        print("ERROR: Git command failed:")
        print(e.stderr)

# === Main ===
if __name__ == "__main__":
    git_commit_only()

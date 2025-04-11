import os
import subprocess
import logging
from datetime import datetime
from project_path import set_root_path
set_root_path()

from env_loader import load_environment

# Load environment based on device
load_environment()

# Set up UTF-8 logging
log_file = "git_commit.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    encoding="utf-8"
)

# Environment Variables
LOCAL_GIT_REPO = os.path.normpath(os.getenv("LOCAL_GIT_REPO"))
COMMIT_PREFIX = os.getenv("COMMIT_PREFIX", "Auto-commit:")
GIT_PATH = "C:/Program Files/Git/cmd/git.exe"

def run_subprocess_command(command_list, allow_fail=False):
    """Run subprocess commands and handle output."""
    try:
        result = subprocess.run(
            command_list, cwd=LOCAL_GIT_REPO, check=True,
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Git command failed: {' '.join(command_list)}\n{e.stderr}")
        if allow_fail:
            return None
        raise e

def main():
    if not os.path.isdir(LOCAL_GIT_REPO):
        raise FileNotFoundError(f"LOCAL_GIT_REPO not found or invalid: {LOCAL_GIT_REPO}")

    # Verify Git installation
    git_version = run_subprocess_command([GIT_PATH, "--version"])
    logging.info(f"Git available: {git_version}")

    # Check for changes
    changes = run_subprocess_command([GIT_PATH, "status", "--porcelain"], allow_fail=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Commit changes
    if not changes:
        logging.info("No changes detected. Forcing an empty commit.")
        commit_msg = f"{COMMIT_PREFIX} No changes detected ({timestamp})"
        run_subprocess_command([GIT_PATH, "commit", "--allow-empty", "-m", commit_msg])
    else:
        run_subprocess_command([GIT_PATH, "add", "-A"])
        commit_msg = f"{COMMIT_PREFIX} {timestamp}"
        run_subprocess_command([GIT_PATH, "commit", "-m", commit_msg])
        logging.info(f"Commit created: {commit_msg}")

    # Push commit
    run_subprocess_command([GIT_PATH, "push", "origin", "main"])
    logging.info("Git push successful.")

if __name__ == "__main__":
    try:
        main()
        print("Auto Git Commit completed successfully.")
    except Exception as e:
        logging.error(f"Auto Git Commit failed: {e}")
        print(f"Error: {e}")

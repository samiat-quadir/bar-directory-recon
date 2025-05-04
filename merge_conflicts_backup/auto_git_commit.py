<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> 3ccf4fd (Committing all changes)
import logging
import os
import subprocess
from datetime import datetime

<<<<<<< HEAD
=======
=======
import logging
import os
import subprocess
from datetime import datetime

>>>>>>> 54c6ae3 (Committing all changes)
>>>>>>> 3ccf4fd (Committing all changes)
from env_loader import load_environment

# Load env vars early
load_environment()

# Setup logging
logging.basicConfig(
    filename="git_commit_notify.log",
    level=logging.INFO,
<<<<<<< HEAD
    format="%(asctime)s — %(levelname)s — %(message)s",
    encoding="utf-8",
=======
<<<<<<< HEAD
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
=======
    format="%(asctime)s — %(levelname)s — %(message)s",
    encoding="utf-8",
>>>>>>> 54c6ae3 (Committing all changes)
>>>>>>> 3ccf4fd (Committing all changes)
)

# Pull config from env
LOCAL_GIT_REPO = os.getenv("LOCAL_GIT_REPO")
COMMIT_PREFIX = os.getenv("COMMIT_PREFIX", "Auto-commit:")


<<<<<<< HEAD
def run_git_command(command_list, allow_fail=False):
    """Executes git command with optional error handling"""
    try:
        result = subprocess.run(command_list, cwd=LOCAL_GIT_REPO, check=True, capture_output=True, text=True)
        return result.stdout.strip()
=======
<<<<<<< HEAD
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

=======

def run_git_command(command_list, allow_fail=False):
    """Executes git command with optional error handling"""
    try:
        result = subprocess.run(command_list, cwd=LOCAL_GIT_REPO, check=True, capture_output=True, text=True)
        return result.stdout.strip()
>>>>>>> 54c6ae3 (Committing all changes)
>>>>>>> 3ccf4fd (Committing all changes)
    except subprocess.CalledProcessError as e:
        logging.error(f"[Git Error] {e.stderr}")
        if not allow_fail:
            raise
        return None

<<<<<<< HEAD

def main(commit_message=None):
=======
<<<<<<< HEAD
# === Main ===
=======

def main(commit_message=None):
"""TODO: Add docstring."""
>>>>>>> 3ccf4fd (Committing all changes)
    if not commit_message:
        commit_message = f"{COMMIT_PREFIX} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    os.chdir(LOCAL_GIT_REPO)

    changes = run_git_command(["git", "status", "--porcelain"], allow_fail=True)

    if not changes:
        logging.info("No changes found, performing empty commit.")
        run_git_command(["git", "commit", "--allow-empty", "-m", commit_message])
    else:
        run_git_command(["git", "add", "-A"])
        run_git_command(["git", "commit", "-m", commit_message])

    run_git_command(["git", "push", "origin", "main"])
    logging.info("Git push successful.")

    return f"Commit message: {commit_message}\nChanges: {changes or 'No tracked file changes.'}"


# For standalone testing (optional)
<<<<<<< HEAD
=======
>>>>>>> 54c6ae3 (Committing all changes)
>>>>>>> 3ccf4fd (Committing all changes)
if __name__ == "__main__":
    main()

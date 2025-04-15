import os
import logging
from datetime import datetime
from env_loader import load_environment
import subprocess

# Load env vars early
load_environment()

# Setup logging
logging.basicConfig(
    filename="git_commit_notify.log",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    encoding="utf-8"
)

# Pull config from env
LOCAL_GIT_REPO = os.getenv("LOCAL_GIT_REPO")
COMMIT_PREFIX = os.getenv("COMMIT_PREFIX", "Auto-commit:")

def run_git_command(command_list, allow_fail=False):
    """Executes git command with optional error handling"""
    try:
        result = subprocess.run(
            command_list,
            cwd=LOCAL_GIT_REPO,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"[Git Error] {e.stderr}")
        if not allow_fail:
            raise
        return None

def main(commit_message=None):
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
if __name__ == "__main__":
    main()

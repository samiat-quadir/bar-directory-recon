import os
import subprocess
import logging
from datetime import datetime
from env_loader import load_environment  # Smart loader for ASUS vs Work .env

# Load environment based on current device
load_environment()

# Set up logging (UTF-8 encoded)
log_file = "git_commit.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    encoding="utf-8"
)

# Environment Variables
LOCAL_GIT_REPO = os.getenv("LOCAL_GIT_REPO")
COMMIT_PREFIX = os.getenv("COMMIT_PREFIX", "Auto-commit:")

def run_git_command(command_list, allow_fail=False):
    """Helper to run subprocess commands and return output."""
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
        logging.error(f"❌ Git command failed: {' '.join(command_list)}\n{e.stderr}")
        if not allow_fail:
            raise
        return None

def main():
    os.chdir(LOCAL_GIT_REPO)
    
    # Check if there are any staged or unstaged changes
    changes = run_git_command(["git", "status", "--porcelain"], allow_fail=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not changes:
        logging.info("⚠️ No changes detected. Forcing an empty commit.")
        commit_msg = f"{COMMIT_PREFIX} No changes detected"
        run_git_command(["git", "commit", "--allow-empty", "-m", commit_msg])
    else:
        run_git_command(["git", "add", "-A"])
        commit_msg = f"{COMMIT_PREFIX} {timestamp}"
        run_git_command(["git", "commit", "-m", commit_msg])
        logging.info(f"✅ Commit created: {commit_msg}")

    # Push the changes
    run_git_command(["git", "push", "origin", "main"])
    logging.info("✅ Git push successful.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"🔥 Auto Git Commit failed: {e}")
        print(f"❌ Error: {e}")
    else:
        print("✅ Auto Git Commit completed successfully.")

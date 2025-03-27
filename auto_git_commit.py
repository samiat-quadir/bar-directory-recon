import os
import subprocess
import logging
from datetime import datetime
from env_loader import load_environment  # Smart loader for ASUS vs Work .env

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

def run_git_command(command_list, allow_fail=False):
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
    except FileNotFoundError as fnf_error:
        logging.error(f"❌ File not found error: {fnf_error}")
        raise

def main():
    if not os.path.isdir(LOCAL_GIT_REPO):
        raise FileNotFoundError(f"LOCAL_GIT_REPO not found or invalid: {LOCAL_GIT_REPO}")
    
    # Ensure Git is available
    try:
        git_version = run_git_command(["git", "--version"])
        logging.info(f"✅ Git available: {git_version}")
    except Exception as e:
        raise EnvironmentError("❌ Git is not accessible from this environment.") from e

    os.chdir(LOCAL_GIT_REPO)

    # Step 1: Check changes
    changes = run_git_command(["git", "status", "--porcelain"], allow_fail=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Step 2: Add & commit
    if not changes:
        logging.info("⚠️ No changes detected. Forcing an empty commit.")
        commit_msg = f"{COMMIT_PREFIX} No changes detected"
        run_git_command(["git", "commit", "--allow-empty", "-m", commit_msg])
    else:
        run_git_command(["git", "add", "-A"])
        commit_msg = f"{COMMIT_PREFIX} {timestamp}"
        run_git_command(["git", "commit", "-m", commit_msg])
        logging.info(f"✅ Commit created: {commit_msg}")

    # Step 3: Push
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

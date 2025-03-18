import os
import time
import logging
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

# Environment Variables
LOCAL_GIT_REPO = os.getenv("LOCAL_GIT_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")  # Defaults to 'main' if not set
LOG_FILE = os.path.join(LOCAL_GIT_REPO, "git_commit.log")  # Log file path

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def git_commit_and_push():
    """Commits and pushes changes to GitHub with improved error handling & logging."""
    os.chdir(LOCAL_GIT_REPO)

    # Check for changes
    status_output = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status_output.stdout.strip():
        logging.info("No changes detected. Skipping commit.")
        return

    try:
        # Stage all changes
        subprocess.run(["git", "add", "."], check=True)

        # Commit with timestamp
        commit_message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push to remote branch
        subprocess.run(["git", "push", "origin", GITHUB_BRANCH], check=True)

        logging.info(f"✅ Git commit and push successful: {commit_message}")
        return True  # Indicates success
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Git commit failed: {e}")
        return False  # Indicates failure

if __name__ == "__main__":
    success = git_commit_and_push()
    if not success:
        print("❌ Git commit failed. Check log for details.")
    else:
        print("✅ Git commit and push completed successfully.")

import os
import subprocess
import logging
from datetime import datetime

# Logging setup
LOG_FILE = r"C:\Users\samqu\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon\git_commit.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set Git repository path
LOCAL_GIT_REPO = r"C:\Users\samqu\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon"

def git_commit_and_push():
    """Commits and pushes changes to GitHub, forcing an empty commit if no changes are detected."""
    os.chdir(LOCAL_GIT_REPO)

    try:
        # Check for unstaged changes
        status_output = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        
        if not status_output.stdout.strip():
            logging.info("⚠️ No changes detected. Forcing an empty commit.")
            print("⚠️ No changes detected. Forcing an empty commit.")

            # Force an empty commit to ensure Git updates
            subprocess.run(["git", "commit", "--allow-empty", "-m", "Auto-commit: No changes detected"], check=True)
        else:
            # Stage all changes and commit normally
            subprocess.run(["git", "add", "-A"], check=True)
            commit_message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push changes
        subprocess.run(["git", "push", "origin", "main"], check=True)
        logging.info("✅ Git push successful.")
        print("✅ Git push successful.")

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Git command failed: {e}")
        print(f"❌ Git command failed: {e}")

# Run script
if __name__ == "__main__":
    git_commit_and_push()

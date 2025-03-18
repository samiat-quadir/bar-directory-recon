import os
import subprocess
from datetime import datetime
from time import sleep

# Load environment variables
LOCAL_GIT_REPO = os.getenv("LOCAL_GIT_REPO")
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

# Navigate to the repository
os.chdir(LOCAL_GIT_REPO)

def git_commit_and_push():
    """Automates committing and pushing changes to GitHub."""
    # Check for changes
    status_output = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status_output.stdout.strip():
        print(f"[{datetime.now()}] No changes detected, skipping commit.")
        return

    try:
        # Stage all changes
        subprocess.run(["git", "add", "."], check=True)

        # Commit with timestamp
        commit_message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push to remote with retry logic
        for attempt in range(3):
            push_process = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
            if push_process.returncode == 0:
                print(f"[{datetime.now()}] ✅ Changes committed & pushed successfully.")
                return
            else:
                print(f"[{datetime.now()}] ❌ Push failed. Retrying... ({attempt+1}/3)")
                sleep(60)  # Wait 1 minute before retrying

        print(f"[{datetime.now()}] ❌ Push failed after 3 attempts.")

    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now()}] ❌ Git commit failed: {e}")

# Execute the function
git_commit_and_push()

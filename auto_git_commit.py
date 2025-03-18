import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

LOCAL_GIT_REPO = os.getenv("LOCAL_GIT_REPO")

def git_commit_and_push():
    os.chdir(LOCAL_GIT_REPO)

    # Check for changes before committing
    status_output = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status_output.stdout.strip():
        print(f"[{datetime.now()}] No changes detected, skipping commit.")
        return

    # Add all changes
    subprocess.run(["git", "add", "."], check=True)

    # Commit with timestamp
    commit_message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "commit", "-m", commit_message], check=True)

    # Push to GitHub
    push_result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)

    # Log push success or failure
    if "error" in push_result.stderr.lower():
        print(f"[{datetime.now()}] ❌ Git push failed: {push_result.stderr}")
    else:
        print(f"[{datetime.now()}] ✅ Git push successful.")

if __name__ == "__main__":
    git_commit_and_push()

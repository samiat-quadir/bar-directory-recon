import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

# Retrieve GitHub token from environment variables
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
GITHUB_REPO = "https://github.com/samiat-quadir/bar-directory-recon.git"
GITHUB_AUTH_REPO = f"https://{GITHUB_ACCESS_TOKEN}@github.com/samiat-quadir/bar-directory-recon.git"

def git_commit_and_push():
    """Auto-commits and pushes changes to GitHub."""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-commit: Scheduled update"], check=True)
        subprocess.run(["git", "push", GITHUB_AUTH_REPO, "main"], check=True)
        print("✅ Repository updated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    git_commit_and_push()

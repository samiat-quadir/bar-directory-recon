import os
import subprocess

GIT_REPO_PATH = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon"

def auto_commit_push():
    """Automatically commit and push updates to GitHub if there are changes."""
    os.chdir(GIT_REPO_PATH)
    
    # Check if there are changes before committing
    status_output = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    
    if not status_output.stdout.strip():
        print("✅ No changes detected. Repository is up to date.")
        return
    
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Auto-commit: Scheduled update"])
    subprocess.run(["git", "push", "origin", "main"])
    print("✅ Repository updated successfully!")

if __name__ == "__main__":
    auto_commit_push()

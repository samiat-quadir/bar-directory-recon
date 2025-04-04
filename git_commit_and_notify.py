import os
import sys
import logging
from datetime import datetime

# Add parent folder to path to load modules cleanly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from env_loader import load_environment
from auto_git_commit import run_git_command
from notifier import send_html_notification
from motion_task_via_email import create_task_email

# === Load Environment ===
load_environment()

# === Logging Setup ===
logging.basicConfig(
    filename="git_commit_and_notify.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def git_commit_and_notify():
    try:
        # === Step 1: Git Commit ===
        commit_msg = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        git_result = run_git_command(commit_msg)

        # === Step 2: Email Notification ===
        subject = "Git Auto Commit Completed"
        body = f"""
        <h2>Git Commit Successful</h2>
        <p><b>Message:</b> {commit_msg}</p>
        <p><b>Files Changed:</b><br><pre>{git_result['output']}</pre></p>
        <p>Time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}</p>
        """
        send_html_notification(subject, body)

        # === Step 3: Motion Task via Email ===
        task_subject = f"Git Commit - {datetime.now().strftime('%b %d, %Y @ %I:%M %p')}"
        task_body = f"Review and follow up on today's auto git commit. High priority. Due tomorrow, 15min"
        create_task_email(task_subject, task_body)

        logging.info("All actions completed successfully.")
        print("All tasks completed.")

    except Exception as e:
        logging.error(f"Git commit and notify failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    git_commit_and_notify()

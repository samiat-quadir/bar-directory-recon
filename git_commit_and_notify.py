import os
import sys
import logging
from datetime import datetime

# Add ./src folder to path for imports
SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from env_loader import load_environment
from auto_git_commit import main as git_auto_commit
from notifier import send_html_notification
from motion_create_task import create_motion_task

# Load environment
load_environment()

# Setup logging
logging.basicConfig(
    filename="git_commit_and_notify.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def git_commit_and_notify():
    try:
        # 1. Run Git Commit Automation
        git_auto_commit()  # runs full commit logic from auto_git_commit.py

        # 2. Send Email Notification
        timestamp = datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')
        subject = "Git Auto Commit Completed"
        body = f"""
        <h2>Git Commit Completed</h2>
        <p><b>Timestamp:</b> {timestamp}</p>
        <p><b>Status:</b> Git commit, push, and logs completed.</p>
        """

        send_html_notification(subject, body)

        # 3. Create Motion Task
        motion_title = f"Git Commit: {datetime.now().strftime('%b %d, %Y @ %H:%M')}"
        create_motion_task(motion_title, label="Auto")

        logging.info("All steps completed successfully.")
        print("All tasks completed.")

    except Exception as e:
        logging.error(f"git_commit_and_notify failed: {e}")
        print(f"Task failed: {e}")

if __name__ == "__main__":
    git_commit_and_notify()

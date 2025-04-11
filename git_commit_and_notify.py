import os
from datetime import datetime

from project_path import set_root_path
set_root_path()

from env_loader import load_environment
from auto_git_commit import main as git_main
from notifier import send_html_notification
from src.motion_task_via_email import send_task_email

load_environment()

def git_commit_and_notify():
    try:
        # Run git commit and push
        git_main()

        # Send Email Notification
        subject = "Git Auto Commit Completed"
        body = (
            f"Git auto-commit and push executed successfully at "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        )
        send_html_notification(subject, body)

        # Trigger Motion task via email
        send_task_email()

        print("All tasks completed successfully.")

    except Exception as e:
        print(f"Error during commit and notify: {e}")

if __name__ == "__main__":
    git_commit_and_notify()

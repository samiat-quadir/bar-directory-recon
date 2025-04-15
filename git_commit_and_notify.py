import os
from datetime import datetime

from project_path import set_root_path
set_root_path()

from env_loader import load_environment
from notifier import send_html_notification
from auto_git_commit import main as run_git_command
from motion_task_via_email import send_task_email

def git_commit_and_notify():
    load_environment()

    try:
        commit_message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        git_output = run_git_command(commit_message)

        send_html_notification(
            subject="Git Auto Commit Completed",
            body=f"<h3>Commit Message</h3><p>{commit_message}</p><pre>{git_output}</pre>"
        )

        send_task_email()
        print("All tasks completed successfully.")

    except Exception as e:
        print(f"[ERROR] Error during commit and notify: {e}")

if __name__ == "__main__":
    git_commit_and_notify()

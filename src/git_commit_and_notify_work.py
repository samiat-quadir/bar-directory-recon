# git_commit_and_notify_work.py (Work Desktop)
import logging
import sys
sys.path.append('src')

from auto_git_commit_work import run_git_commands
from work_notifier import send_html_notification


# Run git commit commands and send notification
def git_commit_and_notify():
    try:
        run_git_commands()
        send_html_notification(
            "✅ Git Commit Successful",
            "<h2>📌 Changes have been successfully committed and pushed from your Work Desktop.</h2>"
        )
    except Exception as e:
        logging.error(f'❌ Combined operation failed: {e}')
        send_html_notification(
            "⚠️ Git Commit Failed",
            f"<h2>Error during Git commit and push:</h2><p>{e}</p>"
        )

if __name__ == "__main__":
    git_commit_and_notify()
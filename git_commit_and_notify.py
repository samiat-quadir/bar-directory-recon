import os
import logging
from datetime import datetime

# Make sure src/ is in the path
try:
    from project_path import set_root_path
    set_root_path()
except Exception:
    pass  # Fallback if already set

# Load environment
from env_loader import load_environment
load_environment()

# Logging
logging.basicConfig(
    filename="git_commit_notify.log",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    encoding="utf-8"
)

# Imports after path is set
from auto_git_commit import main as run_git_commit
from motion_task_via_email import send_task_email

def git_commit_and_notify():
    try:
        commit_output = run_git_commit()
        logging.info("✅ Git commit successful.")
        logging.info(commit_output)

        # Send Motion task via email (fallback)
        send_task_email()
        logging.info("✅ Motion task email sent.")

        print("✅ Email notification sent successfully.")
        print("Motion task email sent successfully.")
        print("All tasks completed successfully.")

    except Exception as e:
        logging.error(f"❌ Error during commit and notify: {str(e)}")
        print(f"[ERROR] Error during commit and notify: {str(e)}")

if __name__ == "__main__":
    git_commit_and_notify()

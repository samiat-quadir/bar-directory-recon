import logging
import os
from datetime import datetime

# Set root path early
try:
    from project_path import set_root_path

    set_root_path()
except Exception:
    pass

from env_loader import load_environment

load_environment()

# Set up logging
logging.basicConfig(
    filename="git_commit_notify.log",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    encoding="utf-8",  # Ensures emoji support in log
)

from auto_git_commit import main as run_git_commit
from motion_task_via_email import send_task_email


def git_commit_and_notify():
    try:
        result = run_git_commit()
        logging.info("✅ Git commit successful.")
        logging.info(result)

        send_task_email()
        logging.info("✅ Motion task email sent successfully.")

        print("Git commit completed.")
        print("Motion task email sent.")
        print("All tasks completed.")

    except Exception as e:
        logging.error(f"❌ Error during commit and notify: {e}")
        print(f"[ERROR] Commit and notify failed: {e}")


if __name__ == "__main__":
    git_commit_and_notify()

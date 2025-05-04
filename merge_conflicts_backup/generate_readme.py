<<<<<<< HEAD
=======
"""TODO: Add docstring."""

>>>>>>> 3ccf4fd (Committing all changes)
import os

from env_loader import load_environment
from project_path import set_root_path

set_root_path()
load_environment()
readme = f"# Bar Directory Recon Project\n\n## Key Paths & Configuration\n\n- Git Repo Path: `{os.getenv('LOCAL_GIT_REPO')}`\n- Gmail User: `{os.getenv('GMAIL_USER')}`\n- Motion Enabled: ✅\n- Log Path: `{os.getenv('GIT_LOG_PATH')}`\n\n## Scripts Summary\n- `git_commit_and_notify.py` – Git commit + email + Motion task\n- `motion_task_via_email.py` – Sends Motion task from email\n- `log_rotator.py` – Archives old log files\n- `health_check.py` – Verifies .env health\n\n---\n\n✅ Everything is auto-scheduled via Task Scheduler and environment-aware\n"
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
print("README.md generated successfully.")

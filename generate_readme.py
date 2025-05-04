import os

from env_loader import load_environment
from project_path import set_root_path

# Ensure environment is loaded properly
set_root_path()
load_environment()

readme = f"""# Bar Directory Recon Project

## Key Paths & Configuration

- Git Repo Path: `{os.getenv('LOCAL_GIT_REPO')}`
- Gmail User: `{os.getenv('GMAIL_USER')}`
- Motion Enabled: ✅
- Log Path: `{os.getenv('GIT_LOG_PATH')}`

## Scripts Summary
- `git_commit_and_notify.py` – Git commit + email + Motion task
- `motion_task_via_email.py` – Sends Motion task from email
- `log_rotator.py` – Archives old log files
- `health_check.py` – Verifies .env health

---

✅ Everything is auto-scheduled via Task Scheduler and environment-aware
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("README.md generated successfully.")

import sys
import subprocess
from pathlib import Path

# Add project root to sys.path so env_loader.py is found
sys.path.append(str(Path(__file__).resolve().parents[1]))

from prefect import flow, task
from prefect.server.schemas.schedules import CronSchedule
from env_loader import load_environment

@task(name="Run Git Commit Script")
def run_git_commit_script():
    try:
        # Load environment (.env.asus or .env)
        load_environment()
        # Execute the existing auto_git_commit.py script
        result = subprocess.run(
            ["python", "auto_git_commit.py"],
            capture_output=True,
            text=True
        )
        # Log outputs
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)

        if result.returncode != 0:
            # Branch-protection push failures or other issues
            print(f"⚠️ Git script exited with code {result.returncode}, continuing flow.")

    except Exception as exc:
        # Catch unexpected errors (e.g. missing files)
        print("❌ Exception during git commit script:", exc)

    # Always return 0 (success) so Prefect flow does not fail
    return 0

@flow(name="Git Auto Commit Flow", description="Runs auto_git_commit.py on schedule without failing on push errors")
def git_auto_commit_flow():
    run_git_commit_script()

if __name__ == "__main__":
    git_auto_commit_flow.deploy(
        name="daily-git-auto-commit",
        work_pool_name="default",
        cron="0 9 * * *",
        schedule=CronSchedule(cron="0 9 * * *", timezone="America/New_York"),
    )

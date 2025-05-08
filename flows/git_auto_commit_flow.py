import datetime
import os
import subprocess
import sys
from pathlib import Path

# Add project root to sys.path so env_loader.py is found
sys.path.append(str(Path(__file__).resolve().parents[1]))

from prefect import flow, task
from prefect.server.schemas.schedules import CronSchedule

from env_loader import load_environment


def save_to_log(stdout, stderr, return_code):
    """
    Save the output of the git commit script to a log file in the logs/ folder.

    Args:
        stdout (str): Standard output from the script execution
        stderr (str): Standard error from the script execution
        return_code (int): Return code from the script execution

    Returns:
        str: Path to the log file
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).resolve().parents[1] / "logs"
    os.makedirs(logs_dir, exist_ok=True)

    # Create a log file name with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"git_auto_commit_{timestamp}.log"

    # Write to log file
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"=== Git Auto Commit Log ({timestamp}) ===\n\n")
        f.write(f"Return Code: {return_code}\n\n")
        f.write("=== Standard Output ===\n")
        f.write(stdout or "No standard output\n")
        f.write("\n=== Standard Error ===\n")
        f.write(stderr or "No standard error\n")
        f.write("\n=== End of Log ===\n")

    return str(log_file)


@task(name="Run Git Commit Script")
def run_git_commit_script():
    try:
        # Load environment (.env.asus or .env)
        load_environment()
        # Execute the existing auto_git_commit.py script
        result = subprocess.run(["python", "auto_git_commit.py"], capture_output=True, text=True)

        # Log outputs to console
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)

        # Save outputs to log file
        log_file = save_to_log(result.stdout, result.stderr, result.returncode)
        print(f"Log saved to: {log_file}")

        if result.returncode != 0:
            # Branch-protection push failures or other issues
            print(f"⚠️ Git script exited with code {result.returncode}, continuing flow.")

    except Exception as exc:
        # Catch unexpected errors (e.g. missing files)
        print("❌ Exception during git commit script:", exc)
        # Log the exception
        log_file = save_to_log("", f"Exception: {str(exc)}", -1)
        print(f"Error log saved to: {log_file}")

    # Always return 0 (success) so Prefect flow does not fail
    return 0


@flow(
    name="Git Auto Commit Flow",
    description="Runs auto_git_commit.py on schedule without failing on push errors",
)
def git_auto_commit_flow():
    run_git_commit_script()


if __name__ == "__main__":
    git_auto_commit_flow.deploy(
        name="daily-git-auto-commit",
        work_pool_name="default",
        cron="0 9 * * *",
        schedule=CronSchedule(cron="0 9 * * *", timezone="America/New_York"),
    )

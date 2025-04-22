import sys
import os
from pathlib import Path

# Add project root to sys.path so env_loader.py is found
sys.path.append(str(Path(__file__).resolve().parents[1]))

from prefect import flow, task
from env_loader import load_environment
import subprocess


@task(name="Run Git Commit Script")
def run_git_commit_script():
    load_environment()
    script_path = "auto_git_commit.py"
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    return result.returncode

@flow(name="Git Auto Commit Flow")
def git_auto_commit_flow():
    code = run_git_commit_script()
    if code != 0:
        raise Exception("Git auto commit script failed")

if __name__ == "__main__":
    git_auto_commit_flow()

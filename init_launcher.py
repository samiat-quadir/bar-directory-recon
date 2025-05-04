# init_launcher.py
import subprocess

scripts = [
    "project_path.py",
    "git_commit_and_notify.py",
    "src/motion_task_via_email.py",
    "src/health_check.py",
    "src/log_rotator.py",
]

for script in scripts:
    try:
        print(f"Running: {script}")
        subprocess.run(["python", script], check=True)
    except Exception as e:
        print(f"Error running {script}: {e}")

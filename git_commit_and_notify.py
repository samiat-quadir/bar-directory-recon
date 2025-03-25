import os
import subprocess
from datetime import datetime
from env_loader import load_environment
load_environment()
from notifier import send_html_notification  # Correctly named function
from dotenv import load_dotenv


# Logging setup
log_path = os.getenv("GIT_LOG_PATH", "git_commit_notify.log")

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} {message}\n")
    print(message)

def run_git_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            log(f"❌ Error running command: {command}\n{result.stderr.strip()}")
            return False, result.stderr.strip()
        return True, result.stdout.strip()
    except Exception as e:
        log(f"❌ Exception during git command: {e}")
        return False, str(e)

def main():
    repo_path = os.getenv("LOCAL_GIT_REPO")
    if not repo_path:
        log("❌ LOCAL_GIT_REPO not found in .env")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Auto-commit: {timestamp}"

    log("📁 Checking repository for changes...")
    changes_detected, output = run_git_command("git status --porcelain", cwd=repo_path)
    if not changes_detected:
        return

    if output.strip() == "":
        log("⚠️ No changes detected. Forcing an empty commit.")
        run_git_command("git commit --allow-empty -m \"Auto-commit: No changes detected\"", cwd=repo_path)
    else:
        run_git_command("git add .", cwd=repo_path)
        run_git_command(f"git commit -m \"{commit_message}\"", cwd=repo_path)

    pushed, push_output = run_git_command("git push origin main", cwd=repo_path)
    if pushed:
        log("✅ Git push successful.")
        try:
            send_html_notification("✅ Git Commit Completed", f"<b>{commit_message}</b><br>Git push was successful.")
        except Exception as e:
            log(f"❌ Email notification error: {e}")
    else:
        log("❌ Git push failed.")

if __name__ == "__main__":
    main()

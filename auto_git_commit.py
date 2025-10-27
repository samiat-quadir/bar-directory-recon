import logging
import os
import subprocess
from datetime import datetime

# === Configuration ===
GIT_EXE = r"C:\Program Files\Git\bin\git.exe"
LOCAL_GIT_REPO = os.getenv(
    "LOCAL_GIT_REPO",
    r"C:\Users\samqu\OneDrive - Digital Age Marketing Group\Desktop\Local Py\Work Projects\bar-directory-recon",
)
LOG_FILE = os.path.join(LOCAL_GIT_REPO, "git_commit.log")

# === Logging Setup ===
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def git_commit_and_push():
    os.chdir(LOCAL_GIT_REPO)

    try:
        status_output = subprocess.run(
            [GIT_EXE, "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )

        if not status_output.stdout.strip():
            logging.info("No changes detected. Forcing an empty commit.")
            subprocess.run(
                [
                    GIT_EXE,
                    "commit",
                    "--allow-empty",
                    "-m",
                    "Auto-commit: No changes detected",
                ],
                check=True,
                timeout=60,
            )

        else:
            subprocess.run([GIT_EXE, "add", "."], check=True, timeout=60)
            commit_msg = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run([GIT_EXE, "commit", "-m", commit_msg], check=True, timeout=60)

        subprocess.run([GIT_EXE, "push", "origin", "main"], check=True, timeout=60)
        logging.info("Git push successful.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Git command failed: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during git commit: {e}")


if __name__ == "__main__":
    git_commit_and_push()

import subprocess
import logging
from datetime import datetime

# Log file setup (optional, can be reused across systems)
LOG_FILE = "git_commit_notify.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_script(script_name):
    try:
        result = subprocess.run(["python", script_name], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            logging.info(f"✅ {script_name} ran successfully.")
            logging.info(result.stdout)
        else:
            logging.error(f"❌ Error running {script_name}: {result.stderr}")
    except Exception as e:
        logging.error(f"❌ Exception occurred while running {script_name}: {e}")

if __name__ == "__main__":
    logging.info("🚀 Starting Git commit and notification process...")

    run_script("auto_git_commit.py")         # Step 1: Run Git commit script
    run_script("asus_notifier.py")           # Step 2: Send notification email via ASUS-specific notifier

    logging.info("✅ Process complete.\n")


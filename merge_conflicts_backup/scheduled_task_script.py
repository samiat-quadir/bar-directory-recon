<<<<<<< HEAD
=======
"""TODO: Add docstring."""

>>>>>>> 3ccf4fd (Committing all changes)
import os
from datetime import datetime

from dotenv import load_dotenv

<<<<<<< HEAD
# Load environment variables
env_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\.env"
load_dotenv(env_path)

# Logging setup with UTF-8 encoding
log_path = r"C:\Users\samq\OneDrive - Digital Age Marketing Group\Desktop\Local Py\task_log.txt"
with open(log_path, "a", encoding="utf-8") as log_file:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

=======
env_path = "C:\\Users\\samq\\OneDrive - Digital Age Marketing Group\\Desktop\\Local Py\\.env"
load_dotenv(env_path)
log_path = "C:\\Users\\samq\\OneDrive - Digital Age Marketing Group\\Desktop\\Local Py\\task_log.txt"
with open(log_path, "a", encoding="utf-8") as log_file:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
>>>>>>> 3ccf4fd (Committing all changes)
    log_file.write(f"\n=== Scheduled Task Run: {now} ===\n")
    paths = {
        "SERVICE_ACCOUNT_KEY_PATH": os.getenv("SERVICE_ACCOUNT_KEY_PATH"),
        "GMAIL_CREDENTIALS_PATH": os.getenv("GMAIL_CREDENTIALS_PATH"),
        "GMAIL_TOKEN_PATH": os.getenv("GMAIL_TOKEN_PATH"),
        "CHROMEDRIVER_PATH": os.getenv("CHROMEDRIVER_PATH"),
        "LOCAL_GIT_REPO": os.getenv("LOCAL_GIT_REPO"),
    }
    for key, actual_path in paths.items():
        if actual_path and os.path.exists(actual_path):
            log_file_entry = f"{now} ✅ {key} verified: {actual_path}\n"
        else:
            log_file_entry = f"{now} ❌ {key} MISSING or INVALID: {actual_path}\n"
<<<<<<< HEAD

=======
>>>>>>> 3ccf4fd (Committing all changes)
        log_file.write(log_file_entry)
        print(log_file_entry)
print("\n✅ Scheduled task completed successfully.")

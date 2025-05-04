import os
from datetime import datetime

from dotenv import load_dotenv

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
        log_file.write(log_file_entry)
        print(log_file_entry)
print("\n✅ Scheduled task completed successfully.")

import os
import time
from datetime import datetime

# === CONFIGURATION ===
RETENTION_DAYS = 7
TARGET_FOLDERS = ["src/logs", "src/backups"]
LOG_FILE = "cleanup_report.log"


def log(message):
<<<<<<< HEAD
=======
"""TODO: Add docstring."""
>>>>>>> 3ccf4fd (Committing all changes)
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}\n"
    print(full_message.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message)


def cleanup_old_files():
<<<<<<< HEAD
=======
"""TODO: Add docstring."""
>>>>>>> 3ccf4fd (Committing all changes)
    now = time.time()
    cutoff = now - (RETENTION_DAYS * 86400)

    for folder in TARGET_FOLDERS:
        full_folder = os.path.abspath(folder)
        if not os.path.exists(full_folder):
            log(f"[SKIP] Folder not found: {full_folder}")
            continue

        deleted_count = 0
        for file in os.listdir(full_folder):
            file_path = os.path.join(full_folder, file)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff:
                try:
                    os.remove(file_path)
                    log(f"[DELETE] Removed: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    log(f"[ERROR] Could not delete {file_path}: {e}")

        if deleted_count == 0:
            log(f"[CLEAN] No files deleted in: {full_folder}")


if __name__ == "__main__":
    log("=== CLEANUP START ===")
    cleanup_old_files()
    log("=== CLEANUP COMPLETE ===\n")

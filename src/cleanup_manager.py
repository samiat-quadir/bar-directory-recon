import os
from datetime import datetime, timedelta

set_root_path()
load_environment()

LOG_DIRS = ["logs", "."]
EXTENSIONS = [".log", ".tmp"]
DAYS_THRESHOLD = 7


def cleanup_old_files():
    threshold_date = datetime.now() - timedelta(days=DAYS_THRESHOLD)
    removed = 0

    for folder in LOG_DIRS:
        if not os.path.exists(folder):
            continue
        for file in os.listdir(folder):
            if any(file.endswith(ext) for ext in EXTENSIONS):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if modified_time < threshold_date:
                        os.remove(file_path)
                        removed += 1
                        logging.info(f"Removed old file: {file_path}")

    print(f"✅ Cleanup complete. Removed {removed} old files.")



if __name__ == "__main__":
    logger.info("Starting cleanup process...")
    cleanup_old_files()
    archive_logs()

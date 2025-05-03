<<<<<<< HEAD
import logging
=======
<<<<<<< HEAD
"""Manage cleanup of log files and temporary data."""
>>>>>>> 3ccf4fd (Committing all changes)
import os
from datetime import datetime, timedelta
<<<<<<< HEAD

from env_loader import load_environment
from project_path import set_root_path
=======
from pathlib import Path

from src.env_loader import load_environment
from src.project_path import set_root_path
from src.utils.logging import setup_logger

=======
import logging
import os
from datetime import datetime, timedelta

from env_loader import load_environment
from project_path import set_root_path

>>>>>>> 54c6ae3 (Committing all changes)
>>>>>>> 3ccf4fd (Committing all changes)

set_root_path()
load_environment()

LOG_DIRS = ["logs", "."]
EXTENSIONS = [".log", ".tmp"]
DAYS_THRESHOLD = 7

<<<<<<< HEAD
=======
<<<<<<< HEAD
logger = setup_logger(__name__)
>>>>>>> 3ccf4fd (Committing all changes)

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

<<<<<<< HEAD
=======
    logger.info(f"✅ Cleanup complete. Removed {removed} old files.")
    return removed

def archive_logs(archive_dir: str = "logs/archive") -> None:
    """Archive logs that shouldn't be deleted yet.
    
    Args:
        archive_dir: Directory to store archived logs
    """
    archive_path = Path(archive_dir)
    archive_path.mkdir(parents=True, exist_ok=True)
    
    date_suffix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = Path("logs")
    
    if not log_dir.exists():
        logger.warning("Log directory does not exist, nothing to archive")
        return
        
    archived = 0
    for log_file in log_dir.glob("*.log"):
        if log_file.name == "cleanup_report.log":
            continue
        
        archive_name = f"{log_file.stem}_{date_suffix}{log_file.suffix}"
        try:
            shutil.move(str(log_file), str(archive_path / archive_name))
            archived += 1
            logger.info(f"Archived: {log_file.name} -> {archive_name}")
        except Exception as e:
            logger.error(f"Failed to archive {log_file}: {e}")
    
    logger.info(f"✅ Archive complete. Moved {archived} files to {archive_dir}")
=======

def cleanup_old_files():
"""TODO: Add docstring."""
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
>>>>>>> 54c6ae3 (Committing all changes)

>>>>>>> 3ccf4fd (Committing all changes)

if __name__ == "__main__":
    logger.info("Starting cleanup process...")
    cleanup_old_files()
    archive_logs()

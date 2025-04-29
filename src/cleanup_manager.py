"""Manage cleanup of log files and temporary data."""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from src.utils.logging import setup_logger
from src.env_loader import load_environment
from src.project_path import set_root_path

set_root_path()
load_environment()

# Configuration
RETENTION_DAYS = 7
TARGET_DIRS = {
    "logs": ["*.log", "*.log.*"],
    "output": ["*.tmp", "*.png", "recon_*.json"],
    "src/backups": ["backup_archive_*.zip"],
    ".": ["*.log", "*.tmp"]
}

logger = setup_logger(__name__)

def should_delete_file(file_path: Path, patterns: list) -> bool:
    """Determine if a file should be deleted based on age and pattern."""
    return (
        any(file_path.match(pattern) for pattern in patterns)
        and file_path.stat().st_mtime < (datetime.now() - timedelta(days=RETENTION_DAYS)).timestamp()
    )

def cleanup_old_files() -> int:
    """Clean up old files based on configured patterns and retention period.
    
    Returns:
        int: Number of files removed
    """
    removed = 0
    
    for directory, patterns in TARGET_DIRS.items():
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.info(f"Directory does not exist, skipping: {directory}")
            continue

        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and should_delete_file(file_path, patterns):
                try:
                    file_path.unlink()
                    removed += 1
                    logger.info(f"Removed old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove {file_path}: {e}")

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

if __name__ == "__main__":
    logger.info("Starting cleanup process...")
    cleanup_old_files()
    archive_logs()

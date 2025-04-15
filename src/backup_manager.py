import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from env_loader import load_environment
from datetime import datetime
import shutil

load_environment()

SOURCE_DIR = "src/backups"
ARCHIVE_DIR = os.path.join(SOURCE_DIR, "archives")

def create_timestamped_archive():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"backup_archive_{timestamp}.zip"
    archive_path = os.path.join(ARCHIVE_DIR, archive_name)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    shutil.make_archive(archive_path.replace(".zip", ""), 'zip', SOURCE_DIR)
    print(f"Archive created at: {archive_path}")

if __name__ == "__main__":
    create_timestamped_archive()

import os
import sys

# Ensure project root is in the Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import shutil
from datetime import datetime

from env_loader import load_environment
from project_path import set_root_path

# Set root path and load environment
set_root_path()
load_environment()


def rotate_logs(log_dir="logs", archive_dir="logs/archive"):
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    logs_to_rotate = [f for f in os.listdir(log_dir) if f.endswith(".log")]
    date_suffix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for log in logs_to_rotate:
        source = os.path.join(log_dir, log)
        destination = os.path.join(archive_dir, f"{log}_{date_suffix}.log")
        shutil.move(source, destination)
        print(f"Archived and removed: {log}")


if __name__ == "__main__":
    rotate_logs()

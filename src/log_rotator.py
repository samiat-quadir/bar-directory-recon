import os
import shutil
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def rotate_logs(log_dir="logs", archive_dir="logs/archive"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    logs_to_rotate = [f for f in os.listdir(log_dir) if f.endswith(".log")]
    date_suffix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for log in logs_to_rotate:
        source = os.path.join(log_dir, log)
        destination = os.path.join(archive_dir, f"{log}_{date_suffix}.log")
        shutil.move(source, destination)
        print(f"Archived and removed: {log}")

if __name__ == "__main__":
    rotate_logs()

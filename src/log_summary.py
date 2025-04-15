import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from env_loader import load_environment
from datetime import datetime

load_environment()

LOG_DIR = "src/logs"
SUMMARY_FILE = os.path.join(LOG_DIR, "log_summary.txt")

def summarize_logs():
    summary = []
    for filename in os.listdir(LOG_DIR):
        if filename.endswith(".log"):
            path = os.path.join(LOG_DIR, filename)
            size_kb = os.path.getsize(path) / 1024
            summary.append(f"{filename}: {size_kb:.2f} KB")
    return "\n".join(summary)

if __name__ == "__main__":
    content = summarize_logs()
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(f"Log Summary — {datetime.now()}\n")
        f.write("=" * 40 + "\n")
        f.write(content + "\n")
    print(f"Log summary saved to {SUMMARY_FILE}")

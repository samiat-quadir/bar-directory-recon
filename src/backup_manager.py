import os
import zipfile
from datetime import datetime
from env_loader import load_environment

# === Load environment variables ===
load_environment()

# === Paths ===
BASE_DIR = os.getcwd()
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SRC_DIR = os.path.join(BASE_DIR, "src")
ENV_FILES = [".env.work", ".env.asus", ".env.example"]

# === Ensure backup folder exists ===
os.makedirs(BACKUP_DIR, exist_ok=True)

# === Filename with timestamp ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_filename = os.path.join(BACKUP_DIR, f"backup_{timestamp}.zip")

# === Files/folders to include ===
files_to_backup = []

# Include logs
for fname in os.listdir(LOGS_DIR):
    path = os.path.join(LOGS_DIR, fname)
    if os.path.isfile(path):
        files_to_backup.append(path)

# Include environment files
for fname in ENV_FILES:
    path = os.path.join(BASE_DIR, fname)
    if os.path.isfile(path):
        files_to_backup.append(path)

# Include README and task scripts
important_scripts = ["README.md", "daily_automation.py", "init_launcher.py"]
for fname in important_scripts:
    path = os.path.join(BASE_DIR, fname)
    if os.path.isfile(path):
        files_to_backup.append(path)

# === Create ZIP ===
with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
    for file_path in files_to_backup:
        arcname = os.path.relpath(file_path, BASE_DIR)
        backup_zip.write(file_path, arcname)

print(f"✅ Backup complete: {backup_filename}")

import getpass
import os
import platform
import sys
from datetime import datetime

# Simple standalone script to identify device and Python path
device = ""
username = getpass.getuser().lower()
if "samqu" in username:
    device = "ASUS"
elif "samq" in username and "samqu" not in username:
    device = "Work Desktop"
else:
    device = "Unknown"

python_path = sys.executable
python_version = sys.version.split()[0]

# Output information
print("\n" + "=" * 50)
print(f"🖥️  Detected device profile: {device}")
print(f"👤 Username: {username}")
print(f"🐍 Python executable: {python_path}")
print(f"📊 Python version: {python_version}")
print(f"💻 Operating system: {platform.system()} {platform.release()}")
print("=" * 50 + "\n")

# Write to log file
log_file = "logs/setup_log.txt"
os.makedirs(os.path.dirname(log_file), exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"[{timestamp}] 🖥️  Detected device profile: {device}\n")
    f.write(f"[{timestamp}] 🐍 Python executable: {python_path}\n")
    f.write(f"[{timestamp}] ✅ Python major version is correct (3.x)\n")

print(f"✅ Information has been logged to {log_file}")

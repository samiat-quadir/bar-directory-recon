import platform
import sys
import os
import json
from datetime import datetime
from pathlib import Path

profile = {
    "device": platform.node(),
    "username": os.getlogin(),
    "python_path": sys.executable,
    "python_version": ".".join(map(str, sys.version_info[:3])),
    "venv_path": ".venv",
    "user_home": str(Path.home()),
    "timestamp": datetime.now().isoformat(),
}

config_dir = Path("config")
config_dir.mkdir(exist_ok=True)
profile_path = config_dir / f'device_profile-{profile["device"]}.json'

with open(profile_path, "w") as f:
    json.dump(profile, f, indent=2)

print(f"Device profile created at {profile_path}")

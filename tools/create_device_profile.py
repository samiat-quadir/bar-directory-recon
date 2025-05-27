import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path


def main() -> None:
    profile = {
        "device": platform.node(),
        "username": os.getlogin(),
        "python_path": sys.executable,
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "user_home": str(Path.home()),
        "timestamp": datetime.now().isoformat(),
        "venv_path": ".venv",
    }

    config_dir = Path("config")
    config_dir.mkdir(parents=True, exist_ok=True)

    profile_path = config_dir / f"device_profile-{profile['device']}.json"

    with open(profile_path, "w") as f:
        json.dump(profile, f, indent=2)

    print(f"Device profile created at {profile_path}")


if __name__ == "__main__":
    main()

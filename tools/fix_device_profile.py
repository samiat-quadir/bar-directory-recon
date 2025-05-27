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
        "user_home": str(Path.home()),
        "timestamp": datetime.now().isoformat(),
    }

    profile_path = Path("config") / f"device_profile-{profile['device']}.json"
    profile_path.parent.mkdir(parents=True, exist_ok=True)

    with open(profile_path, "w") as f:
        json.dump(profile, f, indent=2)

    print(f"✅ Device profile saved to: {profile_path}")


if __name__ == "__main__":
    main()

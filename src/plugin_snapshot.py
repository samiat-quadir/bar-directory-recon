import json
import os
import sys
from datetime import datetime

# Fix path for importing modules from project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from env_loader import load_environment
from project_path import set_root_path

set_root_path()
load_environment()

PLUGIN_FOLDER = os.path.join(os.getcwd(), "src", "plugins")
SNAPSHOT_FILE = os.path.join(PLUGIN_FOLDER, "plugin_snapshot.json")


def scan_plugins():
"""TODO: Add docstring."""
    if not os.path.exists(PLUGIN_FOLDER):
        print(f"❌ Plugin folder not found: {PLUGIN_FOLDER}")
        return

    plugin_data = {}
    for file in os.listdir(PLUGIN_FOLDER):
        if file.endswith(".py"):
            path = os.path.join(PLUGIN_FOLDER, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            plugin_data[file] = {
                "last_modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
                "register_function_present": "def register" in content,
                "size_kb": round(os.path.getsize(path) / 1024, 2),
            }

    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(plugin_data, f, indent=2)

    print(f" Plugin snapshot saved to {SNAPSHOT_FILE}")


if __name__ == "__main__":
    scan_plugins()

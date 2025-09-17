import json
import os
import sys
from datetime import datetime

# File paths
profile_salesrep = os.path.join("config", "device_profile_SALESREP.json")
profile_asus = os.path.join("config", "device_profile_ROG-LUCCI.json")
device_config = os.path.join("config", "device_config.json")
log_path = os.path.join("logs", "device_profile_validation_phase2.log")

results = []
exit_code = 0


def check_python_path(profile_path, label):
    try:
        with open(profile_path, encoding="utf-8") as f:
            data = json.load(f)
        base_path = data["python_path"]["base"]
        if base_path.replace("\\", "/").endswith(".venv/Scripts/python.exe"):
            results.append(f"[OK] {label}: python_path.base is valid.")
        else:
            results.append(
                f"[ERROR] {label}: python_path.base is '{base_path}', expected to end with .venv/Scripts/python.exe."
            )
            return False
        return True
    except Exception as e:
        results.append(f"[ERROR] {label}: Exception: {e}")
        return False


def check_device_config(config_path):
    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        # Accept either 'last_synced' or 'LastUpdated' (case-insensitive)
        last_synced = data.get("last_synced") or data.get("LastUpdated")
        if not last_synced:
            results.append(
                "[ERROR] device_config.json: Missing 'last_synced' or 'LastUpdated' field."
            )
            return False
        try:
            # Try parsing as ISO timestamp
            datetime.fromisoformat(last_synced.replace("Z", "+00:00"))
            results.append(
                "[OK] device_config.json: last_synced/LastUpdated is a valid ISO timestamp."
            )
            return True
        except Exception:
            results.append(
                f"[ERROR] device_config.json: 'last_synced'/'LastUpdated' value '{last_synced}' is not a valid ISO timestamp."
            )
            return False
    except Exception as e:
        results.append(f"[ERROR] device_config.json: Exception: {e}")
        return False


# Run checks
if not check_python_path(profile_salesrep, "device_profile_SALESREP.json"):
    exit_code = 1
if not check_python_path(profile_asus, "device_profile_ROG-LUCCI.json"):
    exit_code = 1
if not check_device_config(device_config):
    exit_code = 1

# Write summary log
with open(log_path, "a", encoding="utf-8") as log:
    log.write(f"\n[VALIDATION RUN {datetime.now().isoformat()}]\n")
    for line in results:
        log.write(line + "\n")
    # VSCode settings/tasks validation
    if not os.path.exists(".vscode/settings.json"):
        log.write("[ERROR] .vscode/settings.json missing.\n")
    else:
        with open(".vscode/settings.json", encoding="utf-8") as s:
            settings = s.read()
            if (
                "python.pythonPath" not in settings
                or "${workspaceFolder}/.venv/Scripts/python.exe" not in settings
            ):
                log.write(
                    "[ERROR] .vscode/settings.json: python.pythonPath not set correctly.\n"
                )
    if not os.path.exists(".vscode/tasks.json"):
        log.write("[ERROR] .vscode/tasks.json missing.\n")
    else:
        with open(".vscode/tasks.json", encoding="utf-8") as t:
            tasks = t.read()
            if "Run Pre-commit" not in tasks:
                log.write("[ERROR] .vscode/tasks.json: Missing task Run Pre-commit.\n")
            if "Test Cross-Device" not in tasks:
                log.write(
                    "[ERROR] .vscode/tasks.json: Missing task Test Cross-Device.\n"
                )
    log.write(f"[SUMMARY] {'OK' if exit_code == 0 else 'ERROR'}\n")

sys.exit(exit_code)

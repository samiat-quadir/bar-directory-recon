import json
import os
import sys
from datetime import datetime


def get_profiles(config_dir):
    profiles = []
    for fname in os.listdir(config_dir):
        if fname.endswith(".json") and "profile" in fname:
            profiles.append(os.path.join(config_dir, fname))
    return profiles


def load_profile(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_error": str(e), "_path": path}


def get_python_path(profile):
    try:
        return profile["python_path"]["base"]
    except Exception:
        return None


def get_last_synced(profile):
    for key in ["last_synced", "LastUpdated", "last_updated"]:
        if key in profile:
            return profile[key]
    return None


def main():
    config_dir = os.path.join(os.path.dirname(__file__), "..", "..", "config")
    config_dir = os.path.abspath(config_dir)
    log_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "logs",
        "phase_4",
        "cross_device_sync.log",
    )
    log_path = os.path.abspath(log_path)
    profiles = get_profiles(config_dir)
    loaded = [load_profile(p) for p in profiles]
    timestamp = datetime.now().isoformat()
    summary = [f"Sync Run: {timestamp}"]
    exit_code = 0

    # Compare python_path and last_synced
    python_paths = {}
    last_synceds = {}
    for prof, path in zip(loaded, profiles):
        if "_error" in prof:
            summary.append(f"[ERROR] Could not load {path}: {prof['_error']}")
            exit_code = 1
            continue
        py_path = get_python_path(prof)
        last_sync = get_last_synced(prof)
        python_paths[path] = py_path
        last_synceds[path] = last_sync

    # Check for mismatches
    py_path_set = set(python_paths.values())
    last_sync_set = set(last_synceds.values())
    if len(py_path_set) > 1:
        summary.append("[MISMATCH] python_path.base values differ:")
        for k, v in python_paths.items():
            summary.append(f"  {os.path.basename(k)}: {v}")
        exit_code = 1
    else:
        summary.append("[OK] All python_path.base values match.")
    if len(last_sync_set) > 1:
        summary.append("[MISMATCH] last_synced/LastUpdated values differ:")
        for k, v in last_synceds.items():
            summary.append(f"  {os.path.basename(k)}: {v}")
        exit_code = 1
    else:
        summary.append("[OK] All last_synced/LastUpdated values match.")

    with open(log_path, "a", encoding="utf-8") as log:
        log.write("\n".join(summary) + "\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

import os
import sys
from datetime import datetime
from getpass import getuser

import yaml

TRACKER_PATH = "planning/phase_28_execution_tracker.yaml"
LOG_PATH = "logs/phase_28/tracker_update.log"
ROLE = "ADA"  # Role identifier for this script


def load_tracker():
    if not os.path.exists(TRACKER_PATH):
        print(f"❌ Tracker file not found: {TRACKER_PATH}")
        sys.exit(1)
    with open(TRACKER_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_tracker(data):
    # Preserve the YAML format and style when saving
    with open(TRACKER_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, default_flow_style=False)


def append_log(entry):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(entry + "\n")


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: python update_tracker_ada.py <task_index>")
        sys.exit(1)

    task_index = int(sys.argv[1])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tracker = load_tracker()
    current_user = getuser().lower()

    # Get the correct structure from the YAML file
    try:
        # Check if "phase_28_execution_tracker" is the top-level key
        if "phase_28_execution_tracker" in tracker:
            tracker_data = tracker["phase_28_execution_tracker"]
        else:
            tracker_data = tracker

        # Initialize task_status if it doesn't exist
        if "task_status" not in tracker_data:
            tracker_data["task_status"] = {}

        # Update the task status for the specified role
        tracker_data["task_status"][ROLE] = task_index

        # Save the updated tracker
        save_tracker(tracker)

        print(f"✅ Updated {ROLE} task index to {task_index}")
        log_line = f"[{timestamp}] {ROLE}@{current_user} → task {task_index}"
        append_log(log_line)
    except Exception as e:
        print(f"❌ Failed to update tracker: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

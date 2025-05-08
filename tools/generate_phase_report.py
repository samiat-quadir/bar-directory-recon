# tools/generate_phase_report.py
from datetime import datetime
from pathlib import Path

import yaml

TRACKER_PATH = Path("planning/phase_28_execution_tracker.yaml")


def main():
    if not TRACKER_PATH.exists():
        print(f"❌ Tracker not found at {TRACKER_PATH}")
        return

    with open(TRACKER_PATH) as f:
        data = yaml.safe_load(f)

    print(f"\n📅 Phase 28 Execution Report ({datetime.now().strftime('%Y-%m-%d')})")
    print(f"Primary Orchestrator: {data['primary_orchestrator']}\n")

    for role, details in data["assistant_roles"].items():
        print(f"🔧 {role} — {details['purpose']}")
        for task in details["critical_tasks"]:
            checkbox = "[ ]" if isinstance(task, str) or not task[0] else "[x]"
            task_line = task if isinstance(task, str) else task[1]
            print(f"  {checkbox} {task_line}")
        print()


if __name__ == "__main__":
    main()

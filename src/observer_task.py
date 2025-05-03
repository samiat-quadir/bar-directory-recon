from datetime import datetime

from env_loader import load_environment
from project_path import set_root_path

set_root_path()
load_environment()


def summarize_automation_run():
"""TODO: Add docstring."""
    log_file = "automation_run.log"
    if not os.path.exists(log_file):
        print("No automation_run.log found.")
        return

    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    success_keywords = [
        "Motion task email sent",
        "README.md generated",
        "Email notification sent",
    ]
    error_keywords = ["Error", "Failed", "Exception"]
    success_count = sum(1 for l in lines if any(k in l for k in success_keywords))
    error_count = sum(1 for l in lines if any(k in l for k in error_keywords))

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(
            f"\n[SUMMARY {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {success_count} successes, ❌ {error_count} errors\n"
        )

    print("✅ Observer summary appended to automation_run.log.")


if __name__ == "__main__":
    summarize_automation_run()

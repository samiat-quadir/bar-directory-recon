import os
import subprocess
from datetime import datetime

# General exclusions for all linting operations
EXCLUDED_PATHS = [".venv", ".venv311", "__pycache__", "archive", "bar-recon-clean"]

# Specific YAML files to exclude from yamllint
WHITELISTED_YAML = {"mega_memory.yaml", "Ai Integration Setup.yaml", "Ai Project Setup & Automation Roadmap.txt"}

LOG_PATH = "logs/lint_report.log"
hr = "=" * 60  # Horizontal rule for better output readability


def should_exclude(path):
    return any(ex in path for ex in EXCLUDED_PATHS)


def collect_yaml_files(root="."):
    for dirpath, _, filenames in os.walk(root):
        if should_exclude(dirpath):
            continue
        for f in filenames:
            if f.endswith((".yaml", ".yml")) and not should_exclude(f) and f not in WHITELISTED_YAML:
                yield os.path.join(dirpath, f)


def run_command(cmd, label):
    print(f"\n🔹 Running: {label}")
    print(hr)
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode == 0:
        print(f"✅ {label} passed.")
    else:
        print(f"❌ {label} failed.")
        print(result.stdout)
        print(result.stderr)
    return result


def run_yamllint():
    print(f"{hr}\n🔍 Running yamllint...\n{hr}")
    for root, _, files in os.walk("."):
        if should_exclude(root):
            continue
        for file in files:
            if (file.endswith(".yaml") or file.endswith(".yml")) and file not in WHITELISTED_YAML:
                filepath = os.path.join(root, file)
                subprocess.run(["yamllint", filepath], check=False)


def main():
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(f"\n\n[{datetime.now()}] Linting Report Start\n")
        log.write(hr + "\n")

    print("\n🧹 Starting selective lint and format checks...")

    # Run isort
    run_command("isort .", "isort")

    # Run black with proper regex exclude pattern
    run_command('black . --exclude "\\.venv|\\.venv311|mega_memory\\.yaml|bar-recon-clean"', "black")

    # Run flake8 (allow line length leniency and exclude known folders)
    run_command("flake8 . --exclude=.venv,.venv311,archive,bar-recon-clean --max-line-length=120", "flake8")

    # Run yamllint with custom config and whitelist
    run_yamllint()

    print("\n✅ Lint checks completed.")


if __name__ == "__main__":
    main()

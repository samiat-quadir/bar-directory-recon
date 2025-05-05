# tools/format_and_lint.py

import subprocess
import sys
from pathlib import Path

# Paths to exclude from YAML linting
YAML_WHITELIST = {
    "mega_memory.yaml",
    "Ai Project Setup & Automation Roadmap.txt",
    "ai_integration_config.yaml",
}


# Color-coded output
def color(msg, code):
    print(f"\033[{code}m{msg}\033[0m")


def run_command(command, name):
    print(f"Running {name}...")
    try:
        subprocess.run(command, shell=True, check=True)
        color(f"PASS: {name} succeeded.\n", "32")
    except subprocess.CalledProcessError as e:
        color(f"FAIL: {name} failed.\n", "31")
        print(e)


def lint_yaml():
    repo_root = Path(".")
    all_yaml_files = [
        str(p) for p in repo_root.rglob("*.yaml") if p.name not in YAML_WHITELIST and ".venv" not in str(p)
    ]
    if not all_yaml_files:
        color("PASS: No YAML files to lint.", "32")
        return
    run_command(f"yamllint {' '.join(all_yaml_files)}", "YAML Lint")


def main():
    run_command("black .", "Black")
    run_command("isort .", "Isort")
    run_command("ruff check .", "Ruff")
    run_command("autoflake --remove-unused-variables --in-place --recursive .", "Autoflake")
    lint_yaml()


if __name__ == "__main__":
    main()

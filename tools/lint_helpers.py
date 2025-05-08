import os
import subprocess
import traceback
from datetime import datetime

# General exclusions for all linting operations
EXCLUDED_PATHS = [".venv", ".venv311", "__pycache__", "archive", "bar-recon-clean"]

# Specific YAML files to exclude from yamllint
WHITELISTED_YAML = {"mega_memory.yaml", "Ai Integration Setup.yaml", "Ai Project Setup & Automation Roadmap.txt"}

LOG_PATH = "logs/lint_report.log"
hr = "=" * 60  # Horizontal rule for better output readability


def get_timestamp():
    """Return formatted timestamp for logs."""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def log_message(message, to_console=True, to_file=True):
    """
    Log message to both console and log file with timestamp.

    Args:
        message (str): The message to log
        to_console (bool): Whether to also print to console
        to_file (bool): Whether to write to log file
    """
    timestamped_message = f"{get_timestamp()} {message}"

    if to_console:
        print(timestamped_message)

    if to_file:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamped_message}\n")


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
    """
    Run a shell command and log the output with timestamps.

    Args:
        cmd (str): Command to run
        label (str): Label for the command in logs

    Returns:
        subprocess.CompletedProcess: Result of the command
    """
    log_message(f"\n🔹 Running: {label}")
    log_message(hr)

    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)

        # Log stdout and stderr with timestamps
        if result.stdout:
            log_message(f"STDOUT:\n{result.stdout.strip()}")

        if result.stderr:
            log_message(f"STDERR:\n{result.stderr.strip()}")

        if result.returncode == 0:
            log_message(f"✅ {label} passed.")
        else:
            log_message(f"❌ {label} failed with exit code {result.returncode}.")

        return result
    except Exception as e:
        error_msg = f"ERROR executing '{cmd}': {str(e)}"
        log_message(error_msg)
        log_message(traceback.format_exc(), to_console=False)

        # Return a mock result to avoid crashing
        class MockResult:
            returncode = 1
            stdout = ""
            stderr = error_msg

        return MockResult()


def run_yamllint():
    log_message(f"{hr}\n🔍 Running yamllint...\n{hr}")
    for root, _, files in os.walk("."):
        if should_exclude(root):
            continue
        for file in files:
            if (file.endswith(".yaml") or file.endswith(".yml")) and file not in WHITELISTED_YAML:
                filepath = os.path.join(root, file)
                try:
                    result = subprocess.run(["yamllint", filepath], check=False, text=True, capture_output=True)
                    if result.stdout:
                        log_message(f"YAMLLINT {filepath}:\n{result.stdout.strip()}")
                    if result.stderr:
                        log_message(f"YAMLLINT ERROR {filepath}:\n{result.stderr.strip()}")
                except Exception as e:
                    log_message(f"ERROR running yamllint on {filepath}: {str(e)}")


def main():
    """Run all linting operations with improved logging."""
    os.makedirs("logs", exist_ok=True)
    log_message(f"\n\n{hr}")
    log_message("Linting Report Start")
    log_message(f"{hr}")

    log_message("\n🧹 Starting selective lint and format checks...")

    # Run isort
    run_command("isort .", "isort")

    # Run black with proper regex exclude pattern
    run_command('black . --exclude "\\.venv|\\.venv311|mega_memory\\.yaml|bar-recon-clean"', "black")

    # Run flake8 (allow line length leniency and exclude known folders)
    run_command("flake8 . --exclude=.venv,.venv311,archive,bar-recon-clean --max-line-length=120", "flake8")

    # Run yamllint with custom config and whitelist
    run_yamllint()

    log_message("\n✅ Lint checks completed.")
    log_message(f"{hr}")


if __name__ == "__main__":
    main()

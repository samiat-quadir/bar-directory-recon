#!/usr/bin/env python3
"""
Run Linters Script

This script is called by the pre-push Git hook to run various linting tools
on staged code before allowing a push to proceed. It helps maintain code
quality across the repository.
"""

import os
import subprocess
import sys


def run_command(command, description):
    """
    Run a shell command and return the result.

    Args:
        command (list): Command to run as a list of arguments
        description (str): Description of the command for logging

    Returns:
        bool: True if command succeeded, False otherwise
    """
    print(f"Running {description}...")
    try:
        result = subprocess.run(command,
                               check=True,
                               capture_output=True,
                               text=True, timeout=60)

        print(f"✅ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return False


def get_staged_python_files():
    """
    Get a list of staged Python files in the repository.

    Returns:
        list: List of staged Python file paths
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            check=True,
            capture_output=True,
            text=True
        , timeout=60)
        files = result.stdout.strip().split('\n')
        return [f for f in files if f.endswith('.py') and os.path.exists(f)]

    except subprocess.CalledProcessError:
        print("⚠️ Warning: Unable to get staged files. Running linters on all Python files.")
        # Fallback to all Python files in the repo
        result = subprocess.run(
            ['git', 'ls-files', '*.py'],
            check=True,
            capture_output=True,
            text=True
        , timeout=60)
        return result.stdout.strip().split('\n')



def main():
    """
    Main function that runs all linters on staged Python files.
    """
    print("🔍 Starting linter checks...")

    # Get the list of files to check
    files = get_staged_python_files()

    if not files:
        print("✅ No Python files to check. Linters passed.")
        return 0

    print(f"Found {len(files)} files to check")

    # Flag to track overall success
    success = True

    # Optional: Run Black (code formatter)
    try:
        import black

        if run_command(["black", "--check"] + files, "Black code formatter"):
            print("💯 Code formatting looks good!")
        else:
            print("⚠️ Code formatting issues found. Run 'black .' to format your code.")
            success = False
    except ImportError:
        print("⚠️ Black not installed. Skipping code formatting check.")

    # Optional: Run Flake8 (linter)
    try:
        import flake8

        if run_command(["flake8"] + files, "Flake8 linter"):
            print("💯 No linting issues found!")
        else:
            print("⚠️ Linting issues found. Please fix them before pushing.")
            success = False
    except ImportError:
        print("⚠️ Flake8 not installed. Skipping linting check.")

    # Optional: Run isort (import sorter)
    try:
        import isort

        if run_command(["isort", "--check-only"] + files, "isort import checker"):
            print("💯 Imports are properly sorted!")
        else:
            print("⚠️ Import sorting issues found. Run 'isort .' to sort imports.")
            success = False
    except ImportError:
        print("⚠️ isort not installed. Skipping import order check.")

    # Optional: Run mypy (type checker)
    try:
        import mypy

        if run_command(["mypy"] + files, "mypy type checker"):
            print("💯 Type checking passed!")
        else:
            print("⚠️ Type checking issues found. Please fix them before pushing.")
            success = False
    except ImportError:
        print("⚠️ mypy not installed. Skipping type checking.")

    if success:
        print("✅ All linter checks passed! You're good to go.")
        return 0
    else:
        print("❌ Some linter checks failed. Please fix the issues before pushing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())


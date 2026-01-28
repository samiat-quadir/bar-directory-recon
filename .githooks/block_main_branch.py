#!/usr/bin/env python3
"""
Pre-commit hook to block direct commits to the main branch.

This hook prevents developers and agents from accidentally committing
directly to main, enforcing the branch → PR → merge workflow.

Exit codes:
  0 - Not on main, commit allowed
  1 - On main, commit blocked
"""

import subprocess
import sys


def get_current_branch() -> str:
    """Get the name of the current Git branch."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # If we can't determine the branch, allow the commit
        # (e.g., during initial commit or detached HEAD)
        return ""
    except subprocess.TimeoutExpired:
        return ""


def main() -> int:
    """Check if we're on main and block the commit if so."""
    branch = get_current_branch()

    if branch == "main":
        print("\n" + "=" * 60)
        print("❌ COMMIT BLOCKED: Direct commits to 'main' are disabled.")
        print("=" * 60)
        print()
        print("Please follow the branch → PR → merge workflow:")
        print()
        print("  1. Create a feature branch:")
        print("     git checkout -b feature/your-feature-name")
        print()
        print("  2. Make your changes and commit to the branch")
        print()
        print("  3. Push and open a Pull Request:")
        print("     git push -u origin feature/your-feature-name")
        print()
        print("  4. Get the PR reviewed and merged via GitHub")
        print()
        print("See CONTRIBUTING.md for the full workflow.")
        print("=" * 60 + "\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

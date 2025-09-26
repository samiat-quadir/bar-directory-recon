"""
Auto Conflict Resolver

A Python script to automatically resolve Git merge conflicts using specified strategies.

Features:
- Auto-detects git repository location
- Supports 'ours' and 'theirs' resolution strategies
- Provides fallback strategy if primary fails
- Command-line argument support
- Robust error handling

Usage:
    python auto_conflict_resolver.py [--primary {ours,theirs}] [--fallback {ours,theirs}] [--repo-path PATH]

Examples:
    python auto_conflict_resolver.py
    python auto_conflict_resolver.py --primary theirs --fallback ours
    python auto_conflict_resolver.py --repo-path /path/to/repo
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_git_repository() -> Path:
    """Find the git repository root starting from the current directory."""
    current_path = Path.cwd()

    # Search upwards for .git directory
    for path in [current_path] + list(current_path.parents):
        if (path / ".git").exists():
            return path

    # If not found, check if current directory is a git repo
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("❌ Error: Not in a git repository or git repository not found.")
        print("Please run this script from within a git repository.")
        sys.exit(1)


def get_conflicted_files() -> list[str]:
    """Get a list of conflicted files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
        return result.stdout.strip().splitlines()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error retrieving conflicted files: {e.stderr}")
        sys.exit(1)


def resolve_file(file: str, primary_strategy: str, fallback_strategy: str) -> bool:
    """Resolve a single conflicted file."""
    try:
        subprocess.run(
            ["git", "checkout", f"--{primary_strategy}", file],
            check=True,
            capture_output=True,
            timeout=60,
        )
        print(f"✅ Resolved {file} using '{primary_strategy}' strategy.")
    except subprocess.CalledProcessError:
        print(f"⚠️ '{primary_strategy}' failed for {file}, trying '{fallback_strategy}'...")
        try:
            subprocess.run(
                ["git", "checkout", f"--{fallback_strategy}", file],
                check=True,
                capture_output=True,
                timeout=60,
            )
            print(f"✅ Resolved {file} using '{fallback_strategy}' strategy.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Both strategies failed for {file}: {e.stderr}")
            return False

    # Add the resolved file to staging
    try:
        subprocess.run(["git", "add", file], check=True, capture_output=True, timeout=60)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to add {file} to staging: {e.stderr}")
        return False

    return True


def resolve_conflicts(primary_strategy: str = "ours", fallback_strategy: str = "theirs") -> None:
    """Resolve all conflicted files."""
    print(
        f"🔧 Starting conflict resolution with primary strategy: '{primary_strategy}', "
        f"fallback: '{fallback_strategy}'"
    )

    conflicted_files = get_conflicted_files()

    if not conflicted_files:
        print("✅ No merge conflicts detected.")
        return

    print(f"📋 Found {len(conflicted_files)} conflicted files:")
    for file in conflicted_files:
        print(f"  • {file}")
    print()

    failed_resolutions: list[str] = []

    for file in conflicted_files:
        success = resolve_file(file, primary_strategy, fallback_strategy)
        if not success:
            failed_resolutions.append(file)

    if failed_resolutions:
        print(f"❌ Failed to resolve the following files: {failed_resolutions}")
        print("🛑 Please resolve these manually and rerun this script.")
        sys.exit(1)

    print(
        f"🎉 Successfully resolved all conflicts using '{primary_strategy}' "
        f"with fallback to '{fallback_strategy}'."
    )
    print("\nNext step: run 'git rebase --continue' to finalize your rebase.")


def main() -> None:
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Automatically resolve Git merge conflicts using specified strategies."
    )
    parser.add_argument(
        "--primary",
        default="ours",
        choices=["ours", "theirs"],
        help="Primary strategy to use for conflict resolution (default: ours)",
    )
    parser.add_argument(
        "--fallback",
        default="theirs",
        choices=["ours", "theirs"],
        help="Fallback strategy if primary fails (default: theirs)",
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        help="Path to git repository (if not provided, will auto-detect)",
    )

    args = parser.parse_args()

    # Change to repository directory
    if args.repo_path:
        repo_path = Path(args.repo_path)
        if not repo_path.exists():
            print(f"❌ Error: Repository path '{args.repo_path}' does not exist.")
            sys.exit(1)
        os.chdir(repo_path)
    else:
        # Auto-detect git repository
        repo_path = find_git_repository()
        os.chdir(repo_path)
        print(f"🔍 Found git repository at: {repo_path}")

    # Resolve conflicts
    resolve_conflicts(args.primary, args.fallback)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Quick setup script for autonomous development operations.
This script prepares the environment for autonomous code changes.
"""

import subprocess
import sys
from pathlib import Path


def setup_autonomous_environment():
    """Set up environment for autonomous operations."""
    print("[*] Setting up autonomous development environment...")

    workspace = Path.cwd()

    # Ensure scripts directory exists
    scripts_dir = workspace / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Make scripts executable (Unix-like systems)
    if sys.platform != "win32":
        for script in scripts_dir.glob("*.py"):
            script.chmod(0o755)

    # Update pre-commit hooks
    try:
        subprocess.run([sys.executable, "-m", "pre_commit", "install"], check=True, cwd=workspace)
        print("[+] Pre-commit hooks updated")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[!] Pre-commit not available, continuing...")

    # Install required packages if needed
    required_packages = [
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "autoflake>=2.0.0",
        "mypy>=1.5.0",
    ]

    for package in required_packages:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "show", package.split(">=")[0]],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            print(f"[*] Installing {package}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
                print(f"[+] {package} installed")
            except subprocess.CalledProcessError:
                print(f"[-] Failed to install {package}")

    print("[+] Autonomous environment setup complete!")
    print("\n[*] Available commands:")
    print("   Format code: python scripts/format_code.py")
    print("   Auto commit: python scripts/auto_commit.py [message]")
    print("   Quick setup: python scripts/quick_setup.py")


if __name__ == "__main__":
    setup_autonomous_environment()

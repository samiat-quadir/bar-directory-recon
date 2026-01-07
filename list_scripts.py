#!/usr/bin/env python3
"""Quick script listing tool"""

from pathlib import Path


def main():
    root = Path(".")

    scripts = []
    for pattern in ["**/*.bat", "**/*.ps1"]:
        for file_path in root.glob(pattern):
            if ".git" not in str(file_path) and "__pycache__" not in str(file_path):
                scripts.append(file_path.name)

    print(f"Found {len(scripts)} scripts:")
    for script in sorted(set(scripts)):
        print(f"  {script}")


if __name__ == "__main__":
    main()

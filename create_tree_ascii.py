#!/usr/bin/env python3
"""
Create a tree structure visualization with ASCII characters
"""

import os
import sys


def print_tree(directory, prefix="", level=0, max_level=3):
    """Print a tree structure of the directory using ASCII characters"""
    if level > max_level:
        return

    items = []
    try:
        items = sorted(os.listdir(directory))
    except PermissionError:
        print(f"{prefix}[Permission Denied]")
        return

    # Filter out some noise and focus on main structure
    if level == 0:
        # Show all files and folders at root
        items = [item for item in items if not item.startswith("__pycache__")]
    elif level >= 2:
        # Limit deeper levels to avoid too much detail
        items = items[:15]  # Show first 15 items

    for i, item in enumerate(items):
        # Don't skip hidden files at root level for .vscode
        if item.startswith(".") and level > 1:
            continue

        path = os.path.join(directory, item)
        is_last = i == len(items) - 1
        current_prefix = "+-- " if is_last else "|-- "

        if os.path.isdir(path):
            print(f"{prefix}{current_prefix}{item}/")
            if level < max_level:
                extension = "    " if is_last else "|   "
                print_tree(path, prefix + extension, level + 1, max_level)
        else:
            print(f"{prefix}{current_prefix}{item}")


if __name__ == "__main__":
    # Allow specifying the directory as a command line argument
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
        max_level = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    else:
        target_dir = ".vscode"
        max_level = 4

    print(f"{target_dir}/")
    print_tree(target_dir, max_level=max_level)

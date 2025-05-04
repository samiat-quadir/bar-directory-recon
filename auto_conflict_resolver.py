import argparse
import os
import shutil
import subprocess
from pathlib import Path

CONFLICT_MARKERS = ["<<<<<<<", "=======", ">>>>>>>"]


def get_conflicted_files():
    result = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, text=True)
    return result.stdout.strip().splitlines()


def backup_files(file_paths, backup_dir="merge_conflicts_backup"):
    os.makedirs(backup_dir, exist_ok=True)
    for file in file_paths:
        src = Path(file)
        dst = Path(backup_dir) / src.name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"✅ Backed up: {src} -> {dst}")


def strip_conflict_markers(file_path, mode):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned_lines = []
    keep = None
    skip = False

    for line in lines:
        if line.startswith("<<<<<<<"):
            keep = "ours" if mode == "keep-ours" else "theirs"
            skip = True
            continue
        elif line.startswith("======="):
            skip = False if keep == "theirs" else True
            continue
        elif line.startswith(">>>>>>>"):
            skip = False
            continue

        if not skip:
            cleaned_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)
    print(f"🧽 Cleaned conflict markers in: {file_path}")


def resolve_all(mode="keep-ours", backup=True):
    conflicted_files = get_conflicted_files()
    if not conflicted_files:
        print("✅ No conflicts detected.")
        return

    if backup:
        backup_files(conflicted_files)

    for file in conflicted_files:
        strip_conflict_markers(file, mode)
        subprocess.run(["git", "add", file])

    print("\n🎯 All conflicted files processed and staged. Run `git commit` to finalize.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolve merge conflicts by auto-choosing 'ours' or 'theirs'.")
    parser.add_argument(
        "--mode",
        choices=["keep-ours", "keep-theirs"],
        default="keep-ours",
        help="Choose which version to keep when resolving conflicts.",
    )
    parser.add_argument("--no-backup", action="store_true", help="Disable file backup before modification.")
    args = parser.parse_args()

    resolve_all(mode=args.mode, backup=not args.no_backup)

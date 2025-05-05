# tools/show_full_project_tree.py

import os
from pathlib import Path


def print_tree(root: Path, prefix: str = ""):
    entries = list(root.iterdir())
    entries.sort()
    pointers = ["├── "] * (len(entries) - 1) + ["└── "]
    for pointer, path in zip(pointers, entries):
        print(prefix + pointer + path.name)
        if path.is_dir() and not path.name.startswith(".venv") and not path.name.startswith(".git"):
            extension = "│   " if pointer == "├── " else "    "
            print_tree(path, prefix + extension)


def save_tree_to_file(output_path="project_tree_report.md"):
    with open(output_path, "w", encoding="utf-8") as f:

        def write_tree(root: Path, prefix: str = ""):
            entries = list(root.iterdir())
            entries.sort()
            pointers = ["├── "] * (len(entries) - 1) + ["└── "]
            for pointer, path in zip(pointers, entries):
                f.write(prefix + pointer + path.name + "\n")
                if path.is_dir() and not path.name.startswith(".venv") and not path.name.startswith(".git"):
                    extension = "│   " if pointer == "├── " else "    "
                    write_tree(path, prefix + extension)

        write_tree(Path("."))


if __name__ == "__main__":
    print("\n📂 Project Folder Structure:\n")
    print_tree(Path("."))
    save_tree_to_file()
    print("\n✅ Saved to 'project_tree_report.md'")

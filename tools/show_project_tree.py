import datetime
from pathlib import Path


def print_tree(start_path: Path, prefix: str = ""):
    items = sorted(start_path.iterdir())
    for i, item in enumerate(items):
        connector = "└── " if i == len(items) - 1 else "├── "
        print(f"{prefix}{connector}{item.name}")
        if item.is_dir():
            extension = "    " if i == len(items) - 1 else "│   "
            print_tree(item, prefix + extension)


def save_tree_to_file(start_path: Path, output_file: Path):
    def write_tree(path: Path, prefix: str = ""):
        items = sorted(path.iterdir())
        for i, item in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            with output_file.open("a", encoding="utf-8") as f:
                f.write(f"{prefix}{connector}{item.name}\n")
            if item.is_dir():
                extension = "    " if i == len(items) - 1 else "│   "
                write_tree(item, prefix + extension)

    # Add the date to the file
    date_generated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with output_file.open("w", encoding="utf-8") as f:
        f.write(f"Project Tree Report - Generated on {date_generated}\n\n")
    write_tree(start_path)


if __name__ == "__main__":
    output_path = Path("project_tree_report.txt")
    save_tree_to_file(Path("."), output_path)
    print(f"Project tree saved to {output_path}")

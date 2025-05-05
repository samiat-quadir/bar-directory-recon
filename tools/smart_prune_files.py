import os
from pathlib import Path


def smart_prune_files(directory: str, extensions_to_prune: list):
    """Prune files with specified extensions in the given directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in extensions_to_prune:
                print(f"Pruning: {file_path}")
                file_path.unlink()


if __name__ == "__main__":
    extensions = [".log", ".bak", ".tmp"]
    smart_prune_files(".", extensions)

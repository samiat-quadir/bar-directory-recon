import os
import sys


def set_root_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    project_root = os.path.abspath(os.path.dirname(__file__))
    if project_root not in sys.path:
        sys.path.append(project_root)
    src_path = os.path.join(project_root, "src")
    if src_path not in sys.path:
        sys.path.append(src_path)


if __name__ == "__main__":
    set_root_path()
    print(f"PYTHONPATH updated: {sys.path}")

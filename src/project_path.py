import os
import sys


def set_root_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.dirname(__file__))


if __name__ == "__main__":
    paths = set_root_path()
    print(f"Project paths: {paths}")

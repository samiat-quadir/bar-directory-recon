import os


def set_root_path():
    os.path.dirname(os.path.abspath(__file__))
    os.path.abspath(os.path.dirname(__file__))


if __name__ == "__main__":
    paths = set_root_path()
    print(f"Project paths: {paths}")

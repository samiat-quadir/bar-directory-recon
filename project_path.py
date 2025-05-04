import os


def set_root_path():
    """
    Sets project path variables but without modifying sys.path.

    Returns:
        dict: Dictionary containing project path information
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.dirname(__file__))
    src_path = os.path.join(project_root, "src")

    return {"current_dir": current_dir, "project_root": project_root, "src_path": src_path}


if __name__ == "__main__":
    paths = set_root_path()
    print(f"Project paths: {paths}")

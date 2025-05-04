import os
import sys



def set_root_path():
<<<<<<< HEAD
    """
    Sets project path variables but without modifying sys.path.

    Returns:
        dict: Dictionary containing project path information
    """
=======
"""TODO: Add docstring."""
>>>>>>> 3ccf4fd (Committing all changes)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.dirname(__file__))
<<<<<<< HEAD
    src_path = os.path.join(project_root, "src")

    return {"current_dir": current_dir, "project_root": project_root, "src_path": src_path}

=======
    if project_root not in sys.path:
        sys.path.append(project_root)
    src_path = os.path.join(project_root, "src")
    if src_path not in sys.path:
        sys.path.append(src_path)
>>>>>>> 3ccf4fd (Committing all changes)


if __name__ == "__main__":
    paths = set_root_path()
    print(f"Project paths: {paths}")

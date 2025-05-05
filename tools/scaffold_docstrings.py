import ast
import os
from pathlib import Path


def scaffold_docstrings(directory: str):
    """Scaffold missing docstrings for Python files in the given directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=str(file_path))

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)) and not ast.get_docstring(node):
                        print(f"Missing docstring in {file_path}: {node.name if hasattr(node, 'name') else 'module'}")


if __name__ == "__main__":
    scaffold_docstrings(".")

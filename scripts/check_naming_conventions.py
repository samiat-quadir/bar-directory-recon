#!/usr/bin/env python3
"""
Check naming conventions across the codebase.
Identifies CamelCase vs snake_case inconsistencies.
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict


class NamingConventionChecker:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.issues = []

    def scan_files(self) -> dict[str, Any]:
        """Scan all Python files for naming issues."""
        results = {
            "files_scanned": 0,
            "issues": [],
            "duplicate_configs": [],
            "camelcase_functions": [],
            "camelcase_variables": [],
            "camelcase_classes": [],
            "inconsistent_modules": [],
        }

        # Scan source files
        for py_file in self.root_dir.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            results["files_scanned"] += 1
            self._analyze_file(py_file, results)

        # Check for duplicate config loaders
        self._check_duplicate_configs(results)

        return results

    def _analyze_file(self, file_path: Path, results: dict[str, Any]):
        """Analyze a single Python file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, file_path, results)
            except SyntaxError:
                results["issues"].append(f"Syntax error in {file_path}")

        except Exception as e:
            results["issues"].append(f"Error reading {file_path}: {e}")

    def _analyze_ast(self, tree: ast.AST, file_path: Path, results: dict[str, Any]):
        """Analyze AST for naming conventions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if self._is_camelcase(node.name) and not node.name.startswith("test"):
                    results["camelcase_functions"].append(
                        {
                            "file": str(file_path),
                            "function": node.name,
                            "line": node.lineno,
                        }
                    )

            elif isinstance(node, ast.ClassDef):
                # Class names should be PascalCase, so we check if they're incorrectly snake_case
                if self._is_snake_case(node.name):
                    results["inconsistent_modules"].append(
                        {
                            "file": str(file_path),
                            "class": node.name,
                            "line": node.lineno,
                            "issue": "Class should use PascalCase",
                        }
                    )

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if self._is_camelcase(target.id) and not target.id.isupper():
                            results["camelcase_variables"].append(
                                {
                                    "file": str(file_path),
                                    "variable": target.id,
                                    "line": node.lineno,
                                }
                            )

    def _is_camelcase(self, name: str) -> bool:
        """Check if a name is camelCase."""
        return bool(re.match(r"^[a-z]+[A-Z][a-zA-Z]*$", name))

    def _is_snake_case(self, name: str) -> bool:
        """Check if a name is snake_case."""
        return bool(re.match(r"^[a-z_]+$", name))

    def _check_duplicate_configs(self, results: dict[str, Any]):
        """Check for duplicate configuration loaders."""
        config_files = []
        for py_file in self.root_dir.rglob("*config*.py"):
            if ".venv" not in str(py_file) and "__pycache__" not in str(py_file):
                config_files.append(str(py_file))

        # Group by base name
        grouped = {}
        for f in config_files:
            base = Path(f).stem
            if base not in grouped:
                grouped[base] = []
            grouped[base].append(f)

        for base, files in grouped.items():
            if len(files) > 1:
                results["duplicate_configs"].append({"base_name": base, "files": files})


def main():
    checker = NamingConventionChecker()
    results = checker.scan_files()

    print("🔍 Naming Convention Analysis Report")
    print("=" * 50)
    print(f"Files scanned: {results['files_scanned']}")
    print()

    if results["duplicate_configs"]:
        print("📋 Duplicate Configuration Loaders:")
        for dup in results["duplicate_configs"]:
            print(f"  Base name: {dup['base_name']}")
            for f in dup["files"]:
                print(f"    - {f}")
            print()

    if results["camelcase_functions"]:
        print("🐪 CamelCase Functions (should be snake_case):")
        for func in results["camelcase_functions"]:
            print(f"  {func['file']}:{func['line']} - {func['function']}")
        print()

    if results["camelcase_variables"]:
        print("🐪 CamelCase Variables (should be snake_case):")
        for var in results["camelcase_variables"]:
            print(f"  {var['file']}:{var['line']} - {var['variable']}")
        print()

    if results["inconsistent_modules"]:
        print("⚠️  Inconsistent Module Naming:")
        for mod in results["inconsistent_modules"]:
            print(f"  {mod['file']}:{mod['line']} - {mod['class']} ({mod['issue']})")
        print()

    if results["issues"]:
        print("❌ Issues:")
        for issue in results["issues"]:
            print(f"  - {issue}")
        print()

    # Summary recommendations
    print("📝 Task 2 Recommendations:")
    print("1. Consolidate duplicate config loaders")
    print("2. Standardize naming conventions")
    print("3. Review module organization")

    return results


if __name__ == "__main__":
    main()

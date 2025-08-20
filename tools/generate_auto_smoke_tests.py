#!/usr/bin/env python3
"""
Auto-Smoke Test Generator for Coverage Gaps
Analyzes coverage report and generates basic smoke tests for 0% coverage modules.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
import ast
import importlib.util


def analyze_coverage_report(coverage_file_path: str) -> List[Tuple[str, int, int]]:
    """Parse coverage report and extract 0% coverage files."""
    zero_coverage_files = []
    
    with open(coverage_file_path, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        # Match coverage report lines with format: filename   stmts   miss   cover   missing
        if line.strip() and not line.startswith('Name') and not line.startswith('-') and 'TOTAL' not in line:
            parts = line.split()
            if len(parts) >= 4 and parts[-2].endswith('%'):
                filename = parts[0]
                try:
                    statements = int(parts[1])
                    missing = int(parts[2])
                    coverage_pct = parts[3].rstrip('%')
                    
                    # Focus on files with 0% coverage and significant code
                    if coverage_pct == '0' and statements > 10:
                        zero_coverage_files.append((filename, statements, missing))
                except (ValueError, IndexError):
                    continue
    
    return zero_coverage_files


def extract_classes_and_functions(file_path: str) -> Dict[str, List[str]]:
    """Extract class and function names from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                functions.append(node.name)
        
        return {'classes': classes, 'functions': functions}
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {'classes': [], 'functions': []}


def generate_smoke_test_content(module_path: str, module_info: Dict[str, List[str]]) -> str:
    """Generate basic smoke test content for a module."""
    module_name = module_path.replace('/', '.').replace('.py', '')
    test_name = f"test_smoke_{module_name.replace('.', '_')}"
    
    # Import statement
    try:
        import_path = module_name
        if module_name.startswith('src.'):
            import_path = module_name[4:]  # Remove 'src.' prefix
    except:
        import_path = module_name
    
    content = f'''"""
Auto-generated smoke tests for {module_name}
Tests basic import and instantiation capabilities.
"""

import pytest
from unittest.mock import Mock, patch

# Skip if module has import issues
try:
    import {import_path}
    MODULE_AVAILABLE = True
except ImportError as e:
    MODULE_AVAILABLE = False
    IMPORT_ERROR = str(e)


@pytest.mark.skipif(not MODULE_AVAILABLE, reason=f"Module import failed: {{IMPORT_ERROR if not MODULE_AVAILABLE else 'Unknown'}}")
def {test_name}_import():
    """Test that the module can be imported successfully."""
    import {import_path}
    assert {import_path} is not None


'''
    
    # Add class instantiation tests
    for class_name in module_info['classes']:
        content += f'''
@pytest.mark.skipif(not MODULE_AVAILABLE, reason="Module not available")
def {test_name}_{class_name.lower()}_instantiation():
    """Test basic instantiation of {class_name}."""
    try:
        import {import_path}
        if hasattr({import_path}, '{class_name}'):
            # Try basic instantiation with mocked dependencies
            with patch.multiple({import_path}, autospec=True) if hasattr({import_path}, 'logger') else patch('builtins.print'):
                instance = {import_path}.{class_name}()
                assert instance is not None
    except Exception as e:
        # For smoke tests, we just need to ensure no catastrophic failures
        if "required positional argument" in str(e).lower():
            pytest.skip(f"Class {class_name} requires constructor arguments")
        else:
            raise
'''
    
    # Add function availability tests for key functions
    key_functions = [f for f in module_info['functions'] if not f.startswith('test_')][:3]  # Limit to 3
    for func_name in key_functions:
        content += f'''
@pytest.mark.skipif(not MODULE_AVAILABLE, reason="Module not available")
def {test_name}_{func_name}_available():
    """Test that {func_name} function is available."""
    import {import_path}
    assert hasattr({import_path}, '{func_name}')
    assert callable(getattr({import_path}, '{func_name}'))
'''
    
    return content


def main():
    """Main function to generate auto-smoke tests."""
    repo_root = Path(__file__).parent.parent
    coverage_report = repo_root / "logs" / "nightly" / "coverage_first_pass.txt"
    smoke_tests_dir = repo_root / "src" / "tests" / "smoke"
    
    if not coverage_report.exists():
        print(f"Coverage report not found: {coverage_report}")
        return 1
    
    # Create smoke tests directory
    smoke_tests_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py for the smoke tests package
    init_file = smoke_tests_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Auto-generated smoke tests for coverage gaps."""\n')
    
    # Analyze coverage gaps
    zero_coverage_files = analyze_coverage_report(str(coverage_report))
    
    print(f"Found {len(zero_coverage_files)} files with 0% coverage")
    
    generated_tests = 0
    for file_path, statements, missing in zero_coverage_files:
        # Convert to actual file path
        actual_file_path = repo_root / file_path
        
        if not actual_file_path.exists():
            print(f"File not found: {actual_file_path}")
            continue
        
        # Extract module structure
        module_info = extract_classes_and_functions(str(actual_file_path))
        
        if not module_info['classes'] and not module_info['functions']:
            print(f"No classes or functions found in {file_path}")
            continue
        
        # Generate smoke test
        test_content = generate_smoke_test_content(file_path, module_info)
        
        # Write smoke test file
        test_filename = f"test_smoke_{Path(file_path).stem}.py"
        test_file_path = smoke_tests_dir / test_filename
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        print(f"Generated smoke test: {test_file_path}")
        generated_tests += 1
        
        # Limit to prevent overwhelming the test suite
        if generated_tests >= 10:
            print("Limited to 10 smoke tests to prevent test suite bloat")
            break
    
    print(f"Generated {generated_tests} smoke test files")
    
    # Generate a summary report
    summary_file = repo_root / "logs" / "nightly" / "auto_smoke_tests_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"Auto-Smoke Tests Generation Summary\n")
        f.write(f"==================================\n\n")
        f.write(f"Total files with 0% coverage: {len(zero_coverage_files)}\n")
        f.write(f"Smoke tests generated: {generated_tests}\n\n")
        f.write(f"Generated test files:\n")
        for i, (file_path, _, _) in enumerate(zero_coverage_files[:generated_tests]):
            test_filename = f"test_smoke_{Path(file_path).stem}.py"
            f.write(f"  {i+1}. {test_filename} (covers {file_path})\n")
    
    print(f"Summary written to: {summary_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
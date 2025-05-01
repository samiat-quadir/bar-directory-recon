"""Root conftest.py for pytest configuration."""

import os
import sys
from pathlib import Path

# Get absolute path to project root
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Add universal_recon to Python path
universal_recon_path = project_root / "universal_recon"
if universal_recon_path.exists():
    sys.path.insert(0, str(universal_recon_path))

# Add tests directory to Python path
tests_path = universal_recon_path / "tests"
if tests_path.exists():
    sys.path.insert(0, str(tests_path))


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "analytics: mark test as analytics test")

"""Test package for bar-directory-recon."""

from pathlib import Path

# Make test data directory path available
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)
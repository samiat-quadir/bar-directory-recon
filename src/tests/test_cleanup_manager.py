"""Tests for cleanup_manager.py."""
import os
from pathlib import Path
import pytest
from datetime import datetime, timedelta
from src.cleanup_manager import cleanup_old_files, archive_logs
from src.utils.logging.logging_manager import setup_logger

# Configure test logger
logger = setup_logger(__name__)

@pytest.fixture
def test_dir(tmp_path: Path) -> Path:
    """Create a temporary test directory."""
    test_dir = tmp_path / "test_cleanup"
    test_dir.mkdir()
    return test_dir

@pytest.fixture
def setup_test_files(test_dir: Path):
    """Set up test files with different ages."""
    def _create_test_file(name: str, days_old: int = 0) -> Path:
        file_path = test_dir / name
        file_path.write_text("test content")
        mod_time = datetime.now() - timedelta(days=days_old)
        os.utime(file_path, (mod_time.timestamp(), mod_time.timestamp()))
        return file_path

    old_log = _create_test_file("old_test.log", days_old=10)
    new_log = _create_test_file("new_test.log", days_old=1)
    return {"old_log": old_log, "new_log": new_log}

def test_cleanup_old_files(test_dir: Path, setup_test_files: dict, monkeypatch):
    """Test cleanup of old log files."""
    # Mock TARGET_DIRS to use our test directory
    import src.cleanup_manager as cm
    monkeypatch.setattr(cm, "TARGET_DIRS", {
        str(test_dir): ["*.log"]
    })
    
    # Run cleanup
    removed = cleanup_old_files()
    
    # Verify old file removed, new file kept
    assert not setup_test_files["old_log"].exists(), "Old file should be removed"
    assert setup_test_files["new_log"].exists(), "New file should be kept"
    assert removed == 1, "Should remove exactly one file"

def test_archive_logs(test_dir: Path, setup_test_files: dict):
    """Test log archiving functionality."""
    archive_dir = test_dir / "archive"
    
    # Run archive
    archive_logs(str(archive_dir))
    
    # Verify archiving
    assert archive_dir.exists(), "Archive directory should be created"
    archived_files = list(archive_dir.glob("*.log"))
    assert len(archived_files) == 2, "Both files should be archived"
    assert not setup_test_files["old_log"].exists(), "Original files should be moved"
    assert not setup_test_files["new_log"].exists(), "Original files should be moved"
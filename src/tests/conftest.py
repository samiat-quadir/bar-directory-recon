"""Configure test environment."""

import sys
from pathlib import Path

import pytest

# Add project root and src to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_PATH))


@pytest.fixture
def project_root() -> Path:
    """Return project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def config_dir(project_root: Path) -> Path:
    """Return config directory."""
    return project_root / "config"


@pytest.fixture
def logs_dir(project_root: Path) -> Path:
    """Return logs directory."""
    return project_root / "logs"


@pytest.fixture
def test_data_dir(project_root: Path) -> Path:
    """Return test data directory."""
    path = project_root / "src" / "tests" / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path

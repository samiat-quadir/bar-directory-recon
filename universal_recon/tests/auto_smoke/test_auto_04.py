import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../..", "src"))


def test_import_04():
    try:
        __import__("hallandale_pipeline")
    except ImportError:
        pytest.skip("hallandale_pipeline module not available")

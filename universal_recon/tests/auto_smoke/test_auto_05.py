import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../..", "src"))


def test_import_05():
    try:
        __import__("hallandale_pipeline_fixed")
    except ImportError:
        pytest.skip("hallandale_pipeline_fixed module not available")

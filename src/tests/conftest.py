# conftest for pytest in src/tests
import os
import sys

# Add src root (one level up) to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

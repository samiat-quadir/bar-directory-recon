# The file `c:\Code\bar-directory-recon\conftest.py` exists, but is empty
#!/usr/bin/env python3
"""
Conftest for pytest to set up PYTHONPATH for src modules.
"""
import os
import sys

# Add project src directory to path for module imports
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
if SRC_DIR not in sys.path:
	sys.path.insert(0, SRC_DIR)

"""
Configure pytest environment for running tests in the universal_recon package.
This file sets up the Python import paths to ensure all tests can correctly
import the necessary modules from the parent directories.
"""
import os

# These path modifications will be removed as they're no longer needed
# All imports should use the proper package structure:
# from universal_recon.utils import module_name, etc.

# Print paths for debugging
print(f"Pytest running from: {os.getcwd()}")

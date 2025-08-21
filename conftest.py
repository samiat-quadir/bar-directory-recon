#!/usr/bin/env python3

"""
Conftest for pytest.

Adds the project `src` directory to PYTHONPATH and provides a minimal,
best-effort workaround for transient Windows file-lock errors that can
cause basetemp cleanup to fail during test teardown.

The mitigation is intentionally small and only used for test runs. It
retries a few times when ``shutil.rmtree`` raises a transient
``PermissionError`` (Windows ``WinError 32``) before giving up.
"""

# isort: skip_file
import errno
import os
import shutil
import sys
import time


# Add project src directory to path for module imports
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# Mitigation for transient Windows file-locks during pytest basetemp cleanup.
# Perform a few short retries when PermissionError occurs.
try:
    _orig_rmtree = shutil.rmtree

    def _safe_rmtree(
        path,
        ignore_errors=False,
        onerror=None,
        *,
        onexc=None,
        dir_fd=None,
    ):
        """Retry a few times for transient PermissionError (WinError 32).

        If retries are exhausted and ignore_errors is True, return silently.
        Otherwise re-raise the last exception.
        """

        retries = 3
        delay = 0.1
        for attempt in range(retries):
            try:
                return _orig_rmtree(
                    path,
                    ignore_errors=ignore_errors,
                    onerror=onerror,
                    onexc=onexc,
                    dir_fd=dir_fd,
                )
            except PermissionError as exc:
                # On Windows, winerror == 32 corresponds to "file in use".
                # Also check errno.EACCES as a secondary indicator.
                if (
                    getattr(exc, "winerror", None) == 32
                    or getattr(exc, "errno", None) == errno.EACCES
                ):
                    if attempt < retries - 1:
                        time.sleep(delay)
                        delay *= 2
                        continue
                    if ignore_errors:
                        return
                # Not a transient PermissionError or retries exhausted; re-raise
                raise

    # Install the wrapper for the duration of the test run.
    # Type checkers may complain; this is test-only, so ignore the
    # static assignment error.
    shutil.rmtree = _safe_rmtree  # type: ignore[assignment]
except Exception:
    # Best-effort: do not prevent tests from running if this mitigation fails.
    pass

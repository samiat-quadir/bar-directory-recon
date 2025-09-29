#!/usr/bin/env python3
"""Pre-commit hook to block device/persona-named files.

This placeholder hook is intentionally permissive for now to unblock
attic cleanup commits. It can be replaced with a stricter implementation
later that enforces naming rules.
"""

import sys

# Minimal no-op to avoid blocking commit while retaining the hook entry.
# A future improvement: scan staged files for disallowed device names.

sys.exit(0)

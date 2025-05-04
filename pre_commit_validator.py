import os
import sys

# Critical folders to check
required_dirs = [
    "universal_recon/analytics",
    "universal_recon/core",
    "universal_recon/validators"
]

missing = [d for d in required_dirs if not os.path.isdir(d)]

if missing:
    print(f"❌ ERROR: Missing critical folders: {', '.join(missing)}")
    print("🛑 Commit blocked. Restore missing directories before committing.")
    sys.exit(1)

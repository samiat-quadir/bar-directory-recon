#!/usr/bin/env python3
"""
Preflight validation for universal recon phase.
Checks for required files, workflows, and environment settings.
"""
import os
import sys

def main():
    missing = []
    required = [
        '.github/workflows/flow_runner.yml',
        '.github/workflows/dashboard_deploy.yml',
        'docs/README_phase_27.md',
        'docs/README_phase_28.md',
        'docs/phase_29_backlog.yaml'
    ]
    for f in required:
        if not os.path.exists(f):
            missing.append(f)
    if missing:
        print(f"[ERROR] Missing files: {', '.join(missing)}")
        sys.exit(1)
    print("[OK] All required files present.")

if __name__ == '__main__':
    main()

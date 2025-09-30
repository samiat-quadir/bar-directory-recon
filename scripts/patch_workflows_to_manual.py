#!/usr/bin/env python3
"""Safe YAML-based workflow patcher: sets top-level 'on' to workflow_dispatch for non-kept workflows.

Usage: python scripts/patch_workflows_to_manual.py
"""
from pathlib import Path

import yaml

KEEP = {
    "ci-fast-parity.yml",
    "security-audit.yml",
    "pip-audit.yml",
    "security_audit.yml",
    "codeql.yml",
    "codeql-analysis.yml",
    "codeql.yaml",
    "lock-drift-check.yml",
    "lockdrift.yml",
}

WF_DIR = Path(".github/workflows")
changed = []
for wf in WF_DIR.glob("*.yml"):
    if wf.name in KEEP:
        continue
    text = wf.read_text(encoding="utf8")
    try:
        data = yaml.safe_load(text) or {}
    except Exception as e:
        print(f"Skipping {wf} due to parse error: {e}")
        continue
    # Replace 'on' with a manual dispatch
    data["on"] = {"workflow_dispatch": {}}
    # Add concurrency group if jobs present and concurrency not set
    if "jobs" in data and "concurrency" not in data:
        data = {
            "concurrency": {
                "group": f"manual-{wf.stem}-$GITHUB_REF",
                "cancel-in-progress": False,
            },
            **data,
        }
    # Dump back
    new_text = yaml.safe_dump(data, sort_keys=False)
    wf.write_text(new_text, encoding="utf8")
    changed.append(str(wf))

print("Patched workflows:", changed)

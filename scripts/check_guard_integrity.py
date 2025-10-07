#!/usr/bin/env python3
"""
Guard Integrity Verifier - Non-blocking CI diagnostic
Ensures guard logic exists in critical workflow files.
"""

import sys
from pathlib import Path

WORKFLOWS_DIR = Path(".github/workflows")
REQUIRED_WORKFLOWS = [
    "fast-parity-ci.yml",
    "pip-audit.yml",
    "ps-lint.yml",
    "ci-workflow-guard.yml",
]
REQUIRED_JOBS = ["audit", "fast-tests (ubuntu-latest)", "fast-tests (windows-latest)"]


def check_workflow_guards():
    """Verify guard logic in workflows (allow PR/push in critical files only)."""
    issues = []

    for workflow in REQUIRED_WORKFLOWS:
        path = WORKFLOWS_DIR / workflow
        if not path.exists():
            if not workflow.startswith("codeql"):
                issues.append(f"❌ Missing: {workflow}")
            continue

        content = path.read_text(encoding="utf-8")

        # Check for guard/short-circuit logic
        has_guard = any(
            keyword in content
            for keyword in [
                "workflow_only",
                "attic_only",
                "short-circuit",
            ]
        )

        if not has_guard and workflow not in ["ci-workflow-guard.yml"]:
            issues.append(f"⚠️  No guard logic in {workflow}")

    return issues


def check_job_names():
    """Verify the three required job names exist in workflows."""
    issues = []
    found_jobs = set()

    for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
        content = workflow_file.read_text(encoding="utf-8")
        for job in REQUIRED_JOBS:
            if f"name: {job}" in content or f'name: "{job}"' in content:
                found_jobs.add(job)

    missing = set(REQUIRED_JOBS) - found_jobs
    if missing:
        issues.append(f"❌ Missing required job names: {', '.join(missing)}")

    return issues, found_jobs


def main():
    print("🔍 Guard Integrity Verifier")
    print("=" * 60)

    guard_issues = check_workflow_guards()
    job_issues, found_jobs = check_job_names()

    all_issues = guard_issues + job_issues

    if all_issues:
        print("\n".join(all_issues))
        print(f"\n❌ FAIL: {len(all_issues)} issue(s) detected")
    else:
        print("✅ PASS: All guard checks successful")
        print(f"✅ Required jobs present: {', '.join(sorted(found_jobs))}")

    # Non-blocking: always exit 0
    sys.exit(0)


if __name__ == "__main__":
    main()

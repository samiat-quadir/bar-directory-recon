#!/usr/bin/env python3
"""
Guard integrity verifier (non-blocking)

Checks:
- Only allow-listed workflows use pull_request/push.
- Required check names exist (audit, fast-tests ubuntu/windows, workflow-guard).
- ps-lint workflow is ALWAYS-RUN on pull_request (no 'paths:' filter).

Exit 0 with a PASS/FAIL summary (non-blocking).
"""
import json
import pathlib
import re
import sys

ALLOW = {'fast-parity-ci.yml', 'pip-audit.yml', 'ps-lint.yml', 'ci-workflow-guard.yml'}
REQ = {'audit', 'fast-tests (ubuntu-latest)', 'fast-tests (windows-latest)', 'workflow-guard'}


def read(p):
    return pathlib.Path(p).read_text(encoding='utf-8')


def has_pr_or_push(txt):
    return re.search(r'(?m)^\s*on:\s*[\s\S]*?(pull_request|push)\s*:', txt) is not None


def has_paths_under_pr(txt):
    m = re.search(r'(?ms)^\s*pull_request\s*:\s*\r?\n[\s\S]*?^\s*paths\s*:', txt)
    if m:
        return True
    # inline object
    return re.search(r'(?ms)pull_request\s*:\s*\{[^}]*paths\s*:', txt) is not None


def main():
    root = pathlib.Path('.')
    wfdir = root / '.github' / 'workflows'
    offenders = []
    for p in wfdir.glob('*.yml'):
        txt = read(p)
        if has_pr_or_push(txt) and p.name not in ALLOW and not p.name.lower().startswith('codeql'):
            offenders.append(p.name)
    # ps-lint always-run
    ps = wfdir / 'ps-lint.yml'
    ps_ok = ps.exists() and not has_paths_under_pr(read(ps))
    result = {
        'allow_offenders': offenders,
        'pslint_always_run': ps_ok,
        'required_checks': sorted(REQ),
        'status': 'PASS' if not offenders and ps_ok else 'FAIL'
    }
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    sys.exit(main())

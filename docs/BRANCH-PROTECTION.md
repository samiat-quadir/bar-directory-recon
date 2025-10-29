# Branch protection for `main`

Enable in **Settings → Branches → Branch protection rules**:

1. Require a pull request before merging
2. Require branches to be up to date before merging
3. Required status checks (search after they run once):
   - ci-fast-parity / fast-tests (ubuntu-latest)
   - ci-fast-parity / fast-tests (windows-latest)
   - lock-drift-check / check
   - Security Audit (pip-audit) / audit
   - (later) CodeQL / Analyze (after a green week)

Notes:

- Checks only appear after at least one run in the last week.
- Our installs use a hash-locked requirements-lock.txt, then editable --no-deps.
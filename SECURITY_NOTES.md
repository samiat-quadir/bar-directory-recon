# Security & dependencies

We use a **constraints → lock** flow:

1. `constraints/YYYY-MM-DD.txt` pins minimum safe versions for top offenders.
2. `requirements.in` references the constraints and `.[dev]`.
3. `requirements-lock.txt` is generated with **hashes** via:
   ```
   pip-compile requirements.in --generate-hashes --output-file requirements-lock.txt
   ```
4. CI installs **from the lock** when present; otherwise falls back to the editable install.
5. `pip-audit` audits the **lock** on PRs to catch new advisories.

**Refresh cadence**
- Update the dated constraints file; then re-run `pip-compile` to refresh the lock.
- Commit both the updated constraints and the regenerated lock.

# Release Playbook (bar-directory-recon)

This one-pager captures the manual-yet-repeatable process we follow for 0.1.x GA releases. The themes are: keep changes small, rely on observable automation, and never skip validation steps.

## 1. Preparation

1. Ensure `main` is green with all required GitHub checks passing.
2. Confirm adapter safe-mode flags and `--no-exec` wiring are still honored in the CLI.
3. Decide on the next semantic version (e.g., 0.1.1) and pre-stage updates for `CHANGELOG.md` and README badges.
4. Clear any open release-blocking issues (security, licensing, or telemetry regressions) before proceeding.

## 2. Parity & packaging checks

1. Run the **release-qa-parity** workflow; wait for the README parity badge to show **PASS** for the target version.
2. Run the **pack-smoke** packaging dry-run workflow on both Ubuntu and Windows runners.
3. In fresh virtual environments on Windows and Linux, install from the artifacts produced by pack-smoke and run:
   - `bdr --version`
   - `bdr doctor --no-exec`
4. Capture screenshots or logs from these runs so the history is auditable.

## 3. TestPyPI validation (if applicable)

1. Use the `publish-testpypi` workflow with a release-candidate tag such as `0.1.1rc1`.
2. In a clean venv, install from TestPyPI using `pip install --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple bar-directory-recon==0.1.1rc1`.
3. Verify `bdr --version` and `bdr doctor --no-exec` on Windows and Linux hosts.
4. Log the results (screenshots or terminal captures) so we can prove RC validation happened.

## 4. PyPI GA publish

1. Confirm **48 hours of uninterrupted green signals** for the six required checks (release-qa-parity, pack-smoke ubuntu, pack-smoke windows, pytest, mypy, flake8).
2. Trigger the manual `publish-pypi` workflow with `skip_existing=true` and the GA version number.
3. After the workflow completes, install from PyPI on Windows and Linux fresh venvs and run:
   - `bdr --version`
   - `bdr doctor --no-exec`
4. Announce the release internally (Teams/Slack) with links to the workflow runs and validation logs.

## 5. Post-release

1. Tag the version in git (`git tag v0.1.1 && git push origin v0.1.1`).
2. Update `CHANGELOG.md`, README badges, and any dashboards to reflect the new GA version.
3. Close or update tracking issues linked to the release, including feature toggles that can return to normal defaults.
4. Archive validation evidence (logs, screenshots) under `docs/phase_logs/` for traceability.

## 6. Rollback (if something goes wrong)

1. Open a "Release X.Y.Z incident" issue and mark the GA release as at-risk; freeze new merges to `main`.
2. Identify the fix strategy:
   - Cut a hotfix version (X.Y.Z+1) that reverts the offending change, **or**
   - Flip safe-mode flags to disable the impacted adapters/features.
3. Run the same steps as above (parity → pack-smoke → TestPyPI if needed → publish-pypi) for the hotfix.
4. Communicate the rollback/hotfix in README/CHANGELOG and in the release announcement channel.
5. Close the incident issue only after the hotfix is validated and telemetry confirms stability.

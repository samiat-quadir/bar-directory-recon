@echo off
REM ============================================================
REM  git_cleanup.bat
REM  Run this from the repo root in a terminal where VS Code's
REM  git integration is NOT holding the index.
REM  Recommended: close VS Code Source Control panel first,
REM  or run from a standalone Command Prompt / PowerShell.
REM ============================================================

echo === Untracking sensitive files ===
git rm --cached client_secret_1020100796152-n6l4bloev9ha8to4mcbc6h3p8e1n1t3e.apps.googleusercontent.com.json
git rm --cached authorized_keys.seed
git rm --cached archive/ssh/ssh_authorized_keys.txt 2>NUL

echo === Untracking committed diagnostic files ===
git rm --cached pip_freeze.txt rogue_pip_freeze.txt onedrive_check.txt 2>NUL
git rm --cached venv_tree_formatted.txt venv_tree_overview.txt venv_tree_structure.txt 2>NUL
git rm --cached git_log.txt 2>NUL

echo === Staging all the archived/moved/new files ===
git add -A

echo === Committing cleanup ===
git commit -m "chore: archive root clutter, fix gitignore, add CLAUDE.md

- Move 100+ phase reports, Alienware/ASUS/SSH diagnostics, and one-off
  scripts to archive/ — actual code in src/ and universal_recon/ unchanged
- Untrack OAuth client secret and SSH authorized_keys (gitignored now)
- Add client_secret*.json, service_account*.json, token.json to .gitignore
- Rename src/webdriver_manager.py -> src/driver_setup.py (shim left in place)
- Remove src/hallandale_pipeline_fixed.py (superseded by hallandale_pipeline.py)
- Fix config/device_profile.json python_path: Python313 -> Python311
- Fix requirements-dev.txt: remove duplicate watchdog/watchfiles lines
- Add CLAUDE.md with entry points, architecture notes, and setup guide

NOTE: OAuth client secret is still in git HISTORY — rotate it at
      console.cloud.google.com before any production use."

echo.
echo ================================================================
echo  IMPORTANT: The OAuth client secret is still in git history.
echo  Rotate it at console.cloud.google.com, then optionally run:
echo    pip install git-filter-repo
echo    git filter-repo --path client_secret_*.json --invert-paths
echo  ...and force-push (coordinate with any collaborators first).
echo ================================================================

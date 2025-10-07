# Oct-8 Guard Flip Runbook

## Goal
Promote **workflow-guard** as a required check (4th) alongside the existing three.

## Preconditions
- Guard stable on main.
- artifacts/branch_protection_oct8.json lists four contexts:
  - audit
  - fast-tests (ubuntu-latest)
  - fast-tests (windows-latest)
  - workflow-guard

## Steps (EOD ET, Oct-8)
1. Inspect latest check names:
   pwsh -NoProfile -File .\scripts\preview-check-names.ps1

2. Preview payload and execute flip:
   pwsh -NoProfile -File .\scripts\flip-guard-required.ps1 -Execute

3. Verify branch protection shows **4** required checks; open a tiny smoke PR to confirm.

## Rollback
Recreate JSON without workflow-guard and re-run the same gh api PUT.
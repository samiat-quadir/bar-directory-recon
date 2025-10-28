# PS-Lint Promotion Runbook (Oct 23+)

## Overview
On Oct 23+ after burn-in period, decide whether to promote ps-lint to required checks or defer.

## Prerequisites
- Guard verifier passes (includes early-exit assertion)
- Promotion kit artifacts exist (see rtifacts/pslint/)
- Review 7-day failure rate via scripts/pslint_promotion_preview.ps1

## Decision Paths

### Option A: Promote (0 failures in last 7 days)
1. Run decision script in execute mode:
   `powershell
   scripts/pslint_promotion_decide.ps1 -Execute
   `
2. Script will:
   - Update branch protection (4→6 required checks)
   - Create smoke PRs to verify new checks
   - Create confirmation issue
3. Monitor smoke PRs for pass/fail
4. If smoke PRs pass, merge them (confirms promotion successful)

### Option B: Defer (failures detected)
1. Run decision script in preview mode:
   `powershell
   scripts/pslint_promotion_decide.ps1
   `
2. Script will:
   - Show failure summary
   - Auto-create "Extend ps-lint burn-in" issue
   - Recommend fix timeline
3. Fix failing tests, then re-run preview after fixes merged

### Option C: Rollback (emergency)
If promotion causes issues:
1. Restore previous branch protection:
   `powershell
   gh api -X PUT repos/samiat-quadir/bar-directory-recon/branches/main/protection 
     --input artifacts/pslint/branch_protection_before.json
   `
2. Create rollback issue explaining reason
3. Schedule retry for later date

## Artifacts Reference
- rtifacts/pslint/branch_protection_before.json - Pre-promotion snapshot
- rtifacts/pslint/branch_protection_preview.json - Proposed state (4→6 checks)
- scripts/pslint_promotion_preview.ps1 - Failure rate + preview only
- scripts/pslint_promotion_decide.ps1 - Promote/defer decision logic

## Links
- [CI Changelog](CI_CHANGELOG.md) - History of CI changes
- [Branch Protection](BRANCH-PROTECTION.md) - Current policy
- [Security Notes](../SECURITY_NOTES.md) - Security-related links

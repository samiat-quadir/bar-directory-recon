# Guard Hardening + Reminder + Runbook (Oct 20, 2025)
# Adds ps-lint early-exit assertion, schedule-only reminder workflow, promotion runbook
# No branch protection change

param()

$ErrorActionPreference = "Stop"

# ──────────────────────────────────────────────────────────────────────────────
# 1. Harden guard to require ps-lint early-exit pattern
# ──────────────────────────────────────────────────────────────────────────────

$guardPath = "scripts\check_guard_integrity.py"

if (-not (Test-Path $guardPath)) {
    throw "Missing $guardPath (ensure prior guard verifier exists)"
}

$guardContent = Get-Content $guardPath -Raw -Encoding UTF8

# Check if already has early-exit function
if ($guardContent -notmatch "def has_pslint_early_exit") {
    Write-Host "[GUARD] Adding has_pslint_early_exit() function..."
    
    # Read lines
    $lines = Get-Content $guardPath -Encoding UTF8
    $newLines = @()
    $insertedFunction = $false
    
    foreach ($line in $lines) {
        # Insert new function before main()
        if (-not $insertedFunction -and $line -match "^def main") {
            # Add new function
            $newLines += ""
            $newLines += "def has_pslint_early_exit(yml_path):"
            $newLines += '    """Check if ps-lint has early-exit pattern (id: changed + gated PSScriptAnalyzer)."""'
            $newLines += "    content = yml_path.read_text(encoding='utf-8')"
            $newLines += "    # Look for id: changed step followed by PSScriptAnalyzer gated on changed"
            $newLines += "    has_changed_id = bool(re.search(r'id:\s*changed', content))"
            $newLines += "    has_gated_pslint = bool(re.search(r'if:\s+steps\.changed\.outputs\.\w+.*PSScriptAnalyzer', content, re.DOTALL))"
            $newLines += "    return has_changed_id and has_gated_pslint"
            $newLines += ""
            $insertedFunction = $true
        }
        
        $newLines += $line
    }
    
    # Write back
    $newLines | Set-Content $guardPath -Encoding UTF8
    Write-Host "[GUARD] Added has_pslint_early_exit() function"
}

# Now inject pslint_early_exit field into result dict
if ($guardContent -notmatch "pslint_early_exit") {
    Write-Host "[GUARD] Adding pslint_early_exit to result dict..."
    
    $lines = Get-Content $guardPath -Encoding UTF8
    $newLines = @()
    
    foreach ($line in $lines) {
        $newLines += $line
        
        # After pslint_names_ok line, add early_exit check
        if ($line -match '"pslint_names_ok":\s*pslint_names_ok') {
            $newLines += "        `"pslint_early_exit`": has_pslint_early_exit(wf_ps_lint),"
        }
        
        # Update PASS condition to require early_exit
        if ($line -match 'status = "PASS" if') {
            # Replace entire condition
            $newLines[-1] = '    status = "PASS" if (not allow_offenders and pslint_always_run and pslint_names_ok and result["pslint_early_exit"]) else "FAIL"'
        }
    }
    
    $newLines | Set-Content $guardPath -Encoding UTF8
    Write-Host "[GUARD] Added pslint_early_exit field and updated PASS condition"
}

Write-Host "`n[GUARD] Hardening complete - now requires ps-lint early-exit pattern`n"

# ──────────────────────────────────────────────────────────────────────────────
# 2. Create schedule-only reminder workflow (exits before Oct 23)
# ──────────────────────────────────────────────────────────────────────────────

$reminderWorkflow = @"
# Schedule-only reminder to ensure ps-lint promotion happens after Oct 23
# This workflow does NOT run on PRs
# Exits early if before Oct 23 cutoff
# Creates/updates reminder issue if ps-lint contexts missing from branch protection

name: ps-lint promotion reminder (schedule-only)

on:
  schedule:
    - cron: '10 13 * * *'  # 09:10 ET daily
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  remind:
    runs-on: ubuntu-latest
    if: github.event_name == 'workflow_dispatch' || github.event_name == 'schedule'
    steps:
      - name: Check if before Oct 23 cutoff
        id: cutoff
        run: |
          # Cutoff: 2025-10-23T13:10:00Z (09:10 ET)
          cutoff=`$(date -d "2025-10-23 13:10:00 UTC" +%s)
          now=`$(date +%s)
          if [ `$now -lt `$cutoff ]; then
            echo "Before Oct 23 cutoff, exiting early"
            echo "skip=true" >> `$GITHUB_OUTPUT
          else
            echo "After Oct 23 cutoff, checking branch protection"
            echo "skip=false" >> `$GITHUB_OUTPUT
          fi

      - name: Get branch protection
        if: steps.cutoff.outputs.skip == 'false'
        id: bp
        run: |
          gh api repos/`${{ github.repository }}/branches/main/protection --jq '.required_status_checks.contexts[]' > contexts.txt || true
          if grep -q 'ps-lint.*ubuntu' contexts.txt && grep -q 'ps-lint.*windows' contexts.txt; then
            echo "ps-lint contexts present, no reminder needed"
            echo "missing=false" >> `$GITHUB_OUTPUT
          else
            echo "ps-lint contexts missing, creating reminder"
            echo "missing=true" >> `$GITHUB_OUTPUT
          fi
        env:
          GH_TOKEN: `${{ secrets.GITHUB_TOKEN }}

      - name: Create or update reminder issue
        if: steps.cutoff.outputs.skip == 'false' && steps.bp.outputs.missing == 'true'
        run: |
          gh issue list --label "reminder" --search "Reminder: ps-lint promotion pending" --json number,state --jq '.[0].number' > issue.txt
          if [ -s issue.txt ]; then
            issue_num=`$(cat issue.txt)
            gh issue comment `$issue_num --body "⏰ Reminder: ps-lint promotion still pending. Run \`scripts/pslint_promotion_decide.ps1 -Execute\` to promote."
          else
            gh issue create --title "Reminder: ps-lint promotion pending" --label "reminder" --body "⏰ ps-lint contexts not yet in branch protection. Run \`scripts/pslint_promotion_decide.ps1 -Execute\` to promote."
          fi
        env:
          GH_TOKEN: `${{ secrets.GITHUB_TOKEN }}
"@

$reminderPath = ".github\workflows\pslint-promo-reminder.yml"
$reminderWorkflow | Set-Content $reminderPath -Encoding UTF8
Write-Host "[REMINDER] Created $reminderPath (schedule-only, exits before Oct 23)`n"

# ──────────────────────────────────────────────────────────────────────────────
# 3. Create promotion runbook in docs/
# ──────────────────────────────────────────────────────────────────────────────

$runbook = @"
# PS-Lint Promotion Runbook (Oct 23+)

## Overview
On Oct 23+ after burn-in period, decide whether to promote ps-lint to required checks or defer.

## Prerequisites
- Guard verifier passes (includes early-exit assertion)
- Promotion kit artifacts exist (see `artifacts/pslint/`)
- Review 7-day failure rate via `scripts/pslint_promotion_preview.ps1`

## Decision Paths

### Option A: Promote (0 failures in last 7 days)
1. Run decision script in execute mode:
   ```powershell
   scripts/pslint_promotion_decide.ps1 -Execute
   ```
2. Script will:
   - Update branch protection (4→6 required checks)
   - Create smoke PRs to verify new checks
   - Create confirmation issue
3. Monitor smoke PRs for pass/fail
4. If smoke PRs pass, merge them (confirms promotion successful)

### Option B: Defer (failures detected)
1. Run decision script in preview mode:
   ```powershell
   scripts/pslint_promotion_decide.ps1
   ```
2. Script will:
   - Show failure summary
   - Auto-create "Extend ps-lint burn-in" issue
   - Recommend fix timeline
3. Fix failing tests, then re-run preview after fixes merged

### Option C: Rollback (emergency)
If promotion causes issues:
1. Restore previous branch protection:
   ```powershell
   gh api -X PUT repos/samiat-quadir/bar-directory-recon/branches/main/protection `
     --input artifacts/pslint/branch_protection_before.json
   ```
2. Create rollback issue explaining reason
3. Schedule retry for later date

## Artifacts Reference
- `artifacts/pslint/branch_protection_before.json` - Pre-promotion snapshot
- `artifacts/pslint/branch_protection_preview.json` - Proposed state (4→6 checks)
- `scripts/pslint_promotion_preview.ps1` - Failure rate + preview only
- `scripts/pslint_promotion_decide.ps1` - Promote/defer decision logic

## Links
- [CI Changelog](CI_CHANGELOG.md) - History of CI changes
- [Branch Protection](BRANCH-PROTECTION.md) - Current policy
- [Security Notes](../SECURITY_NOTES.md) - Security-related links
"@

$runbookPath = "docs\PROMOTION_RUNBOOK.md"
$runbook | Set-Content $runbookPath -Encoding UTF8
Write-Host "[RUNBOOK] Created $runbookPath`n"

# ──────────────────────────────────────────────────────────────────────────────
# 4. Update SECURITY_NOTES.md with runbook link
# ──────────────────────────────────────────────────────────────────────────────

$secNotesPath = "SECURITY_NOTES.md"

if (-not (Test-Path $secNotesPath)) {
    # Create new file with runbook link
    $secNotes = @"
# Security Notes

## CI/CD Security
- [Promotion Runbook](docs/PROMOTION_RUNBOOK.md) - PS-lint promotion decision guide
"@
    $secNotes | Set-Content $secNotesPath -Encoding UTF8
    Write-Host "[SECURITY_NOTES] Created $secNotesPath with runbook link`n"
} else {
    # Append runbook link if not present
    $content = Get-Content $secNotesPath -Raw -Encoding UTF8
    if ($content -notmatch "PROMOTION_RUNBOOK") {
        $content += "`n- [Promotion Runbook](docs/PROMOTION_RUNBOOK.md) - PS-lint promotion decision guide`n"
        $content | Set-Content $secNotesPath -Encoding UTF8 -NoNewline
        Write-Host "[SECURITY_NOTES] Updated $secNotesPath with runbook link`n"
    } else {
        Write-Host "[SECURITY_NOTES] Already has runbook link, skipping`n"
    }
}

Write-Host "✅ Guard hardening + reminder + runbook complete!"
Write-Host "   Modified: $guardPath, $reminderPath, $runbookPath, $secNotesPath"

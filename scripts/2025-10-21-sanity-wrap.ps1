# file: scripts/2025-10-21-sanity-wrap.ps1# file: scripts/2025-10-21-sanity-wrap.ps1

Set-StrictMode -Version Latest; $ErrorActionPreference='Stop'Set-StrictMode -Version Latest; $ErrorActionPreference='Stop'

function Say($m){ Write-Host "==> $m" }function Say($m){ Write-Host "==> $m" }



cd C:\Code\bar-directory-reconcd C:\Code\bar-directory-recon

git fetch origin --prune *> $nullgit fetch origin --prune *> $null

git checkout -q maingit checkout -q main

git reset --hard refs/remotes/origin/main  # Use explicit ref to avoid ambiguitygit reset --hard refs/remotes/origin/main  # Use explicit ref to avoid ambiguity

git clean -xdf -qgit clean -xdf -q



# 1) Confirm PR #280 landed (optional; non-fatal)# 1) Confirm PR #280 landed (optional; non-fatal)

try {try {

  $pr = gh pr view 280 --json state,mergedAt | ConvertFrom-Json  $pr = gh pr view 280 --json state,mergedAt | ConvertFrom-Json

  if ($pr -and $pr.state -eq 'MERGED') { Say "PR #280 merged at $($pr.mergedAt)" } else { Say "PR #280 not merged yet (auto-merge queued)" }  if ($pr -and $pr.state -eq 'MERGED') { Say "PR #280 merged at $($pr.mergedAt)" } else { Say "PR #280 not merged yet (auto-merge queued)" }

} catch { Say "Skipping PR #280 check: $($_.Exception.Message)" }} catch { Say "Skipping PR #280 check: $($_.Exception.Message)" }



# 2) Refresh ps-lint preview counters (artifact-only)# 2) Refresh ps-lint preview counters (artifact-only)

try { try { 

  if (Test-Path scripts\pslint_promotion_preview.ps1) {  if (Test-Path scripts\pslint_promotion_preview.ps1) {

    pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\pslint_promotion_preview.ps1    pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\pslint_promotion_preview.ps1

    Say "Preview counters refreshed"    Say "Preview counters refreshed"

  } else {  } else {

    Say "Preview script not found (expected after PR #279 merge)"    Say "Preview script not found (expected after PR #279 merge)"

  }  }

} catch { Say "Preview script skipped: $($_.Exception.Message)" }} catch { Say "Preview script skipped: $($_.Exception.Message)" }



# 3) Best-effort: dispatch Insights to capture current state# 3) Best-effort: dispatch Insights to capture current state

try { gh workflow run ci-insights-weekly --ref main *> $null; Say "Insights dispatched" } catch { Say "Insights dispatch skipped" }try { gh workflow run ci-insights-weekly --ref main *> $null; Say "Insights dispatched" } catch { Say "Insights dispatch skipped" }



Write-Host "RELAY >> task=oct21_wrap status=ok note=""PR280 check done; preview refreshed; insights dispatched"""Write-Host "RELAY >> task=oct21_wrap status=ok note=""PR280 check done; preview refreshed; insights dispatched"""


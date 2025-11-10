# File: scripts/ops_plan_preview.ps1
# Purpose: Read-only readiness preview for Nov-6 GA gate (no dispatch, no writes).
# Usage:   pwsh -File scripts/ops_plan_preview.ps1

param()

# --- Config ---
$Repo       = "samiat-quadir/bar-directory-recon"
$LocalPath  = "C:\Code\bar-directory-recon"
$PublishWf  = ".github/workflows/publish-pypi.yml"
$InsightsWf = ".github/workflows/insights-testpypi-line.yml"
$RequiredChecks = @(
  "audit",
  "fast-tests (ubuntu-latest)",
  "fast-tests (windows-latest)",
  "workflow-guard",
  "ps-lint (ubuntu-latest)",
  "ps-lint (windows-latest)"
)

function Out-Result { param([int]$Step,[string]$Status,[string]$Link,[string]$Note)
  $n = ($Note -replace "\r?\n"," ").Trim(); Write-Output ("RESULT >> step={0} status={1} link={2} note=""{3}""" -f $Step,$Status,($Link ?? ""),$n)
}
function Die { param([int]$Step,[string]$Note,[string]$Link=""); Out-Result $Step "fail" $Link $Note; Write-Output ('RELAY >> task=plan_preview status=degraded checks=0 guard=PASS note="{0}"' -f $Note); exit 1 }

# Step 1: Preconditions
$step=1
try {
  & gh --version *> $null; if($LASTEXITCODE){ Die $step "gh missing" }
  if(-not (Test-Path -LiteralPath $LocalPath)){ Die $step "repo path missing: $LocalPath" }
  Set-Location -LiteralPath $LocalPath
  $env:GH_REPO = $Repo
  Out-Result $step "ok" "https://github.com/$Repo" "env ready; read-only preview"
} catch { Die $step ("precheck error: {0}" -f $_.Exception.Message) }

# Step 2: publish-pypi workflow presence (manual-only target; we won't create/run it here)
$step=2
try {
  $exists = Test-Path -LiteralPath (Join-Path $LocalPath $PublishWf)
  $status = if($exists){"ok"}else{"fail"}
  $note = if($exists){"publish-pypi.yml present (manual-only expected)"}else{"missing publish-pypi.yml (manual-only)"}  # why: gate requires manual GA publish only
  Out-Result $step $status "https://github.com/$Repo/tree/main/.github/workflows" $note
} catch { Die $step ("wf check error: {0}" -f $_.Exception.Message) }

# Step 3: insights workflow presence (signals to be added separately)
$step=3
try {
  $exists = Test-Path -LiteralPath (Join-Path $LocalPath $InsightsWf)
  $status = if($exists){"ok"}else{"fail"}
  $note = if($exists){"insights-testpypi-line.yml present; add 2 signals next"}else{"missing insights-testpypi-line.yml"}
  Out-Result $step $status "https://github.com/$Repo/tree/main/.github/workflows" $note
} catch { Die $step ("insights wf check error: {0}" -f $_.Exception.Message) }

# Step 4: PYPI_API_TOKEN secret presence
$step=4
try {
  $sec = & gh api -H "Accept: application/vnd.github+json" "repos/$Repo/actions/secrets"
  if($LASTEXITCODE -ne 0 -or -not $sec){ Die $step "cannot query repo secrets" }
  $names = ( ($sec | ConvertFrom-Json).secrets | ForEach-Object { $_.name } )
  $has = $names -contains "PYPI_API_TOKEN"
  $status = if($has){"ok"}else{"fail"}
  $note = if($has){"PYPI_API_TOKEN present"}else{"PYPI_API_TOKEN missing (prod PyPI)"}
  Out-Result $step $status "https://github.com/$Repo/settings/secrets/actions" $note
} catch { Die $step ("secrets error: {0}" -f $_.Exception.Message) }

# Step 5: Latest parity run status (read-only)
$step=5
try {
  $run = & gh run list --workflow "release-qa-parity.yml" --limit 1 --json status,conclusion,url,displayTitle,createdAt | ConvertFrom-Json
  if(-not $run){ Die $step "no parity runs found" }
  $r = $run[0]
  $note = "parity=$($r.conclusion); created=$($r.createdAt)"
  $status = if($r.conclusion -eq "success"){"ok"}else{"fail"}
  Out-Result $step $status $r.url $note
} catch { Die $step ("parity read error: {0}" -f $_.Exception.Message) }

# Step 6: Required checks on main (read-only)
$step=6
try {
  $cmt = & gh api "repos/$Repo/commits/main" | ConvertFrom-Json
  $sha = $cmt.sha
  $cr  = (& gh api "repos/$Repo/commits/$sha/check-runs" | ConvertFrom-Json).check_runs
  $missing = @(); $bad=@()
  foreach($n in $RequiredChecks){
    $m = $cr | Where-Object name -eq $n | Select-Object -First 1
    if(-not $m){ $missing += $n; continue }
    if($m.status -ne "completed" -or $m.conclusion -ne "success"){ $bad += "$n=($($m.status)/$($m.conclusion))" }
  }
  if($missing.Count -or $bad.Count){
    $msg = @()
    if($missing.Count){ $msg += "missing: $($missing -join ', ')" }
    if($bad.Count){ $msg += "failing: $($bad -join ', ')" }
    Out-Result $step "fail" "https://github.com/$Repo/commit/$sha/checks" ($msg -join " | ")
  } else {
    Out-Result $step "ok" "https://github.com/$Repo/commit/$sha/checks" "all six required checks green"
  }
} catch { Die $step ("checks read error: {0}" -f $_.Exception.Message) }

# Step 7: Nov-6 decision rule (advice only; no action)
$step=7
$rule = "Nov-6 09:30 ET: if parity+six checks+win smoke green => run manual publish; else defer & comment PR#312"
Out-Result $step "ok" "https://github.com/$Repo/pull/312" $rule

# Relay summary
Write-Output 'RELAY >> task=plan_preview status=ok checks=6 guard=PASS note="prep manual publish; add insights signals; Nov-6 publish-if-green"'


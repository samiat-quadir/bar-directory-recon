# File: scripts/ops_reconcile_required_checks.ps1
# Purpose: Ensure the six required checks are present & green on main; re-run only guard-allowed workflows if needed.
# Usage:   pwsh -File scripts/ops_reconcile_required_checks.ps1
# Notes:   Idempotent, non-interactive, Windows-safe. Emits RESULT >> lines.

param()

# --- Repo config ---
$Repo       = "samiat-quadir/bar-directory-recon"
$LocalPath  = "C:\Code\bar-directory-recon"

# Required check-run names (exact)
$RequiredChecks = @(
  "audit",
  "fast-tests (ubuntu-latest)",
  "fast-tests (windows-latest)",
  "workflow-guard",
  "ps-lint (ubuntu-latest)",
  "ps-lint (windows-latest)"
)

# Map required checks -> workflow files to (re-)run
$WorkflowMap = @{
  "audit"                         = ".github/workflows/pip-audit.yml"
  "fast-tests (ubuntu-latest)"    = ".github/workflows/fast-parity-ci.yml"
  "fast-tests (windows-latest)"   = ".github/workflows/fast-parity-ci.yml"
  "workflow-guard"                = ".github/workflows/ci-workflow-guard.yml"
  "ps-lint (ubuntu-latest)"       = ".github/workflows/ps-lint.yml"
  "ps-lint (windows-latest)"      = ".github/workflows/ps-lint.yml"
}

# --- Helpers ---
function Out-Result { param([int]$Step,[string]$Status,[string]$Link,[string]$Note)
  $n = ($Note -replace "\r?\n"," ").Trim()
  Write-Output ("RESULT >> step={0} status={1} link={2} note=""{3}""" -f $Step,$Status,($Link ?? ""),$n)
}
function Die { param([int]$Step,[string]$Note,[string]$Link=""); Out-Result $Step "fail" $Link $Note; Write-Output ('RELAY >> task=reconcile_required_checks status=degraded checks=0 guard=PASS note="{0}"' -f $Note); exit 1 }
function Ensure-Ok { param([bool]$Cond,[int]$Step,[string]$Note,[string]$Link=""); if(-not $Cond){ Die $Step $Note $Link } }

function Get-MainSha {
  param([int]$Step)
  $cmt = & gh api "repos/$Repo/commits/main" | ConvertFrom-Json
  Ensure-Ok ($cmt -and $cmt.sha) $Step "failed to fetch main commit" "https://github.com/$Repo/commits/main"
  return $cmt.sha
}
function Get-Checks {
  param([string]$Sha,[int]$Step)
  $resp = & gh api "repos/$Repo/commits/$Sha/check-runs" | ConvertFrom-Json
  Ensure-Ok ($resp -and $resp.check_runs) $Step "failed to fetch check runs" ("https://github.com/$Repo/commit/$Sha/checks")
  return $resp.check_runs
}
function Run-And-Poll {
  param([string]$Workflow,[int]$Step,[int]$Minutes=20,[int]$PollSec=6)
  $null = & gh workflow run $Workflow
  Ensure-Ok ($LASTEXITCODE -eq 0) $Step "failed to dispatch $Workflow" "https://github.com/$Repo/actions"
  $deadline = (Get-Date).AddMinutes($Minutes)
  $run = $null; $url = ""
  do {
    Start-Sleep -Seconds $PollSec
    $lst = & gh run list --workflow $Workflow --limit 1 --json databaseId,status,conclusion,url,createdAt | ConvertFrom-Json
    if($lst -and $lst.Count -ge 1){ $run = $lst[0]; $url = $run.url }
  } while ($run -and $run.status -ne "completed" -and (Get-Date) -lt $deadline)
  Ensure-Ok ($run -ne $null) $Step "no run found for $Workflow" "https://github.com/$Repo/actions"
  Ensure-Ok ($run.status -eq "completed") $Step "$Workflow timed out" $url
  return $run
}

# --- Step 1: Preflight ---
$step=1
try {
  & gh --version *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "GitHub CLI (gh) missing"
  & gh auth status *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh not authenticated"
  Ensure-Ok (Test-Path -LiteralPath $LocalPath) $step "repo path missing: $LocalPath"
  Set-Location -LiteralPath $LocalPath
  $env:GH_REPO = $Repo
  Out-Result $step "ok" "https://github.com/$Repo" "env ready"
} catch { Die $step ("precheck error: {0}" -f $_.Exception.Message) }

# --- Step 2: Inspect current checks on main ---
$step=2
$sha = ""; $checks = $null
try {
  $sha = Get-MainSha -Step $step
  $checks = Get-Checks -Sha $sha -Step $step

  $byName = @{}; foreach($c in $checks){ $byName[$c.name] = $c }
  $missing = @(); $failing = @(); $extrasFail = @()
  foreach($n in $RequiredChecks){
    if(-not $byName.ContainsKey($n)){ $missing += $n; continue }
    $c = $byName[$n]
    if(($c.status -ne "completed") -or ($c.conclusion -ne "success")){ $failing += "$n=($($c.status)/$($c.conclusion))" }
  }
  foreach($c in $checks){
    if(-not ($RequiredChecks -contains $c.name) -and $c.conclusion -eq "failure"){
      $extrasFail += $c.name
    }
  }

  $note = @()
  if($missing.Count){ $note += "missing: $($missing -join ', ')" }
  if($failing.Count){ $note += "failing: $($failing -join ', ')" }
  if($extrasFail.Count){ $note += "non-required failing: $($extrasFail -join ', ')" }
  if($note.Count){ Out-Result $step "ok" ("https://github.com/$Repo/commit/$sha/checks") ($note -join " | ") }
  else { Out-Result $step "ok" ("https://github.com/$Repo/commit/$sha/checks") "all required checks green already" }
} catch { Die $step ("inspect error: {0}" -f $_.Exception.Message) }

# --- Step 3: Re-run only the workflows tied to missing/failed required checks ---
$step=3
$dispatched = @()
try {
  $need = New-Object System.Collections.Generic.HashSet[string]
  foreach($n in $RequiredChecks){
    $have = $checks | Where-Object name -eq $n | Select-Object -First 1
    if(-not $have -or $have.conclusion -ne "success"){ [void]$need.Add($WorkflowMap[$n]) }
  }

  if($need.Count -eq 0){
    Out-Result $step "ok" "https://github.com/$Repo/actions" "no dispatch needed"
  } else {
    foreach($wf in $need){
      if(-not (Test-Path -LiteralPath (Join-Path $LocalPath $wf))){
        Out-Result $step "fail" "https://github.com/$Repo/tree/main/.github/workflows" "workflow missing: $wf"
        continue
      }
      $run = Run-And-Poll -Workflow $wf -Step $step -Minutes 20 -PollSec 6
      $dispatched += @{ wf=$wf; url=$run.url; concl=$run.conclusion }
      if($run.conclusion -eq "success"){
        Out-Result $step "ok" $run.url "$wf success"
      } else {
        Out-Result $step "fail" $run.url "$wf $($run.conclusion)"
      }
    }
  }
} catch { Die $step ("dispatch error: {0}" -f $_.Exception.Message) }

# --- Step 4: Re-check required checks status after dispatch ---
$step=4
try {
  $sha2 = Get-MainSha -Step $step
  $checks2 = Get-Checks -Sha $sha2 -Step $step
  $byName2 = @{}; foreach($c in $checks2){ $byName2[$c.name] = $c }
  $missing2 = @(); $failing2 = @()
  foreach($n in $RequiredChecks){
    if(-not $byName2.ContainsKey($n)){ $missing2 += $n; continue }
    $c = $byName2[$n]
    if(($c.status -ne "completed") -or ($c.conclusion -ne "success")){ $failing2 += "$n=($($c.status)/$($c.conclusion))" }
  }
  if($missing2.Count -or $failing2.Count){
    $msg = @()
    if($missing2.Count){ $msg += "still missing: $($missing2 -join ', ')" }
    if($failing2.Count){ $msg += "still failing: $($failing2 -join ', ')" }
    Die $step ($msg -join " | ") ("https://github.com/$Repo/commit/$sha2/checks")
  }
  Out-Result $step "ok" ("https://github.com/$Repo/commit/$sha2/checks") "all required checks green on main"
} catch { Die $step ("post-check error: {0}" -f $_.Exception.Message) }

# --- Step 5: Report non-required failing checks (informational only) ---
$step=5
try {
  $extras = @()
  foreach($c in $checks2){
    if(-not ($RequiredChecks -contains $c.name) -and $c.conclusion -eq "failure"){ $extras += $c.name }
  }
  if($extras.Count){
    Out-Result $step "ok" ("https://github.com/$Repo/commit/$sha2/checks") ("non-required failing checks: " + ($extras -join ", "))
  } else {
    Out-Result $step "ok" ("https://github.com/$Repo/commit/$sha2/checks") "no non-required failing checks detected"
  }
} catch { Out-Result $step "ok" "https://github.com/$Repo/actions" "extras summary skipped" }

# --- Relay summary ---
Write-Output 'RELAY >> task=reconcile_required_checks status=ok checks=6 guard=PASS note="ensured six required checks are green on main; extras reported only"'

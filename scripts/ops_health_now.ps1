# File: scripts/ops_health_now.ps1
# Purpose: Run an immediate health check: parity on tag + ensure six required checks are green on main.
# Usage:   pwsh -File scripts/ops_health_now.ps1 [-Tag v0.1.1]
# Notes:   Idempotent. Windows-safe. Uses only guard-allowed workflows.

param(
  [string]$Tag = "v0.1.1"
)

# --- Repo config ---
$Repo        = "samiat-quadir/bar-directory-recon"
$LocalPath   = "C:\Code\bar-directory-recon"

# Workflows (guard-allowed)
$ParityWf    = ".github/workflows/release-qa-parity.yml"
$FastCIWf    = ".github/workflows/fast-parity-ci.yml"
$AuditWf     = ".github/workflows/pip-audit.yml"
$PsLintWf    = ".github/workflows/ps-lint.yml"
$GuardWf     = ".github/workflows/ci-workflow-guard.yml"

# Required check-run names (EXACT)
$RequiredChecks = @(
  "audit",
  "fast-tests (ubuntu-latest)",
  "fast-tests (windows-latest)",
  "workflow-guard",
  "ps-lint (ubuntu-latest)",
  "ps-lint (windows-latest)"
)

# Map required check name -> workflow file
$WorkflowMap = @{
  "audit"                         = $AuditWf
  "fast-tests (ubuntu-latest)"    = $FastCIWf
  "fast-tests (windows-latest)"   = $FastCIWf
  "workflow-guard"                = $GuardWf
  "ps-lint (ubuntu-latest)"       = $PsLintWf
  "ps-lint (windows-latest)"      = $PsLintWf
}

# --- Helpers ---
function Out-Result { param([int]$Step,[string]$Status,[string]$Link,[string]$Note)
  $n = ($Note -replace "\r?\n"," ").Trim()
  Write-Output ("RESULT >> step={0} status={1} link={2} note=""{3}""" -f $Step,$Status,($Link ?? ""),$n)
}
function Die { param([int]$Step,[string]$Note,[string]$Link=""); Out-Result $Step "fail" $Link $Note; Write-Output ('RELAY >> task=health_now status=degraded checks=0 guard=PASS note="{0}"' -f $Note); exit 1 }
function Ensure-Ok { param([bool]$Cond,[int]$Step,[string]$Msg,[string]$Link=""); if(-not $Cond){ Die $Step $Msg $Link } }

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
  param([string]$Workflow,[hashtable]$Inputs,[int]$Minutes=20,[int]$PollSec=6,[int]$Step)
  $args = @($Workflow)
  foreach($k in $Inputs.Keys){ $args += @('-f', "$k=$($Inputs[$k])") }
  $null = & gh workflow run @args
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
function Get-InputKey([string]$Yaml){
  if($Yaml -match '(?ms)workflow_dispatch:\s*inputs:.*?^\s*tag\s*:'){ return 'tag' }
  if($Yaml -match '(?ms)workflow_dispatch:\s*inputs:\s*([A-Za-z0-9_\-]+)\s*:'){ return $Matches[1] }
  return 'tag'
}

# --- Step 1: Preflight ---
$step=1
try {
  & gh --version *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "GitHub CLI (gh) missing"
  & gh auth status *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh not authenticated"
  Ensure-Ok (Test-Path -LiteralPath $LocalPath) $step "repo path missing: $LocalPath"
  Set-Location -LiteralPath $LocalPath
  $env:GH_REPO = $Repo
  foreach($wf in @($ParityWf,$FastCIWf,$AuditWf,$PsLintWf,$GuardWf)){
    Ensure-Ok (Test-Path -LiteralPath (Join-Path $LocalPath $wf)) $step "missing workflow: $wf" "https://github.com/$Repo/tree/main/.github/workflows"
  }
  Out-Result $step "ok" "https://github.com/$Repo" "env ready; workflows present"
} catch { Die $step ("precheck error: {0}" -f $_.Exception.Message) }

# --- Step 2: Parity on tag (manual) ---
$step=2
$parityUrl = ""
try {
  $wfText = Get-Content -LiteralPath (Join-Path $LocalPath $ParityWf) -Raw
  $key = Get-InputKey $wfText
  $run = Run-And-Poll -Workflow $ParityWf -Inputs @{$key=$Tag} -Minutes 15 -PollSec 5 -Step $step
  $parityUrl = $run.url
  if($run.conclusion -ne "success"){
    Out-Result $step "fail" $parityUrl ("parity {0} on {1}" -f $run.conclusion,$Tag)
    Write-Output ('RELAY >> task=health_now status=degraded checks=0 guard=PASS note="parity {0} on {1}"' -f $run.conclusion,$Tag)
    exit 2
  }
  Out-Result $step "ok" $parityUrl ("parity PASS on {0}" -f $Tag)
} catch { Die $step ("parity error: {0}" -f $_.Exception.Message) }

# --- Step 3: Inspect required checks on main ---
$step=3
$sha = ""; $checks = $null
try {
  $sha = Get-MainSha -Step $step
  $checks = Get-Checks -Sha $sha -Step $step

  $byName = @{}; foreach($c in $checks){ $byName[$c.name] = $c }
  $missing = @(); $failing = @()
  foreach($n in $RequiredChecks){
    if(-not $byName.ContainsKey($n)){ $missing += $n; continue }
    $c = $byName[$n]
    if(($c.status -ne "completed") -or ($c.conclusion -ne "success")){ $failing += "$n=($($c.status)/$($c.conclusion))" }
  }
  $msg = @()
  if($missing.Count){ $msg += "missing: $($missing -join ', ')" }
  if($failing.Count){ $msg += "failing: $($failing -join ', ')" }
  if($msg.Count){ Out-Result $step "ok" ("https://github.com/$Repo/commit/$sha/checks") ($msg -join " | ") }
  else { Out-Result $step "ok" ("https://github.com/$Repo/commit/$sha/checks") "all required checks already green" }
} catch { Die $step ("inspect error: {0}" -f $_.Exception.Message) }

# --- Step 4: Re-run only workflows for missing/failing required checks ---
$step=4
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
      $run = Run-And-Poll -Workflow $wf -Inputs @{} -Minutes 20 -PollSec 6 -Step $step
      if($run.conclusion -eq "success"){ $statusNote = "success" } else { $statusNote = $run.conclusion }
      if($run.url){ $link = $run.url } else { $link = "https://github.com/$Repo/actions" }
      Out-Result $step "ok" $link "re-ran $wf → $statusNote"
      if($run.conclusion -ne "success"){ Die $step ("$wf $($run.conclusion)") $run.url }
    }
  }
} catch { Die $step ("dispatch error: {0}" -f $_.Exception.Message) }

# --- Step 5: Final verification of required checks ---
$step=5
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
  Out-Result $step "ok" ("https://github.com/$Repo/commit/$sha2/checks") "all six required checks green on main"
} catch { Die $step ("post-check error: {0}" -f $_.Exception.Message) }

# --- Summary ---
Write-Output 'RELAY >> task=health_now status=ok checks=6 guard=PASS note="parity PASS; ensured required checks green on main"'

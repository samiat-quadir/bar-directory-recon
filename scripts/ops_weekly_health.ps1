# File: scripts/ops_weekly_health.ps1
# Purpose: Weekly health check: verify six required checks on main and optionally trigger CI.
# Usage:   pwsh -File scripts/ops_weekly_health.ps1 [-TriggerCI]
# Notes:   Idempotent, non-interactive. Emits RESULT lines per step + RELAY summary.

param(
  [switch]$TriggerCI
)

# --- Repo config ---
$Repo               = "samiat-quadir/bar-directory-recon"
$LocalPath          = "C:\Code\bar-directory-recon"
$CiWorkflowFile     = ".github/workflows/ci.yml"
$RequiredChecks = @(
  "audit",
  "fast-tests (ubuntu-latest)",
  "fast-tests (windows-latest)",
  "workflow-guard",
  "ps-lint (ubuntu-latest)",
  "ps-lint (windows-latest)"
)

# --- Helpers ---
function Out-Result { param([int]$Step,[string]$Status,[string]$Link,[string]$Note)
  $n = ($Note -replace "\r?\n"," ").Trim()
  Write-Output ("RESULT >> step={0} status={1} link={2} note=""{3}""" -f $Step,$Status,($Link ?? ""),$n)
}
function Die { param([int]$Step,[string]$Note,[string]$Link=""); Out-Result $Step "fail" $Link $Note; Write-Output ('RELAY >> task=weekly_health status=degraded checks=0 guard=PASS note="{0}"' -f $Note); exit 1 }
function Ensure-Ok { param([bool]$Cond,[int]$Step,[string]$Note,[string]$Link=""); if(-not $Cond){ Die $Step $Note $Link } }

# --- Step 1: Preconditions ---
$step = 1
try {
  & gh --version *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh missing"
  & gh auth status *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh not authenticated"
  Ensure-Ok (Test-Path -LiteralPath $LocalPath) $step "repo path missing: $LocalPath"
  Set-Location -LiteralPath $LocalPath
  $env:GH_REPO = $Repo
  Ensure-Ok (Test-Path -LiteralPath (Join-Path $LocalPath $CiWorkflowFile)) $step "CI workflow missing: $CiWorkflowFile" "https://github.com/$Repo/tree/main/.github/workflows"
  Out-Result $step "ok" "https://github.com/$Repo" "env ready; repo set; CI workflow present"
} catch { Die $step ("precheck error: {0}" -f $_.Exception.Message) }

# --- Step 2: Optionally trigger CI workflow ---
$step = 2
$ciRunUrl = ""
try {
  if ($TriggerCI) {
    $null = & gh workflow run $CiWorkflowFile
    Ensure-Ok ($LASTEXITCODE -eq 0) $step "failed to dispatch CI workflow"

    # Poll most recent run of CI workflow (15m max)
    $deadline = (Get-Date).AddMinutes(15)
    $run = $null
    do {
      Start-Sleep -Seconds 5
      $list = & gh run list --workflow $CiWorkflowFile --limit 1 --json databaseId,status,conclusion,url,createdAt | ConvertFrom-Json
      if($list -and $list.Count -ge 1){ $run = $list[0]; $ciRunUrl = $run.url }
    } while ($run -and $run.status -ne "completed" -and (Get-Date) -lt $deadline)

    Ensure-Ok ($run -ne $null) $step "no CI run found to poll"
    Ensure-Ok ($run.status -eq "completed") $step "CI workflow timed out" $ciRunUrl
    if($run.conclusion -ne "success"){
      Out-Result $step "fail" $ciRunUrl ("CI {0}" -f $run.conclusion)
      Write-Output ('RELAY >> task=weekly_health status=degraded checks=0 guard=PASS note="CI {0}"' -f $run.conclusion)
      exit 2
    }
    Out-Result $step "ok" $ciRunUrl "CI triggered and PASS"
  } else {
    # Just check most recent CI run status
    $list = & gh run list --workflow $CiWorkflowFile --limit 1 --json databaseId,status,conclusion,url,createdAt | ConvertFrom-Json
    if($list -and $list.Count -ge 1){ 
      $run = $list[0]
      $ciRunUrl = $run.url
      $status = if($run.status -eq "completed"){"$($run.conclusion)"}else{"$($run.status)"}
      Out-Result $step "ok" $ciRunUrl ("latest CI: {0}" -f $status)
    } else {
      Out-Result $step "ok" "https://github.com/$Repo/actions" "no recent CI runs found"
    }
  }
} catch { Die $step ("CI check error: {0}" -f $_.Exception.Message) $ciRunUrl }

# --- Step 3: Verify required checks on main ---
$step = 3
try {
  $cmt = & gh api "repos/$Repo/commits/main" | ConvertFrom-Json
  Ensure-Ok (($cmt -ne $null) -and ($null -ne $cmt.sha)) $step "failed to fetch main commit"
  $sha = $cmt.sha

  $cr  = (& gh api "repos/$Repo/commits/$sha/check-runs" | ConvertFrom-Json).check_runs
  Ensure-Ok ($null -ne $cr) $step "failed to fetch check runs"

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
    Out-Result $step "fail" ("https://github.com/$Repo/commit/$sha/checks") ($msg -join " | ")
    Write-Output ('RELAY >> task=weekly_health status=degraded checks={0} guard=ATTN note="{1}"' -f $RequiredChecks.Count, ($msg -join " | "))
    exit 3
  }

  Out-Result $step "ok" ("https://github.com/$Repo/commit/$sha/checks") "all six required checks green on main"
} catch { Die $step ("checks error: {0}" -f $_.Exception.Message) }

# --- Summary ---
Write-Output 'RELAY >> task=weekly_health status=ok checks=6 guard=PASS note="main checks verified; CI status reported"'

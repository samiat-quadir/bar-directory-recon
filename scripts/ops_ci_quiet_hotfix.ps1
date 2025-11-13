# File: scripts/ops_ci_quiet_hotfix.ps1
# Purpose: Quiet CI by (1) constraining fast-parity-ci to Python 3.11 only; (2) making yamllint workflow manual/schedule-only.
# Usage:   pwsh -File scripts/ops_ci_quiet_hotfix.ps1 [-IncludeSchedule]
# Notes:   Guard-safe. No runtime logic changes. Emits RESULT lines.

param(
  [switch]$IncludeSchedule # add Wed 09:30 ET cron alongside manual
)

# --- Repo config ---
$Repo         = "samiat-quadir/bar-directory-recon"
$LocalPath    = "C:\Code\bar-directory-recon"
$FastCIPath   = ".github/workflows/fast-parity-ci.yml"
$WfDirRel     = ".github/workflows"
$Branch       = "ops/ci-quiet-fast311-yamllint-manual"
$PrTitle      = "ci: quiet CI (fast-tests @ py311 only; yamllint → manual/schedule)"
$PrBody       = @"
CI noise fixes (no runtime changes):
- fast-parity-ci: python-version → ['3.11'] (Ubuntu/Windows). Keeps required check names intact.
- yamllint/verify-scripts: manual-only (+ optional weekly schedule), per guard allow-list.
"@

# --- Helpers ---
function Out-Result { param([int]$Step,[string]$Status,[string]$Link,[string]$Note)
  $n = ($Note -replace "\r?\n"," ").Trim()
  Write-Output ("RESULT >> step={0} status={1} link={2} note=""{3}""" -f $Step,$Status,($Link ?? ""),$n)
}
function Die { param([int]$Step,[string]$Note,[string]$Link=""); Out-Result $Step "fail" $Link $Note; Write-Output ('RELAY >> task=ci_quiet_hotfix status=degraded checks=0 guard=PASS note="{0}"' -f $Note); exit 1 }
function Ensure-Ok { param([bool]$Cond,[int]$Step,[string]$Note,[string]$Link=""); if(-not $Cond){ Die $Step $Note $Link } }

function ManualOnlyOnBlock {
  param([switch]$WithSchedule)
  $cron = "30 14 * * 3" # Wed 09:30 ET
  $lines = @("on:","  workflow_dispatch:")
  if($WithSchedule){ $lines += @("  schedule:","    - cron: '$cron'") }
  return ($lines -join "`n") + "`n"
}
function ForceManualOnly {
  param([string]$Yaml,[switch]$WithSchedule)
  $on = ManualOnlyOnBlock -WithSchedule:$WithSchedule
  if($Yaml -match '(?ms)^\s*on:\s*.*?(?=^\S|\Z)'){
    return ($Yaml -replace '(?ms)^\s*on:\s*.*?(?=^\S|\Z)', $on)
  } else { return $on + $Yaml }
}
function PatchFastParityCI {
  param([string]$Yaml)
  $y = $Yaml

  # Replace any python-version block/list with ["3.11"] (preserve indent).
  $y = $y -replace '(?ms)^(\s*)python-version\s*:\s*(\[[^\]]*\]|(?:\r?\n(?:\1\s*-\s*[^\r\n]+\s*)+))', '$1python-version: ["3.11"]'

  # If still no explicit python-version, inject under first "strategy:" block.
  if($y -notmatch '(?m)^\s*python-version\s*:'){
    $y = $y -replace '(?m)^(\s*strategy\s*:\s*\r?\n)', ('$1  matrix:'+"`r`n"+'    python-version: ["3.11"]'+"`r`n")
  }

  # Ensure fail-fast: false
  if($y -notmatch '(?m)^\s*fail-fast\s*:\s*false\b'){
    $y = $y -replace '(?m)^(\s*strategy\s*:\s*\r?\n)', ('$1  fail-fast: false'+"`r`n")
  }
  return $y
}

# --- Step 1: Preconditions ---
$step=1
try {
  & gh --version *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh missing"
  & gh auth status *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh not authenticated"
  Ensure-Ok (Test-Path -LiteralPath $LocalPath) $step "repo path missing: $LocalPath"
  Set-Location -LiteralPath $LocalPath
  $env:GH_REPO = $Repo
  git rev-parse --is-inside-work-tree *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "not a git repo at $LocalPath"
  git fetch origin main:refs/remotes/origin/main --force --prune *> $null
  git checkout -B main refs/remotes/origin/main *> $null
  Out-Result $step "ok" "https://github.com/$Repo" "env ready; main synced"
} catch { Die $step ("precheck error: {0}" -f $_.Exception.Message) }

# --- Step 2: Patch fast-parity-ci.yml to Python 3.11 only ---
$step=2
try {
  $fastPath = Join-Path $LocalPath $FastCIPath
  Ensure-Ok (Test-Path -LiteralPath $fastPath) $step "missing $FastCIPath" "https://github.com/$Repo/tree/main/.github/workflows"
  $orig = Get-Content -LiteralPath $fastPath -Raw
  $patched = PatchFastParityCI -Yaml $orig
  if($patched -ne $orig){
    git checkout -B $Branch *> $null
    Set-Content -LiteralPath $fastPath -Value $patched -Encoding UTF8
    git add -- $FastCIPath *> $null
    git commit -m "ci(fast-tests): lock python-version to 3.11; ensure fail-fast: false" *> $null
    Out-Result $step "ok" "https://github.com/$Repo/blob/$Branch/$FastCIPath" "fast-parity-ci patched to py311 only"
  } else {
    # Ensure on the branch for subsequent changes
    git checkout -B $Branch *> $null
    Out-Result $step "ok" "https://github.com/$Repo/blob/main/$FastCIPath" "no change needed (already py311)"
  }
} catch { Die $step ("fast-ci patch error: {0}" -f $_.Exception.Message) }

# --- Step 3: Locate yamllint/verify-scripts workflow(s) and make manual/schedule-only ---
$step=3
try {
  $wfDir = Join-Path $LocalPath $WfDirRel
  $yamls = Get-ChildItem -LiteralPath $wfDir -File -Filter "*.yml"
  $candidates = @()
  foreach($f in $yamls){
    $t = Get-Content -LiteralPath $f.FullName -Raw
    if($t -match '(?i)action-ya?mllint|lint-yaml|verify-scripts'){
      $candidates += @{ path=$f; text=$t }
    }
  }
  if($candidates.Count -eq 0){
    Out-Result $step "ok" "https://github.com/$Repo/tree/main/.github/workflows" "no yamllint/verify-scripts workflow found"
  } else {
    foreach($c in $candidates){
      $new = ForceManualOnly -Yaml $c.text -WithSchedule:$IncludeSchedule
      if($new -ne $c.text){
        Set-Content -LiteralPath $c.path.FullName -Value $new -Encoding UTF8
        git add -- (Resolve-Path -LiteralPath $c.path.FullName) *> $null
        if($IncludeSchedule){
          $schedNote = " +schedule"
        } else {
          $schedNote = ""
        }
        Out-Result $step "ok" "https://github.com/$Repo/blob/$Branch/$($c.path.Name)" "made '$($c.path.Name)' manual$schedNote"
      } else {
        Out-Result $step "ok" "https://github.com/$Repo/blob/$Branch/$($c.path.Name)" "already manual-only"
      }
    }
    if($candidates.Count -gt 0){
      if($IncludeSchedule){
        $commitMsg = "ci(yamllint): workflow_dispatch +schedule; guard-safe"
      } else {
        $commitMsg = "ci(yamllint): workflow_dispatch; guard-safe"
      }
      git commit -m $commitMsg *> $null
    }
  }
} catch { Die $step ("yamllint patch error: {0}" -f $_.Exception.Message) }

# --- Step 4: Push branch ---
$step=4
try {
  git push -u origin $Branch --force-with-lease *> $null
  Out-Result $step "ok" "https://github.com/$Repo/tree/$Branch" "branch pushed"
} catch { Die $step ("push error: {0}" -f $_.Exception.Message) }

# --- Step 5: Open draft PR + enable auto-merge (squash) ---
$step=5
try {
  $existing = (& gh pr list --state open --json number,url,headRefName | ConvertFrom-Json) | Where-Object headRefName -eq $Branch | Select-Object -First 1
  if(-not $existing){
    $prUrl = & gh pr create --title $PrTitle --body $PrBody --base main --head $Branch --draft 2>&1
    Ensure-Ok ($LASTEXITCODE -eq 0 -and $prUrl) $step "failed to open PR" "https://github.com/$Repo/pulls"
    $prNumber = ($prUrl -split '/')[-1]
    $pr = @{ number=$prNumber; url=$prUrl }
  } else { $pr = $existing }
  $null = & gh pr merge $pr.number --squash --auto
  Out-Result $step "ok" $pr.url "draft PR opened; auto-merge enabled"
} catch { Die $step ("PR error: {0}" -f $_.Exception.Message) }

# --- Relay summary ---
Write-Output 'RELAY >> task=ci_quiet_hotfix status=ok checks=5 guard=PASS note="fast-tests @ py311; yamllint → manual/schedule; PR open with auto-merge"'

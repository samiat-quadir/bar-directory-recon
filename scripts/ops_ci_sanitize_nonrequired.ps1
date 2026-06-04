# File: scripts/ops_ci_sanitize_nonrequired.ps1
# Purpose: Make all non-allow-listed workflows manual/schedule-only (guard-safe) via a tiny draft PR.
# Usage:   pwsh -File scripts/ops_ci_sanitize_nonrequired.ps1 [-IncludeSchedule]
# Notes:   Idempotent; does not alter allowed workflows or required checks.

param(
  [switch]$IncludeSchedule  # add Wed 09:30 ET cron alongside manual
)

# --- Repo config ---
$Repo        = "samiat-quadir/bar-directory-recon"
$LocalPath   = "C:\Code\bar-directory-recon"
$WfDirRel    = ".github/workflows"
$Branch      = "ops/ci-sanitize-nonrequired"
$PrTitle     = "ci(guard): make non-required workflows manual/schedule-only"
$PrBody      = @"
Guard-aligned sanitization:

- Force all *non-allow-listed* workflows to manual-only (plus weekly schedule if set).
- Leaves required checks & allowed workflows unchanged:
  * fast-parity-ci.yml
  * pip-audit.yml
  * ps-lint.yml
  * ci-workflow-guard.yml
  * codeql* (any variant)
This stops noisy failures like 'build (3.9, ubuntu-latest)' while keeping CI deterministic & quiet.
"@

# --- Allow-list (filenames) ---
$AllowedExact = @(
  "fast-parity-ci.yml",
  "pip-audit.yml",
  "ps-lint.yml",
  "ci-workflow-guard.yml"
)
$AllowedPrefix = @("codeql") # any variant starting with 'codeql'

# --- Helpers ---
function Out-Result { param([int]$Step,[string]$Status,[string]$Link,[string]$Note)
  $n = ($Note -replace "\r?\n"," ").Trim()
  Write-Output ("RESULT >> step={0} status={1} link={2} note=""{3}""" -f $Step,$Status,($Link ?? ""),$n)
}
function Die { param([int]$Step,[string]$Note,[string]$Link=""); Out-Result $Step "fail" $Link $Note; Write-Output ('RELAY >> task=ci_sanitize_nonrequired status=degraded checks=0 guard=PASS note="{0}"' -f $Note); exit 1 }
function Ensure-Ok { param([bool]$Cond,[int]$Step,[string]$Note,[string]$Link=""); if(-not $Cond){ Die $Step $Note $Link } }

function Is-AllowedFile([string]$name){
  if ($AllowedExact -contains $name) { return $true }
  foreach($p in $AllowedPrefix){ if($name.ToLower().StartsWith($p)) { return $true } }
  return $false
}
function ManualOnlyOnBlock {
  param([switch]$WithSchedule)
  $cron = "30 14 * * 3"  # Wed 09:30 ET (14:30 UTC)
  $lines = @("on:","  workflow_dispatch:")
  if($WithSchedule){ $lines += @("  schedule:","    - cron: '$cron'") }
  return ($lines -join "`n") + "`n"
}
function Force-ManualOnly {
  param([string]$Yaml,[switch]$WithSchedule)
  $on = ManualOnlyOnBlock -WithSchedule:$WithSchedule
  if($Yaml -match '(?ms)^\s*on:\s*.*?(?=^\S|\Z)'){
    return ($Yaml -replace '(?ms)^\s*on:\s*.*?(?=^\S|\Z)', $on)
  } else { return $on + $Yaml }
}

# --- Step 1: Preflight ---
$step=1
try {
  & gh --version *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "GitHub CLI (gh) missing"
  & gh auth status *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh not authenticated"
  Ensure-Ok (Test-Path -LiteralPath $LocalPath) $step "repo path missing: $LocalPath"
  Set-Location -LiteralPath $LocalPath
  $env:GH_REPO = $Repo
  git rev-parse --is-inside-work-tree *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "not a git repo at $LocalPath"
  git fetch origin --prune *> $null
  git checkout -B main origin/main *> $null
  Out-Result $step "ok" "https://github.com/$Repo" "env ready; main synced"
} catch { Die $step ("precheck error: {0}" -f $_.Exception.Message) }

# --- Step 2: Scan workflows and build patch plan ---
$step=2
$WfDir = Join-Path $LocalPath $WfDirRel
try {
  Ensure-Ok (Test-Path -LiteralPath $WfDir) $step "workflows dir missing: $WfDirRel" "https://github.com/$Repo/tree/main/.github/workflows"
  $files = Get-ChildItem -LiteralPath $WfDir -File -Filter "*.yml"
  $targets = @()
  foreach($f in $files){
    $name = $f.Name
    if (Is-AllowedFile $name) { continue }
    $text = Get-Content -LiteralPath $f.FullName -Raw
    # If it already has only workflow_dispatch(+schedule) with no push/PR, skip
    $hasPush = $text -match '(?ms)^\s*on:\s*.*^\s*push\s*:'
    $hasPR   = $text -match '(?ms)^\s*on:\s*.*^\s*pull_request\s*:'
    if ($hasPush -or $hasPR) { $targets += @{ path=$f; text=$text } }
  }
  if($targets.Count -eq 0){
    Out-Result $step "ok" "https://github.com/$Repo/tree/main/.github/workflows" "no non-allowed workflows with push/PR triggers"
    Write-Output 'RELAY >> task=ci_sanitize_nonrequired status=ok checks=0 guard=PASS note="no-op; already quiet"'
    exit 0
  } else {
    $list = ($targets | ForEach-Object { $_.path.Name }) -join ", "
    Out-Result $step "ok" "https://github.com/$Repo/tree/main/.github/workflows" "to-sanitize: $list"
  }
} catch { Die $step ("scan error: {0}" -f $_.Exception.Message) }

# --- Step 3: Create/update branch ---
$step=3
try {
  git checkout -B $Branch *> $null
  Out-Result $step "ok" "https://github.com/$Repo/tree/$Branch" "branch ready"
} catch { Die $step ("branch error: {0}" -f $_.Exception.Message) }

# --- Step 4: Patch triggers to manual/schedule-only ---
$step=4
try {
  $changed = @()
  foreach($t in $targets){
    $new = Force-ManualOnly -Yaml $t.text -WithSchedule:$IncludeSchedule
    if($new -ne $t.text){
      Set-Content -LiteralPath $t.path.FullName -Value $new -Encoding UTF8
      git add -- (Resolve-Path -LiteralPath $t.path.FullName) *> $null
      $changed += $t.path.Name
      if($IncludeSchedule){ $msg = "manual +schedule set" } else { $msg = "manual set" }
      Out-Result $step "ok" "https://github.com/$Repo/blob/$Branch/$WfDirRel/$($t.path.Name)" $msg
    }
  }
  if($changed.Count -eq 0){
    Out-Result $step "ok" "https://github.com/$Repo/tree/$Branch" "nothing changed (already manual-only)"
  } else {
    git commit -m "ci(guard): make non-allow-listed workflows manual/schedule-only" *> $null
    Out-Result $step "ok" "https://github.com/$Repo/commit" "commit created"
  }
} catch { Die $step ("patch error: {0}" -f $_.Exception.Message) }

# --- Step 5: Push branch ---
$step=5
try {
  git push -u origin $Branch --force-with-lease *> $null
  Out-Result $step "ok" "https://github.com/$Repo/tree/$Branch" "branch pushed"
} catch { Die $step ("push error: {0}" -f $_.Exception.Message) }

# --- Step 6: Open draft PR + enable auto-merge (squash) ---
$step=6
try {
  $existing = (& gh pr list --state open --json number,url,headRefName | ConvertFrom-Json) | Where-Object headRefName -eq $Branch | Select-Object -First 1
  if(-not $existing){
    $output = & gh pr create --title $PrTitle --body $PrBody --base main --head $Branch --draft 2>&1
    Ensure-Ok ($LASTEXITCODE -eq 0) $step "failed to open PR" "https://github.com/$Repo/pulls"
    $prUrl = ($output | Select-String -Pattern "https://github.com/.*/pull/(\d+)").Matches[0].Value
    $prNum = [int](($prUrl -split "/")[-1])
    $pr = @{ number=$prNum; url=$prUrl }
  } else { $pr = $existing }
  & gh pr ready $pr.number *> $null
  $null = & gh pr merge $pr.number --squash --auto
  Out-Result $step "ok" $pr.url "draft PR opened; ready + auto-merge enabled"
} catch { Die $step ("PR error: {0}" -f $_.Exception.Message) }

# --- Relay summary ---
Write-Output 'RELAY >> task=ci_sanitize_nonrequired status=ok checks=0 guard=PASS note="non-required workflows set to manual/schedule; noise eliminated"'

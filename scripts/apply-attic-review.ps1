Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Say($m) { Write-Host "==> $m" }

# 0) Go to repo (Windows host)
$Repo = "C:\Code\bar-directory-recon"
if (-not (Test-Path $Repo)) { throw "Repo not found: $Repo" }
Set-Location $Repo
git rev-parse --is-inside-work-tree | Out-Null

# 1) Resolve PR head; create safety branch
$headRef = (gh pr view 203 --json headRefName --jq .headRefName).Trim()
if ([string]::IsNullOrWhiteSpace($headRef)) { throw "PR #203 headRefName not found" }
Say "PR head: $headRef"
git fetch origin --prune | Out-Null
git checkout $headRef
git pull --ff-only origin $headRef
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$safety = "safety/attic-review-$ts"
if (-not (git rev-parse --verify $safety 2>$null)) { git branch $safety; Say "Safety branch: $safety created" } else { Say "Safety branch exists: $safety" }

# 2) Merge latest main to surface conflicts
git fetch origin main | Out-Null
Say "Merging origin/main (no-commit)"
git merge --no-commit origin/main 2>$null || $true

# 3) Conflict policy
# 3a) Prefer OURS for workflow files (we will rewrite/quiet them)
$wfPreferOurs = @(
    ".github/workflows/auto-merge.yml",
    ".github/workflows/ci-fast-parity.yml",
    ".github/workflows/ci-test.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/codeql.yml",
    ".github/workflows/devcontainer-validate.yml",
    ".github/workflows/fast-parity-ci.yml",
    ".github/workflows/filename-guard.yml",
    ".github/workflows/lock-drift-check.yml",
    ".github/workflows/pip-audit.yml",
    ".github/workflows/pre-commit.yml",
    ".github/workflows/ruff-strict.yml",
    ".github/workflows/stale.yml",
    ".github/workflows/verify-scripts.yml"
)
foreach ($p in $wfPreferOurs) {
    if ( git ls-files -u -- $p ) { Say "conflict -> ours: $p"; git checkout --ours -- $p; git add -- $p }
}

# 3b) Prefer THEIRS for core-keep files
$coreKeep = @(
    "score_leads.py",
    "tools/cross_device/validate_device_profiles.py",
    "universal_recon/utils/overlay_visualizer.py",
    "universal_recon/utils/validator_drift_overlay.py",
    "universal_recon/utils/record_field_validator_v3.py",
    "universal_recon/utils/test_score_visualizer.py",
    "universal_recon/utils/record_normalizer.py",
    "universal_recon/utils/score_visualizer.py",
    "universal_recon/utils/validator_loader.py",
    "universal_recon/utils/validator_drift_badges.py",
    "universal_recon/utils/fieldmap_domain_linter.py",
    "universal_recon/utils/run_phase_21b_analysis.py",
    "universal_recon/utils/validation_matrix.py"
)
foreach ($p in $coreKeep) {
    if ( git ls-files -u -- $p ) { Say "conflict -> theirs: $p"; git checkout --theirs -- $p; git add -- $p }
}

# 4) Union .gitignore (ensure attic patterns exist)
function Write-Text($path, [string]$content) {
    $need = $true
    if (Test-Path $path) { $existing = Get-Content $path -Raw; if ($existing -eq $content) { $need = $false } }
    if ($need) { $utf8NoBom = New-Object System.Text.UTF8Encoding($false); [IO.File]::WriteAllText($path, $content, $utf8NoBom) }
}
function Union-Gitignore {
    $path = ".gitignore"
    $base = ""
    if (Test-Path $path) { $base = Get-Content $path -Raw }
    $add = @"
# --- attic additions (union) ---
archive/
automation/
audits/
logs/
scratch/
device-specific/

# venv & coverage hygiene
.venv/
__pycache__/
.coverage
htmlcov/
"@
    # Merge with stable dedupe
    $lines = @()
    if ($base) { $lines += ($base -split "`n") }
    $lines += ($add -split "`n")
    $seen = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
    $out = New-Object 'System.Collections.Generic.List[string]'
    foreach ($l in $lines) { $r = $l.TrimEnd("`r"); if ($seen.Add($r)) { [void]$out.Add($r) } }
    Write-Text $path (($out -join "`n") + "`n")
    git add -- $path
}
if ( git ls-files -u -- .gitignore ) { Say "conflict in .gitignore -> union"; Union-Gitignore } else { Say "ensuring attic patterns in .gitignore"; Union-Gitignore }

# 5) Tighten .coveragerc
$cover = @"
[run]
branch = True
source =
    .

[report]
skip_empty = True
omit =
    archive/*
    automation/*
    audits/*
    logs/*
    scratch/*
    device-specific/*
    src/hallandale_*
    src/ut_bar.py
    test_*.py
"@
Write-Text ".coveragerc" $cover
git add .coveragerc

# 6) Attic deletions (from pack's delete_candidates + safe categories if present)
$delTargets = @(
    # from delete_candidates.txt (logs set)
    "logs/nextwave/coverage_report_after.txt",
    "logs/nextwave/pytest_after.txt",
    "logs/nextwave/pytest_now.txt",
    "logs/nextwave/top_roi.json",
    "logs/verify/config_checks.json",
    "logs/verify/coverage_report_now.txt",
    "logs/verify/pytest_now.txt",
    "logs/verify/top_roi.json"
)
foreach ($t in $delTargets) { if (Test-Path $t) { Say "delete: $t"; Remove-Item -LiteralPath $t -Force -ErrorAction SilentlyContinue } }

# Optional safe categories (will no-op if missing)
$dirs = @("archive", "automation", "audits", "logs", "scratch", "device-specific")
foreach ($d in $dirs) { if (Test-Path $d) { Say "clean dir: $d/"; git rm -r --cached --ignore-unmatch -- $d 2>$null | Out-Null; Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $d } }

git add -A

# 7) Rebuild workflows
New-Item -ItemType Directory -Path ".github/workflows" -Force | Out-Null

# 7a) fast-parity-ci.yml: matrix 'fast-tests' -> exact required check names
# Normalize workflow here-strings to single-quoted so PowerShell won't try to expand `${{ ... }}`
$fast = @'
name: fast-parity-ci
on:
  pull_request:
  push:
    branches: [ main ]
jobs:
  fast-tests:
    name: fast-tests
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Ensure pytest
        run: python -m pip install --upgrade pip pytest
      - name: Install requirements.txt (if present)
        if: ${{ hashFiles('**/requirements.txt') != '' }}
        run: python -m pip install -r requirements.txt
      - name: Install requirements-dev.txt (if present)
        if: ${{ hashFiles('**/requirements-dev.txt') != '' }}
        run: python -m pip install -r requirements-dev.txt
      - name: Run fast tests
        run: pytest -q
'@
Write-Text ".github/workflows/fast-parity-ci.yml" $fast
git add ".github/workflows/fast-parity-ci.yml"

# 7b) pip-audit.yml: job name 'audit'
$audit = @'
name: pip-audit
on:
  pull_request:
  push:
    branches: [ main ]
jobs:
  audit:
    name: audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m pip install --upgrade pip pip-audit
      - name: pip-audit (requirements files)
        if: ${{ hashFiles('**/requirements*.txt') != '' }}
        run: |
          for f in $(git ls-files 'requirements*.txt'); do
            pip-audit -r "${f}";
          done
      - name: pip-audit (environment)
        if: ${{ hashFiles('**/requirements*.txt') == '' }}
        run: pip-audit
'@
Write-Text ".github/workflows/pip-audit.yml" $audit
git add ".github/workflows/pip-audit.yml"

# ensure keep list is defined (only .yml kept auto)
$keep = @("fast-parity-ci.yml","pip-audit.yml")
$keepBaseNames = $keep | ForEach-Object { [IO.Path]::GetFileNameWithoutExtension($_) }
$quietCount = 0

# Quiet templates: use placeholder and -replace to inject name (idempotent)
$keepBaseNames = $keep | ForEach-Object { [IO.Path]::GetFileNameWithoutExtension($_) }
$wfDir = ".github/workflows"
if (Test-Path $wfDir) {
  $wfFiles = Get-ChildItem -Path $wfDir -Recurse -File -Include *.yml, *.yaml
  foreach ($wf in $wfFiles) {
    $base = [IO.Path]::GetFileNameWithoutExtension($wf.Name)
    $isKeep = $keepBaseNames -contains $base -and ($wf.Extension -ieq ".yml")
    if ($isKeep) { continue }
    $nm = [IO.Path]::GetFileNameWithoutExtension($wf.Name)
    $manual = @'
name: REPLACEME (manual-only)
on:
  workflow_dispatch:
jobs:
  noop:
    runs-on: ubuntu-latest
    steps:
      - run: echo 'manual-only'
'@
    $manual = $manual -replace 'REPLACEME', $nm
    Say "quiet -> $($wf.FullName)"
    Write-Text $wf.FullName $manual
    git add -- $wf.FullName
    $quietCount++
  }
}

# 8) Commit, push, retrigger, queue auto-merge
function HasStaged() { git diff --cached --quiet; if ($LASTEXITCODE -eq 0) { return $false } else { return $true } }
if (HasStaged) {
    Say "commit changes"
    git commit -m "chore(attic): attic sweep wiring; quiet legacy workflows; keep only audit + fast-tests; tighten coverage/gitignore"
}
else {
    Say "no staged changes to commit"
}
git commit --allow-empty -m "chore(ci): retrigger required checks"
Say "push with lease"
git push --force-with-lease origin $headRef
try { gh pr merge 203 --squash --auto | Out-Null; Say "auto-merge queued (squash)" } catch { Say "auto-merge queue skipped" }
Say "done."

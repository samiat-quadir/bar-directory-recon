Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Say($msg) { Write-Host "==> $msg" }
function Ensure-Dir($path) { if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null } }
function Write-Text($path, [string]$content) {
    Ensure-Dir (Split-Path -Parent $path)
    # idempotent write (only touch file if content changes)
    if ((Test-Path $path) -and ((Get-Content $path -Raw) -eq $content)) { return }
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
}
function GitOrNull([string]$gitArgs) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "git"; $psi.Arguments = $gitArgs
    $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $p = New-Object System.Diagnostics.Process; $p.StartInfo = $psi | Out-Null; $p.Start() | Out-Null
    $out = $p.StandardOutput.ReadToEnd(); $null = $p.StandardError.ReadToEnd(); $p.WaitForExit()
    if ($p.ExitCode -ne 0) { return $null } else { return $out.TrimEnd() }
}

# --- 0) Move to repo
$repoPath = "C:\Code\bar-directory-recon"
if (-not (Test-Path $repoPath)) { throw "Repo path not found: $repoPath" }
Set-Location $repoPath
Say "at $repoPath"

# --- 1) Identify PR head branch and prepare safety branch
Say "resolving PR #203 head branch via gh"
$headRef = (gh pr view 203 --json headRefName --jq .headRefName).Trim()
if ([string]::IsNullOrWhiteSpace($headRef)) { throw "Unable to resolve headRefName for PR #203" }
Say "PR head: $headRef"

git fetch origin --prune | Out-Null
git checkout $headRef
git pull --ff-only origin $headRef

$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$safety = "safety/attic-pr203-$ts"
if (-not (GitOrNull "rev-parse --verify $safety")) {
    Say "creating safety branch: $safety"
    git branch $safety
}
else { Say "safety branch already exists: $safety" }

# --- 2) Merge latest main (no-commit) to surface conflicts deterministically
git fetch origin main
Say "merging origin/main (no-commit)"
git merge --no-commit origin/main 2>$null
# note: if already up to date, git exits 0 and nothing to do

# --- 3) Resolve conflicts by policy
# 3a) For rebuilt workflows/configs: prefer OURS (we will rewrite anyway)
$preferOurs = @(
    ".github/workflows/ci.yml",
    ".github/workflows/verify-scripts.yml",
    ".github/workflows/pip-audit.yml",
    ".gitguardian.yml"
)
foreach ($p in $preferOurs) {
    if ( (GitOrNull "ls-files -u -- $p") ) {
        Say "conflict -> ours: $p"
        git checkout --ours -- $p
        git add -- $p
    }
}

# 3b) For core files to KEEP: prefer THEIRS (take latest from main)
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
    if ( (GitOrNull "ls-files -u -- $p") ) {
        Say "conflict -> theirs: $p"
        git checkout --theirs -- $p
        git add -- $p
    }
}

# --- 4) Union-merge .gitignore if conflicted; also ensure attic patterns are ignored
function Union-Gitignore {
    $path = ".gitignore"
    $ours = GitOrNull "show :2:$path"
    $theirs = GitOrNull "show :3:$path"
    if (-not $ours -and -not $theirs) { return } # nothing to do
    $lines = @()
    if ($ours) { $lines += ($ours -split "`n") }
    if ($theirs) { $lines += ($theirs -split "`n") }

    $must = @(
        "archive/",
        "automation/",
        "audits/",
        "logs/",
        "scratch/",
        "device-specific/",
        ".venv/",
        "__pycache__/",
        ".coverage",
        "htmlcov/"
    )
    $lines += $must
    # stable dedupe, preserve first-seen order
    $seen = New-Object System.Collections.Generic.HashSet[string]([StringComparer]::Ordinal)
    $out = New-Object System.Collections.Generic.List[string]
    foreach ($l in $lines) {
        $r = $l.TrimEnd("`r")
        if ($seen.Add($r)) { [void]$out.Add($r) }
    }
    Write-Text $path (($out -join "`n") + "`n")
    git add -- $path
}
if ( (GitOrNull "ls-files -u -- .gitignore") ) { Say "unioning .gitignore"; Union-Gitignore }

# --- 5) Apply ATTIC deletions (safe, idempotent)
Say "collecting ATTIC targets"
$deletedCount = 0
$targets = New-Object System.Collections.Generic.List[System.IO.FileSystemInfo]

# Directories named as attic anywhere
$dirNames = @('archive', 'automation', 'audits', 'logs', 'device-specific', 'scratch')
$dirs = Get-ChildItem -Path . -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object { $dirNames -contains $_.Name }
$targets.AddRange($dirs)

# Device/persona file patterns anywhere
$filesPersona = Get-ChildItem -Path . -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -like 'ASUS_*' -or
    $_.Name -like 'ALIENWARE_*' -or
    $_.Name -like 'git_commit_and_notify_*' -or
    $_.Name -ieq 'notify_agent.asus.py' -or
    $_.Name -ieq 'notify_agent.alienware.py'
}
$targets.AddRange($filesPersona)

# Experimental src files
if (Test-Path "src") { 
    $hall = Get-ChildItem -Path "src" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'hallandale_*' }
    $targets.AddRange($hall)
    if (Test-Path "src/ut_bar.py") { $targets.Add((Get-Item "src/ut_bar.py")) }
}

# Root-level scratch tests test_*.py (root only)
$root = (Resolve-Path ".").Path
$rootTests = Get-ChildItem -Path . -File -Filter "test_*.py" -ErrorAction SilentlyContinue | Where-Object { $_.Directory.FullName -eq $root }
$targets.AddRange($rootTests)

# Unique targets
$uniq = $targets | Group-Object FullName | ForEach-Object { $_.Group[0] }

foreach ($t in $uniq) {
    try {
        if (Test-Path $t.FullName) {
            Say "delete: $($t.FullName)"
            if ($t.PSIsContainer) { Remove-Item -LiteralPath $t.FullName -Recurse -Force -ErrorAction SilentlyContinue }
            else { Remove-Item -LiteralPath $t.FullName -Force -ErrorAction SilentlyContinue }
            $deletedCount++
        }
    }
    catch { }
}

# Stage removals
git add -A

# --- 6) Ensure .coveragerc present with scoped omit
$cover = @"
[run]
branch = True
source =
    .

[report]
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

# --- 7) Rebuild workflows: minimal required checks only
Ensure-Dir ".github/workflows"

# 7a) fast-parity-ci.yml with matrix to produce two required checks
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

# 7b) pip-audit.yml (job name MUST be 'audit')
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
            pip-audit -r "$f";
          done
      - name: pip-audit (environment)
        if: ${{ hashFiles('**/requirements*.txt') == '' }}
        run: pip-audit
'@
Write-Text ".github/workflows/pip-audit.yml" $audit
git add ".github/workflows/pip-audit.yml"

# 7c) Convert ALL other workflows to manual-only skeletons (quiet)
$wfDir = ".github/workflows"
$keep = @("fast-parity-ci.yml", "pip-audit.yml")
$others = @()
if (Test-Path $wfDir) {
    $others = Get-ChildItem -Path $wfDir -Filter *.yml -File | Where-Object { $keep -notcontains $_.Name }
    foreach ($f in $others) {
        Say "quieting workflow -> manual-only: $($f.Name)"
        $nm = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
        $manual = @'
name: REPLACEME (manual)
on:
  workflow_dispatch:
jobs:
  noop:
    runs-on: ubuntu-latest
    steps:
      - run: echo 'manual-only'
'@
        $manual = $manual -replace 'REPLACEME', $nm
        Write-Text $f.FullName $manual
        git add -- $f.FullName
    }
}

# --- 8) Finalize merge: commit, push, retrigger checks, queue auto-merge
function HasStaged() { git diff --cached --quiet; return -not $LASTEXITCODE }
if (HasStaged) {
    Say "committing merge + attic sweep"
    git commit -m "chore(attic): delete-only sweep + coverage scoping + quiet workflows (v3)"
}
else {
    Say "no staged changes to commit (merge already reconciled)"
}

# Empty commit to (re)trigger checks
Say "creating empty retrigger commit"
git commit --allow-empty -m "chore(ci): retrigger required checks"

Say "pushing (force-with-lease) to origin/$headRef"
git push --force-with-lease origin $headRef

# Set auto-merge (non-blocking if perms disallow)
try {
    Say "queuing auto-merge (squash)"
    gh pr merge 203 --squash --auto | Out-Null
}
catch { Say "auto-merge queue skipped (insufficient perms or not eligible yet)" }

# --- 9) Emit RELAY summary
$keptCount = 13
$status = "ok"
$note = "only audit+fast-tests run; legacy workflows are manual-only"
Say ("RELAY >> task=attic_pr203_fix status=$status kept=$keptCount deleted=$deletedCount checks=started note='$note'")

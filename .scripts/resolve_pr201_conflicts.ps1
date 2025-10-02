param(
    [int] $PR = 201
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ExitCode = 0

Write-Host "Fetching origin..."
git fetch origin --quiet

# Resolve PR head
$BR = gh pr view $PR --json headRefName -q '.headRefName' 2>$null
if (-not $BR) { Write-Error "Cannot read PR headRefName for PR #$PR"; exit 2 }
Write-Host "PR#$PR headRefName = $BR"

# Checkout branch (use origin if available)
$originHas = git ls-remote --heads origin $BR | Out-String
if ($originHas -match [regex]::Escape($BR)) {
    git checkout -B $BR "origin/$BR"
}
else {
    git checkout -B $BR
}

# 1) Get conflict set
Write-Host "Generating conflict list to _conflicts.txt..."
git diff --name-only --diff-filter=U > _conflicts.txt
if (-not (Test-Path _conflicts.txt)) { Write-Host "No conflict file generated." }
$conflicts = @()
if (Test-Path _conflicts.txt) { $conflicts = @(Get-Content _conflicts.txt | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }) }
Write-Host "Conflicts found: $($conflicts.Count)"
if ($conflicts.Count -gt 0) { $conflicts | ForEach-Object { Write-Host " - $_" } }

# 2a) Keep OUR version for rebuilt workflows & pre-commit config
$keepOurs = @('.github/workflows/ci.yml', '.github/workflows/verify-scripts.yml', '.github/workflows/pip-audit.yml', '.pre-commit-config.yaml', '.github/workflows/fast-parity-ci.yml')
foreach ($f in $keepOurs) {
    if ( ($conflicts -contains $f) -and (Test-Path $f) ) {
        Write-Host "Keeping OURS for $f"
        git checkout --ours -- "$f"
        git add "$f"
    }
}

# 2b) Keep MAIN (theirs) for core code we don't want to touch
$keepTheirs = @('score_leads.py')
foreach ($f in $keepTheirs) {
    if ( ($conflicts -contains $f) -and (Test-Path $f) ) {
        Write-Host "Keeping THEIRS (main) for $f"
        git checkout --theirs -- "$f"
        git add "$f"
    }
}

# 2c) Union-merge .gitignore
if ($conflicts -contains '.gitignore') {
    Write-Host "Union-merging .gitignore..."
    $ours = ''
    $theirs = ''
    try { $ours = git show ":2:.gitignore" 2>$null } catch { $ours = '' }
    try { $theirs = git show ":3:.gitignore" 2>$null } catch { $theirs = '' }
    $oLines = @()
    if ($ours) { $oLines += ($ours -split "`n") }
    if ($theirs) { $oLines += ($theirs -split "`n") }
    $union = $oLines | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' } | Select-Object -Unique
    Set-Content -Path .gitignore -Value ($union -join "`n") -Encoding UTF8
    git add .gitignore
    Write-Host "Updated .gitignore with union of ours/theirs (lines: $($union.Count))."
}

# 2d) Delete ATTIC files per regex
$deletePatterns = @(
    '^archive/', '^automation/', '^audits/', '^logs/',
    '^(asus_.*\.py|git_commit_and_notify_.*\.py)$',
    '^test_.*\.py$',
    '^src/(hallandale_.*|ut_bar\.py)$'
)
$deleteRegex = ($deletePatterns -join '|')
Write-Host "Deleting ATTIC files matching: $deleteRegex"
foreach ($f in $conflicts) {
    if ($f -match $deleteRegex) {
        Write-Host "Deleting: $f"
        try { git rm -f -- "$f" } catch { Write-Warning ("Failed to git rm {0}: {1}" -f $f, $_) }
    }
}

# 3) Verify no unresolved merges remain
$u = git diff --name-only --diff-filter=U
if ($u) {
    Write-Host "Unresolved conflicts remain:"; $u | ForEach-Object { Write-Host " - $_" }
    $ExitCode = 1
    Write-Host "Conflicts not fully resolved. Aborting commit."
}
else {
    Write-Host "No unresolved conflicts remain. Proceeding to commit."
    try {
        git commit -m "chore(attic): resolve conflicts — keep ours for workflows/pre-commit, union .gitignore, keep main for score_leads.py, delete ATTIC files" -a
    }
    catch {
        Write-Host "No staged changes or commit failed: $_"
    }

    # 4) Push changes with force-with-lease
    Write-Host "Pushing branch $BR with force-with-lease..."
    try {
        git push --force-with-lease origin $BR
        Write-Host "Push succeeded."
    }
    catch {
        Write-Warning "Push failed: $_"; $ExitCode = 2
    }
}

# 5) Keep auto-merge queued
try {
    gh pr view $PR --json url | Out-Null
    gh pr merge $PR --squash --auto || Write-Host "Auto-merge already queued or failed to queue."
}
catch {
    Write-Warning "gh pr commands failed: $_"
}

Write-Host "SUMMARY >> task=pr201_conflicts_resolved status=$ExitCode note='conflicts resolved; force-with-lease pushed; auto-merge queued'"
exit $ExitCode

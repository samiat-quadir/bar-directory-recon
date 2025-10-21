# Attic sweep v3: delete-only sweep cut from fresh origin/main
# Creates _attic_delete.txt, removes files, adds .coveragerc and tightens .gitignore,
# creates a branch from origin/main, opens a PR and queues auto-merge.

param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'   # continue on non-fatal errors

$repo = 'C:\Code\bar-directory-recon'
Write-Output "Working repo: $repo"
Set-Location -Path $repo

Write-Output 'Fetching origin...'
git fetch origin --prune --quiet

Write-Output 'Attempting to close old PR #201 (non-fatal)...'
try {
    gh pr close 201 -c "Superseded by v3: delete-only sweep cut from current main." -q
    Write-Output 'PR #201 closed (or was already closed).'
}
catch {
    Write-Output 'gh pr close failed or PR not open — continuing.'
}

Write-Output 'Checking out fresh main from origin/main...'
git checkout -B main origin/main

$ts = Get-Date -Format yyyyMMdd-HHmm
$BR = "chore/attic-sweep-v3-$ts"
Write-Output "Creating branch: $BR"
git switch -c $BR

Write-Output 'Generating deletion list (_attic_delete.txt)...'
$all = git ls-files
$namepat = '(?i)(ali|ace|asus|alienware|mothership|work[-_ ]?desktop)'
$rules = @(
    '^archive/', '^automation/', '^audits/', '^logs/',
    '^(asus_.*\.py|git_commit_and_notify_.*\.py)$',
    '^test_.*\.py$',
    '^src/(hallandale_.*|ut_bar\.py)$'
)
$drop = @()
foreach ($f in $all) {
    if ($f -like '.github/*' -or $f -like '.devcontainer/*' -or $f -like 'tests/*' -or $f -eq 'pyproject.toml') { continue }
    if ($f -match $namepat) { $drop += $f; continue }
    foreach ($r in $rules) { if ($f -match $r) { $drop += $f; break } }
}

$drop | Set-Content -LiteralPath _attic_delete.txt -Encoding UTF8
Write-Output "Wrote $($drop.Count) entries to _attic_delete.txt"

if ($drop.Count -gt 0) {
    Write-Output 'Applying deletions via git rm -f...'
    # Remove files listed (ignore errors for already-removed entries)
    Get-Content _attic_delete.txt | ForEach-Object {
        $p = $_.Trim()
        if ($p -ne '') {
            try {
                git rm -f -- "$p" 2>$null
                Write-Output "Removed: $p"
            }
            catch {
                Write-Output "git rm failed for: $p -- continuing"
            }
        }
    }
}
else {
    Write-Output 'No files matched deletion rules.'
}

Write-Output 'Creating .coveragerc with scoped omits...'
$cov = @'
[run]
omit =
  archive/*
  automation/*
  audits/*
  logs/*
  scripts/*
  async_*.py
  complete_verification.py
  run_cross_device_task.py
  tools/auto_conflict_resolver.py
[report]
skip_empty = True
'@
Set-Content -LiteralPath .coveragerc -Value $cov -Encoding UTF8

Write-Output 'Ensuring .gitignore exists and contains standard ignores...'
if (-not (Test-Path .gitignore)) { '' | Set-Content -LiteralPath .gitignore -Encoding UTF8 }
$gi = Get-Content .gitignore -Raw
$adds = @('outputs/', 'logs/', '__pycache__/', '*.pyc', '.pytest_tmp/')
foreach ($a in $adds) {
    if ($gi -notmatch [regex]::Escape($a)) { Add-Content -LiteralPath .gitignore "`n$a" }
}

Write-Output 'Staging .coveragerc and .gitignore...'
git add .coveragerc .gitignore

# If there are staged changes, commit. Use git diff --cached --name-only to detect.
$staged = git diff --cached --name-only
if ($staged) {
    Write-Output 'Committing staged changes...'
    git commit -m "chore(attic): delete-only sweep from fresh main + .coveragerc + .gitignore"
}
else {
    Write-Output 'No staged changes to commit.'
}

Write-Output 'Pushing branch to origin...'
try { git push -u origin HEAD -q } catch { Write-Output 'git push failed' }

Write-Output 'Creating PR via gh...'
$prOutput = ''
$prURL = ''
try {
    $prOutput = gh pr create -f -d -t "chore(attic): delete-only sweep + coverage scoping (v3)" -b "Cut from current origin/main to avoid conflicts. Removes ATTIC files; adds .coveragerc & .gitignore." 2>&1
    $m = ($prOutput | Select-String -Pattern 'https?://\S+' -AllMatches)
    if ($m.Matches.Count -gt 0) { $prURL = $m.Matches[0].Value }
    Write-Output "gh pr create output: $prOutput"
}
catch {
    Write-Output 'gh pr create failed.'
}

# Attempt to queue auto-merge (squash). This may fail if auto-merge is not available/allowed.
$mergeStatus = 0
if ($prURL -ne '') {
    Write-Output "Attempting to merge PR $prURL (squash + auto)..."
    try {
        gh pr merge $prURL --squash --auto 2>&1 | ForEach-Object { Write-Output "merge: $_" }
        $mergeStatus = $LASTEXITCODE
    }
    catch {
        Write-Output 'gh pr merge failed or auto-merge was not queued.'
        $mergeStatus = $LASTEXITCODE
    }
}
else {
    Write-Output 'No PR URL; skipping gh pr merge.'
}

# Final summary line as requested
$finalStatus = $mergeStatus
if ($null -eq $finalStatus) { $finalStatus = $LASTEXITCODE }
Write-Output "SUMMARY >> task=attic_v3 status=$finalStatus pr=$prURL note=\"fresh-main delete-only\""

# Exit with final status
exit $finalStatus

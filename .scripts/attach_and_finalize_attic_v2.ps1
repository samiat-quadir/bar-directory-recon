# Safe finalizer for Attic v2 PR #201
# Runs discrete, PowerShell-friendly steps to attach to PR head, untrack logs/outputs,
# commit, rebase/push, and queue auto-merge.

param(
    [int] $PR = 201
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = Resolve-Path -Path '.'
Write-Host "Working directory: $repo"

# 1) Fetch origin
Write-Host "Fetching from origin..."
git fetch origin --quiet

# 1a) discover head branch
Write-Host "Discovering PR #$PR headRefName via gh..."
$head = gh pr view $PR --json headRefName -q '.headRefName' 2>$null
if (-not $head) {
    Write-Error "Cannot read PR headRefName for PR #$PR"
    exit 2
}
Write-Host "PR#$PR headRefName = $head"

# 1b) checkout or create local branch from origin
Write-Host "Checking out branch $head (origin/$head if present)..."
$originRefExists = git ls-remote --heads origin $head | Out-String
if ($originRefExists -match $head) {
    git checkout -B $head "origin/$head"
}
else {
    git checkout -B $head
}

# 2) Untrack artifacts
Write-Host "Identifying tracked files under 'logs' and 'outputs'..."
$trackedRaw = git ls-files -- 'logs' 'outputs' 2>$null
$tracked = $trackedRaw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
if ($tracked.Count -gt 0) {
    Write-Host "Found $($tracked.Count) tracked paths; will untrack them (git rm --cached)..."
    foreach ($f in $tracked) {
        Write-Host "Untracking: $f"
        git rm -f --cached -- "$f"
    }
}
else {
    Write-Host "No tracked files found under 'logs' or 'outputs'."
}

# Ensure .gitignore contains the entries
$gitignorePath = ".gitignore"
if (-not (Test-Path $gitignorePath)) { New-Item -ItemType File -Path $gitignorePath -Force | Out-Null }
$gi = Get-Content $gitignorePath -Raw -ErrorAction SilentlyContinue
$add = @('outputs/', 'logs/', '__pycache__/', '*.pyc', '.pytest_tmp/')
$added = $false
foreach ($a in $add) {
    if ($gi -notmatch [regex]::Escape($a)) {
        Add-Content $gitignorePath "`n$a"
        $added = $true
        Write-Host "Appended to .gitignore: $a"
    }
}
if ($added) { git add .gitignore } else { Write-Host ".gitignore already had entries." }

# 3) Commit changes (if any)
Write-Host "Committing changes (if present)..."
try {
    git commit -m "chore(attic): untrack logs/outputs; tighten .gitignore" | Out-Null
    Write-Host "Committed changes."
}
catch {
    Write-Host "No changes to commit or commit failed: $_"
}

# 4) Rebase onto origin/main if possible
Write-Host "Fetching origin/main and attempting rebase..."
git fetch origin --quiet
try {
    git rebase origin/main
    Write-Host "Rebase onto origin/main completed."
}
catch {
    Write-Host "Rebase failed or not clean; attempting fast-forward merge instead..."
    try {
        git merge --ff-only origin/main
        Write-Host "Fast-forward merge succeeded."
    }
    catch {
        Write-Error "Could not rebase or fast-forward onto origin/main. Resolve locally and re-run. Error: $_"
        exit 3
    }
}

# 5) Push changes
Write-Host "Pushing branch to origin (force-with-lease)..."
try {
    git push --force-with-lease origin $head
    Write-Host "Push succeeded."
}
catch {
    Write-Error "Push failed: $_"
    exit 4
}

# 6) Queue auto-merge
Write-Host "Ensuring PR #$PR is queued for auto-merge (squash)..."
try {
    gh pr merge $PR --squash --auto
    Write-Host "Auto-merge queued for PR #$PR."
}
catch {
    Write-Error "Failed to queue auto-merge via gh: $_"
    exit 5
}

Write-Host "All done."
exit 0

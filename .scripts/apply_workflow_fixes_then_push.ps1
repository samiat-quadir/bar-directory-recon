# Apply workflow changes made in workspace, run YAML checks, commit, rebase, push, and queue auto-merge for PR #201
param(
    [int] $PR = 201
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Fetching origin..."
git fetch origin --quiet

# Resolve PR head
$head = gh pr view $PR --json headRefName -q '.headRefName' 2>$null
if (-not $head) { Write-Error "Cannot read PR headRefName for PR #$PR"; exit 2 }
Write-Host "PR#$PR headRefName = $head"

# Checkout the branch (use origin/branch if it exists)
Write-Host "Checking out branch $head (origin/$head if present)..."
$originRef = git ls-remote --heads origin $head | Out-String
if ($originRef -match [regex]::Escape($head)) {
    git checkout -B $head "origin/$head"
}
else {
    git checkout -B $head
}

# Untrack any tracked artifacts under logs/ and outputs/ (idempotent)
Write-Host "Untracking any tracked files under logs/ and outputs/"
$tracked = @(git ls-files -- 'logs' 'outputs' 2>$null | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
if ($tracked.Count -gt 0) { foreach ($f in $tracked) { Write-Host "Untracking: $f"; git rm -f --cached -- "$f" } } else { Write-Host "No tracked logs/outputs found." }

# Ensure .gitignore entries (append if missing)
$gi = ".gitignore"
if (-not (Test-Path $gi)) { New-Item -ItemType File -Path $gi | Out-Null }
$gicont = Get-Content $gi -Raw -ErrorAction SilentlyContinue
$add = @('outputs/', 'logs/', '__pycache__/', '*.pyc', '.pytest_tmp/')
$added = $false
foreach ($a in $add) { if ($gicont -notmatch [regex]::Escape($a)) { Add-Content $gi "`n$a"; $added = $true; Write-Host "Added $a to .gitignore" } }
if ($added) { git add .gitignore }

# Stage workflow and gitguardian changes
Write-Host "Staging workflow and gitguardian changes..."
git add .github/workflows/*.yml .gitguardian.yml .pre-commit-config.yaml

# Install pre-commit if needed and run check-yaml
if (-not (Test-Path .venv)) { py -3.11 -m venv .venv }
.\.venv\Scripts\python -m pip install -U pip pre-commit

# Run pre-commit check-yaml
Write-Host "Running pre-commit check-yaml..."
.\.venv\Scripts\python -m pre_commit run check-yaml --all-files -v
$exit = $LASTEXITCODE
Write-Host "pre-commit exit: $exit"
if ($exit -ne 0) {
    Write-Host "YAML lint failed; please inspect the pre-commit output above. Aborting before commit/push to avoid bad YAML in repo."
    exit 3
}

# Commit changes if any
try {
    git commit -m "ci: valid YAML; run fast-tests+audit on PRs; make legacy jobs manual-only" -a | Out-Null
    Write-Host "Committed workflow updates."
}
catch {
    Write-Host "No changes to commit or commit failed: $_"
}

# Rebase onto origin/main or fast-forward
git fetch origin --quiet
try { git rebase origin/main; Write-Host "Rebase onto origin/main succeeded." } catch { Write-Host "Rebase failed; attempting fast-forward merge..."; git merge --ff-only origin/main }

# Push
Write-Host "Pushing branch to origin with force-with-lease..."
try { git push --force-with-lease origin $head; Write-Host "Push succeeded." } catch { Write-Error "Push failed: $_"; exit 4 }

# Queue auto-merge
try { gh pr merge $PR --squash --auto; Write-Host "Auto-merge queued for PR #$PR." } catch { Write-Error "Failed to queue auto-merge: $_"; exit 5 }

Write-Host "Finished apply_workflow_fixes_then_push.ps1"
exit 0

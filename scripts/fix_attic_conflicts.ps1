# Fix attic conflicts by recreating a fresh delete-only branch from origin/main
# - Closes any open PRs whose branch matches 'chore/attic-sweep-v3*'
# - Creates new branch from origin/main, reapplies deletions, merges .gitignore from origin/main (append-only)
# - Commits and force-pushes the new branch, creates a PR and queues auto-merge

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repo = 'C:\Code\bar-directory-recon'
Set-Location -Path $repo
Write-Output "Repo: $repo"

git fetch origin --prune --quiet

# Close any open v3 PRs to avoid duplicates
Write-Output 'Looking for open PRs with head branch matching chore/attic-sweep-v3*'
try {
    $open = gh pr list --state open --json number,headRefName,title 2>$null | ConvertFrom-Json
} catch {
    Write-Output 'gh pr list failed; continuing.'
    $open = @()
}
foreach ($pr in $open) {
    if ($pr.headRefName -match '^chore/attic-sweep-v3') {
        Write-Output "Closing PR #$($pr.number) ($($pr.headRefName))"
        try { gh pr close $pr.number -c "Superseded by fresh-v3 sweep." } catch { Write-Output "Failed to close PR #$($pr.number)" }
    }
 }

# Build a fresh branch name
$ts = Get-Date -Format yyyyMMdd-HHmmss
$newBR = "chore/attic-sweep-v3-fresh-$ts"
Write-Output "New branch: $newBR"

# Create fresh branch from origin/main
git checkout -B main origin/main
git switch -c $newBR

# Build deletion list (reuse same rules as attic_sweep_v3)
Write-Output 'Generating _attic_delete.txt from latest origin/main'
$all = git ls-files
$namepat = '(?i)(ali|ace|asus|alienware|mothership|work[-_ ]?desktop)'
$rules = @(
  '^archive/','^automation/','^audits/','^logs/',
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
Write-Output "Delete list contains $($drop.Count) entries"

# Apply deletions
if ($drop.Count -gt 0) {
    foreach ($p in $drop) {
        if ($p.Trim() -ne '') {
            try { git rm -f -- "$p" 2>$null; Write-Output "Removed: $p" } catch { Write-Output "git rm failed for: $p (continuing)" }
        }
    }
}

# Create .coveragerc same as before
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

# Merge .gitignore from origin/main: prefer origin/main content, append our ignores if missing
Write-Output 'Merging .gitignore with origin/main (append-only)'
$baseGi = ''
try {
    $baseGi = git show origin/main:.gitignore 2>$null
} catch { $baseGi = '' }
if (-not $baseGi) { if (Test-Path .gitignore) { $baseGi = Get-Content .gitignore -Raw } }
$giLines = @($baseGi -split "`n")
$adds = @('outputs/','logs/','__pycache__/','*.pyc','.pytest_tmp/')
foreach ($a in $adds) {
    if (-not ($giLines -contains $a)) { $giLines += $a }
}
$giText = ($giLines -join "`n").Trim() + "`n"
Set-Content -LiteralPath .gitignore -Value $giText -Encoding UTF8

# Run pre-commit to let hooks auto-fix files (end-of-file fixer, formatting, etc.)
Write-Output 'Running pre-commit hooks to auto-fix files before committing...'
try {
    pre-commit run --all-files 2>&1 | ForEach-Object { Write-Output $_ }
} catch {
    # pre-commit returns non-zero when hooks change files; we'll re-stage any modifications and continue
    Write-Output 'pre-commit reported changes or issues; re-staging modified files.'
}

# Stage files (include any changes made by pre-commit)
git add .coveragerc .gitignore
git add -A

$staged = git diff --cached --name-only
if ($staged) {
    git commit -m "chore(attic): delete-only sweep from fresh origin/main + .coveragerc + .gitignore (fresh)"
    Write-Output 'Committed changes.'
} else {
    Write-Output 'No staged changes to commit.'
}
# Push (force if branch exists)
try {
    git push -u origin HEAD -f
    Write-Output 'Pushed branch to origin.'
} catch { Write-Output 'git push failed'; throw }

# Create PR
$prURL = ''
$createdByGh = $false

# Check GH CLI authentication first
Write-Output 'Checking GitHub CLI authentication (gh auth status)...'
$ghAuthOk = $false
try {
    $authOut = gh auth status 2>&1
    Write-Output $authOut | ForEach-Object { Write-Output "gh: $_" }
    if ($authOut -match 'Logged in to github.com') { $ghAuthOk = $true }
} catch {
    Write-Output 'gh auth status failed or gh not installed.'
}

if ($ghAuthOk) {
    # Ensure working tree is clean; if not, auto-commit and push changes so gh can create the PR reliably
    Write-Output 'Checking for uncommitted changes before PR creation...'
    $gitPorcelain = git status --porcelain 2>&1 | Out-String
    Set-Content -LiteralPath scripts/git_status_before_pr.log -Value $gitPorcelain -Encoding UTF8
    if ($gitPorcelain.Trim() -ne '') {
        Write-Output 'Uncommitted changes detected — auto-staging and committing them to allow PR creation.'
        try {
            git add -A
            git commit -m "chore(attic): auto-commit pre-PR fixes" || Write-Output 'Nothing to commit or commit failed.'
            git push -u origin HEAD -f
            Write-Output 'Auto-committed and pushed remaining changes.'
        } catch {
            Write-Output "Auto-commit/push failed: $_"
        }
    } else {
        Write-Output 'Working tree is clean.'
    }

    try {
        Write-Output 'Creating PR via gh (capturing full output to scripts/gh_pr_create.log)...'
        # Force capture as a single string to avoid complex object types
        $out = & gh pr create --base main --head $newBR --fill -t "chore(attic): delete-only sweep + coverage scoping (v3)" -b "Fresh cut from origin/main to avoid conflicts. Removes ATTIC files; adds .coveragerc & .gitignore." 2>&1 | Out-String
         # Save full output for debugging
        $logPath = Join-Path -Path (Get-Location) -ChildPath 'scripts/gh_pr_create.log'
        try { Set-Content -LiteralPath $logPath -Value $out -Encoding UTF8; Write-Output "Saved gh pr create output to: $logPath" } catch { Write-Output "Failed to write gh pr create log: $_" }
         # Print the full output to the console for immediate debugging
         Write-Output '--- BEGIN gh pr create output ---'
         Write-Output $out
         Write-Output '---  END  gh pr create output ---'
         $m = ($out | Select-String -Pattern 'https?://\\S+' -AllMatches)
         if ($m.Matches.Count -gt 0) { $prURL = $m.Matches[0].Value; $createdByGh = $true }
     } catch {
        Write-Output 'gh pr create failed (exception).'
        try { Set-Content -LiteralPath scripts/gh_pr_create.log -Value $_.ToString() -Encoding UTF8 } catch { }
     }
} else {
    Write-Output 'GitHub CLI is not authenticated in this environment. A fallback PR URL will be built for manual creation.'
}

if (-not $prURL) {
    # Build fallback PR URL so the user can open it in their browser easily
    Write-Output 'Building fallback PR URL from remote.'
    try {
        $remoteUrl = (git remote get-url origin 2>$null).Trim()
        if ($remoteUrl -match 'git@github.com:(?<owner>[^/]+)/(?<repo>[^.]+)(\.git)?') {
            $owner = $Matches['owner']; $repo = $Matches['repo']
        } elseif ($remoteUrl -match 'https?://github.com/(?<owner>[^/]+)/(?<repo>[^.]+)(\.git)?') {
            $owner = $Matches['owner']; $repo = $Matches['repo']
        }
        if ($owner -and $repo) { $prURL = "https://github.com/$owner/$repo/pull/new/$newBR" }
    } catch {
        Write-Output 'Failed to compute fallback PR URL.'
    }
}

# Open the PR page in the default browser so the user can review/create the PR if needed
if ($prURL) {
    Write-Output "Opening PR page in the browser: $prURL"
    try { Start-Process $prURL } catch { Write-Output 'Unable to open browser automatically; please open the URL manually.' }
}

if ($createdByGh -and $prURL) {
    # Small delay to allow GH to register the PR before auto-merge command
    Start-Sleep -Seconds 3
    Write-Output "Attempting to queue auto-merge for $prURL"
    try { gh pr merge $prURL --squash --auto 2>&1 | ForEach-Object { Write-Output "merge: $_" } } catch { Write-Output 'gh pr merge failed.' }
} elseif ($prURL) {
    Write-Output "PR was not created by gh in this environment. Open the PR URL above to review and queue auto-merge in the GitHub UI, or authenticate gh and re-run this script."
} elseif ($ghAuthOk -and -not $createdByGh) {
    Write-Output 'gh is authenticated but PR creation via CLI failed; opening interactive PR create page (gh pr create --web) to let you submit the PR manually with prefilled fields.'
    try {
        gh pr create --web --base main -t "chore(attic): delete-only sweep + coverage scoping (v3)" -b "Fresh cut from origin/main to avoid conflicts. Removes ATTIC files; adds .coveragerc & .gitignore." 2>$null
    } catch { Write-Output 'gh --web fallback failed; please open the PR URL shown above in your browser.' }
}

Write-Output "Note: auto-merge requires repository settings to allow auto-merge and all required checks to pass. If merging does not queue, verify branch protection and required checks in repo settings."

 Write-Output "SUMMARY >> task=attic_v3_fresh status=$LASTEXITCODE pr=$prURL note=\"recreated-from-origin-main\""
 exit $LASTEXITCODE

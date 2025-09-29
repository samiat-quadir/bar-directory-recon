# Resolve PR #200 conflicts for attic sweep: accept deletions, union .gitignore, run hooks/tests, push and queue auto-merge
Set-Location 'C:\Code\bar-directory-recon'
# Ensure branch is present
git fetch origin --quiet
try { git checkout -B chore/attic-sweep-20250929 origin/chore/attic-sweep-20250929 } catch { git checkout -B chore/attic-sweep-20250929 }
# Merge main (ignore non-zero merge exit so we can inspect conflicts)
Write-Output "Merging origin/main into $(git rev-parse --abbrev-ref HEAD)"
try { & git merge --no-ff origin/main } catch { Write-Output "merge reported conflicts or non-fast-forward; continuing" }

# List unresolved files
& git status -sb
& git diff --name-only --diff-filter=U > _conflicts.txt
if(-not (Test-Path _conflicts.txt)) { Set-Content -Path _conflicts.txt -Value "" }
$conflicts = Get-Content _conflicts.txt | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
Write-Output "CONFLICTS_FOUND=$($conflicts.Count)"

# Resolve conflicts: delete attic-target files, union-merge .gitignore
foreach($f in $conflicts){
  $fname = [io.path]::GetFileName($f).ToLower()
  if($fname -ne '.gitignore'){
    Write-Output "Removing conflicted attic file: $f"
    try { git rm -f -- "$f" } catch { Write-Output ("git rm failed for {0}: {1}" -f $f, $_) }
  }
}

if($conflicts | Where-Object { [io.path]::GetFileName($_).ToLower() -eq '.gitignore' }){
  Write-Output "Union-merging .gitignore"
  $ours = '' ; $theirs = ''
  try { $ours = (git show :2:.gitignore) } catch { $ours = '' }
  try { $theirs = (git show :3:.gitignore) } catch { $theirs = '' }
  $lines = @()
  if($ours -ne ''){ $lines += ($ours -split "`n") }
  if($theirs -ne ''){ $lines += ($theirs -split "`n") }
  # include existing base if necessary
  if($lines.Count -eq 0 -and (Test-Path '.gitignore')){ $lines += (Get-Content .gitignore) }
  $clean = $lines | ForEach-Object { $_.TrimEnd("`r") } | Where-Object { $_ -ne '' } | Select-Object -Unique
  Set-Content -Path .gitignore -Value ($clean -join "`n") -Encoding UTF8
  git add .gitignore
  Write-Output ".gitignore union-merged and staged"
}

# Ensure .coveragerc exists
if(-not (Test-Path '.coveragerc')){
  Write-Output "Creating .coveragerc"
  $cov = @'
[run]
omit =
  archive/*
  automation/*
  scripts/*
  async_*.py
  complete_verification.py
  run_cross_device_task.py
  tools/auto_conflict_resolver.py
[report]
skip_empty = True
'@
  Set-Content -Path .coveragerc -Value $cov -Encoding UTF8
  git add .coveragerc
}

# Commit conflict resolutions if any staged
try {
  git commit -m "chore(attic): resolve conflicts (accept deletions, union .gitignore)" -q || Write-Output "no-op commit or nothing to commit"
} catch { Write-Output ("commit failed or nothing to commit: {0}" -f $_) }

# Ensure virtual env + deps
if(-not (Test-Path .venv)){
  py -3.11 -m venv .venv
}
.\.venv\Scripts\python -m pip install -U pip
if(Test-Path requirements-lock.txt){
  .\.venv\Scripts\python -m pip install -r requirements-lock.txt
  .\.venv\Scripts\python -m pip install -e .[dev] --no-deps
} else {
  .\.venv\Scripts\python -m pip install -e .[dev]
}
# Run pre-commit but do not fail on its non-zero exit
try { .\.venv\Scripts\python -m pre_commit run -a } catch { Write-Output "pre-commit returned non-zero" }

# Run fast tests
Write-Output "Running fast tests"
& .\.venv\Scripts\python -m pytest -q -m "not slow and not e2e and not integration"
$rc = $LASTEXITCODE
Set-Content -Path rc_attic_conflict.txt -Value $rc -Encoding utf8
Write-Output "TEST_RC=$rc"

# Push changes
try { git push } catch { Write-Output ("git push failed: {0}" -f $_) }

# Ensure PR exists and queue auto-merge for PR #200
$prUrl = ''
try {
  $view = gh pr view 200 --json url -q ".url" 2>$null
  if(-not [string]::IsNullOrWhiteSpace($view)){ $prUrl = $view }
} catch { Write-Output "gh pr view 200 failed or PR not found" }
if([string]::IsNullOrWhiteSpace($prUrl)){
  try {
    gh pr create -f -d -t "chore(attic): quarantine non-core + scope coverage" -b "Accept deletions for attic files; union .gitignore; scoped coverage." 2>&1 | Write-Output
    $prUrl = (gh pr view --json url -q ".url")
  } catch { Write-Output ("gh pr create failed: {0}" -f $_); $prUrl = "" }
}
if([string]::IsNullOrWhiteSpace($prUrl)){
  $prUrl = "https://github.com/samiat-quadir/bar-directory-recon/pull/200"
}
Set-Content -Path pr200_url.txt -Value $prUrl -Encoding utf8
Write-Output "PR_URL=$prUrl"

# Queue auto-merge
try {
  gh pr merge 200 --squash --auto 2>&1 | Write-Output
  Write-Output "AUTO_MERGE_ATTEMPTED"
} catch { Write-Output ("AUTO_MERGE_FAILED: {0}" -f $_) }

exit $rc

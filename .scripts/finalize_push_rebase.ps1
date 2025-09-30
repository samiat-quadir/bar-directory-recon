param(
  [string] $Branch = 'chore/attic-sweep-v2-20250929v2'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Checking git status..."
git status --porcelain

Write-Host "Staging any remaining changes..."
git add -A

Write-Host "Committing if needed..."
try { git commit -m 'chore(attic): commit auto-fixes to enable CI' -a | Out-Null; Write-Host 'Committed auto-fixes.' } catch { Write-Host 'No changes to commit.' }

Write-Host "Fetching origin..."
git fetch origin --prune

Write-Host "Attempting to rebase onto origin/$Branch"
try {
  git rebase "origin/$Branch"
  Write-Host 'Rebase succeeded.'
} catch {
  Write-Error "Rebase failed. Please inspect conflicts and resolve manually. Aborting.
$_"
  git rebase --abort 2>$null || Out-Null
  exit 1
}

Write-Host "Pushing with force-with-lease..."
try {
  git push --force-with-lease origin $Branch
  Write-Host 'Push succeeded.'
} catch {
  Write-Error "Push failed: $_"
  exit 2
}

exit 0

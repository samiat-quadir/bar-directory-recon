param(
    [string] $Branch = 'chore/attic-sweep-v2-20250929v2'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Fetching and updating origin/$Branch explicitly..."
# Force fetch remote branch into origin/$Branch ref
git fetch origin +refs/heads/$Branch:refs/remotes/origin/$Branch

Write-Host "Local HEAD:"; git rev-parse --verify --short HEAD
Write-Host "Origin branch name: $Branch"
Write-Host "Origin/$Branch SHA:"; git rev-parse --verify --short origin/$Branch

Write-Host "Showing commits local..origin"
try { git log --oneline origin/$Branch..HEAD -n 10 } catch { Write-Host 'No local commits ahead or origin ref missing' }

Write-Host "Attempting to rebase onto origin/$Branch"
try { git rebase origin/$Branch; Write-Host 'Rebase onto origin branch done.' } catch { Write-Error "Rebase failed: $_"; git rebase --abort 2>$null || Out-Null; exit 1 }

Write-Host "Force-pushing local HEAD to origin/$Branch with lease..."
try { git push --force-with-lease origin HEAD:refs/heads/$Branch; Write-Host 'Push completed.' } catch { Write-Error "Push failed: $_"; exit 2 }

exit 0

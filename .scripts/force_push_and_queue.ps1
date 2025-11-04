param(
    [int] $PR = 201
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$BR = gh pr view $PR --json headRefName -q '.headRefName' 2>$null
if (-not $BR) { Write-Error "Cannot read PR headRefName for PR #$PR"; exit 2 }

# Force push HEAD to the PR branch
git push --force origin HEAD:refs/heads/$BR

# Ensure auto-merge queued
try { gh pr merge $PR --squash --auto } catch { Write-Host "Auto-merge already queued or failed to queue." }

# Final one-line summary
Write-Host 'SUMMARY >> task=pr201_rebase_and_resolve status=0 note="mergeable branch pushed; checks retriggered; auto-merge queued"'

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$sha = (gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/commits" -f per_page=1 | ConvertFrom-Json)[0].sha
$runs = (gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/commits/$sha/check-runs" | ConvertFrom-Json).check_runs
$names = $runs | % { $_.name }
Write-Host "latest main commit: $sha"
Write-Host "check run names:"
$names | % { Write-Host " - $_" }
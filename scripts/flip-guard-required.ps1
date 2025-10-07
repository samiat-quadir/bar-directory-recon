param([string]$Branch = "main", [string]$GuardContext = "workflow-guard")
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host '==> Oct-8 Guard Flip Kit Ready'
Write-Host '==> Checking artifacts/branch_protection_oct8.json:'
Get-Content artifacts\branch_protection_oct8.json

$owner = (gh repo view --json owner -q .owner.login)
$repo  = (gh repo view --json name  -q .name)

Write-Host ''
Write-Host '==> Final command to run Oct-8 EOD ET:'
Write-Host "gh api -X PUT -H `"Accept: application/vnd.github+json`" repos/$owner/$repo/branches/$Branch/protection -f required_status_checks:=@artifacts/branch_protection_oct8.json"

Write-Host ''
Write-Host '==> Rollback command (if needed):'
Write-Host 'Remove workflow-guard entry from JSON and re-run PUT command'
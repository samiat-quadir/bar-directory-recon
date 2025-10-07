param([switch]$Execute, [string]$Branch = "main")
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$owner = (gh repo view --json owner -q .owner.login)
$repo  = (gh repo view --json name  -q .name)
Write-Host "==> Preview payload from artifacts/branch_protection_oct8.json"
if(-not (Test-Path "artifacts\branch_protection_oct8.json")){ throw "Missing artifacts\branch_protection_oct8.json" }
Get-Content artifacts\branch_protection_oct8.json
$cmd = "gh api -X PUT -H `"Accept: application/vnd.github+json`" repos/$owner/$repo/branches/$Branch/protection -f required_status_checks:=@artifacts/branch_protection_oct8.json"
Write-Host "==> Command:"
Write-Host $cmd
if($Execute){ Write-Host "==> Executing flip..."; iex $cmd; Write-Host "==> Done." } else { Write-Host "==> Dry-run (no changes applied)." }

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Set-Location 'C:\Code\bar-directory-recon'
$sha = git rev-parse HEAD
Write-Output "HEAD: $sha"
$json = gh api repos/samiat-quadir/bar-directory-recon/commits/$sha/check-runs --silent
$obj = $json | ConvertFrom-Json
if (-not $obj.check_runs) { Write-Output 'no check_runs' ; exit 0 }
$noncompleted = $obj.check_runs | Where-Object { $_.status -ne 'completed' }
Write-Output 'RUNNING (non-completed) check runs:'
if ($noncompleted.Count -eq 0) { Write-Output '  none' } else { $noncompleted | ForEach-Object { Write-Output ("  " + $_.name + " | status=" + $_.status + " | conclusion=" + (if ($_.conclusion) { $_.conclusion } else { 'null' })) } }
Write-Output ''
Write-Output 'ALL check runs (first 50):'
$obj.check_runs | Select-Object -First 50 | ForEach-Object { Write-Output ("  " + $_.name + " | status=" + $_.status + " | conclusion=" + (if ($_.conclusion) { $_.conclusion } else { 'null' })) }

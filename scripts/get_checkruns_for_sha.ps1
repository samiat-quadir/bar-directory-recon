param([string]$sha)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $sha) { Write-Output 'usage: .\get_checkruns_for_sha.ps1 <sha>'; exit 1 }
Set-Location 'C:\Code\bar-directory-recon'
$json = gh api "/repos/samiat-quadir/bar-directory-recon/commits/$sha/check-runs" --silent
if (-not $json) { Write-Output 'no check-runs JSON'; exit 0 }
$obj = $json | ConvertFrom-Json
Write-Output "Check-runs for $sha (non-completed):"
$nc = $obj.check_runs | Where-Object { $_.status -ne 'completed' }
if (-not $nc -or $nc.Count -eq 0) { Write-Output '  none' } else { $nc | ForEach-Object { Write-Output ("  " + $_.name + " | status=" + $_.status + " | conclusion=" + ($_.conclusion -ne $null ? $_.conclusion : 'null')) } }
Write-Output ''
Write-Output 'All check-runs (first 80):'
$obj.check_runs | Select-Object -First 80 | ForEach-Object { Write-Output ("  " + $_.name + " | status=" + $_.status + " | conclusion=" + ($_.conclusion -ne $null ? $_.conclusion : 'null')) }

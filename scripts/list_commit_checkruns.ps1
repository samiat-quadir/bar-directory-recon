Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Set-Location 'C:\Code\bar-directory-recon'
$pr = 203
$meta = gh pr view $pr --json headRefOid, headRefName --jq '. | {oid:.headRefOid, ref:.headRefName}'
$info = $meta | ConvertFrom-Json
$sha = $info.oid
$ref = $info.ref
Write-Output "PR $pr headRef: $ref ($sha)"
$json = gh api "/repos/samiat-quadir/bar-directory-recon/commits/$sha/check-runs" --silent
if (-not $json) { Write-Output 'No check-runs JSON returned'; exit 0 }
$obj = $json | ConvertFrom-Json
$nonCompleted = $obj.check_runs | Where-Object { $_.status -ne 'completed' }
Write-Output 'RUNNING (non-completed) check runs:'
if (-not $nonCompleted -or $nonCompleted.Count -eq 0) { Write-Output '  none' } else { $nonCompleted | ForEach-Object { Write-Output ("  " + $_.name + " | status=" + $_.status + " | conclusion=" + ($_.conclusion -ne $null ? $_.conclusion : 'null')) } }
Write-Output ''
Write-Output 'ALL check runs (first 80):'
$obj.check_runs | Select-Object -First 80 | ForEach-Object { Write-Output ("  " + $_.name + " | status=" + $_.status + " | conclusion=" + ($_.conclusion -ne $null ? $_.conclusion : 'null')) }
